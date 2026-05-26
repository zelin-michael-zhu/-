from pydantic import BaseModel, ConfigDict


class DocumentIn(BaseModel):
    applicant_id: int | None = None
    name: str
    type: str
    status: str = "missing"
    file_path: str | None = None


class DocumentOut(DocumentIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
