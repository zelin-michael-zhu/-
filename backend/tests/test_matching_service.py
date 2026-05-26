from types import SimpleNamespace

from app.services.matching.matching_service import category, score_program


def test_demo_applicant_can_generate_match_score():
    applicant = SimpleNamespace(
        gpa_converted_4=3.62,
        gpa_value=3.62,
        target_countries_json='["Hong Kong", "Singapore"]',
        target_fields_json='["Business Analytics", "Finance"]',
        ielts=7.0,
        toefl=None,
    )
    program = SimpleNamespace(country="Hong Kong", field="Business Analytics")
    score, reasons, risks = score_program(applicant, program)
    assert score >= 85
    assert category(score) == "Strong Target"
    assert reasons
    assert risks == []
