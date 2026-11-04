"""Unit tests for Milestone 3 application drafting and claim verification."""
import pytest
from careerpilot.domain.models import NormalizedJob, CareerProfile, WorkplaceType, SalaryRange
from careerpilot.drafting.drafter import ApplicationDrafter
from careerpilot.drafting.verifier import ClaimVerifier
from careerpilot.drafting.models import CVVariant, CoverEmail, ApplicationStatus
from careerpilot.matching.providers import MockLLMProvider
from careerpilot.storage.repository import JobRepository


@pytest.mark.asyncio
async def test_application_drafter_creates_grounded_package(
    repository: JobRepository,
    sample_career_profile: CareerProfile,
):
    job = NormalizedJob(
        dedup_key="anthropic_drafting_test",
        title="Senior AI Engineer",
        company="Anthropic",
        workplace_type=WorkplaceType.REMOTE,
        description_clean="Python, FastAPI, and agentic LLM systems with LangGraph.",
        salary=SalaryRange(min_amount=190000.0, max_amount=240000.0),
    )
    repository.save_job(job)

    drafter = ApplicationDrafter(MockLLMProvider(), repository)
    package = await drafter.draft_application(job, sample_career_profile)

    assert package.job_id == job.id
    assert package.status == ApplicationStatus.DRAFTED
    assert len(package.draft_hash) == 64  # SHA-256

    # Verify CV variant
    assert "Senior AI" in package.cv_variant.tailored_headline
    assert len(package.cv_variant.highlighted_skills) >= 3
    assert len(package.cv_variant.highlighted_experience) >= 1

    # Verify Cover Email
    assert "Anthropic" in package.cover_email.body_paragraphs[0] or "Senior AI Engineer" in package.cover_email.subject
    assert len(package.cover_email.body_paragraphs) >= 2

    # Verify Grounding
    assert package.grounding_report.is_strictly_grounded is True
    assert "Python" in package.grounding_report.supported_claims

    # Verify audit event
    events = repository.get_audit_events(entity_id=package.id)
    assert any(e.action == "APPLICATION_DRAFTED" for e in events)


def test_claim_verifier_flags_unsupported_skills(sample_career_profile: CareerProfile):
    # Candidate does NOT have Rust or Go on profile
    cv = CVVariant(
        tailored_headline="Senior Rust & Go Architect",
        tailored_summary="Expert in low-level Rust systems and Go microservices.",
        highlighted_skills=["Python", "Rust", "Go"],
    )
    email = CoverEmail(
        subject="Application for Rust Role",
        salutation="Dear Team,",
        body_paragraphs=["I have 10 years of experience with Rust programming."],
        call_to_action="Contact me.",
        sign_off="Best, Candidate",
    )

    report = ClaimVerifier.verify(cv, email, sample_career_profile)

    assert report.is_strictly_grounded is False
    assert "Rust" in report.unsupported_claims
    assert "Go" in report.unsupported_claims
    assert "Python" in report.supported_claims
