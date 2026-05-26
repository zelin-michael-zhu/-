# Backend Flow

The backend is a FastAPI app under `backend/`.

- Routers expose `/api/...` endpoints.
- SQLAlchemy models use MySQL through `mysql+pymysql`.
- Alembic creates the schema.
- Browser Agent chooses an executor through `BrowserAgentService`.
- Risk classification happens before browser actions.
