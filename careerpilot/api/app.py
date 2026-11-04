"""FastAPI application for CareerPilot AI web dashboard and REST API."""
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from careerpilot.domain.models import RawJobListing, CareerProfile, IngestStatus
from careerpilot.storage.database import init_db, get_connection
from careerpilot.storage.repository import JobRepository
from careerpilot.intake.pipeline import JobIntakePipeline
from careerpilot.matching.matcher import JobMatcher
from careerpilot.matching.providers import MockLLMProvider
from careerpilot.matching.ranker import JobRanker
from careerpilot.api.dashboard_html import DASHBOARD_HTML

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = "careerpilot.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and default data is seeded
    init_db(DB_PATH)
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    
    # Check if profile exists, if not seed it
    profile = repo.get_career_profile()
    if not profile:
        profile_path = PROJECT_ROOT / "data" / "sample_career_profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            profile = CareerProfile.model_validate(data)
            repo.save_career_profile(profile)

    # Check if jobs exist, if not seed sample jobs
    existing_jobs = repo.list_jobs(limit=1)
    if not existing_jobs:
        jobs_path = PROJECT_ROOT / "data" / "sample_jobs.json"
        if jobs_path.exists():
            with open(jobs_path, "r", encoding="utf-8") as f:
                jobs_data = json.load(f)
            raw_jobs = [RawJobListing(**item) for item in jobs_data]
            pipeline = JobIntakePipeline(repo)
            results = pipeline.process_batch(raw_jobs)
            
            # Match accepted jobs automatically for initial dashboard display
            matcher = JobMatcher(MockLLMProvider(), repo)
            for res in results:
                if res.status == IngestStatus.ACCEPTED and res.job and profile:
                    await matcher.evaluate_job(res.job, profile)
    conn.close()
    yield


app = FastAPI(
    title="CareerPilot AI API",
    description="Production-grade AI Career Agent API with Untrusted Input Defense & Explainable Matching",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the interactive CareerPilot AI Web Dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/profile")
async def get_profile():
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    profile = repo.get_career_profile()
    conn.close()
    if not profile:
        raise HTTPException(status_code=404, detail="Career profile not found")
    return profile


@app.get("/api/jobs")
async def list_jobs():
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    jobs = repo.list_jobs()
    conn.close()
    return jobs


@app.get("/api/matches")
async def list_matches():
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    profile = repo.get_career_profile()
    if not profile:
        conn.close()
        return []
    ranker = JobRanker(repo)
    ranked = ranker.rank_opportunities(profile, min_score=0.0)
    conn.close()
    return ranked


@app.post("/api/ingest")
async def ingest_job(raw: RawJobListing):
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    pipeline = JobIntakePipeline(repo)
    result = pipeline.process_job(raw)
    
    # If accepted, trigger match evaluation immediately
    if result.status == IngestStatus.ACCEPTED and result.job:
        profile = repo.get_career_profile()
        if profile:
            matcher = JobMatcher(MockLLMProvider(), repo)
            await matcher.evaluate_job(result.job, profile)
            
    conn.close()
    return result


@app.get("/api/audit")
async def get_audit_trail():
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    events = repo.get_audit_events()
    conn.close()
    return list(reversed(events))
