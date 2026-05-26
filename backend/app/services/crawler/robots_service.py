from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from app.core.config import settings

_CACHE: dict[str, RobotFileParser | None] = {}


def get_robots_parser(url: str) -> RobotFileParser | None:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url in _CACHE:
        return _CACHE[robots_url]
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
        _CACHE[robots_url] = parser
        return parser
    except Exception:
        _CACHE[robots_url] = None
        return None


def check_robots(url: str) -> dict:
    if not settings.crawler_respect_robots:
        return {"allowed": True, "status": "disabled", "message": "robots.txt check disabled by config"}
    parser = get_robots_parser(url)
    if parser is None:
        return {"allowed": False, "status": "unknown", "message": "robots.txt unavailable; skipped by conservative policy"}
    allowed = parser.can_fetch(settings.crawler_user_agent, url)
    return {"allowed": allowed, "status": "allowed" if allowed else "disallowed", "message": "robots.txt checked"}


def allowed_by_robots(url: str) -> bool:
    return bool(check_robots(url)["allowed"])
