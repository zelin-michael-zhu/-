import argparse
from app.core.database import SessionLocal
from app.services.crawler.crawl_pipeline import run_crawler_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--university-id", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--discover-only", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--use-playwright", action="store_true")
    parser.add_argument("--max-pages-per-domain", type=int, default=10)
    parser.add_argument("--depth", type=int)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        print(run_crawler_pipeline(
            db,
            dry_run=args.dry_run,
            max_pages_per_domain=args.max_pages_per_domain,
            university_id=args.university_id,
            discover_only=args.discover_only,
            fetch=args.fetch,
            use_playwright=args.use_playwright,
            depth=args.depth,
        ))
    finally:
        db.close()
