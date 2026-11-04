"""FastAPI application for CareerPilot AI web dashboard and REST API."""
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from careerpilot.core.config import settings
from careerpilot.domain.models import RawJobListing, CareerProfile, IngestStatus, AuditEvent
from careerpilot.storage.database import init_db, get_connection
from careerpilot.storage.repository import JobRepository
from careerpilot.intake.pipeline import JobIntakePipeline
from careerpilot.matching.matcher import JobMatcher
from careerpilot.matching.providers import MockLLMProvider
from careerpilot.matching.ranker import JobRanker
from careerpilot.drafting.drafter import ApplicationDrafter
from careerpilot.drafting.models import ApplicationPackage, ApplicationStatus, CVVariant, CoverEmail, GroundingReport
from careerpilot.profile.parser import parse_resume_file
from careerpilot.services.email_dispatcher import EmailDispatcher
from careerpilot.api.dashboard_html import DASHBOARD_HTML

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = "careerpilot.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DB_PATH)
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    
    profile = repo.get_career_profile()
    if not profile:
        profile_path = PROJECT_ROOT / "data" / "sample_career_profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            profile = CareerProfile.model_validate(data)
            repo.save_career_profile(profile)

    existing_jobs = repo.list_jobs(limit=1)
    if not existing_jobs:
        jobs_path = PROJECT_ROOT / "data" / "sample_jobs.json"
        if jobs_path.exists():
            with open(jobs_path, "r", encoding="utf-8") as f:
                jobs_data = json.load(f)
            raw_jobs = [RawJobListing(**item) for item in jobs_data]
            pipeline = JobIntakePipeline(repo)
            results = pipeline.process_batch(raw_jobs)
            
            matcher = JobMatcher(MockLLMProvider(), repo)
            for res in results:
                if res.status == IngestStatus.ACCEPTED and res.job and profile:
                    await matcher.evaluate_job(res.job, profile)
    conn.close()
    yield


