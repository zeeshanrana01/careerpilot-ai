"""Pydantic domain models for CareerPilot AI."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkplaceType(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    UNSPECIFIED = "UNSPECIFIED"


class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    OTHER = "OTHER"


class JobStatus(str, Enum):
    NEW = "NEW"
    SKIPPED = "SKIPPED"
    MATCHED = "MATCHED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class IngestStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    INVALID_SCHEMA = "INVALID_SCHEMA"
    EXPIRED = "EXPIRED"
    SECURITY_REJECTED = "SECURITY_REJECTED"


class RecommendationType(str, Enum):
    APPLY = "APPLY"
    CONSIDER = "CONSIDER"
    SKIP = "SKIP"


class SalaryRange(BaseModel):
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: str = "USD"
    period: str = "YEARLY"  # YEARLY, MONTHLY, HOURLY


class RawJobListing(BaseModel):
    """Raw, untrusted job posting input from any source."""
    title: str = Field(..., description="Raw job title")
    company: str = Field(..., description="Raw company name")
    description: str = Field(..., description="Raw job description or HTML content")
    location: Optional[str] = Field(None, description="Location text")
    source_url: Optional[str] = Field(None, description="Direct URL of the listing")
    source_name: str = Field("unknown", description="Source provider, e.g. linkedin, indeed, company_site")
    posted_date: Optional[str] = Field(None, description="Raw posted date string")
    deadline: Optional[str] = Field(None, description="Raw deadline string")
    salary_raw: Optional[str] = Field(None, description="Raw salary representation")
    employment_type: Optional[str] = Field(None, description="Raw employment type")
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary provider metadata")


class NormalizedJob(BaseModel):
    """Normalized, sanitized, validated job listing ready for storage and matching."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    dedup_key: str = Field(..., description="Deterministic unique fingerprint")
    title: str = Field(..., min_length=2)
    company: str = Field(..., min_length=1)
    location: Optional[str] = None
    workplace_type: WorkplaceType = WorkplaceType.UNSPECIFIED
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    description_clean: str = Field(..., min_length=10)
    salary: Optional[SalaryRange] = None
    source_url: Optional[str] = None
    source_name: str = "unknown"
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    security_flags: list[str] = Field(default_factory=list)
    status: JobStatus = JobStatus.NEW
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class IngestResult(BaseModel):
    """Result of processing a single raw job through the intake pipeline."""
    status: IngestStatus
    job: Optional[NormalizedJob] = None
    dedup_key: Optional[str] = None
    rejection_reason: Optional[str] = None
    security_warnings: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    """Audit record tracking every action taken on jobs, applications, or approvals."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: str = Field(..., description="job, application, approval_request, intake, match")
    entity_id: str = Field(..., description="Identifier of the target entity")
    action: str = Field(..., description="Action name e.g. JOB_INGESTED, JOB_MATCH_EVALUATED")
    actor: str = Field("system", description="User, system, or agent persona")
    outcome: str = Field("SUCCESS", description="SUCCESS, FAILURE, SKIPPED")
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_utc_now)


# Career profile models
class VerifiedSkill(BaseModel):
    name: str
    category: str = "technical"
    years_experience: Optional[float] = None
    proficiency: str = "advanced"


class VerifiedExperience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = "Present"
    location: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    skills_used: list[str] = Field(default_factory=list)


class VerifiedProject(BaseModel):
    name: str
    role: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    link: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class VerifiedCertification(BaseModel):
    name: str
    issuer: str
    issue_date: str
    credential_id: Optional[str] = None
    url: Optional[str] = None


class CareerPreferences(BaseModel):
    target_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_only: bool = False
    min_acceptable_salary: Optional[float] = None
    preferred_technologies: list[str] = Field(default_factory=list)
    excluded_industries: list[str] = Field(default_factory=list)


class CareerProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: str
    summary: str
    skills: list[VerifiedSkill] = Field(default_factory=list)
    experience: list[VerifiedExperience] = Field(default_factory=list)
    projects: list[VerifiedProject] = Field(default_factory=list)
    certifications: list[VerifiedCertification] = Field(default_factory=list)
    preferences: CareerPreferences = Field(default_factory=CareerPreferences)
    updated_at: datetime = Field(default_factory=_utc_now)


# Milestone 2: Job Intelligence & Match Evaluation Models
class MatchedRequirement(BaseModel):
    """Specific requirement matched with verified candidate profile evidence."""
    requirement: str = Field(..., description="Job requirement extracted from description")
    candidate_evidence: str = Field(..., description="Exact verified skill, project, or experience point")
    confidence: str = Field("high", description="high, medium, low")


class JobMatchEvaluation(BaseModel):
    """Detailed explainable matching evaluation produced by local/cloud AI."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Match score from 0 to 100")
    recommendation: RecommendationType
    strengths: list[MatchedRequirement] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list, description="Missing requirements or unmet qualifications")
    reasoning: str = Field(..., description="Executive summary explaining why this job matches or doesn't")
    grounding_verified: bool = Field(True, description="Strict validation that claims are rooted in verified CV facts")
    created_at: datetime = Field(default_factory=_utc_now)


class RankedJob(BaseModel):
    """Normalized job packaged with its match evaluation and preference-weighted rank."""
    job: NormalizedJob
    evaluation: JobMatchEvaluation
    rank: int
    preference_fit: bool = True
