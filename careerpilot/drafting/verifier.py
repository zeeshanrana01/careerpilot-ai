"""Automated claim verification engine for application drafts."""
import re
from careerpilot.domain.models import CareerProfile
from careerpilot.drafting.models import CVVariant, CoverEmail, GroundingReport

# Common technical buzzwords to check against candidate profile
TECH_REGEX = re.compile(
    r"\b(Python|PyTorch|TensorFlow|JAX|LangGraph|LangChain|FastAPI|Docker|Kubernetes|vLLM|"
    r"PostgreSQL|Redis|ChromaDB|Qdrant|Milvus|Kafka|AWS|GCP|Azure|Rust|C\+\+|Go|Java|"
    r"React|Next\.js|TypeScript|GraphQL|REST|gRPC|CI/CD|Linux)\b",
    re.IGNORECASE
)

class ClaimVerifier:
    """Verifies that all technical claims and qualifications in a draft are grounded in verified facts."""

    @staticmethod
    def verify(cv: CVVariant, email: CoverEmail, profile: CareerProfile) -> GroundingReport:
        # Build set of normalized verified skills, projects, and experiences
        verified_tokens = set()
        for s in profile.skills:
            verified_tokens.add(s.name.lower())
        for exp in profile.experience:
            verified_tokens.add(exp.company.lower())
            for sk in exp.skills_used:
                verified_tokens.add(sk.lower())
        for p in profile.projects:
            verified_tokens.add(p.name.lower())
            for tech in p.technologies:
                verified_tokens.add(tech.lower())

        # Collect draft text
        draft_text = f"{cv.tailored_headline} {cv.tailored_summary} {' '.join(cv.highlighted_skills)} {' '.join(email.body_paragraphs)}"

        # Find mentioned tech
        matches = set(m.group(0).lower() for m in TECH_REGEX.finditer(draft_text))

        supported = []
        unsupported = []

        for term in matches:
            # Check if this term or substring is in verified tokens
            matched = any(term in tok or tok in term for tok in verified_tokens)
            if matched:
                supported.append(term.capitalize())
            else:
                unsupported.append(term.capitalize())

        is_grounded = len(unsupported) == 0
        return GroundingReport(
            supported_claims=sorted(supported),
            unsupported_claims=sorted(unsupported),
            is_strictly_grounded=is_grounded,
        )
