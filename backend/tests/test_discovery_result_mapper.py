import pytest
from unittest.mock import MagicMock, patch

from app.services.discovery.discovery_result_mapper import (
    map_program_to_result_card,
    map_programs_to_result_cards,
    map_run_to_status_steps,
    map_discovery_result,
    programs_to_advanced_details,
)


class MockUniversity:
    name = "Test University"


class MockProgram:
    def __init__(self):
        self.id = 1
        self.program_name = "MSc Business Analytics"
        self.university = MockUniversity()
        self.degree_type = "MSc"
        self.field = "Business Analytics"
        self.duration = "1 year"
        self.tuition_amount = 300000
        self.tuition_currency = "HKD"
        self.application_deadline = None
        self.deadline_note = None
        self.intake = "2026 Fall"
        self.ielts_requirement = "6.5"
        self.toefl_requirement = "90"
        self.gre_required = False
        self.gmat_required = False
        self.work_experience_required = True
        self.program_url = "https://example.com/program"
        self.source_url = "https://example.com/source"
        self.description = "A great program for analytics."
        self.extraction_confidence = 0.85
        self.review_status = "auto_extracted"
        self.country = "Hong Kong"
        self.city = "Hong Kong"
        self.faculty = "Business School"
        self.study_mode = "Full-time"
        self.raw_text_snapshot = "<html>raw page content</html>" * 100
        self.last_checked = None


class TestDiscoveryResultMapper:
    def test_map_program_hides_raw_text(self):
        p = MockProgram()
        result = map_program_to_result_card(p)
        assert "raw_text_snapshot" not in result
        assert "content_hash" not in result
        assert "parser_version" not in result

    def test_map_program_exposes_user_fields(self):
        p = MockProgram()
        result = map_program_to_result_card(p)
        assert result["id"] == 1
        assert result["program_name"] == "MSc Business Analytics"
        assert result["university_name"] == "Test University"
        assert result["degree_type"] == "MSc"
        assert result["field"] == "Business Analytics"
        assert result["duration"] == "1 year"
        assert result["tuition_amount"] == 300000
        assert result["tuition_currency"] == "HKD"
        assert result["ielts_requirement"] == "6.5"
        assert result["toefl_requirement"] == "90"
        assert result["extraction_confidence"] == 0.85

    def test_map_programs_to_result_cards(self):
        programs = [MockProgram(), MockProgram()]
        result = map_programs_to_result_cards(programs)
        assert len(result) == 2
        for card in result:
            assert "raw_text_snapshot" not in card

    def test_map_run_to_status_steps_queued(self):
        mock_run = MagicMock()
        mock_run.status = "queued"
        steps = map_run_to_status_steps(mock_run)
        assert len(steps) == 6

    def test_map_run_to_status_steps_completed(self):
        mock_run = MagicMock()
        mock_run.status = "completed"
        steps = map_run_to_status_steps(mock_run)
        assert len(steps) == 6
        assert all(s["status"] == "completed" for s in steps)

    def test_map_discovery_result_empty(self):
        mock_run = MagicMock()
        mock_run.id = 1
        mock_run.status = "completed"
        result = map_discovery_result(mock_run, programs=[], candidate_count=0)
        assert result["run_id"] == 1
        assert result["programs"] == []
        assert result["progress_summary"]["programs_extracted"] == 0

    def test_map_discovery_result_with_programs(self):
        mock_run = MagicMock()
        mock_run.id = 1
        mock_run.status = "completed"
        programs = [MockProgram()]
        result = map_discovery_result(
            mock_run, programs=programs, candidate_count=5, success_count=3
        )
        assert result["progress_summary"]["total_candidates"] == 5
        assert result["progress_summary"]["pages_fetched"] == 3
        assert result["progress_summary"]["programs_extracted"] == 1
        assert len(result["programs"]) == 1

    def test_advanced_details_includes_raw_snapshot(self):
        programs = [MockProgram()]
        result = programs_to_advanced_details(programs)
        assert "raw_text_snapshot" in result[0]
        assert len(result[0]["raw_text_snapshot"]) <= 2000

    def test_no_stack_trace_in_output(self):
        p = MockProgram()
        result = map_program_to_result_card(p)
        flat = str(result)
        assert "Traceback" not in flat
        assert "stack trace" not in flat.lower()
