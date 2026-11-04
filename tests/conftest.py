"""Pytest fixtures for CareerPilot AI tests."""
import json
import sqlite3
from pathlib import Path
import pytest

from careerpilot.storage.database import SCHEMA_PATH
from careerpilot.storage.repository import JobRepository
from careerpilot.intake.pipeline import JobIntakePipeline
from careerpilot.matching.matcher import JobMatcher
from careerpilot.matching.providers import MockLLMProvider
from careerpilot.matching.ranker import JobRanker
from careerpilot.domain.models import RawJobListing, CareerProfile

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def sqlite_conn():
    """In-memory SQLite connection with full schema loaded."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        
    yield conn
    conn.close()


@pytest.fixture
def repository(sqlite_conn):
    """JobRepository backed by in-memory SQLite."""
    return JobRepository(sqlite_conn)


@pytest.fixture
def intake_pipeline(repository):
    """JobIntakePipeline wired to in-memory repository."""
    return JobIntakePipeline(repository)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for fast deterministic testing."""
    return MockLLMProvider()


@pytest.fixture
def job_matcher(mock_llm_provider, repository):
    """JobMatcher initialized with mock provider and repository."""
    return JobMatcher(mock_llm_provider, repository)


@pytest.fixture
def job_ranker(repository):
    """JobRanker initialized with repository."""
    return JobRanker(repository)


@pytest.fixture
def sample_jobs_raw() -> list[RawJobListing]:
    """Load sample raw job listings from JSON data file."""
    path = DATA_DIR / "sample_jobs.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [RawJobListing(**item) for item in data]


@pytest.fixture
def sample_career_profile() -> CareerProfile:
    """Load sample verified career profile for Rana."""
    path = DATA_DIR / "sample_career_profile.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return CareerProfile.model_validate(data)
