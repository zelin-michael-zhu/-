from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class University(Base, TimestampMixin):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    short_name: Mapped[str | None] = mapped_column(String(80), index=True)
    country: Mapped[str] = mapped_column(String(80), index=True)
    city: Mapped[str | None] = mapped_column(String(120))
    official_website: Mapped[str | None] = mapped_column(String(500))
    admissions_website: Mapped[str | None] = mapped_column(String(500))
    ranking_note: Mapped[str | None] = mapped_column(String(255))
    programs = relationship("Program", back_populates="university")


class CrawlSource(Base, TimestampMixin):
    __tablename__ = "crawl_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"))
    source_type: Mapped[str] = mapped_column(String(80), default="program_index")
    url: Mapped[str] = mapped_column(String(700), index=True)
    allowed_by_robots: Mapped[bool | None] = mapped_column(Boolean)
    crawl_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    last_crawled_at: Mapped[DateTime | None] = mapped_column(DateTime)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(String(80), index=True)
    source_name: Mapped[str | None] = mapped_column(String(255))
    official_domain: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class RawPage(Base):
    __tablename__ = "raw_pages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crawl_source_id: Mapped[int | None] = mapped_column(ForeignKey("crawl_sources.id"))
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"), index=True)
    url: Mapped[str] = mapped_column(String(700), index=True)
    final_url: Mapped[str | None] = mapped_column(String(800))
    http_status: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str | None] = mapped_column(String(160))
    title: Mapped[str | None] = mapped_column(String(500))
    html: Mapped[str | None] = mapped_column(LONGTEXT)
    text_content: Mapped[str | None] = mapped_column(LONGTEXT)
    screenshot_path: Mapped[str | None] = mapped_column(String(500))
    content_hash: Mapped[str | None] = mapped_column(String(80), index=True)
    fetched_at: Mapped[DateTime | None] = mapped_column(DateTime)
    parser_version: Mapped[str | None] = mapped_column(String(40), default="v1")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class Program(Base, TimestampMixin):
    __tablename__ = "programs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"), index=True)
    program_name: Mapped[str] = mapped_column(String(255), index=True)
    normalized_program_name: Mapped[str | None] = mapped_column(String(255), index=True)
    degree_type: Mapped[str | None] = mapped_column(String(80))
    field: Mapped[str | None] = mapped_column(String(120), index=True)
    country: Mapped[str | None] = mapped_column(String(80), index=True)
    city: Mapped[str | None] = mapped_column(String(120))
    faculty: Mapped[str | None] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(255))
    study_mode: Mapped[str | None] = mapped_column(String(80))
    duration: Mapped[str | None] = mapped_column(String(120))
    tuition_amount: Mapped[float | None] = mapped_column(Float)
    tuition_currency: Mapped[str | None] = mapped_column(String(16))
    tuition_note: Mapped[str | None] = mapped_column(Text)
    application_deadline: Mapped[Date | None] = mapped_column(Date, index=True)
    deadline_note: Mapped[str | None] = mapped_column(Text)
    intake: Mapped[str | None] = mapped_column(String(120))
    application_url: Mapped[str | None] = mapped_column(String(800))
    program_url: Mapped[str | None] = mapped_column(String(800))
    requirements_url: Mapped[str | None] = mapped_column(String(800))
    curriculum_url: Mapped[str | None] = mapped_column(String(800))
    source_url: Mapped[str | None] = mapped_column(String(800))
    description: Mapped[str | None] = mapped_column(Text)
    curriculum_summary: Mapped[str | None] = mapped_column(Text)
    career_summary: Mapped[str | None] = mapped_column(Text)
    language_requirement: Mapped[str | None] = mapped_column(Text)
    ielts_requirement: Mapped[str | None] = mapped_column(String(80))
    toefl_requirement: Mapped[str | None] = mapped_column(String(80))
    gre_required: Mapped[bool | None] = mapped_column(Boolean)
    gmat_required: Mapped[bool | None] = mapped_column(Boolean)
    gpa_requirement: Mapped[str | None] = mapped_column(String(120))
    work_experience_required: Mapped[bool | None] = mapped_column(Boolean)
    recommendation_letters_required: Mapped[int | None] = mapped_column(Integer)
    personal_statement_required: Mapped[bool | None] = mapped_column(Boolean)
    cv_required: Mapped[bool | None] = mapped_column(Boolean)
    transcript_required: Mapped[bool | None] = mapped_column(Boolean)
    application_fee: Mapped[float | None] = mapped_column(Float)
    application_fee_currency: Mapped[str | None] = mapped_column(String(16))
    scholarship_info: Mapped[str | None] = mapped_column(Text)
    raw_text_snapshot: Mapped[str | None] = mapped_column(LONGTEXT)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, index=True)
    review_status: Mapped[str] = mapped_column(String(40), default="auto_extracted", index=True)
    last_checked: Mapped[DateTime | None] = mapped_column(DateTime)
    university = relationship("University", back_populates="programs")


