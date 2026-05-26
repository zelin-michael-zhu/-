from app.models import CrawlerRun, ExtractionRun, Program


DISCOVERY_STEPS_EN = [
    "Checking official source",
    "Reading robots.txt",
    "Discovering program links",
    "Fetching allowed pages",
    "Extracting program details",
    "Preparing results",
]

DISCOVERY_STEPS_ZH = [
    "检查官方来源",
    "读取 robots.txt",
    "发现项目链接",
    "抓取允许页面",
    "抽取项目详情",
    "准备结果",
]


def map_program_to_result_card(program: Program) -> dict:
    return {
        "id": program.id,
        "program_name": program.program_name,
        "university_name": program.university.name if program.university else None,
        "degree_type": program.degree_type,
        "field": program.field,
        "duration": program.duration,
        "tuition_amount": program.tuition_amount,
        "tuition_currency": program.tuition_currency,
        "application_deadline": str(program.application_deadline) if program.application_deadline else None,
        "deadline_note": program.deadline_note,
        "intake": program.intake,
        "ielts_requirement": program.ielts_requirement,
        "toefl_requirement": program.toefl_requirement,
        "gre_required": program.gre_required,
        "gmat_required": program.gmat_required,
        "work_experience_required": program.work_experience_required,
        "program_url": program.program_url,
        "source_url": program.source_url,
        "description_preview": (program.description or "")[:300],
        "extraction_confidence": program.extraction_confidence,
        "review_status": program.review_status,
        "country": program.country,
        "city": program.city,
        "faculty": program.faculty,
        "study_mode": program.study_mode,
    }


def map_programs_to_result_cards(programs: list[Program]) -> list[dict]:
    return [map_program_to_result_card(p) for p in programs]


def map_run_to_status_steps(run: CrawlerRun | None) -> list[dict]:
    if not run:
        steps = DISCOVERY_STEPS_EN
        return [{"step": s, "status": "pending"} for s in steps]

    status_map = {
        "queued": 0,
        "running": 2,
        "completed": 6,
        "failed": -1,
    }
    progress = status_map.get(run.status, 0)

    steps = DISCOVERY_STEPS_EN
    return [
        {"step": step, "status": "completed" if i < progress else "pending"}
        for i, step in enumerate(steps)
    ]


def map_discovery_result(
    run: CrawlerRun | None,
    programs: list[Program],
    candidate_count: int = 0,
    success_count: int = 0,
    skipped_count: int = 0,
    failed_count: int = 0,
) -> dict:
    return {
        "run_id": run.id if run else None,
        "status": run.status if run else "unknown",
        "progress_summary": {
            "total_candidates": candidate_count,
            "pages_fetched": success_count,
            "pages_skipped": skipped_count,
            "pages_failed": failed_count,
            "programs_extracted": len(programs),
        },
        "programs": map_programs_to_result_cards(programs),
        "steps": map_run_to_status_steps(run),
    }


def map_extraction_runs_to_steps(runs: list[ExtractionRun]) -> list[dict]:
    return [
        {
            "id": r.id,
            "status": r.status,
            "confidence": r.confidence,
            "model": r.model_name,
        }
        for r in runs
    ]


def programs_to_advanced_details(programs: list[Program]) -> list[dict]:
    return [
        {
            "id": p.id,
            "program_name": p.program_name,
            "raw_text_snapshot": (p.raw_text_snapshot or "")[:2000] if p.raw_text_snapshot else None,
            "extraction_confidence": p.extraction_confidence,
            "review_status": p.review_status,
            "source_url": p.source_url,
            "last_checked": str(p.last_checked) if p.last_checked else None,
        }
        for p in programs
    ]
