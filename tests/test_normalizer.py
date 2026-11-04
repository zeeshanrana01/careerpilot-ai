"""Unit tests for deterministic job normalization logic."""
from datetime import timezone
from careerpilot.domain.models import WorkplaceType, EmploymentType
from careerpilot.intake.normalizer import (
    normalize_title,
    normalize_company,
    normalize_location,
    parse_salary,
    parse_datetime,
    normalize_employment_type,
)
from careerpilot.core.security import clean_untrusted_text


def test_normalize_title_abbreviations_and_workplace():
    title, workplace = normalize_title("Sr. AI Eng. (Remote)")
    assert title == "Senior AI Engineer"
    assert workplace == WorkplaceType.REMOTE


def test_normalize_title_brackets_and_casing():
    title, workplace = normalize_title("LEAD MACHINE LEARNING SWE [HYBRID]")
    assert title == "Lead Machine Learning Software Engineer"
    assert workplace == WorkplaceType.HYBRID


def test_normalize_company_suffixes():
    display, core = normalize_company("Anthropic, Inc.")
    assert display == "Anthropic"
    assert core == "anthropic"

    display, core = normalize_company("Google LLC")
    assert display == "Google"
    assert core == "google"

    display, core = normalize_company("DeepMind Technologies Ltd.")
    assert display == "DeepMind Technologies"
    assert core == "deepmindtechnologies"


def test_normalize_location_and_workplace_inference():
    loc, workplace = normalize_location("San Francisco, CA / Remote", WorkplaceType.UNSPECIFIED)
    assert loc == "San Francisco, CA / Remote"
    assert workplace == WorkplaceType.REMOTE

    loc, workplace = normalize_location("Hybrid - Austin, TX", WorkplaceType.UNSPECIFIED)
    assert workplace == WorkplaceType.HYBRID


def test_parse_salary_k_notation():
    salary = parse_salary("$150k - $200k / year")
    assert salary is not None
    assert salary.min_amount == 150000.0
    assert salary.max_amount == 200000.0
    assert salary.currency == "USD"
    assert salary.period == "YEARLY"


def test_parse_salary_hourly_and_euro():
    salary = parse_salary("€60 - €85 per hour")
    assert salary is not None
    assert salary.min_amount == 60.0
    assert salary.max_amount == 85.0
    assert salary.currency == "EUR"
    assert salary.period == "HOURLY"


def test_clean_untrusted_text_strips_html_and_scripts():
    raw_html = """
    <div>
        <h3>Job Overview</h3>
        <script>alert('malicious payload');</script>
        <p>Looking for a passionate AI engineer.</p>
        <style>body { display: none; }</style>
    </div>
    """
    clean, warnings = clean_untrusted_text(raw_html)
    assert "<script>" not in clean
    assert "alert" not in clean
    assert "<style>" not in clean
    assert "Looking for a passionate AI engineer." in clean


def test_parse_datetime_iso():
    dt = parse_datetime("2026-11-01T15:30:00Z")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 11
    assert dt.day == 1
    assert dt.tzinfo == timezone.utc


def test_normalize_employment_type():
    assert normalize_employment_type("Contractor / B2B") == EmploymentType.CONTRACT
    assert normalize_employment_type("Full Time") == EmploymentType.FULL_TIME
    assert normalize_employment_type("Summer Intern") == EmploymentType.INTERNSHIP