class ProgramRequirement(Base, TimestampMixin):
    __tablename__ = "program_requirements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    requirement_type: Mapped[str] = mapped_column(String(80))
    requirement_name: Mapped[str] = mapped_column(String(160))
    requirement_value: Mapped[str | None] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(800))


class ProgramDeadline(Base, TimestampMixin):
    __tablename__ = "program_deadlines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    round_name: Mapped[str | None] = mapped_column(String(120))
    deadline_date: Mapped[Date | None] = mapped_column(Date)
    deadline_text: Mapped[str | None] = mapped_column(String(255))
    intake: Mapped[str | None] = mapped_column(String(120))
    is_international: Mapped[bool | None] = mapped_column(Boolean)
    source_url: Mapped[str | None] = mapped_column(String(800))


class ProgramDocument(Base, TimestampMixin):
    __tablename__ = "program_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(120))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    quantity: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(800))


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_page_id: Mapped[int | None] = mapped_column(ForeignKey("raw_pages.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(120), default="mock-regex")
    extractor_version: Mapped[str] = mapped_column(String(40), default="v1")
    status: Mapped[str] = mapped_column(String(40), default="success", index=True)
    extracted_json: Mapped[str | None] = mapped_column(LONGTEXT)
    confidence: Mapped[float | None] = mapped_column(Float)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class CrawlerRun(Base):
    __tablename__ = "crawler_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="queued", index=True)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime)
    total_sources: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)


class Applicant(Base, TimestampMixin):
    __tablename__ = "applicants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    university: Mapped[str | None] = mapped_column(String(255))
    college: Mapped[str | None] = mapped_column(String(255))
    major: Mapped[str | None] = mapped_column(String(160))
    degree: Mapped[str | None] = mapped_column(String(80))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    gpa_value: Mapped[float | None] = mapped_column(Float)
    gpa_scale: Mapped[float | None] = mapped_column(Float)
    gpa_converted_4: Mapped[float | None] = mapped_column(Float)
    ranking: Mapped[str | None] = mapped_column(String(80))
    ielts: Mapped[float | None] = mapped_column(Float)
    toefl: Mapped[int | None] = mapped_column(Integer)
    gre: Mapped[int | None] = mapped_column(Integer)
    gmat: Mapped[int | None] = mapped_column(Integer)
    target_countries_json: Mapped[str | None] = mapped_column(LONGTEXT)
    target_fields_json: Mapped[str | None] = mapped_column(LONGTEXT)
    preference_priority: Mapped[str | None] = mapped_column(String(80))
    budget: Mapped[float | None] = mapped_column(Float)
    experiences_json: Mapped[str | None] = mapped_column(LONGTEXT)
    awards_json: Mapped[str | None] = mapped_column(LONGTEXT)
    papers_json: Mapped[str | None] = mapped_column(LONGTEXT)


class ProgramMatch(Base, TimestampMixin):
    __tablename__ = "program_matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    match_score: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(80), index=True)
    reasons_json: Mapped[str | None] = mapped_column(LONGTEXT)
    risks_json: Mapped[str | None] = mapped_column(LONGTEXT)
    program = relationship("Program")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int | None] = mapped_column(ForeignKey("applicants.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="missing", index=True)
    file_path: Mapped[str | None] = mapped_column(String(500))
    original_filename: Mapped[str | None] = mapped_column(String(255))
    stored_filename: Mapped[str | None] = mapped_column(String(255))
    content_type: Mapped[str | None] = mapped_column(String(160))
    file_size: Mapped[int | None] = mapped_column(Integer)
    file_hash: Mapped[str | None] = mapped_column(String(80), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    used_by_json: Mapped[str | None] = mapped_column(LONGTEXT)
    notes: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[DateTime | None] = mapped_column(DateTime)
    last_updated: Mapped[DateTime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    status: Mapped[str] = mapped_column(String(60), default="Not Started", index=True)
    deadline: Mapped[Date | None] = mapped_column(Date)
    missing_items_json: Mapped[str | None] = mapped_column(LONGTEXT)
    notes: Mapped[str | None] = mapped_column(Text)
    last_activity: Mapped[DateTime | None] = mapped_column(DateTime)
    program = relationship("Program")


class EmailItem(Base):
    __tablename__ = "email_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int | None] = mapped_column(ForeignKey("applicants.id"), index=True)
    sender: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(500))
    body_preview: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), index=True)
    related_program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    suggested_action: Mapped[str | None] = mapped_column(Text)
    received_at: Mapped[DateTime | None] = mapped_column(DateTime)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class BrowserTask(Base, TimestampMixin):
    __tablename__ = "browser_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int | None] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"), index=True)
    task_name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    current_step: Mapped[str | None] = mapped_column(String(255))
    logs_json: Mapped[str | None] = mapped_column(LONGTEXT)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80), default="mock")
    recommendations_json: Mapped[str | None] = mapped_column(LONGTEXT)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class ApplicationPlan(Base, TimestampMixin):
    __tablename__ = "application_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    selected_program_ids_json: Mapped[str | None] = mapped_column(LONGTEXT)
    generated_recommendations_json: Mapped[str | None] = mapped_column(LONGTEXT)
    global_missing_documents_json: Mapped[str | None] = mapped_column(LONGTEXT)
    next_actions_json: Mapped[str | None] = mapped_column(LONGTEXT)


