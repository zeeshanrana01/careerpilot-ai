"""Tests for outbound email dispatcher and auto-apply mechanics."""
import json
import pytest
from fastapi.testclient import TestClient

from careerpilot.api.app import app
from careerpilot.domain.models import CareerProfile, NormalizedJob, WorkplaceType, EmploymentType
from careerpilot.drafting.models import ApplicationPackage, CVVariant, CoverEmail, CVExperienceBullet, CVProjectHighlight
from careerpilot.services.email_dispatcher import EmailDispatcher
from careerpilot.storage.database import init_db, get_connection
from careerpilot.storage.repository import JobRepository


@pytest.fixture
def test_repo(tmp_path):
    db_file = str(tmp_path / "test_dispatcher.db")
    init_db(db_file)
    conn = get_connection(db_file)
    repo = JobRepository(conn)
    yield repo
    conn.close()


@pytest.fixture
def sample_package():
    return ApplicationPackage(
        id="app-test-123",
        job_id="job-test-456",
        cv_variant=CVVariant(
            tailored_headline="Senior AI Engineer - Agentic Systems",
            tailored_summary="Experienced builder of grounded AI workflows.",
            highlighted_skills=["Python", "FastAPI", "LangGraph"],
            highlighted_experience=[
                CVExperienceBullet(
                    title="AI Engineer",
                    company="Tech Corp",
                    highlights=["Engineered production multi-agent RAG"],
                )
            ],
            highlighted_projects=[
                CVProjectHighlight(
                    name="CareerPilot AI",
                    role="Architect",
                    highlights=["Autonomous career workflow"],
                    technologies=["FastAPI", "Python"],
                )
            ],
        ),
        cover_email=CoverEmail(
            subject="Application for AI Engineer - Rana Zeeshan",
            salutation="Dear Hiring Team at Future AI,",
            body_paragraphs=[
                "I am excited to submit my application for the AI Engineer role.",
                "With deep experience in LangGraph, Python, and FastAPI, I build reliable, production-ready systems.",
            ],
            call_to_action="I would welcome the opportunity to discuss how my background aligns with your vision.",
            sign_off="Best regards,",
        ),
        draft_hash="sha256-test-hash",
    )


@pytest.fixture
def sample_job():
    return NormalizedJob(
        id="job-test-456",
        dedup_key="key-future-ai",
        title="AI Engineer",
        company="Future AI",
        workplace_type=WorkplaceType.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        description_clean="Looking for an AI engineer to develop agentic LLM applications using Python and FastAPI.",
    )


@pytest.fixture
def sample_profile():
    return CareerProfile(
        id="profile-test-789",
        full_name="Rana Zeeshan",
        email="rana.zeeshan@example.com",
        phone="+92 300 1234567",
        headline="Senior AI Engineer",
        summary="Specialist in Agentic AI and LLM Engineering.",
        skills=[],
        experience=[],
        projects=[],
        certifications=[],
    )


def test_build_mime_message(test_repo, sample_package, sample_job, sample_profile):
    dispatcher = EmailDispatcher(test_repo, sandbox_mode=True)
    msg = dispatcher.build_mime_message(sample_package, sample_job, sample_profile, "careers@futureai.com")

    assert msg["Subject"] == "Application for AI Engineer - Rana Zeeshan"
    assert "careers@futureai.com" in msg["To"]
    assert "Rana Zeeshan" in msg["From"]
    assert msg["Message-ID"] is not None


def test_sandbox_dispatch_records_audit(test_repo, sample_package, sample_job, sample_profile):
    dispatcher = EmailDispatcher(test_repo, sandbox_mode=True)
    result = dispatcher.dispatch(sample_package, sample_job, sample_profile)

    assert result.success is True
    assert result.status == "SENT_SANDBOX"
    assert "futureai" in result.recipient

    events = test_repo.get_audit_events()
    assert any(e.action == "APPLICATION_SUBMITTED" for e in events)


def test_api_cv_upload_json():
    client = TestClient(app)
    profile_data = {
        "full_name": "Rana Zeeshan Upload Test",
        "email": "rana.upload@example.com",
        "headline": "Lead Applied AI Engineer",
        "summary": "Proven track record in building multi-agent AI systems and verifiable RAG pipelines.",
        "skills": [{"name": "Python", "category": "technical", "years_experience": 5.0, "proficiency": "expert"}],
        "experience": [],
        "projects": [],
        "certifications": [],
    }
    file_bytes = json.dumps(profile_data).encode("utf-8")
    response = client.post(
        "/api/profile/upload",
        files={"file": ("profile.json", file_bytes, "application/json")},
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "SUCCESS"
    assert "Rana Zeeshan Upload Test" in res_data["message"]


def test_api_settings_endpoints():
    client = TestClient(app)
    # Get settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "auto_apply_enabled" in data
    assert "auto_apply_threshold" in data

    # Update settings
    update_res = client.post(
        "/api/settings",
        json={"auto_apply_enabled": True, "auto_apply_threshold": 88.0},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["auto_apply_enabled"] is True
    assert updated["auto_apply_threshold"] == 88.0

    # Reset back to False for clean state
    client.post("/api/settings", json={"auto_apply_enabled": False, "auto_apply_threshold": 85.0})
