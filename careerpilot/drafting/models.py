"""Domain models for Milestone 3 Application Drafting."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ApplicationStatus(str, Enum):
    DRAFTED = "DRAFTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"

class CVExperienceBullet(BaseModel):
    title: str
    company: str
    highlights: list[str] = Field(default_factory=list)

class CVProjectHighlight(BaseModel):
    name: str
    role: str
    highlights: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)

class CVVariant(BaseModel):
    """Job-tailored CV variant emphasizing verified experiences relevant to the role."""
    tailored_headline: str
    tailored_summary: str
    highlighted_skills: list[str] = Field(default_factory=list)
    highlighted_experience: list[CVExperienceBullet] = Field(default_factory=list)
    highlighted_projects: list[CVProjectHighlight] = Field(default_factory=list)

class CoverEmail(BaseModel):
    """Personalized cover email or application letter."""
    subject: str
    salutation: str
    body_paragraphs: list[str] = Field(default_factory=list)
    call_to_action: str
    sign_off: str

class GroundingReport(BaseModel):
    """Verification audit confirming all draft claims match verified profile facts."""
    supported_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    is_strictly_grounded: bool = True

class ApplicationPackage(BaseModel):
    """Complete application package ready for human review and cryptographic approval."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    cv_variant: CVVariant
    cover_email: CoverEmail
    grounding_report: GroundingReport = Field(default_factory=GroundingReport)
    draft_hash: str = Field("", description="SHA-256 payload hash of the exact draft evaluated")
    status: ApplicationStatus = ApplicationStatus.DRAFTED
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
