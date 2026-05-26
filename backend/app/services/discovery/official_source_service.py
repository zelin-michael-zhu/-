from sqlalchemy.orm import Session

from app.models import CrawlSource, University

FIELDS = [
    "Business Analytics",
    "Finance",
    "FinTech",
    "Data Science",
    "Management",
    "Marketing Analytics",
    "Economics",
    "Information Systems",
    "Computer Science",
    "Supply Chain",
]


def get_regions(db: Session) -> list[str]:
    rows = (
        db.query(CrawlSource.region)
        .filter(CrawlSource.region.isnot(None), CrawlSource.status == "active")
        .distinct()
        .order_by(CrawlSource.region)
        .all()
    )
    regions = [r[0] for r in rows if r[0]]
    region_order = {"Hong Kong": 0, "Singapore": 1, "United Kingdom": 2, "Australia": 3}
    regions.sort(key=lambda r: region_order.get(r, 99))
    return regions


def get_universities_by_region(region: str, db: Session) -> list[dict]:
    rows = (
        db.query(University)
        .join(CrawlSource, CrawlSource.university_id == University.id)
        .filter(CrawlSource.region == region, CrawlSource.status.in_(["active", "needs_manual_confirmation"]))
        .distinct()
        .order_by(University.name)
        .all()
    )
    if not rows:
        rows = (
            db.query(University)
            .filter(University.country == region)
            .order_by(University.name)
            .all()
        )
    return [
        {
            "id": u.id,
            "name": u.name,
            "short_name": u.short_name,
            "country": u.country,
            "city": u.city,
        }
        for u in rows
    ]


def get_sources_by_university(university_id: int, db: Session) -> list[dict]:
    rows = (
        db.query(CrawlSource)
        .filter(
            CrawlSource.university_id == university_id,
            CrawlSource.status.in_(["active", "needs_manual_confirmation"]),
        )
        .order_by(CrawlSource.source_type, CrawlSource.id)
        .all()
    )
    return [
        {
            "id": s.id,
            "source_name": s.source_name,
            "source_type": s.source_type,
            "url": s.url,
            "status": s.status,
        }
        for s in rows
    ]


def get_fields() -> list[str]:
    return FIELDS
