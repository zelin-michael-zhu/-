import pytest
from unittest.mock import MagicMock, patch

from app.services.discovery.discovery_service import analyze_url


class TestDiscoveryService:
    @patch("app.services.discovery.discovery_service.validate_url")
    def test_analyze_url_rejects_non_official(self, mock_validate):
        mock_validate.return_value = {
            "is_official": False,
            "matched_source_id": None,
            "matched_university_id": None,
            "domain": "random.com",
            "region": None,
            "message": "Not an official domain.",
        }
        mock_db = MagicMock()
        result = analyze_url("https://random.com/page", db=mock_db)
        assert result["validation"]["is_official"] is False
