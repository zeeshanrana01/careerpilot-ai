"""Deterministic normalization for raw job listings."""
import re
from datetime import datetime, timezone
from typing import Optional
from dateutil import parser as date_parser

from careerpilot.domain.models import (
    WorkplaceType,
    EmploymentType,
    SalaryRange,
)

# Common company suffixes to strip for canonical entity matching
LEGAL_SUFFIXES_REGEX = re.compile(
    r"(?i)[,\s]+(inc\.?|incorporated|llc\.?|ltd\.?|limited|corp\.?|corporation|co\.?|gmbh|sa|bv|pvt\.?)(?=\s|$|\.)"
)

# Title normalization dictionary (regex pattern -> replacement)
TITLE_ABBREVIATIONS = [
    (re.compile(r"(?i)\bsr\.?(?=\s|$|[,\-/])"), "Senior"),
    (re.compile(r"(?i)\bjr\.?(?=\s|$|[,\-/])"), "Junior"),
    (re.compile(r"(?i)\beng\.?(?=\s|$|[,\-/])"), "Engineer"),
    (re.compile(r"(?i)\bswe(?=\s|$|[,\-/])"), "Software Engineer"),
    (re.compile(r"(?i)\bsw(?=\s|$|[,\-/])"), "Software"),
    (re.compile(r"(?i)\bml(?=\s|$|[,\-/])"), "Machine Learning"),
    (re.compile(r"(?i)\bai(?=\s|$|[,\-/])"), "AI"),
    (re.compile(r"(?i)\bnlp(?=\s|$|[,\-/])"), "NLP"),
    (re.compile(r"(?i)\bgenai(?=\s|$|[,\-/])"), "Generative AI"),
    (re.compile(r"(?i)\bllm(?=\s|$|[,\-/])"), "LLM"),
]


def normalize_title(raw_title: str) -> tuple[str, WorkplaceType]:
    """
    Clean job title, standardize abbreviations, and extract workplace indicator if embedded in title.
    Example: 'Sr. AI Eng. (Remote)' -> ('Senior AI Engineer', WorkplaceType.REMOTE)
    """
    if not raw_title:
        return "", WorkplaceType.UNSPECIFIED
    
    title = raw_title.strip()
    detected_workplace = WorkplaceType.UNSPECIFIED
    
    if re.search(r"(?i)\b(remote|work from home|wfh)\b", title):
        detected_workplace = WorkplaceType.REMOTE
    elif re.search(r"(?i)\bhybrid\b", title):
        detected_workplace = WorkplaceType.HYBRID
    elif re.search(r"(?i)\b(on-site|onsite|in-office)\b", title):
        detected_workplace = WorkplaceType.ONSITE
        
    title = re.sub(r"(?i)\s*[\(\[\{]\s*(remote|hybrid|on-site|onsite|wfh)\s*[\)\]\}]", "", title)
    title = re.sub(r"(?i)\s*-\s*(remote|hybrid|on-site|onsite|wfh)\b", "", title)

    if title.isupper() and len(title) > 4:
        title = title.title()

    for pattern, replacement in TITLE_ABBREVIATIONS:
        title = pattern.sub(replacement, title)
        
    title = re.sub(r"\s+", " ", title).strip()

    title = re.sub(r"\bAi\b", "AI", title)
    title = re.sub(r"\bMl\b", "ML", title)
    title = re.sub(r"\bLlm\b", "LLM", title)
    title = re.sub(r"\bNlp\b", "NLP", title)

    return title, detected_workplace


def normalize_company(raw_company: str) -> tuple[str, str]:
    """
    Normalize company name.
    Returns: (display_name, core_key)
    Example: 'Anthropic, PBC.' -> ('Anthropic', 'anthropic')
    """
    if not raw_company:
        return "", ""
    
    display = raw_company.strip()
    cleaned = LEGAL_SUFFIXES_REGEX.sub("", display)
    cleaned = re.sub(r"[,\.]+$", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        cleaned = display
        
    core_key = re.sub(r"[^a-z0-9]", "", cleaned.lower())
    return cleaned, core_key


def normalize_location(raw_location: Optional[str], fallback_workplace: WorkplaceType) -> tuple[Optional[str], WorkplaceType]:
    """Extract location string and refine workplace type."""
    if not raw_location:
        return None, fallback_workplace
    
    loc = raw_location.strip()
    workplace = fallback_workplace
    
    if re.search(r"(?i)\b(remote|work from home|wfh)\b", loc):
        workplace = WorkplaceType.REMOTE
    elif re.search(r"(?i)\bhybrid\b", loc):
        workplace = WorkplaceType.HYBRID
    elif re.search(r"(?i)\b(on-site|onsite|in-office)\b", loc):
        workplace = WorkplaceType.ONSITE
        
    loc = re.sub(r"\s+", " ", loc).strip()
    return (loc if loc else None), workplace


def parse_salary(salary_raw: Optional[str]) -> Optional[SalaryRange]:
    """
    Parse messy salary strings into structured numeric ranges.
    Handles '$150k - $200k', '€80,000 - €100,000', etc.
    """
    if not salary_raw:
        return None
    
    raw = salary_raw.strip().lower()
    
    currency = "USD"
    if "€" in raw or "eur" in raw:
        currency = "EUR"
    elif "£" in raw or "gbp" in raw:
        currency = "GBP"
    elif "pkr" in raw or "rs" in raw:
        currency = "PKR"
    elif "cad" in raw:
        currency = "CAD"
        
    period = "YEARLY"
    if "hour" in raw or "/hr" in raw or "hr" in raw:
        period = "HOURLY"
    elif "month" in raw or "/mo" in raw:
        period = "MONTHLY"
        
    pattern = re.compile(r"[\$€£]?\s*(\d+(?:[,\.]\d+)?)\s*(k)?", re.IGNORECASE)
    matches = pattern.findall(raw)
    
    if not matches:
        return None
    
    numbers: list[float] = []
    for num_str, is_k in matches:
        clean_num = num_str.replace(",", "")
        try:
            val = float(clean_num)
            if is_k or (val < 1000 and period == "YEARLY"):
                val *= 1000.0
            numbers.append(val)
        except ValueError:
            continue
            
    if not numbers:
        return None
        
    min_amount = min(numbers)
    max_amount = max(numbers)
    
    return SalaryRange(
        min_amount=min_amount,
        max_amount=max_amount,
        currency=currency,
        period=period
    )


def parse_datetime(raw_date: Optional[str]) -> Optional[datetime]:
    """Parse dates robustly into UTC datetime."""
    if not raw_date:
        return None
    
    try:
        parsed = date_parser.parse(raw_date)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        return parsed
    except Exception:
        return None


def normalize_employment_type(raw_type: Optional[str]) -> EmploymentType:
    """Normalize employment types into standard enum."""
    if not raw_type:
        return EmploymentType.FULL_TIME
    
    text = raw_type.lower()
    if "contract" in text or "freelance" in text:
        return EmploymentType.CONTRACT
    elif "part" in text or "half" in text:
        return EmploymentType.PART_TIME
    elif "intern" in text:
        return EmploymentType.INTERNSHIP
    elif "full" in text:
        return EmploymentType.FULL_TIME
    return EmploymentType.OTHER
