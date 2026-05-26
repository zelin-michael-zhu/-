from app.services.crawler.link_discovery import discover_candidate_links
from app.services.crawler.page_cleaner import clean_page
from app.services.crawler.program_url_classifier import classify_program_url
from app.services.extraction.mock_llm_extractor import extract_program


def test_link_discovery_scores_and_excludes_urls():
    html = """
    <a href="/programmes/msc-business-analytics">MSc Business Analytics</a>
    <a href="/news/msc-event">News event</a>
    <a href="/login">Portal login</a>
    """
    links = discover_candidate_links("https://example.edu", html)
    assert links
    assert links[0]["url"].endswith("/programmes/msc-business-analytics")
    assert all("login" not in item["url"] for item in links)


def test_page_cleaner_removes_shell_and_keeps_content():
    cleaned = clean_page("<nav>Menu</nav><h1>MSc Finance</h1><script>x()</script><ul><li>IELTS 7.0</li></ul><footer>Footer</footer>")
    assert "Menu" not in cleaned["text_content"]
    assert "x()" not in cleaned["text_content"]
    assert "MSc Finance" in cleaned["text_content"]
    assert "IELTS 7.0" in cleaned["text_content"]


def test_mock_extractor_uses_source_evidence_and_unknowns():
    result = extract_program("MSc Business Analytics\nIELTS 7.0\nApplication deadline: 2027-01-15\nCV and transcript required", "https://example.edu/msc")
    assert result.program_name.startswith("MSc Business Analytics")
    assert result.ielts_requirement == "7.0"
    assert "CV" in result.required_documents
    assert result.source_evidence[0]["source_url"] == "https://example.edu/msc"


def test_crawler_safety_classifier_excludes_portal_payment():
    assert classify_program_url("https://example.edu/login/payment", "payment", "")["is_candidate"] is False
    assert classify_program_url("https://example.edu/programmes/msc-finance", "MSc Finance", "")["is_candidate"] is True
