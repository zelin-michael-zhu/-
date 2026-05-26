from collections import defaultdict, deque
from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import CrawlSource, CrawlerRun, RawPage
from app.services.crawler.fetcher_static import fetch_static
from app.services.crawler.link_discovery import discover_candidate_links


def _same_domain(url: str, source_url: str) -> bool:
    return urlparse(url).netloc == urlparse(source_url).netloc


def _save_raw_page(db: Session, source: CrawlSource, fetched: dict) -> RawPage:
    existing = db.query(RawPage).filter(RawPage.url == fetched["url"], RawPage.content_hash == fetched.get("content_hash")).first()
    if existing:
        return existing
    page = RawPage(
        crawl_source_id=source.id,
        university_id=source.university_id,
        url=fetched["url"],
        final_url=fetched.get("final_url"),
        http_status=fetched.get("http_status"),
        content_type=fetched.get("content_type"),
        title=fetched.get("title"),
        html=fetched.get("html"),
        text_content=fetched.get("text_content"),
        content_hash=fetched.get("content_hash"),
        fetched_at=datetime.utcnow(),
        parser_version="v2",
    )
    db.add(page)
    db.flush()
    return page


def run_crawler_pipeline(
    db: Session,
    dry_run: bool = True,
    max_pages_per_domain: int | None = None,
    university_id: int | None = None,
    discover_only: bool = False,
    fetch: bool = False,
    use_playwright: bool = False,
    engine: str = "native_static",
    depth: int | None = None,
) -> dict:
    max_pages = max_pages_per_domain or settings.crawler_max_pages_per_domain
    max_depth = depth if depth is not None else settings.crawler_max_depth
    run = CrawlerRun(
        run_name="crawler dry run" if dry_run else "crawler run",
        status="running",
        started_at=datetime.utcnow(),
        total_sources=0,
        success_count=0,
        skipped_count=0,
        failed_count=0,
        notes="Robots-aware public university crawler. No login, no payment, no form submit.",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    query = db.query(CrawlSource)
    if university_id:
        query = query.filter(CrawlSource.university_id == university_id)
    sources = query.order_by(CrawlSource.id.asc()).all()
    run.total_sources = len(sources)
    candidates: list[dict] = []
    fetched_pages: list[int] = []
    domain_counts: dict[str, int] = defaultdict(int)

    for source in sources:
        queue = deque([(source.url, 0)])
        visited: set[str] = set()
        while queue:
            url, current_depth = queue.popleft()
            if url in visited or current_depth > max_depth:
                continue
            visited.add(url)
            domain = urlparse(url).netloc
            if domain_counts[domain] >= max_pages:
                run.skipped_count += 1
                continue
            if settings.crawler_allowed_domains_only and not _same_domain(url, source.url):
                run.skipped_count += 1
                continue
            if engine == "native_playwright":
                try:
                    from app.services.crawler.fetcher_playwright import fetch_playwright
                    fetched = fetch_playwright(url)
                except ImportError:
                    fetched = fetch_static(url, respect_robots=settings.crawler_respect_robots)
            else:
                fetched = fetch_static(url, respect_robots=settings.crawler_respect_robots)
            if fetched.get("skipped_by_robots"):
                source.allowed_by_robots = False
                source.crawl_status = "skipped"
                source.failure_reason = fetched.get("robots", {}).get("message")
                run.skipped_count += 1
                continue
            if fetched.get("status") != "success":
                run.skipped_count += 1
                continue
            source.allowed_by_robots = True
            source.crawl_status = "discovered" if dry_run or discover_only else "fetched"
            source.last_crawled_at = datetime.utcnow()
            domain_counts[domain] += 1
            discovered = discover_candidate_links(url, fetched.get("html") or "")
            for item in discovered:
                item["source_url"] = source.url
                item["university_id"] = source.university_id
                item["depth"] = current_depth + 1
                candidates.append(item)
                if current_depth + 1 <= max_depth and not dry_run and fetch and item["url"] not in visited:
                    queue.append((item["url"], current_depth + 1))
            if not dry_run and (fetch or not discover_only):
                page = _save_raw_page(db, source, fetched)
                fetched_pages.append(page.id)
                run.success_count += 1
            else:
                run.success_count += 1
            if dry_run or discover_only:
                break
        db.commit()

    run.status = "completed"
    run.completed_at = datetime.utcnow()
    db.commit()
    return {
        "run_id": run.id,
        "dry_run": dry_run,
        "discover_only": discover_only,
        "fetch": fetch,
        "use_playwright": use_playwright,
        "engine": engine,
        "max_pages_per_domain": max_pages,
        "depth": max_depth,
        "candidate_links": candidates[:200],
        "fetched_raw_page_ids": fetched_pages,
        "total_candidates": len(candidates),
        "success_count": run.success_count,
        "skipped_count": run.skipped_count,
        "failed_count": run.failed_count,
    }
