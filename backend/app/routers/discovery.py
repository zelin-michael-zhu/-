from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discovery import AnalyzeUrlRequest, FindProgramsRequest
from app.services.discovery import official_source_service, url_validation_service
from app.services.discovery.crawler_engine_router import get_available_engines
from app.services.discovery.discovery_service import analyze_url, find_programs, get_discovery_results

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/regions")
def list_regions(db: Session = Depends(get_db)):
    return official_source_service.get_regions(db)


@router.get("/universities")
def list_universities(region: str, db: Session = Depends(get_db)):
    return official_source_service.get_universities_by_region(region, db)


@router.get("/sources")
def list_sources(university_id: int, db: Session = Depends(get_db)):
    return official_source_service.get_sources_by_university(university_id, db)


@router.get("/fields")
def list_fields():
    return official_source_service.get_fields()


@router.get("/engines")
def list_engines():
    return get_available_engines()


@router.post("/find-programs")
def discovery_find_programs(payload: FindProgramsRequest, db: Session = Depends(get_db)):
    result = find_programs(
        db,
        university_id=payload.university_id,
        field=payload.field,
        url=payload.url,
        engine=payload.engine,
        max_pages=payload.max_pages,
    )
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("validation", {}).get("message", "URL not allowed."))
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error."))
    return result


@router.post("/analyze-url")
def discovery_analyze_url(payload: AnalyzeUrlRequest, db: Session = Depends(get_db)):
    validation = url_validation_service.validate_url(payload.url, db)
    return {
        "url": payload.url,
        "validation": validation,
        "field": payload.field,
        "engine": payload.engine,
    }


@router.get("/results/{run_id}")
def discovery_results(run_id: int, db: Session = Depends(get_db)):
    result = get_discovery_results(run_id, db)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Run not found.")
    return result