class AgentTask(Base, TimestampMixin):
    __tablename__ = "agent_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_plan_id: Mapped[int | None] = mapped_column(ForeignKey("application_plans.id"), index=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    risk_level: Mapped[str | None] = mapped_column(String(40), index=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    input_json: Mapped[str | None] = mapped_column(LONGTEXT)
    result_json: Mapped[str | None] = mapped_column(LONGTEXT)
    logs_json: Mapped[str | None] = mapped_column(LONGTEXT)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int | None] = mapped_column(ForeignKey("applicants.id"), index=True)
    application_plan_id: Mapped[int | None] = mapped_column(ForeignKey("application_plans.id"), index=True)
    agent_task_id: Mapped[int | None] = mapped_column(ForeignKey("agent_tasks.id"), index=True)
    actor: Mapped[str] = mapped_column(String(40), default="system", index=True)
    action: Mapped[str] = mapped_column(String(160), index=True)
    risk_level: Mapped[str | None] = mapped_column(String(40), index=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    message: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(LONGTEXT)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class PortalSession(Base, TimestampMixin):
    __tablename__ = "portal_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"), index=True)
    executor_type: Mapped[str] = mapped_column(String(40), default="mock", index=True)
    portal_url: Mapped[str | None] = mapped_column(String(900))
    status: Mapped[str] = mapped_column(String(60), default="not_started", index=True)
    last_page_url: Mapped[str | None] = mapped_column(String(900))
    last_snapshot_text: Mapped[str | None] = mapped_column(LONGTEXT)
    last_screenshot_path: Mapped[str | None] = mapped_column(String(700))


class EmailTrackingRule(Base, TimestampMixin):
    __tablename__ = "email_tracking_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"), index=True)
    sender_pattern: Mapped[str | None] = mapped_column(String(255))
    subject_keywords_json: Mapped[str | None] = mapped_column(LONGTEXT)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class PendingAction(Base, TimestampMixin):
    __tablename__ = "pending_actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"), index=True)
    portal_session_id: Mapped[int | None] = mapped_column(ForeignKey("portal_sessions.id"), index=True)
    agent_task_id: Mapped[int | None] = mapped_column(ForeignKey("agent_tasks.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(80), index=True)
    target_label: Mapped[str | None] = mapped_column(String(255))
    target_selector: Mapped[str | None] = mapped_column(String(500))
    proposed_value: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(40), default="low", index=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    reason: Mapped[str | None] = mapped_column(Text)
