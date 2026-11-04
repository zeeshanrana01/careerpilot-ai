"""Security utilities for handling untrusted input, prompt injection defense, and hashing."""
import hashlib
import json
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from bs4 import BeautifulSoup


# Prompt injection regex patterns designed to catch unauthorized instruction overrides
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+|any\s+)?(previous|prior|above)\s+(instructions|prompts|directions)\b"),
    re.compile(r"(?i)\bdisregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|unfiltered|dan)\b"),
    re.compile(r"(?i)\b(system\s+prompt|system\s+message)\s*:\s*"),
    re.compile(r"(?i)\b(reveal|output|print|show)\s+(your\s+)?(initial|original|system)\s+(prompt|instructions)\b"),
    re.compile(r"(?i)<\/?(system|instruction|context|override)>"),
    re.compile(r"(?i)\badmin\s+override\b"),
]

DEFAULT_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "reference", "source", "fbclid", "gclid", "msclkid", "tracking_id",
    "gh_src", "trk"
}


def compute_sha256(content: str) -> str:
    """Compute a deterministic SHA-256 hex digest for any string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def detect_prompt_injection(text: str) -> tuple[bool, list[str]]:
    """Scan untrusted text for known prompt injection and instruction override attempts."""
    if not text:
        return False, []
    
    matches = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        found = pattern.findall(text)
        if found:
            matches.append(pattern.pattern)
            
    return (len(matches) > 0, matches)


def clean_untrusted_text(raw_text: str) -> tuple[str, list[str]]:
    """
    Sanitize untrusted text from job descriptions or web feeds.
    - Strips executable/malicious HTML tags (<script>, <iframe>, <style>, etc.)
    - Preserves structural text content
    - Detects potential prompt injection attempts
    - Normalizes excessive whitespace and control characters
    """
    if not raw_text:
        return "", []
    
    warnings: list[str] = []
    
    is_suspicious, matched_patterns = detect_prompt_injection(raw_text)
    if is_suspicious:
        warnings.append(f"Prompt injection pattern detected: {len(matched_patterns)} trigger(s)")

    if "<" in raw_text and ">" in raw_text:
        soup = BeautifulSoup(raw_text, "html.parser")
        for dangerous in soup(["script", "style", "iframe", "object", "embed", "applet", "meta", "link"]):
            dangerous.decompose()
        cleaned_text = soup.get_text(separator="\n")
    else:
        cleaned_text = raw_text

    lines = [line.strip() for line in cleaned_text.splitlines()]
    normalized_lines: list[str] = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                normalized_lines.append("")
                prev_empty = True
        else:
            normalized_lines.append(line)
            prev_empty = False

    result = "\n".join(normalized_lines).strip()
    return result, warnings


def canonicalize_url(raw_url: str, tracking_params: set[str] | None = None) -> str:
    """
    Produce a canonical version of a job URL by:
    - Lowercasing scheme and host
    - Stripping marketing/tracking query parameters (utm_*, ref, gclid, etc.)
    - Sorting remaining query parameters deterministically
    - Stripping fragment (#) and trailing slashes
    """
    if not raw_url:
        return ""
    
    params_to_strip = tracking_params or DEFAULT_TRACKING_PARAMS
    
    parsed = urlparse(raw_url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    if not path and netloc:
        path = ""
    
    filtered_query: list[tuple[str, str]] = []
    if parsed.query:
        for k, v in parse_qsl(parsed.query, keep_blank_values=False):
            if k.lower() not in params_to_strip:
                filtered_query.append((k, v))
                
    filtered_query.sort(key=lambda item: item[0])
    query_str = urlencode(filtered_query)
    
    return urlunparse((scheme, netloc, path, "", query_str, ""))


def extract_json_from_llm(content: str) -> dict:
    """
    Safely extract and parse JSON object from LLM response text,
    stripping markdown backticks, explanations, or trailing commentary.
    """
    content = content.strip()
    # If wrapped in markdown code blocks: ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if match:
        content = match.group(1).strip()
    else:
        # Fallback to finding outer-most braces
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            content = content[start : end + 1]
            
    return json.loads(content)
