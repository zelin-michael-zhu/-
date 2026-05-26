from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CrawlSource, CrawlerRun, Program, RawPage, University
from app.services.crawler.crawl_pipeline import run_crawler_pipeline
from app.services.discovery.discovery_result_mapper import map_discovery_result
from app.services.discovery.url_validation_service import validate_url
from app.services.extraction.extraction_pipeline import extract_raw_pages


def find_programs(
    db: Session,
    university_id: int | None = None,
    field: str | None = None,
    url: str | None = None,
    engine: str = "native_static",
    max_pages: int = 10,
) -> dict:
    if url:
        validation = validate_url(url, db)
        if not validation["is_official"]:
            return {
                "run_id": None,
                "status": "rejected",
                "progress_summary": {},
                "programs": [],
                "steps": [],
                "error": validation["message"],
                "validation": validation,
            }
        if validation.get("matched_university_id"):
            university_id = validation["matched_university_id"]

    if not university_id:
        return {
            "run_id": None,
            "status": "error",
            "progress_summary": {},
            "programs": [],
            "steps": [],
            "error": "No university selected and no valid URL provided.",
        }

    uni = db.query(University).filter(University.id == university_id).first()
    uni_name = uni.name if uni else f"University #{university_id}"

    pipeline_result = run_crawler_pipeline(
        db,
        dry_run=False,
        max_pages_per_domain=max_pages,
        university_id=university_id,
        fetch=True,
    )

    run = db.query(CrawlerRun).filter(CrawlerRun.id == pipeline_result["run_id"]).first()
    if run:
        run.run_name = f"discovery: {uni_name} - {field or 'all'}"

    extract_result = extract_raw_pages(
        db,
        limit=max_pages,
        university_id=university_id,
        provider="mock",
    )

    program_ids = extract_result.get("program_ids", [])
    programs: list[Program] = []
    if program_ids:
        programs = db.query(Program).filter(Program.id.in_(program_ids)).all()
        if field:
            programs = [p for p in programs if p.field and field.lower() in p.field.lower()]

    run = db.query(CrawlerRun).filter(CrawlerRun.id == pipeline_result["run_id"]).first()
    db.commit()

    return map_discovery_result(
        run=run,
        programs=programs,
        candidate_count=pipeline_result.get("total_candidates", 0),
        success_count=pipeline_result.get("success_count", 0),
        skipped_count=pipeline_result.get("skipped_count", 0),
        failed_count=pipeline_result.get("failed_count", 0),
    )


def analyze_url(url: str, field: str | None = None, engine: str = "native_static", db: Session | None = None) -> dict:
    validation = validate_url(url, db) if db else None
    return {
        "url": url,
        "validation": validation,
        "field": field,
        "engine": engine,
    }


def get_discovery_results(run_id: int, db: Session) -> dict:
    run = db.query(CrawlerRun).filter(CrawlerRun.id == run_id).first()
    if not run:
        return {
            "run_id": run_id,
            "status": "not_found",
            "progress_summary": {},
            "programs": [],
            "steps": [],
            "error": "Run not found.",
        }

    raw_page_ids = [
        r[0]
        for r in db.query(RawPage.id)
        .filter(
            RawPage.crawl_source_id.in_(
                db.query(CrawlSource.id).filter(
                    CrawlSource.university_id.in_(
                        db.query(CrawlSource.university_id)
                        .filter(CrawlSource.last_crawled_at >= run.started_at)
                        .distinct()
                    )
                )
            )
        )
        .all()
    ]

    programs: list[Program] = []
    if raw_page_ids:
        programs = (
            db.query(Program)
            .filter(Program.source_url.in_(
                db.query(RawPage.url).filter(RawPage.id.in_(raw_page_ids))
            ))
            .all()
        )

    return map_discovery_result(
        run=run,
        programs=programs,
        candidate_count=run.total_sources or 0,
        success_count=run.success_count or 0,
        skipped_count=run.skipped_count or 0,
        failed_count=run.failed_count or 0,
    )
