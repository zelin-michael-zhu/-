from pydantic import BaseModel


class FindProgramsRequest(BaseModel):
    university_id: int | None = None
    field: str | None = None
    url: str | None = None
    engine: str = "native_static"
    max_pages: int = 10


class AnalyzeUrlRequest(BaseModel):
    url: str
    field: str | None = None
    engine: str = "native_static"