app = FastAPI(
    title="CareerPilot AI API",
    description="Production-grade AI Career Agent API with Untrusted Input Defense, Matching & Drafting",
    version="0.3.0",
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


@app.post("/api/profile/upload")
async def upload_cv(file: UploadFile = File(...)):
    """Upload candidate CV (PDF, JSON, or text), parse profile, and re-evaluate matches."""
    try:
        content = await file.read()
        profile = parse_resume_file(file.filename or "resume.pdf", content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    repo.save_career_profile(profile)

    # Re-evaluate all accepted jobs against the new profile
    jobs = repo.list_jobs(limit=100)
    matcher = JobMatcher(MockLLMProvider(), repo)
    recalculated = 0
    for job in jobs:
        await matcher.evaluate_job(job, profile)
        recalculated += 1

    repo.record_audit_event(
        AuditEvent(
            entity_type="career_profile",
            entity_id=profile.id,
            action="PROFILE_UPDATED",
            actor="user",
            outcome="SUCCESS",
            details={
                "candidate": profile.full_name,
                "skills_count": len(profile.skills),
                "recalculated_jobs": recalculated,
            },
        )
    )
    conn.close()
    return {
        "status": "SUCCESS",
        "message": f"Successfully loaded CV for {profile.full_name}. Re-evaluated {recalculated} opportunities.",
        "profile": profile,
    }


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
    
    if result.status == IngestStatus.ACCEPTED and result.job:
        profile = repo.get_career_profile()
        if profile:
            matcher = JobMatcher(MockLLMProvider(), repo)
            evaluation = await matcher.evaluate_job(result.job, profile)
            # Autonomous auto-apply trigger for high-confidence matches
            if settings.auto_apply_enabled and evaluation and evaluation.overall_score >= settings.auto_apply_threshold:
                drafter = ApplicationDrafter(MockLLMProvider(), repo)
                package = await drafter.draft_application(result.job, profile)
                if package.grounding_report.is_strictly_grounded:
                    dispatcher = EmailDispatcher(repo, sandbox_mode=settings.sandbox_email_mode)
                    dispatcher.dispatch(package, result.job, profile)
                    with conn:
                        conn.execute("UPDATE applications SET status = 'SUBMITTED' WHERE id = ?", (package.id,))
                        conn.execute("UPDATE approval_requests SET approval_status = 'APPROVED' WHERE id = ?", (package.id,))
            
    conn.close()
    return result


@app.post("/api/applications/draft/{job_id}")
async def create_application_draft(job_id: str):
    """Generate tailored CV variant and cover email package grounded in verified facts."""
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    job = repo.get_job_by_id(job_id)
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
    profile = repo.get_career_profile()
    if not profile:
        conn.close()
        raise HTTPException(status_code=400, detail="Verified career profile missing")

    drafter = ApplicationDrafter(MockLLMProvider(), repo)
    package = await drafter.draft_application(job, profile)
    conn.close()
    return package


@app.get("/api/applications/{job_id}")
async def get_application_by_job(job_id: str):
    """Retrieve existing application package for a job."""
    conn = get_connection(DB_PATH)
    cursor = conn.execute("SELECT * FROM applications WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="No application draft exists for this job")
        
    cv = CVVariant.model_validate_json(row["cv_version"])
    email = CoverEmail.model_validate_json(row["email_draft"])
    
    # Check approval request
    req_cur = conn.execute("SELECT payload_hash FROM approval_requests WHERE application_id = ?", (row["id"],))
    req_row = req_cur.fetchone()
    draft_hash = req_row["payload_hash"] if req_row else ""
    
    package = ApplicationPackage(
        id=row["id"],
        job_id=row["job_id"],
        cv_variant=cv,
        cover_email=email,
        draft_hash=draft_hash,
        status=ApplicationStatus(row["status"]),
    )
    conn.close()
    return package


@app.post("/api/applications/{app_id}/approve")
async def approve_application(app_id: str):
    """Human-in-the-loop approval: marks application APPROVED and logs audit trail."""
    conn = get_connection(DB_PATH)
    with conn:
        conn.execute("UPDATE applications SET status = 'APPROVED' WHERE id = ?", (app_id,))
        conn.execute("UPDATE approval_requests SET approval_status = 'APPROVED' WHERE id = ?", (app_id,))
        
    repo = JobRepository(conn)
    repo.record_audit_event(
        AuditEvent(
            entity_type="application",
            entity_id=app_id,
            action="APPLICATION_APPROVED",
            actor="human_reviewer",
            outcome="SUCCESS",
            details={"application_id": app_id},
        )
    )
    conn.close()
    return {"status": "APPROVED", "message": "Application approved by human reviewer."}


@app.post("/api/applications/{app_id}/reject")
async def reject_application(app_id: str):
    """Human-in-the-loop rejection."""
    conn = get_connection(DB_PATH)
    with conn:
        conn.execute("UPDATE applications SET status = 'REJECTED' WHERE id = ?", (app_id,))
        conn.execute("UPDATE approval_requests SET approval_status = 'REJECTED' WHERE id = ?", (app_id,))
        
    repo = JobRepository(conn)
    repo.record_audit_event(
        AuditEvent(
            entity_type="application",
            entity_id=app_id,
            action="APPLICATION_REJECTED",
            actor="human_reviewer",
            outcome="FAILURE",
            details={"application_id": app_id},
        )
    )
    conn.close()
    return {"status": "REJECTED", "message": "Application marked as rejected."}


@app.post("/api/applications/{app_id}/send")
async def send_application(app_id: str, recipient_override: Optional[str] = None):
    """Deliver approved application via outbound Email Dispatcher (SMTP or Sandbox)."""
    conn = get_connection(DB_PATH)
    cursor = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found")

    cv = CVVariant.model_validate_json(row["cv_version"])
    email = CoverEmail.model_validate_json(row["email_draft"])
    req_cur = conn.execute("SELECT payload_hash FROM approval_requests WHERE application_id = ?", (row["id"],))
    req_row = req_cur.fetchone()
    draft_hash = req_row["payload_hash"] if req_row else ""

    package = ApplicationPackage(
        id=row["id"],
        job_id=row["job_id"],
        cv_variant=cv,
        cover_email=email,
        draft_hash=draft_hash,
        status=ApplicationStatus(row["status"]),
    )

    repo = JobRepository(conn)
    job = repo.get_job_by_id(package.job_id)
    profile = repo.get_career_profile()
    if not job or not profile:
        conn.close()
        raise HTTPException(status_code=400, detail="Associated job or profile missing")

    dispatcher = EmailDispatcher(repo, sandbox_mode=settings.sandbox_email_mode)
    result = dispatcher.dispatch(package, job, profile, recipient_override=recipient_override)

    if result.success:
        with conn:
            conn.execute("UPDATE applications SET status = 'SUBMITTED' WHERE id = ?", (app_id,))
            conn.execute("UPDATE approval_requests SET approval_status = 'APPROVED' WHERE id = ?", (app_id,))

    conn.close()
    return result.to_dict()


class SettingsUpdate(BaseModel):
    auto_apply_enabled: Optional[bool] = None
    auto_apply_threshold: Optional[float] = None
    sandbox_email_mode: Optional[bool] = None


@app.get("/api/settings")
async def get_system_settings():
    """Retrieve operational automation and dispatcher settings."""
    return {
        "auto_apply_enabled": settings.auto_apply_enabled,
        "auto_apply_threshold": settings.auto_apply_threshold,
        "sandbox_email_mode": settings.sandbox_email_mode,
        "llm_provider": settings.llm_provider,
        "smtp_configured": bool(settings.smtp_user and settings.smtp_password),
    }


@app.post("/api/settings")
async def update_system_settings(update: SettingsUpdate):
    """Update runtime auto-apply and dispatcher controls."""
    if update.auto_apply_enabled is not None:
        settings.auto_apply_enabled = update.auto_apply_enabled
    if update.auto_apply_threshold is not None:
        settings.auto_apply_threshold = update.auto_apply_threshold
    if update.sandbox_email_mode is not None:
        settings.sandbox_email_mode = update.sandbox_email_mode
    return await get_system_settings()


@app.get("/api/audit")
async def get_audit_trail():
    conn = get_connection(DB_PATH)
    repo = JobRepository(conn)
    events = repo.get_audit_events()
    conn.close()
    return list(reversed(events))
