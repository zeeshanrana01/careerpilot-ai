"""Unit tests for deterministic deduplication and URL canonicalization."""
from careerpilot.domain.models import WorkplaceType
from careerpilot.intake.deduplicator import generate_dedup_key, compute_url_fingerprint
from careerpilot.core.security import canonicalize_url


def test_dedup_key_matches_across_formatting_and_legal_suffixes():
    key1 = generate_dedup_key(
        company="Anthropic, Inc.",
        title="Sr. AI Eng. (Remote)",
        location="Remote",
        workplace_type=WorkplaceType.REMOTE
    )
    key2 = generate_dedup_key(
        company="Anthropic",
        title="Senior AI Engineer",
        location=None,
        workplace_type=WorkplaceType.REMOTE
    )
    assert key1 == key2
    assert len(key1) == 64


def test_dedup_key_differentiates_distinct_roles():
    key_eng = generate_dedup_key(
        company="Anthropic",
        title="Senior AI Engineer",
        workplace_type=WorkplaceType.REMOTE
    )
    key_sci = generate_dedup_key(
        company="Anthropic",
        title="Research Scientist",
        workplace_type=WorkplaceType.REMOTE
    )
    assert key_eng != key_sci


def test_url_canonicalization_strips_marketing_parameters():
    url1 = "https://jobs.lever.co/company/job-123"
    url2 = "https://jobs.lever.co/company/job-123/?utm_source=linkedin&utm_medium=job_board&ref=aggregate"
    url3 = "HTTPS://JOBS.LEVER.CO/company/job-123#overview"

    assert canonicalize_url(url1) == "https://jobs.lever.co/company/job-123"
    assert canonicalize_url(url2) == "https://jobs.lever.co/company/job-123"
    assert canonicalize_url(url3) == "https://jobs.lever.co/company/job-123"


def test_url_fingerprint():
    fp1 = compute_url_fingerprint("https://example.com/job?utm_source=slack")
    fp2 = compute_url_fingerprint("https://example.com/job")
    assert fp1 == fp2
    assert fp1 is not None
