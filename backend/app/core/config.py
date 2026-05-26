from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://applypilot:applypilot_dev_password@localhost:3306/applypilot?charset=utf8mb4"
    backend_cors_origins: str = "http://localhost:3000"
    crawler_user_agent: str = "ApplyPilotResearchBot/0.1 contact=your-email@example.com"
    crawler_delay_seconds: int = 3
    crawler_max_pages_per_domain: int = 30
    crawler_max_depth: int = 2
    crawler_concurrency: int = 1
    crawler_respect_robots: bool = True
    crawler_allowed_domains_only: bool = True
    browser_executor_default: str = "mock"
    opencli_session: str = "applypilot"
    document_storage_dir: str = "./storage/documents"
    document_max_file_size_mb: int = 20
    document_allowed_extensions: str = "pdf,doc,docx,jpg,jpeg,png"
    document_allowed_content_types: str = "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/jpeg,image/png"
    ai_provider: str = "mock"
    extraction_model: str = ""
    recommendation_model: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    discovery_default_engine: str = "native_static"
    firecrawl_api_key: str = ""
    jina_reader_enabled: bool = False
    apify_api_token: str = ""
    discovery_allow_external_engines: bool = False
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
