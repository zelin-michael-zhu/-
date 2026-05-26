from pydantic import BaseModel


class CrawlerRequest(BaseModel):
    max_pages_per_domain: int = 10
    dry_run: bool = True
    use_playwright: bool = False
    countries: list[str] = []
    university_ids: list[int] = []
