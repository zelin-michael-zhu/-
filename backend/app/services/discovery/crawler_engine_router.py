import requests
from urllib.parse import urlparse

from app.core.config import settings
from app.services.crawler.fetcher_static import fetch_static


def _fallback_result(engine: str, reason: str) -> dict:
    return {
        "engine": engine,
        "status": "unavailable",
        "html": None,
        "text_content": None,
        "title": None,
        "url": None,
        "http_status": None,
        "error": reason,
        "fallback_available": engine not in ("jina_reader", "firecrawl", "apify"),
    }


def _jina_fetch(url: str) -> dict:
    if not settings.jina_reader_enabled:
        return _fallback_result("jina_reader", "Jina Reader is not enabled. Set JINA_READER_ENABLED=true.")
    try:
        jina_url = f"https://r.jina.ai/{url}"
        resp = requests.get(jina_url, timeout=30, headers={"User-Agent": settings.crawler_user_agent})
        if resp.status_code != 200:
            return _fallback_result("jina_reader", f"Jina Reader returned HTTP {resp.status_code}")
        text = resp.text
        return {
            "engine": "jina_reader",
            "status": "success",
            "html": None,
            "text_content": text,
            "title": None,
            "url": url,
            "http_status": 200,
        }
    except Exception as exc:
        return _fallback_result("jina_reader", f"Jina Reader request failed: {exc}")


def _firecrawl_fetch(url: str) -> dict:
    if not settings.firecrawl_api_key:
        return _fallback_result("firecrawl", "Firecrawl API key is not configured.")
    if not settings.discovery_allow_external_engines:
        return _fallback_result("firecrawl", "External engines are disabled by configuration.")
    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "formats": ["markdown"]},
            headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
            timeout=60,
        )
        if resp.status_code != 200:
            return _fallback_result("firecrawl", f"Firecrawl API returned HTTP {resp.status_code}")
        data = resp.json()
        markdown = data.get("data", {}).get("markdown", "")
        return {
            "engine": "firecrawl",
            "status": "success",
            "html": data.get("data", {}).get("html"),
            "text_content": markdown,
            "title": data.get("data", {}).get("metadata", {}).get("title"),
            "url": url,
            "http_status": 200,
        }
    except Exception as exc:
        return _fallback_result("firecrawl", f"Firecrawl request failed: {exc}")


def _apify_fetch(url: str) -> dict:
    if not settings.apify_api_token:
        return _fallback_result("apify", "Apify API token is not configured.")
    if not settings.discovery_allow_external_engines:
        return _fallback_result("apify", "External engines are disabled by configuration.")
    return _fallback_result("apify", "Apify engine is not implemented yet.")


ENGINES = {
    "native_static": None,
    "native_playwright": None,
    "jina_reader": _jina_fetch,
    "firecrawl": _firecrawl_fetch,
    "apify": _apify_fetch,
}

ENGINE_PRIORITY = ["native_static", "jina_reader", "firecrawl", "native_playwright", "apify"]


def get_available_engines() -> list[dict]:
    result = []
    for name in ENGINE_PRIORITY:
        if name == "native_static":
            result.append({"name": name, "available": True, "label": "Native Static"})
        elif name == "native_playwright":
            result.append({"name": name, "available": True, "label": "Native Playwright"})
        elif name == "jina_reader":
            result.append({
                "name": name,
                "available": settings.jina_reader_enabled,
                "label": "Jina Reader",
            })
        elif name == "firecrawl":
            available = bool(settings.firecrawl_api_key and settings.discovery_allow_external_engines)
            result.append({"name": name, "available": available, "label": "Firecrawl"})
        elif name == "apify":
            available = bool(settings.apify_api_token and settings.discovery_allow_external_engines)
            result.append({"name": name, "available": available, "label": "Apify"})
    return result


def route_crawl(url: str, engine: str = "native_static") -> dict:
    engine = engine or "native_static"
    if engine not in ENGINES:
        return _fallback_result(engine, f"Unknown engine: {engine}")

    if engine == "native_static":
        fetched = fetch_static(url, respect_robots=settings.crawler_respect_robots)
        if fetched.get("skipped_by_robots"):
            return _fallback_result("native_static", f"Blocked by robots.txt: {fetched.get('robots', {}).get('message', '')}")
        if fetched.get("status") != "success":
            return _fallback_result("native_static", fetched.get("error", "Native static fetch failed"))
        return {
            "engine": "native_static",
            "status": "success",
            "html": fetched.get("html"),
            "text_content": fetched.get("text_content"),
            "title": fetched.get("title"),
            "url": fetched.get("url"),
            "http_status": fetched.get("http_status"),
        }

    if engine == "native_playwright":
        try:
            from app.services.crawler.fetcher_playwright import fetch_playwright
            fetched = fetch_playwright(url)
            if fetched.get("status") != "success":
                return _fallback_result("native_playwright", fetched.get("error", "Playwright fetch failed"))
            return {
                "engine": "native_playwright",
                "status": "success",
                "html": fetched.get("html"),
                "text_content": fetched.get("text_content"),
                "title": fetched.get("title"),
                "url": fetched.get("url"),
                "http_status": fetched.get("http_status"),
            }
        except ImportError:
            return _fallback_result("native_playwright", "Playwright is not installed.")

    handler = ENGINES.get(engine)
    if handler:
        return handler(url)

    return _fallback_result(engine, f"Engine '{engine}' is not implemented.")


def route_crawl_with_fallback(url: str, engine: str = "auto") -> dict:
    if engine == "auto":
        for name in ENGINE_PRIORITY:
            if name == "jina_reader" and not settings.jina_reader_enabled:
                continue
            if name == "firecrawl" and not (
                settings.firecrawl_api_key and settings.discovery_allow_external_engines
            ):
                continue
            if name == "apify" and not (
                settings.apify_api_token and settings.discovery_allow_external_engines
            ):
                continue
            result = route_crawl(url, name)
            if result.get("status") == "success":
                return result
        result = route_crawl(url, "native_static")
        if result.get("status") == "success":
            return result
        return {
            "engine": "auto",
            "status": "failed",
            "html": None,
            "text_content": None,
            "title": None,
            "url": url,
            "http_status": None,
            "error": "All engines failed.",
            "fallback_available": False,
        }
    return route_crawl(url, engine)
