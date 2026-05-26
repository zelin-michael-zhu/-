import hashlib
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from app.core.config import settings
from app.services.crawler.page_cleaner import clean_page
from app.services.crawler.robots_service import check_robots

_LAST_FETCH: dict[str, float] = {}


def _rate_limit(domain: str) -> None:
    last = _LAST_FETCH.get(domain)
    if last is not None:
        wait = settings.crawler_delay_seconds - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
    _LAST_FETCH[domain] = time.time()


def fetch_static(url: str, respect_robots: bool = True) -> dict:
    robots = check_robots(url) if respect_robots else {"allowed": True, "status": "disabled"}
    if not robots["allowed"]:
        return {"url": url, "status": "skipped", "skipped_by_robots": True, "robots": robots}
    domain = urlparse(url).netloc
    _rate_limit(domain)
    response = requests.get(url, headers={"User-Agent": settings.crawler_user_agent}, timeout=20)
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        return {"url": url, "final_url": response.url, "http_status": response.status_code, "content_type": content_type, "status": "skipped", "reason": "non-html"}
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    cleaned = clean_page(response.text)
    return {
        "status": "success",
        "url": url,
        "final_url": response.url,
        "http_status": response.status_code,
        "content_type": content_type,
        "title": cleaned.get("title") or title,
        "html": response.text,
        "text_content": cleaned["text_content"],
        "content_hash": hashlib.sha256(response.text.encode("utf-8")).hexdigest(),
        "robots": robots,
    }
