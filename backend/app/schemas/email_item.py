from pydantic import BaseModel, ConfigDict


class EmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    body_preview: str | None = None
    category: str
    ai_summary: str | None = None
    suggested_action: str | None = None
    model_config = ConfigDict(from_attributes=True)
