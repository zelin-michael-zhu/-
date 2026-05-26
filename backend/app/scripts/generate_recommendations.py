import argparse

from app.core.database import SessionLocal
from app.services.recommendations.recommendation_service import RecommendationService


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--applicant-id", type=int, required=True)
    parser.add_argument("--provider", default="mock")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        print(RecommendationService(db).generate(args.applicant_id, args.provider))
    finally:
        db.close()
