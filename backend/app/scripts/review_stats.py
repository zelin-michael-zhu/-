from app.core.database import SessionLocal
from app.models import Program


if __name__ == "__main__":
    db = SessionLocal()
    try:
        rows = db.query(Program.review_status, Program.id).all()
        stats = {}
        for status, _ in rows:
            stats[status] = stats.get(status, 0) + 1
        print(stats)
    finally:
        db.close()
