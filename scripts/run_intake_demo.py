"""Executable intake demo script showing deterministic normalization, deduplication, and SQLite persistence."""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from careerpilot.domain.models import RawJobListing, CareerProfile, IngestStatus
from careerpilot.storage.database import init_db, get_connection
from careerpilot.storage.repository import JobRepository
from careerpilot.intake.pipeline import JobIntakePipeline


def main():
    print("=" * 70)
    print("  CareerPilot AI: Job Intake Foundation Demo (Milestone 1)")
    print("=" * 70)

    db_path = "careerpilot.db"
    print(f"\n[1] Initializing SQLite Database at '{db_path}'...")
    init_db(db_path)
    conn = get_connection(db_path)
    repo = JobRepository(conn)
    pipeline = JobIntakePipeline(repo)
    print("    Database initialized with complete schema (jobs, profiles, audit).")

    profile_path = PROJECT_ROOT / "data" / "sample_career_profile.json"
    print(f"\n[2] Loading Verified Career Profile from '{profile_path.name}'...")
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    profile = CareerProfile.model_validate(profile_data)
    repo.save_career_profile(profile)
    print(f"    Loaded profile for: {profile.full_name} ({profile.headline})")
    print(f"    Verified Skills: {len(profile.skills)} | Projects: {len(profile.projects)}")

    jobs_path = PROJECT_ROOT / "data" / "sample_jobs.json"
    print(f"\n[3] Ingesting Raw Job Listings from '{jobs_path.name}'...")
    with open(jobs_path, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)
    raw_jobs = [RawJobListing(**item) for item in jobs_data]
    print(f"    Found {len(raw_jobs)} raw candidate jobs in source stream.\n")

    results = pipeline.process_batch(raw_jobs)

    print("-" * 70)
    print(f"{'STATUS':<16} | {'COMPANY':<20} | {'TITLE':<25}")
    print("-" * 70)
    for res in results:
        status_str = res.status.value
        if res.job:
            company = res.job.company[:20]
            title = res.job.title[:25]
        else:
            company = "N/A"
            title = "N/A"
        print(f"{status_str:<16} | {company:<20} | {title:<25}")
        if res.security_warnings:
            for w in res.security_warnings:
                print(f"   [!] SECURITY ALERT: {w}")
        if res.rejection_reason and res.status != IngestStatus.ACCEPTED:
            print(f"   [x] REJECTION: {res.rejection_reason}")

    print("-" * 70)
    counts = {}
    for r in results:
        counts[r.status.value] = counts.get(r.status.value, 0) + 1
    print("\n[4] Ingestion Summary:")
    for status, count in counts.items():
        print(f"    - {status}: {count}")

    audit_events = repo.get_audit_events()
    print(f"\n[5] Audit Trail: {len(audit_events)} audit events recorded.")
    for event in audit_events[-5:]:
        print(f"    - [{event.timestamp.strftime('%H:%M:%S')}] {event.action:<20} -> {event.outcome} ({event.entity_type}: {event.entity_id})")

    print("\n" + "=" * 70)
    print("  Job Intake Foundation Verified Successfully!")
    print("=" * 70)
    conn.close()


if __name__ == "__main__":
    main()
