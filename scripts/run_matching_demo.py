"""Interactive end-to-end demo of CareerPilot AI Job Intake & Explainable CV Matching."""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from careerpilot.domain.models import RawJobListing, CareerProfile, IngestStatus
from careerpilot.storage.database import init_db, get_connection
from careerpilot.storage.repository import JobRepository
from careerpilot.intake.pipeline import JobIntakePipeline
from careerpilot.matching.matcher import JobMatcher
from careerpilot.matching.providers import MockLLMProvider
from careerpilot.matching.ranker import JobRanker


async def main():
    print("=" * 80)
    print("  CareerPilot AI: Job Intake & Explainable CV Matching Demo (Milestones 1 & 2)")
    print("=" * 80)

    db_path = "careerpilot.db"
    print(f"\n[1] Initializing SQLite Database at '{db_path}'...")
    init_db(db_path)
    conn = get_connection(db_path)
    repo = JobRepository(conn)
    intake = JobIntakePipeline(repo)
    provider = MockLLMProvider()
    matcher = JobMatcher(provider, repo)
    ranker = JobRanker(repo)
    print("    Complete schema ready (jobs, career_profile, job_matches, audit_events).")

    # Load Career Profile
    profile_path = PROJECT_ROOT / "data" / "sample_career_profile.json"
    print(f"\n[2] Loading Verified Career Profile: '{profile_path.name}'...")
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    profile = CareerProfile.model_validate(profile_data)
    repo.save_career_profile(profile)
    print(f"    Candidate: {profile.full_name} | {profile.headline}")
    print(f"    Target Roles: {', '.join(profile.preferences.target_roles)}")
    print(f"    Verified Technical Skills: {len(profile.skills)} verified skills")

    # Ingest Job Stream
    jobs_path = PROJECT_ROOT / "data" / "sample_jobs.json"
    print(f"\n[3] Ingesting Job Listings from '{jobs_path.name}'...")
    with open(jobs_path, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)
    raw_jobs = [RawJobListing(**item) for item in jobs_data]
    ingest_results = intake.process_batch(raw_jobs)
    print(f"    Ingested {len(raw_jobs)} listings:")
    for res in ingest_results:
        st = res.status.value
        title = res.job.title if res.job else "N/A"
        comp = res.job.company if res.job else "N/A"
        print(f"    - [{st:<14}] {comp:<20} | {title}")
        if res.security_warnings:
            for w in res.security_warnings:
                print(f"      [!] SECURITY FLAG: {w}")

    # Evaluate Job Matches with Hybrid AI
    accepted_jobs = [r.job for r in ingest_results if r.status == IngestStatus.ACCEPTED and r.job]
    print(f"\n[4] Running AI Match Engine on {len(accepted_jobs)} Accepted Opportunities...")
    for job in accepted_jobs:
        await matcher.evaluate_job(job, profile)

    # Rank Opportunities
    ranked = ranker.rank_opportunities(profile, min_score=40.0)
    print("\n" + "=" * 80)
    print("  EXPLAINABLE CAREER MATCHING REPORT & OPPORTUNITY RANKINGS")
    print("=" * 80)

    for r in ranked:
        salary_str = f"${r.job.salary.min_amount:,.0f} - ${r.job.salary.max_amount:,.0f}" if r.job.salary and r.job.salary.min_amount else "Unspecified"
        print(f"\n  RANK #{r.rank}: {r.job.title} @ {r.job.company}")
        print(f"  Score: {r.evaluation.overall_score:.1f}/100 | Recommendation: [{r.evaluation.recommendation.value}] | Workplace: {r.job.workplace_type.value} | Salary: {salary_str}")
        print(f"  Executive Assessment: {r.evaluation.reasoning}")
        print("  Strengths (Verified Evidence Citations):")
        for s in r.evaluation.strengths[:3]:
            print(f"    * {s.requirement} -> {s.candidate_evidence}")
        print("  Gaps / Missing Qualifications:")
        for g in r.evaluation.gaps:
            print(f"    x {g}")
        print("-" * 80)

    # Audit Trail
    events = repo.get_audit_events()
    print(f"\n[5] Audit Trail Status: {len(events)} tamper-evident audit records preserved in database.")
    print("=" * 80)
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
