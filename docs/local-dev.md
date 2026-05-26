# Local Development

1. Start MySQL:

```bash
docker compose up -d
```

2. Start backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed_universities
python -m app.scripts.seed_demo_data
uvicorn main:app --reload
```

3. Start frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

4. Run tests:

```bash
cd backend
pytest
```
