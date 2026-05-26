import pytest
from unittest.mock import MagicMock, patch

from app.services.discovery.url_validation_service import validate_url


class TestUrlValidationService:
    def test_rejects_invalid_scheme(self):
        mock_db = MagicMock()
        result = validate_url("ftp://example.com/page", mock_db)
        assert result["is_official"] is False
        assert "scheme" in result["message"].lower()

    def test_rejects_social_media_domain(self):
        mock_db = MagicMock()
        result = validate_url("https://facebook.com/university-page", mock_db)
        assert result["is_official"] is False

    def test_rejects_login_path(self):
        mock_db = MagicMock()
        result = validate_url("https://admissions.hku.hk/login", mock_db)
        assert result["is_official"] is False
        assert "login" in result["message"].lower()

    def test_rejects_portal_path(self):
        mock_db = MagicMock()
        result = validate_url("https://admissions.hku.hk/portal/student", mock_db)
        assert result["is_official"] is False

    def test_rejects_payment_path(self):
        mock_db = MagicMock()
        result = validate_url("https://admissions.hku.hk/payment/checkout", mock_db)
        assert result["is_official"] is False

    def test_rejects_third_party_agent_domain(self):
        mock_db = MagicMock()
        result = validate_url("https://some-agency.com/hku-programs", mock_db)
        assert result["is_official"] is False

    def test_rejects_study_abroad_site(self):
        mock_db = MagicMock()
        result = validate_url("https://www.liuxue.com/hku", mock_db)
        assert result["is_official"] is False

    @patch("app.services.discovery.url_validation_service.CrawlSource")
    def test_matches_official_domain_exact(self, MockCrawlSource):
        mock_db = MagicMock()
        mock_source = MagicMock()
        mock_source.official_domain = "admissions.hku.hk"
        mock_source.university_id = 1
        mock_source.region = "Hong Kong"
        mock_source.id = 10
        MockCrawlSource.official_domain.isnot.return_value = True
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_source]

        result = validate_url("https://admissions.hku.hk/tpg/programme-list", mock_db)
        assert result["is_official"] is True
        assert result["matched_university_id"] == 1
        assert result["region"] == "Hong Kong"

    @patch("app.services.discovery.url_validation_service.CrawlSource")
    def test_matches_official_domain_subdomain(self, MockCrawlSource):
        mock_db = MagicMock()
        mock_source = MagicMock()
        mock_source.official_domain = "hku.hk"
        mock_source.university_id = 1
        mock_source.region = "Hong Kong"
        mock_source.id = 10
        MockCrawlSource.official_domain.isnot.return_value = True
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_source]

        result = validate_url("https://admissions.hku.hk/some-page", mock_db)
        assert result["is_official"] is True

    @patch("app.services.discovery.url_validation_service.CrawlSource")
    def test_rejects_unknown_domain(self, MockCrawlSource):
        mock_db = MagicMock()
        mock_source = MagicMock()
        mock_source.official_domain = "hku.hk"
        mock_source.university_id = 1
        mock_source.region = "Hong Kong"
        mock_source.id = 10
        MockCrawlSource.official_domain.isnot.return_value = True
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_source]

        result = validate_url("https://random-site.com/program", mock_db)
        assert result["is_official"] is False
