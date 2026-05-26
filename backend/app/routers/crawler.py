from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import CrawlerRun, RawPage, ExtractionRun
from app.schemas.crawler import CrawlerRequest
from app.services.crawler.crawl_pipeline import run_crawler_pipeline
from app.services.extraction.extraction_pipeline import extract_raw_pages
from app.scripts.seed_universities import seed_universities
from app.scripts.seed_crawl_sources import seed_crawl_sources

router = APIRouter(prefix="/crawler", tags=["crawler"])


@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    universities = seed_universities(db)
    sources = seed_crawl_sources(db)
    return {"universities": universities, "crawl_sources": sources}


@router.post("/seed-sources")
def seed_sources(db: Session = Depends(get_db)):
    return seed(db)


@router.post("/discover")
def discover(payload: CrawlerRequest, db: Session = Depends(get_db)):
    return run_crawler_pipeline(db, dry_run=True, discover_only=True, max_pages_per_domain=payload.max_pages_per_domain)


@router.post("/fetch")
def fetch(payload: CrawlerRequest, db: Session = Depends(get_db)):
    return run_crawler_pipeline(db, dry_run=payload.dry_run, fetch=True, max_pages_per_domain=payload.max_pages_per_domain)


@router.post("/extract")
def extract(payload: dict | None = None, db: Session = Depends(get_db)):
    payload = payload or {}
    return extract_raw_pages(db, limit=payload.get("limit", 20), university_id=payload.get("university_id"), raw_page_id=payload.get("raw_page_id"), provider=payload.get("provider", "mock"))


@router.post("/run-full-pipeline")
def run_full_pipeline(payload: CrawlerRequest, db: Session = Depends(get_db)):
    return run_crawler_pipeline(db, dry_run=payload.dry_run, max_pages_per_domain=payload.max_pages_per_domain)


@router.get("/runs")
def runs(db: Session = Depends(get_db)):
    return db.query(CrawlerRun).order_by(CrawlerRun.id.desc()).limit(50).all()


@router.get("/raw-pages")
def raw_pages(db: Session = Depends(get_db)):
    return db.query(RawPage).order_by(RawPage.id.desc()).limit(50).all()


@router.get("/extraction-runs")
def extraction_runs(db: Session = Depends(get_db)):
    return db.query(ExtractionRun).order_by(ExtractionRun.id.desc()).limit(50).all()
