from sqlalchemy.orm import Session


class ApplicationOrchestrator:
    """Entry point reserved for the broader one-click application plan workflow."""

    def __init__(self, db: Session):
        self.db = db
