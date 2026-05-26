INCLUDE = ["master", "masters", "msc", "ma", "postgraduate", "taught", "programme", "program", "course", "business analytics", "finance", "fintech", "data science", "management", "marketing", "economics", "information systems", "computer science", "supply chain"]
EXCLUDE = ["undergraduate", "phd", "research degree", "news", "events", "staff", "alumni", "login", "portal", "payment", "apply payment", "apply-now-payment", "facebook", "twitter", "linkedin", "instagram", ".zip", ".js", ".css"]


def is_candidate_program_url(url: str) -> bool:
    lowered = url.lower()
    return any(word in lowered for word in INCLUDE) and not any(word in lowered for word in EXCLUDE)


def classify_program_url(url: str, anchor_text: str = "", surrounding_text: str = "") -> dict:
    text = f"{url} {anchor_text} {surrounding_text}".lower()
    score = 0
    reasons: list[str] = []
    for word in INCLUDE:
        if word in text:
            score += 10
            reasons.append(f"includes {word}")
    for word in EXCLUDE:
        if word in text:
            score -= 30
            reasons.append(f"excludes {word}")
    if ".pdf" in text:
        score -= 10
        reasons.append("pdf skipped by default")
    return {"is_candidate": score >= 10, "score": max(score, 0), "reason": "; ".join(reasons) or "No programme signal"}
