from app.core.database import SessionLocal
from app.models import University

UNIVERSITIES = [
    ("The University of Hong Kong", "HKU", "Hong Kong", "Hong Kong"),
    ("The Chinese University of Hong Kong", "CUHK", "Hong Kong", "Hong Kong"),
    ("The Hong Kong University of Science and Technology", "HKUST", "Hong Kong", "Hong Kong"),
    ("City University of Hong Kong", "CityU", "Hong Kong", "Hong Kong"),
    ("The Hong Kong Polytechnic University", "PolyU", "Hong Kong", "Hong Kong"),
    ("Hong Kong Baptist University", "HKBU", "Hong Kong", "Hong Kong"),
    ("National University of Singapore", "NUS", "Singapore", "Singapore"),
    ("Nanyang Technological University", "NTU", "Singapore", "Singapore"),
    ("Singapore Management University", "SMU", "Singapore", "Singapore"),
    ("University College London", "UCL", "United Kingdom", "London"),
    ("Imperial College London", "Imperial", "United Kingdom", "London"),
    ("University of Manchester", "Manchester", "United Kingdom", "Manchester"),
    ("University of Warwick", "Warwick", "United Kingdom", "Coventry"),
    ("University of Edinburgh", "Edinburgh", "United Kingdom", "Edinburgh"),
    ("King's College London", "KCL", "United Kingdom", "London"),
    ("London School of Economics and Political Science", "LSE", "United Kingdom", "London"),
    ("University of Bristol", "Bristol", "United Kingdom", "Bristol"),
    ("University of Glasgow", "Glasgow", "United Kingdom", "Glasgow"),
    ("University of Southampton", "Southampton", "United Kingdom", "Southampton"),
    ("University of Melbourne", "Melbourne", "Australia", "Melbourne"),
    ("University of Sydney", "Sydney", "Australia", "Sydney"),
    ("UNSW Sydney", "UNSW", "Australia", "Sydney"),
    ("Monash University", "Monash", "Australia", "Melbourne"),
    ("Australian National University", "ANU", "Australia", "Canberra"),
    ("University of Queensland", "UQ", "Australia", "Brisbane"),
]


def seed_universities(db) -> int:
    count = 0
    for name, short, country, city in UNIVERSITIES:
        if not db.query(University).filter(University.name == name).first():
            db.add(University(name=name, short_name=short, country=country, city=city, official_website=f"https://www.{short.lower().replace(' ', '')}.edu", admissions_website=None))
            count += 1
    db.commit()
    return count


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print({"inserted": seed_universities(db)})
    finally:
        db.close()
