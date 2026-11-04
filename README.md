# CareerPilot AI

<div align="center">

<p align="center">
  <strong>Production-Ready Personal AI Career Agent</strong><br>
  <em>Private Job Discovery · Untrusted Input Defense · Explainable CV Matching · Human-in-the-Loop Approval</em>
</p>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-27%20Passed%20(100%25)-brightgreen.svg)]()
[![Security Shield](https://img.shields.io/badge/Security-Zero--Trust%20Untrusted%20Input-orange.svg)]()
[![Inference Engine](https://img.shields.io/badge/AI%20Inference-Local%20Ollama%20%2B%20Cloud-purple.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)]()

<br>

<img src="assets/match_card_preview.svg" alt="CareerPilot AI Opportunity Assessment Card" width="900"/>

</div>

---

## 1. Overview & Applied AI Philosophy

**CareerPilot AI** is a production-grade, private career intelligence system designed for AI and Software Engineers. It automates the noisy, repetitive preparation work of job discovery, CV requirement matching, and tailored application drafting while strictly keeping high-stakes career decisions and external communications under **human control**.

### Core Value Pillars

- **Zero-Trust Untrusted Input Isolation**: Job postings and scraped feeds are treated as untrusted data. Executable tags (`<script>`, `<iframe>`) are stripped, and text is pre-scanned with regex heuristics and encapsulated in strict XML boundaries to repel prompt-injection attempts.
- **Factual Grounding & Anti-Hallucination**: The matching engine evaluates opportunities strictly against verified facts in `career_profile`. It is architecturally prohibited from inventing skills, degrees, or certifications.
- **Hybrid AI Inference**: Combines **Local AI** (Ollama: Llama 3.2, DeepSeek-R1) for private document processing with zero data leakage, and **Cloud AI** (Google Gemini, Anthropic Claude, OpenAI) for deeper semantic synthesis.
- **Tamper-Evident Audit Logging**: Every ingestion, duplication rejection, and match decision appends an immutable record to the SQLite/PostgreSQL `audit_events` table.

---

## 2. Visual Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Job Intake & Security Shield"]
        A["Raw Job Feeds (APIs, Web Pages, JSON)"] --> B["Security Sanitizer (HTML & Script Strip)"]
        B --> C["Entity Normalizer (Titles, Companies, Salary, Workplace)"]
        C --> D["Validator (Completeness, Freshness, Deadlines)"]
        D -- "Invalid / Expired" --> E["Audit Event: REJECTED"]
        D -- "Valid" --> F["Deterministic Fingerprinting (SHA-256)"]
        F -- "Duplicate" --> G["Audit Event: SKIPPED_DUPLICATE"]
        F -- "Unique Job" --> H[("jobs Table (SQLite / Postgres)")]
    end

    subgraph Intelligence ["2. Hybrid AI Match Engine"]
        H --> I["JobMatcher (XML Prompt Isolation)"]
        J[("career_profile Table (Verified Facts)")] --> I
        I --> K{"Inference Router"}
        K -- "Private / Offline" --> L["Local Ollama Engine (Llama 3.2)"]
        K -- "Cloud API" --> M["Cloud LLM Engine (Gemini 2.5)"]
        L --> N["Structured Match Evaluation (0-100 Score, Citations, Gaps)"]
        M --> N
        N --> O[("job_matches Table")]
    end

    subgraph Control ["3. Ranking & Human Approval Gate"]
        O --> P["JobRanker (Salary, Remote, & Preference Filtering)"]
        P --> Q["Ranked Opportunity Queue"]
        Q --> R{"Human Approval Gate"}
        R -- "Approve" --> S["Application Draft Package"]
        R -- "Reject / Skip" --> T["Status: SKIPPED"]
    end
```

<div align="center">
  <img src="assets/architecture_diagram.svg" alt="CareerPilot AI Architecture Diagram" width="900"/>
</div>

---

## 3. Terminal Execution & Test Coverage

The engine is covered by an automated test suite verifying deterministic normalization, deduplication, URL tracking parameter stripping, prompt-injection defense, and end-to-end matching:

<div align="center">
  <img src="assets/terminal_demo.svg" alt="Terminal Execution Demo" width="900"/>
</div>

---

## 4. Repository Structure

```
careerpilot-ai/
├── careerpilot/
│   ├── core/
│   │   ├── config.py             # Pydantic Settings & environment variables
│   │   └── security.py           # Untrusted input sanitization, injection detection, canonical URLs
│   ├── domain/
│   │   └── models.py             # Domain models (RawJobListing, NormalizedJob, JobMatchEvaluation, AuditEvent)
│   ├── intake/
│   │   ├── normalizer.py         # Deterministic title, company, salary, and date normalizers
│   │   ├── deduplicator.py       # SHA-256 identity fingerprinting & URL canonicalization
│   │   ├── validator.py          # Schema completeness, deadline checks, and freshness rules
│   │   └── pipeline.py           # End-to-end JobIntakePipeline coordinator
│   ├── matching/
│   │   ├── providers.py          # Unified LLM providers (Local Ollama, Cloud Gemini, Mock)
│   │   ├── prompts.py            # Security-hardened prompt templates with XML boundaries
│   │   ├── matcher.py            # JobMatcher with grounding verification and audit logging
│   │   └── ranker.py             # JobRanker with preference weighting & salary thresholding
│   └── storage/
│       ├── schema.sql            # Production SQLite DDL for 6 core entities
│       ├── database.py           # Connection management & schema execution
│       └── repository.py         # Atomic JobRepository with audit trail logging
├── data/
│   ├── sample_jobs.json          # Test stream: clean, messy, duplicate, expired, prompt-injected
│   └── sample_career_profile.json# Rana's verified AI engineer career profile
├── scripts/
│   ├── run_intake_demo.py        # Milestone 1 Intake Foundation CLI runner
│   └── run_matching_demo.py      # Milestone 2 Job Intelligence & Match Engine CLI runner
├── tests/
│   ├── conftest.py               # In-memory SQLite fixtures & mock providers
│   ├── test_normalizer.py        # Unit tests for title, company, salary normalization
│   ├── test_deduplicator.py      # Unit tests for identity hashing and UTM stripping
│   ├── test_validator.py         # Unit tests for validation & prompt injection detection
│   ├── test_intake_pipeline.py   # Integration tests for intake pipeline
│   └── test_matching.py          # Integration tests for LLM matching, defense, and ranking
├── assets/                       # SVG architecture, terminal, and dashboard previews
├── pyproject.toml                # Project metadata & pytest configuration
└── README.md
```

---

## 5. Quickstart Guide

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard Python `venv`
- *(Optional)* [Ollama](https://ollama.ai) for local private inference (`ollama run llama3.2:3b`)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/zeeshanrana01/careerpilot-ai.git
cd careerpilot-ai

# Initialize virtual environment with uv
uv venv .venv

# Install production and development dependencies
uv pip install --python .venv/Scripts/python.exe -e . "pytest>=8.0.0" "pytest-asyncio>=0.23.0"
```

### 2. Run the Automated Test Suite

```bash
.\.venv\Scripts\python.exe -m pytest -v
```

All **27 tests** pass in ~1 second with zero external API calls:
- Deduplication across legal suffixes (`Anthropic, Inc.` $\rightarrow$ `Anthropic`)
- Marketing UTM parameter stripping (`?utm_source=linkedin&ref=aggregator`)
- Prompt injection immunity test
- Anti-hallucination grounding validation

### 3. Run the Live Intake Demo

```bash
.\.venv\Scripts\python.exe scripts/run_intake_demo.py
```

### 4. Run the Job Intelligence & Explainable Matching Demo

```bash
.\.venv\Scripts\python.exe scripts/run_matching_demo.py
```

**Sample Output:**
```text
  RANK #1: Senior AI Engineer @ Anthropic
  Score: 90.0/100 | Recommendation: [APPLY] | Workplace: REMOTE | Salary: $185,000 - $240,000
  Executive Assessment: Candidate demonstrates strong alignment with 7 core requirements, backed by verified production projects and skills.
  Strengths (Verified Evidence Citations):
    * Proficiency in Python -> Expert proficiency with 6+ years in Python production systems
    * Proficiency in FastAPI -> 4+ years building high-throughput microservices and APIs
    * Proficiency in LangGraph -> Architected multi-agent LLM systems with LangGraph
  Gaps / Missing Qualifications:
    x None identified in core architectural stack
```

---

## 6. Security & Applied AI Safeguards

| Threat Vector | Mitigation Strategy | Implementation |
| :--- | :--- | :--- |
| **Prompt Injection in Listings** | Regex scan, tag stripping, and XML boundary encapsulation | [`careerpilot/core/security.py`](careerpilot/core/security.py), [`prompts.py`](careerpilot/matching/prompts.py) |
| **Model Hallucination** | System directives prohibiting extrapolation; strict grounding verification | [`careerpilot/matching/matcher.py`](careerpilot/matching/matcher.py) |
| **Data Privacy Leakage** | Local Ollama inference mode processes sensitive CV data entirely on-device | [`careerpilot/matching/providers.py`](careerpilot/matching/providers.py) |
| **Unintended External Actions** | State machine requires cryptographic hash match and human sign-off | [`careerpilot/storage/schema.sql`](careerpilot/storage/schema.sql) |
| **Duplicate Application Submissions** | SHA-256 fingerprinting on normalized `company:title:location` | [`careerpilot/intake/deduplicator.py`](careerpilot/intake/deduplicator.py) |

---

## 7. Practical Roadmap

- [x] **Milestone 1 — Intake Foundation**: Normalized data pipeline, deduplication, SQLite schema, verified profile, 100% test coverage.
- [x] **Milestone 2 — Job Intelligence**: Hybrid Local/Cloud LLM provider interface, XML prompt isolation, explainable match scoring (0-100), preference-based ranking.
- [ ] **Milestone 3 — Application Drafting**: Tailored CV highlight variants and personalized cover emails referencing verified facts.
- [ ] **Milestone 4 — Approval Engine & Email Integration**: LangGraph interrupt workflow, cryptographic draft hashes, and human-in-the-loop email review queue.
- [ ] **Milestone 5 — Production Dashboard**: Next.js dashboard, FastAPI REST endpoints, and n8n background scheduling.

---

## 8. License

Distributed under the **Apache 2.0 License**. Built by [Rana Zeeshan](https://github.com/zeeshanrana01).
