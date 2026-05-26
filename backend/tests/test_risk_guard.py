from app.services.browser_agent.risk_guard import RiskGuard


def test_fill_first_name_low_risk():
    result = RiskGuard().classify("fill first name")
    assert result["risk_level"] == "low"
    assert result["blocked"] is False


def test_save_draft_low_risk():
    result = RiskGuard().classify("save draft")
    assert result["risk_level"] == "low"
    assert result["blocked"] is False


def test_final_submit_blocked():
    result = RiskGuard().classify("final submit application")
    assert result["risk_level"] == "high"
    assert result["blocked"] is True


def test_payment_blocked():
    result = RiskGuard().classify("payment application fee")
    assert result["risk_level"] == "high"
    assert result["blocked"] is True


def test_invite_recommender_requires_approval():
    result = RiskGuard().classify("invite recommender")
    assert result["risk_level"] == "medium"
    assert result["requires_approval"] is True
    assert result["blocked"] is False
