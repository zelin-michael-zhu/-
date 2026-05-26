import pytest
from unittest.mock import patch

from app.services.discovery.crawler_engine_router import (
    route_crawl,
    route_crawl_with_fallback,
    get_available_engines,
)


class TestCrawlerEngineRouter:
    def test_native_static_is_default(self):
        result = route_crawl("https://example.com", "native_static")
        assert result["engine"] == "native_static"

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_jina_unavailable_when_disabled(self, mock_settings):
        mock_settings.jina_reader_enabled = False
        result = route_crawl("https://example.com", "jina_reader")
        assert result["status"] == "unavailable"
        assert "not enabled" in result.get("error", "")

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_firecrawl_unavailable_without_api_key(self, mock_settings):
        mock_settings.firecrawl_api_key = ""
        result = route_crawl("https://example.com", "firecrawl")
        assert result["status"] == "unavailable"
        assert "not configured" in result.get("error", "")

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_firecrawl_disabled_by_config(self, mock_settings):
        mock_settings.firecrawl_api_key = "test-key"
        mock_settings.discovery_allow_external_engines = False
        result = route_crawl("https://example.com", "firecrawl")
        assert result["status"] == "unavailable"
        assert "disabled" in result.get("error", "").lower()

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_apify_unavailable_without_token(self, mock_settings):
        mock_settings.apify_api_token = ""
        result = route_crawl("https://example.com", "apify")
        assert result["status"] == "unavailable"

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_apify_disabled_by_config(self, mock_settings):
        mock_settings.apify_api_token = "test-token"
        mock_settings.discovery_allow_external_engines = False
        result = route_crawl("https://example.com", "apify")
        assert result["status"] == "unavailable"

    def test_unknown_engine_returns_fallback(self):
        result = route_crawl("https://example.com", "nonexistent_engine")
        assert result["status"] == "unavailable"
        assert "unknown" in result.get("error", "").lower()

    @patch("app.services.discovery.crawler_engine_router.settings")
    def test_auto_fallback_works(self, mock_settings):
        mock_settings.jina_reader_enabled = False
        mock_settings.firecrawl_api_key = ""
        mock_settings.apify_api_token = ""
        mock_settings.discovery_allow_external_engines = False
        result = route_crawl_with_fallback("https://example.com", "auto")
        assert result["engine"] in ("native_static", "auto")

    def test_get_available_engines_returns_list(self):
        engines = get_available_engines()
        assert isinstance(engines, list)
        assert any(e["name"] == "native_static" for e in engines)
        assert any(e["name"] == "jina_reader" for e in engines)
        assert any(e["name"] == "firecrawl" for e in engines)
        assert any(e["name"] == "apify" for e in engines)
        native = next(e for e in engines if e["name"] == "native_static")
        assert native["available"] is True
