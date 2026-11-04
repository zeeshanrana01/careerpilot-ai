"""Deterministic deduplication and fingerprint generation for job listings."""
import re
from typing import Optional
from careerpilot.core.security import compute_sha256, canonicalize_url
from careerpilot.intake.normalizer import normalize_company, normalize_title
from careerpilot.domain.models import WorkplaceType


def generate_dedup_key(
    company: str,
    title: str,
    location: Optional[str] = None,
    workplace_type: WorkplaceType = WorkplaceType.UNSPECIFIED
) -> str:
    """
    Generate a deterministic SHA-256 fingerprint for a job listing based on its core identity.
    Ignores superficial formatting, case differences, and marketing tracking tags.
    """
    _, company_core = normalize_company(company)
    title_clean, _ = normalize_title(title)
    
    title_core = re.sub(r"[^a-z0-9]", "", title_clean.lower())
    
    if workplace_type == WorkplaceType.REMOTE:
        loc_core = "remote"
    elif location:
        loc_core = re.sub(r"[^a-z0-9]", "", location.lower())
    else:
        loc_core = "unspecified"
        
    raw_key = f"{company_core}:{title_core}:{loc_core}"
    return compute_sha256(raw_key)


def compute_url_fingerprint(url: Optional[str]) -> Optional[str]:
    """Compute deterministic hash of canonicalized URL if URL is available."""
    if not url:
        return None
    canonical = canonicalize_url(url)
    return compute_sha256(canonical) if canonical else None
