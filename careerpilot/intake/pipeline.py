"""Job intake pipeline: end-to-end normalization, validation, deduplication, and persistence."""
from datetime import datetime, timezone
from typing import Optional

from careerpilot.core.security import clean_untrusted_text, canonicalize_url
from careerpilot.domain.models import (
    RawJobListing,
    NormalizedJob,
    IngestResult,
    IngestStatus,
    AuditEvent,
    JobStatus,
)
from careerpilot.intake.normalizer import (
    normalize_title,
    normalize_company,
    normalize_location,
    parse_salary,
    parse_datetime,
    normalize_employment_type,
)
from careerpilot.intake.deduplicator import generate_dedup_key
from careerpilot.intake.validator import validate_raw_job
from careerpilot.storage.repository import JobRepository


class JobIntakePipeline:
    """Production job ingestion pipeline ensuring untrusted inputs are securely sanitized, normalized, and deduplicated."""

    def __init__(self, repository: JobRepository):
        self.repo = repository

    def process_job(
        self,
        raw: RawJobListing,
        current_time: Optional[datetime] = None
    ) -> IngestResult:
        """Process a single raw job listing through the intake pipeline."""
        now = current_time or datetime.now(timezone.utc)

        # 1. Sanitize untrusted description and extract security warnings
        clean_desc, security_warnings = clean_untrusted_text(raw.description)

        # 2. Parse dates
        parsed_posted = parse_datetime(raw.posted_date)
        parsed_deadline = parse_datetime(raw.deadline)

        # 3. Validate raw data and constraints
        validation = validate_raw_job(
            raw=raw,
            parsed_deadline=parsed_deadline,
            security_flags=security_warnings,
            current_time=now,
        )

        if not validation.is_valid:
            self.repo.record_audit_event(
                AuditEvent(
                    entity_type="job_intake",
                    entity_id=raw.source_url or raw.title or "unspecified",
                    action="JOB_REJECTED",
                    actor="intake_pipeline",
                    outcome="FAILURE",
                    details={
                        "company": raw.company,
                        "title": raw.title,
                        "status": validation.status.value,
                        "errors": validation.errors,
                    },
                )
            )
            return IngestResult(
                status=validation.status,
                rejection_reason="; ".join(validation.errors),
                security_warnings=security_warnings,
            )

        # 4. Normalize entities
        title_clean, workplace_from_title = normalize_title(raw.title)
        company_clean, _ = normalize_company(raw.company)
        location_clean, final_workplace = normalize_location(raw.location, workplace_from_title)
        employment_type = normalize_employment_type(raw.employment_type)
        salary = parse_salary(raw.salary_raw)
        canonical_url = canonicalize_url(raw.source_url) if raw.source_url else None

        # 5. Generate deterministic deduplication fingerprint
        dedup_key = generate_dedup_key(
            company=company_clean,
            title=title_clean,
            location=location_clean,
            workplace_type=final_workplace,
        )

        # 6. Check for duplicate in database
        existing = self.repo.get_job_by_dedup_key(dedup_key)
        if existing:
            self.repo.record_audit_event(
                AuditEvent(
                    entity_type="job",
                    entity_id=existing.id,
                    action="JOB_DUPLICATE_IGNORED",
                    actor="intake_pipeline",
                    outcome="SKIPPED",
                    details={
                        "dedup_key": dedup_key,
                        "source": raw.source_name,
                        "new_url": canonical_url,
                    },
                )
            )
            return IngestResult(
                status=IngestStatus.DUPLICATE,
                dedup_key=dedup_key,
                job=existing,
                rejection_reason=f"Duplicate of existing job '{existing.title}' at '{existing.company}' (ID: {existing.id})",
                security_warnings=security_warnings,
            )

        # 7. Construct normalized entity
        normalized_job = NormalizedJob(
            dedup_key=dedup_key,
            title=title_clean,
            company=company_clean,
            location=location_clean,
            workplace_type=final_workplace,
            employment_type=employment_type,
            description_clean=clean_desc,
            salary=salary,
            source_url=canonical_url,
            source_name=raw.source_name,
            posted_date=parsed_posted,
            deadline=parsed_deadline,
            security_flags=security_warnings,
            status=JobStatus.NEW,
            created_at=now,
            updated_at=now,
        )

        # 8. Atomically persist
        success, message = self.repo.save_job(normalized_job)
        if not success:
            return IngestResult(
                status=IngestStatus.DUPLICATE,
                dedup_key=dedup_key,
                rejection_reason=message,
                security_warnings=security_warnings,
            )

        # 9. Audit event
        self.repo.record_audit_event(
            AuditEvent(
                entity_type="job",
                entity_id=normalized_job.id,
                action="JOB_INGESTED",
                actor="intake_pipeline",
                outcome="SUCCESS",
                details={
                    "dedup_key": dedup_key,
                    "company": normalized_job.company,
                    "title": normalized_job.title,
                    "source": normalized_job.source_name,
                    "security_flags_count": len(security_warnings),
                },
            )
        )

        return IngestResult(
            status=IngestStatus.ACCEPTED,
            job=normalized_job,
            dedup_key=dedup_key,
            security_warnings=security_warnings,
        )

    def process_batch(
        self,
        raw_jobs: list[RawJobListing],
        current_time: Optional[datetime] = None
    ) -> list[IngestResult]:
        """
        Process a collection of raw job listings.
        Maintains an in-batch cache to catch duplicates occurring within the same batch.
        """
        results: list[IngestResult] = []
        seen_batch_keys: set[str] = set()

        for raw in raw_jobs:
            res = self.process_job(raw, current_time=current_time)
            if res.status == IngestStatus.ACCEPTED and res.dedup_key:
                seen_batch_keys.add(res.dedup_key)
            results.append(res)

        return results
