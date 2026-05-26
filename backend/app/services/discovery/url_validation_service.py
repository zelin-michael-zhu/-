from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models import CrawlSource

BLOCKED_PATH_KEYWORDS = ["login", "portal", "payment", "checkout", "signin", "signup", "register"]
BLOCKED_DOMAIN_KEYWORDS = [
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "weibo.com",
    "youtube.com", "tiktok.com", "reddit.com", "medium.com", "zhihu.com",
    "agent.com", "agency.com", "consultancy.com", "intermediary",
    "liuxue.com", "studyabroad.com", "abroad.com",
]


def validate_url(url: str, db: Session) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {
            "is_official": False,
            "matched_source_id": None,
            "matched_university_id": None,
            "domain": parsed.netloc,
            "region": None,
            "message": "Invalid URL scheme. Only http and https are allowed.",
        }

    netloc = parsed.netloc.lower()

    for keyword in BLOCKED_DOMAIN_KEYWORDS:
        if keyword in netloc:
            return {
                "is_official": False,
                "matched_source_id": None,
                "matched_university_id": None,
                "domain": netloc,
                "region": None,
                "message": "This domain is not an official university website.",
            }

    path = parsed.path.lower()
    for keyword in BLOCKED_PATH_KEYWORDS:
        if keyword in path:
            return {
                "is_official": False,
                "matched_source_id": None,
                "matched_university_id": None,
                "domain": netloc,
                "region": None,
                "message": "Login, portal, and payment pages are not supported.",
            }

    sources = db.query(CrawlSource).filter(CrawlSource.official_domain.isnot(None)).all()
    for source in sources:
        if not source.official_domain:
            continue
        official = source.official_domain.lower()
        if netloc == official or netloc.endswith("." + official):
            return {
                "is_official": True,
                "matched_source_id": source.id,
                "matched_university_id": source.university_id,
                "domain": netloc,
                "region": source.region,
                "message": "This URL matches an official university source.",
            }

    return {
        "is_official": False,
        "matched_source_id": None,
        "matched_university_id": None,
        "domain": netloc,
        "region": None,
        "message": "This domain does not match any known official university source.",
    }
