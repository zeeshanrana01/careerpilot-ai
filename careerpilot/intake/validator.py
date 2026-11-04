"""Validation engine for job intake: schema completeness, deadlines, and security compliance."""
from datetime import datetime, timezone
from typing import Optional
from careerpilot.domain.models import RawJobListing, IngestStatus
from careerpilot.core.config import settings


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        status: IngestStatus,
        errors: list[str] | None = None,
        warnings: list[str] | None = None
    ):
        self.is_valid = is_valid
        self.status = status
        self.errors = errors or []
        self.warnings = warnings or []

    def __repr__(self) -> str:
        return f"<ValidationResult valid={self.is_valid} status={self.status} errors={self.errors}>"


def validate_raw_job(
    raw: RawJobListing,
    parsed_deadline: Optional[datetime] = None,
    security_flags: Optional[list[str]] = None,
    current_time: Optional[datetime] = None
) -> ValidationResult:
    """
    Validate raw job listing before normalization and ingestion.
    Enforces required fields, non-trivial descriptions, freshness, and security boundaries.
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    if not raw.title or not raw.title.strip():
        errors.append("Job title is missing or empty.")
    elif len(raw.title.strip()) < 2:
        errors.append(f"Job title '{raw.title}' is too short.")
        
    if not raw.company or not raw.company.strip():
        errors.append("Company name is missing or empty.")
        
    desc = (raw.description or "").strip()
    if not desc:
        errors.append("Job description is missing or empty.")
    elif len(desc) < settings.min_description_length:
        errors.append(f"Job description is too short ({len(desc)} chars, minimum is {settings.min_description_length}).")
        
    now = current_time or datetime.now(timezone.utc)
    if parsed_deadline:
        if parsed_deadline.tzinfo is None:
            parsed_deadline = parsed_deadline.replace(tzinfo=timezone.utc)
        if parsed_deadline < now:
            return ValidationResult(
                is_valid=False,
                status=IngestStatus.EXPIRED,
                errors=[f"Job deadline has passed: {parsed_deadline.isoformat()} < {now.isoformat()}"]
            )
            
    if security_flags:
        for flag in security_flags:
            warnings.append(f"Security Alert: {flag}")
            
    if errors:
        return ValidationResult(
            is_valid=False,
            status=IngestStatus.INVALID_SCHEMA,
            errors=errors,
            warnings=warnings
        )
        
    return ValidationResult(
        is_valid=True,
        status=IngestStatus.ACCEPTED,
        warnings=warnings
    )
