from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import health, universities, programs, crawler, applicants, matches, documents, applications, emails, browser_agent, ai, dashboard, recommendations, portal_assistant, discovery

app = FastAPI(title="ApplyPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.backend_cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    health.router,
    universities.router,
    programs.router,
    discovery.router,
    crawler.router,
    applicants.router,
    matches.router,
    documents.router,
    applications.router,
    emails.router,
    browser_agent.router,
    ai.router,
    dashboard.router,
    recommendations.router,
    portal_assistant.router,
]:
    app.include_router(router, prefix="/api")
