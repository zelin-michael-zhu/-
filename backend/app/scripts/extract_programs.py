import argparse
from app.core.database import SessionLocal
from app.services.extraction.extraction_pipeline import extract_raw_pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-page-id", type=int)
    parser.add_argument("--university-id", type=int)
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        print(extract_raw_pages(db, limit=args.limit, university_id=args.university_id, raw_page_id=args.raw_page_id, provider=args.provider))
    finally:
        db.close()
