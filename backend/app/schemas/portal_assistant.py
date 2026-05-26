from pydantic import BaseModel


class StartPortalSessionRequest(BaseModel):
    applicant_id: int = 1
    program_id: int | None = None
    executor_type: str = "mock"
    portal_url: str | None = None
    snapshot_text: str | None = None


class PortalSessionRequest(BaseModel):
    session_id: int


class PortalSnapshotRequest(BaseModel):
    session_id: int
    snapshot_text: str | None = None
