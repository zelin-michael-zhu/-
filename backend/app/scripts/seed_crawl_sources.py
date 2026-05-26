from app.core.database import SessionLocal
from app.models import CrawlSource, University
from app.scripts.seed_universities import seed_universities

SOURCES = {
    "HKU": (
        "https://admissions.hku.hk/tpg/programme-list",
        "official taught postgraduate programme list",
        "Hong Kong",
        "HKU Taught Postgraduate Programme List",
        "admissions.hku.hk",
        "active",
    ),
    "CUHK": (
        "https://www.gs.cuhk.edu.hk/admissions/programmes",
        "official graduate school programme list",
        "Hong Kong",
        "CUHK Graduate School Programmes",
        "gs.cuhk.edu.hk",
        "active",
    ),
    "HKUST": (
        "https://prog-crs.hkust.edu.hk/pgprog",
        "official postgraduate programme search",
        "Hong Kong",
        "HKUST Postgraduate Programme Search",
        "prog-crs.hkust.edu.hk",
        "active",
    ),
    "CityU": (
        "https://www.cityu.edu.hk/pg/programmes",
        "official CityU postgraduate programmes",
        "Hong Kong",
        "CityU Postgraduate Programmes",
        "cityu.edu.hk",
        "active",
    ),
    "PolyU": (
        "https://www.polyu.edu.hk/study/pg/programmes",
        "official PolyU postgraduate programmes",
        "Hong Kong",
        "PolyU Postgraduate Programmes",
        "polyu.edu.hk",
        "active",
    ),
    "HKBU": (
        "https://gs.hkbu.edu.hk/programmes",
        "official HKBU graduate school programmes",
        "Hong Kong",
        "HKBU Graduate School Programmes",
        "hkbu.edu.hk",
        "active",
    ),
    "NUS": (
        "https://www.nus.edu.sg/registrar/prospective-students/graduate/graduate-programme",
        "official graduate programme page; needs_manual_confirmation",
        "Singapore",
        "NUS Graduate Programme",
        "nus.edu.sg",
        "needs_manual_confirmation",
    ),
    "NTU": (
        "https://www.ntu.edu.sg/admissions/graduate",
        "official graduate admissions page; needs_manual_confirmation",
        "Singapore",
        "NTU Graduate Admissions",
        "ntu.edu.sg",
        "needs_manual_confirmation",
    ),
    "SMU": (
        "https://masters.smu.edu.sg/programmes",
        "official SMU masters programme list",
        "Singapore",
        "SMU Masters Programmes",
        "smu.edu.sg",
        "active",
    ),
    "UCL": (
        "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees",
        "official graduate taught degrees list",
        "United Kingdom",
        "UCL Graduate Taught Degrees",
        "ucl.ac.uk",
        "active",
    ),
    "Imperial": (
        "https://www.imperial.ac.uk/study/courses/postgraduate-taught/",
        "official Imperial postgraduate taught courses",
        "United Kingdom",
        "Imperial College Postgraduate Taught Courses",
        "imperial.ac.uk",
        "active",
    ),
    "Manchester": (
        "https://www.manchester.ac.uk/study/masters/courses/list/",
        "official master's courses list",
        "United Kingdom",
        "Manchester Master's Courses",
        "manchester.ac.uk",
        "active",
    ),
    "Warwick": (
        "https://warwick.ac.uk/study/postgraduate/courses/",
        "official postgraduate courses list",
        "United Kingdom",
        "Warwick Postgraduate Courses",
        "warwick.ac.uk",
        "active",
    ),
    "Edinburgh": (
        "https://www.ed.ac.uk/studying/postgraduate/degrees",
        "official postgraduate degrees list",
        "United Kingdom",
        "Edinburgh Postgraduate Degrees",
        "ed.ac.uk",
        "active",
    ),
    "KCL": (
        "https://www.kcl.ac.uk/study/postgraduate-taught/courses",
        "official KCL postgraduate taught courses",
        "United Kingdom",
        "King's College London PG Taught Courses",
        "kcl.ac.uk",
        "active",
    ),
    "LSE": (
        "https://www.lse.ac.uk/study-at-lse/Graduate/degree-programmes",
        "official LSE graduate degree programmes",
        "United Kingdom",
        "LSE Graduate Degree Programmes",
        "lse.ac.uk",
        "active",
    ),
    "Bristol": (
        "https://www.bristol.ac.uk/study/postgraduate/",
        "official Bristol postgraduate study",
        "United Kingdom",
        "Bristol Postgraduate Study",
        "bristol.ac.uk",
        "active",
    ),
    "Glasgow": (
        "https://www.gla.ac.uk/postgraduate/taught/",
        "official Glasgow postgraduate taught",
        "United Kingdom",
        "Glasgow Postgraduate Taught",
        "gla.ac.uk",
        "active",
    ),
    "Southampton": (
        "https://www.southampton.ac.uk/courses/postgraduate/taught.page",
        "official Southampton postgraduate taught",
        "United Kingdom",
        "Southampton Postgraduate Taught",
        "southampton.ac.uk",
        "active",
    ),
    "Melbourne": (
        "https://study.unimelb.edu.au/find/courses/graduate/",
        "official Melbourne graduate courses",
        "Australia",
        "Melbourne Graduate Courses",
        "unimelb.edu.au",
        "active",
    ),
    "Sydney": (
        "https://www.sydney.edu.au/courses/search.html?search-type=course&course-level=pg",
        "official Sydney postgraduate courses",
        "Australia",
        "Sydney Postgraduate Courses",
        "sydney.edu.au",
        "active",
    ),
    "UNSW": (
        "https://www.unsw.edu.au/study/postgraduate",
        "official UNSW postgraduate study",
        "Australia",
        "UNSW Postgraduate Study",
        "unsw.edu.au",
        "active",
    ),
    "Monash": (
        "https://www.monash.edu/study/courses/find-a-course?courseview=postgraduate",
        "official Monash postgraduate courses",
        "Australia",
        "Monash Postgraduate Courses",
        "monash.edu",
        "active",
    ),
    "ANU": (
        "https://programsandcourses.anu.edu.au/",
        "official ANU programs and courses",
        "Australia",
        "ANU Programs and Courses",
        "anu.edu.au",
        "active",
    ),
    "UQ": (
        "https://study.uq.edu.au/study-options/programs",
        "official UQ programs",
        "Australia",
        "University of Queensland Programs",
        "uq.edu.au",
        "active",
    ),
}


def seed_crawl_sources(db) -> int:
    seed_universities(db)
    count = 0
    for short_name, (url, notes, region, source_name, official_domain, status) in SOURCES.items():
        uni = db.query(University).filter(University.short_name == short_name).first()
        if not uni:
            uni = db.query(University).filter(University.name.ilike(f"%{short_name}%")).first()
        if not uni:
            continue
        existing = db.query(CrawlSource).filter(
            CrawlSource.university_id == uni.id, CrawlSource.url == url
        ).first()
        if existing:
            existing.notes = notes
            existing.region = region
            existing.source_name = source_name
            existing.official_domain = official_domain
            existing.status = status
            continue
        db.add(
            CrawlSource(
                university_id=uni.id,
                source_type="program_index",
                url=url,
                crawl_status="pending",
                notes=notes,
                region=region,
                source_name=source_name,
                official_domain=official_domain,
                status=status,
            )
        )
        count += 1
    db.commit()
    return count


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print({"inserted": seed_crawl_sources(db)})
    finally:
        db.close()
