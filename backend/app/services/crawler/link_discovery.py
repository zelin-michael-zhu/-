from urllib.parse import urldefrag, urljoin, urlparse
from bs4 import BeautifulSoup
from app.services.crawler.program_url_classifier import classify_program_url, is_candidate_program_url


def discover_links(base_url: str, html: str) -> list[str]:
    return [item["url"] for item in discover_candidate_links(base_url, html)]


def _normalize_url(base_url: str, href: str) -> str:
    url = urljoin(base_url, href)
    url, _ = urldefrag(url)
    return url


def discover_candidate_links(base_url: str, html: str, same_domain_only: bool = True) -> list[dict]:
    soup = BeautifulSoup(html or "", "html.parser")
    parsed_base = urlparse(base_url)
    links: dict[str, dict] = {}
    for anchor in soup.find_all("a", href=True):
        url = _normalize_url(base_url, anchor["href"])
        parsed = urlparse(url)
        if same_domain_only and parsed.netloc and parsed.netloc != parsed_base.netloc:
            continue
        anchor_text = anchor.get_text(" ", strip=True)
        parent = anchor_text
        classified = classify_program_url(url, anchor_text, parent)
        if classified["is_candidate"] and is_candidate_program_url(url):
            current = links.get(url)
            payload = {
                "url": url,
                "anchor_text": anchor_text,
                "surrounding_text": parent,
                "score": classified["score"],
                "reason": classified["reason"],
            }
            if not current or payload["score"] > current["score"]:
                links[url] = payload
    return sorted(links.values(), key=lambda item: item["score"], reverse=True)
