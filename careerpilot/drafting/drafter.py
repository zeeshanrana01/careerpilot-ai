"""Application drafting coordinator."""
import json
from datetime import datetime, timezone
from careerpilot.core.security import compute_sha256
from careerpilot.domain.models import NormalizedJob, CareerProfile, AuditEvent
from careerpilot.drafting.models import (
    ApplicationPackage,
    ApplicationStatus,
    CVVariant,
    CoverEmail,
    CVExperienceBullet,
    CVProjectHighlight,
)
from careerpilot.drafting.verifier import ClaimVerifier
from careerpilot.drafting.prompts import SYSTEM_DRAFTING_PROMPT, build_drafting_prompt
from careerpilot.matching.providers import LLMProvider
from careerpilot.storage.repository import JobRepository

class ApplicationDrafter:
    """Coordinates tailored CV generation, cover email drafting, and claim grounding verification."""

    def __init__(self, provider: LLMProvider, repository: JobRepository):
        self.provider = provider
        self.repo = repository

    async def draft_application(
        self,
        job: NormalizedJob,
        profile: CareerProfile,
    ) -> ApplicationPackage:
        prompt = build_drafting_prompt(job, profile)
        
        # Invoke LLM
        raw = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=SYSTEM_DRAFTING_PROMPT,
        )

        cv_raw = raw.get("cv_variant", {})
        email_raw = raw.get("cover_email", {})

        # Parse CV Variant
        exp_bullets = [
            CVExperienceBullet(**b) for b in cv_raw.get("highlighted_experience", [])
        ]
        proj_highlights = [
            CVProjectHighlight(**p) for p in cv_raw.get("highlighted_projects", [])
        ]

        cv_variant = CVVariant(
            tailored_headline=cv_raw.get("tailored_headline", f"{job.title} | AI Systems Specialist"),
            tailored_summary=cv_raw.get("tailored_summary", profile.summary),
            highlighted_skills=cv_raw.get("highlighted_skills", [s.name for s in profile.skills[:5]]),
            highlighted_experience=exp_bullets,
            highlighted_projects=proj_highlights,
        )

        # Parse Cover Email
        cover_email = CoverEmail(
            subject=email_raw.get("subject", f"Application: {job.title} - {profile.full_name}"),
            salutation=email_raw.get("salutation", "Dear Hiring Team,"),
            body_paragraphs=email_raw.get("body_paragraphs", [
                f"I am writing to express my strong enthusiasm for the {job.title} role at {job.company}."
            ]),
            call_to_action=email_raw.get("call_to_action", "I look forward to discussing how my background can benefit your team."),
            sign_off=email_raw.get("sign_off", f"Best regards,\n{profile.full_name}"),
        )

        # Run automated claim verification
        grounding = ClaimVerifier.verify(cv_variant, cover_email, profile)

        # Compute cryptographic payload hash for approval idempotency
        payload_string = json.dumps({
            "cv": cv_variant.model_dump(),
            "email": cover_email.model_dump(),
        }, sort_keys=True)
        draft_hash = compute_sha256(payload_string)

        package = ApplicationPackage(
            job_id=job.id,
            cv_variant=cv_variant,
            cover_email=cover_email,
            grounding_report=grounding,
            draft_hash=draft_hash,
            status=ApplicationStatus.DRAFTED,
        )

        # Persist in SQLite applications and approval_requests table
        self._persist_application(package, job)

        # Log audit event
        self.repo.record_audit_event(
            AuditEvent(
                entity_type="application",
                entity_id=package.id,
                action="APPLICATION_DRAFTED",
                actor="application_drafter",
                outcome="SUCCESS",
                details={
                    "job_id": job.id,
                    "company": job.company,
                    "draft_hash": draft_hash,
                    "is_grounded": grounding.is_strictly_grounded,
                    "supported_claims_count": len(grounding.supported_claims),
                },
            )
        )

        return package

    def _persist_application(self, pkg: ApplicationPackage, job: NormalizedJob) -> None:
        conn = self.repo.conn
        cv_json = pkg.cv_variant.model_dump_json()
        email_json = pkg.cover_email.model_dump_json()
        
        with conn:
            # Upsert into applications table
            conn.execute(
                """
                INSERT OR REPLACE INTO applications (
                    id, job_id, cv_version, email_draft, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pkg.id,
                    job.id,
                    cv_json,
                    email_json,
                    pkg.status.value,
                    pkg.created_at.isoformat(),
                    pkg.updated_at.isoformat(),
                )
            )

            # Insert into approval_requests table
            conn.execute(
                """
                INSERT OR REPLACE INTO approval_requests (
                    id, application_id, proposed_action, payload_hash, approval_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    pkg.id,  # using same id as request id for 1-to-1 correlation
                    pkg.id,
                    "SUBMIT_APPLICATION",
                    pkg.draft_hash,
                    "PENDING",
                    pkg.created_at.isoformat(),
                )
            )
