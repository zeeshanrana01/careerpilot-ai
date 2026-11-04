"""Data access repository for jobs, profiles, matches, and audit events."""
import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

from careerpilot.domain.models import (
    NormalizedJob,
    WorkplaceType,
    EmploymentType,
    SalaryRange,
    JobStatus,
    AuditEvent,
    CareerProfile,
    JobMatchEvaluation,
    RecommendationType,
    MatchedRequirement,
)


class JobRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_job(self, job: NormalizedJob) -> tuple[bool, str]:
        """
        Atomically persist a normalized job listing.
        Returns: (is_inserted, message)
        """
        existing = self.get_job_by_dedup_key(job.dedup_key)
        if existing:
            return False, f"Duplicate job already exists with ID: {existing.id}"

        sec_flags_json = json.dumps(job.security_flags)
        salary_min = job.salary.min_amount if job.salary else None
        salary_max = job.salary.max_amount if job.salary else None
        salary_curr = job.salary.currency if job.salary else "USD"
        salary_period = job.salary.period if job.salary else "YEARLY"
        posted_str = job.posted_date.isoformat() if job.posted_date else None
        deadline_str = job.deadline.isoformat() if job.deadline else None

        query = """
        INSERT INTO jobs (
            id, dedup_key, title, company, location, workplace_type,
            employment_type, description_clean, salary_min, salary_max,
            salary_currency, salary_period, source_url, source_name,
            posted_date, deadline, security_flags, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.conn:
                self.conn.execute(
                    query,
                    (
                        job.id,
                        job.dedup_key,
                        job.title,
                        job.company,
                        job.location,
                        job.workplace_type.value,
                        job.employment_type.value,
                        job.description_clean,
                        salary_min,
                        salary_max,
                        salary_curr,
                        salary_period,
                        job.source_url,
                        job.source_name,
                        posted_str,
                        deadline_str,
                        sec_flags_json,
                        job.status.value,
                        job.created_at.isoformat(),
                        job.updated_at.isoformat(),
                    ),
                )
            return True, "Job successfully persisted"
        except sqlite3.IntegrityError as e:
            return False, f"Database integrity conflict: {str(e)}"

    def get_job_by_dedup_key(self, dedup_key: str) -> Optional[NormalizedJob]:
        cursor = self.conn.execute("SELECT * FROM jobs WHERE dedup_key = ?", (dedup_key,))
        row = cursor.fetchone()
        return self._row_to_job(row) if row else None

    def get_job_by_id(self, job_id: str) -> Optional[NormalizedJob]:
        cursor = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        return self._row_to_job(row) if row else None

    def list_jobs(self, status: Optional[JobStatus] = None, limit: int = 50) -> list[NormalizedJob]:
        if status:
            cursor = self.conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status.value, limit),
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            )
        return [self._row_to_job(row) for row in cursor.fetchall()]

    def update_job_status(self, job_id: str, new_status: JobStatus) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?",
                (new_status.value, _utc_now_iso(), job_id),
            )

    def save_job_match(self, match: JobMatchEvaluation) -> None:
        strengths_data = [s.model_dump() for s in match.strengths]
        query = """
        INSERT OR REPLACE INTO job_matches (
            id, job_id, overall_score, recommendation, strengths_json,
            gaps_json, reasoning, grounding_verified, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.conn:
            self.conn.execute(
                query,
                (
                    match.id,
                    match.job_id,
                    match.overall_score,
                    match.recommendation.value,
                    json.dumps(strengths_data),
                    json.dumps(match.gaps),
                    match.reasoning,
                    1 if match.grounding_verified else 0,
                    match.created_at.isoformat(),
                ),
            )

    def get_job_match(self, job_id: str) -> Optional[JobMatchEvaluation]:
        cursor = self.conn.execute("SELECT * FROM job_matches WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_match(row)

    def list_ranked_matches(self, min_score: float = 0.0) -> list[tuple[NormalizedJob, JobMatchEvaluation]]:
        """Return jobs joined with their match evaluations, sorted descending by score."""
        query = """
        SELECT j.*, m.id as match_id, m.overall_score, m.recommendation,
               m.strengths_json, m.gaps_json, m.reasoning, m.grounding_verified,
               m.created_at as match_created_at
        FROM jobs j
        JOIN job_matches m ON j.id = m.job_id
        WHERE m.overall_score >= ?
        ORDER BY m.overall_score DESC
        """
        cursor = self.conn.execute(query, (min_score,))
        results = []
        for row in cursor.fetchall():
            job = self._row_to_job(row)
            strengths_raw = json.loads(row["strengths_json"])
            strengths = [MatchedRequirement(**s) for s in strengths_raw]
            match = JobMatchEvaluation(
                id=row["match_id"],
                job_id=row["id"],
                overall_score=row["overall_score"],
                recommendation=RecommendationType(row["recommendation"]),
                strengths=strengths,
                gaps=json.loads(row["gaps_json"]),
                reasoning=row["reasoning"],
                grounding_verified=bool(row["grounding_verified"]),
                created_at=datetime.fromisoformat(row["match_created_at"]),
            )
            results.append((job, match))
        return results

    def record_audit_event(self, event: AuditEvent) -> None:
        query = """
        INSERT INTO audit_events (
            id, entity_type, entity_id, action, actor, outcome, details_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.conn:
            self.conn.execute(
                query,
                (
                    event.id,
                    event.entity_type,
                    event.entity_id,
                    event.action,
                    event.actor,
                    event.outcome,
                    json.dumps(event.details),
                    event.timestamp.isoformat(),
                ),
            )

    def get_audit_events(self, entity_id: Optional[str] = None) -> list[AuditEvent]:
        if entity_id:
            cursor = self.conn.execute(
                "SELECT * FROM audit_events WHERE entity_id = ? ORDER BY created_at ASC",
                (entity_id,),
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM audit_events ORDER BY created_at ASC"
            )
        events = []
        for row in cursor.fetchall():
            events.append(
                AuditEvent(
                    id=row["id"],
                    entity_type=row["entity_type"],
                    entity_id=row["entity_id"],
                    action=row["action"],
                    actor=row["actor"],
                    outcome=row["outcome"],
                    details=json.loads(row["details_json"]),
                    timestamp=datetime.fromisoformat(row["created_at"]),
                )
            )
        return events

    def save_career_profile(self, profile: CareerProfile) -> None:
        query = """
        INSERT OR REPLACE INTO career_profile (
            id, full_name, email, phone, location, headline, summary, data_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.conn:
            self.conn.execute(
                query,
                (
                    profile.id,
                    profile.full_name,
                    profile.email,
                    profile.phone,
                    profile.location,
                    profile.headline,
                    profile.summary,
                    profile.model_dump_json(),
                    profile.updated_at.isoformat(),
                ),
            )

    def get_career_profile(self) -> Optional[CareerProfile]:
        cursor = self.conn.execute("SELECT data_json FROM career_profile LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return None
        return CareerProfile.model_validate_json(row["data_json"])

    def _row_to_match(self, row: sqlite3.Row) -> JobMatchEvaluation:
        strengths_raw = json.loads(row["strengths_json"])
        strengths = [MatchedRequirement(**s) for s in strengths_raw]
        return JobMatchEvaluation(
            id=row["id"],
            job_id=row["job_id"],
            overall_score=row["overall_score"],
            recommendation=RecommendationType(row["recommendation"]),
            strengths=strengths,
            gaps=json.loads(row["gaps_json"]),
            reasoning=row["reasoning"],
            grounding_verified=bool(row["grounding_verified"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_job(self, row: sqlite3.Row) -> NormalizedJob:
        salary = None
        if row["salary_min"] is not None or row["salary_max"] is not None:
            salary = SalaryRange(
                min_amount=row["salary_min"],
                max_amount=row["salary_max"],
                currency=row["salary_currency"] or "USD",
                period=row["salary_period"] or "YEARLY",
            )

        posted_date = (
            datetime.fromisoformat(row["posted_date"]) if row["posted_date"] else None
        )
        deadline = (
            datetime.fromisoformat(row["deadline"]) if row["deadline"] else None
        )

        return NormalizedJob(
            id=row["id"],
            dedup_key=row["dedup_key"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            workplace_type=WorkplaceType(row["workplace_type"]),
            employment_type=EmploymentType(row["employment_type"]),
            description_clean=row["description_clean"],
            salary=salary,
            source_url=row["source_url"],
            source_name=row["source_name"],
            posted_date=posted_date,
            deadline=deadline,
            security_flags=json.loads(row["security_flags"] or "[]"),
            status=JobStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
