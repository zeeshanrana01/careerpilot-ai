-- CareerPilot AI SQLite Schema (Production Foundation)

-- 1. Jobs table: Normalized job listings with deduplication constraint
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    dedup_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    workplace_type TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    description_clean TEXT NOT NULL,
    salary_min REAL,
    salary_max REAL,
    salary_currency TEXT DEFAULT 'USD',
    salary_period TEXT DEFAULT 'YEARLY',
    source_url TEXT,
    source_name TEXT NOT NULL,
    posted_date TEXT,
    deadline TEXT,
    security_flags TEXT,
    status TEXT NOT NULL DEFAULT 'NEW',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_dedup_key ON jobs(dedup_key);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_source_url ON jobs(source_url);

-- 2. Verified Career Profile table
CREATE TABLE IF NOT EXISTS career_profile (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    headline TEXT NOT NULL,
    summary TEXT NOT NULL,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 3. Job Matches table: evaluation against verified CV
CREATE TABLE IF NOT EXISTS job_matches (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    overall_score REAL NOT NULL,
    recommendation TEXT NOT NULL,
    strengths_json TEXT NOT NULL,
    gaps_json TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    grounding_verified INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    CONSTRAINT uq_job_match UNIQUE(job_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_score ON job_matches(overall_score DESC);

-- 4. Applications table: tailored submissions
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    cv_version TEXT NOT NULL,
    email_draft TEXT,
    status TEXT NOT NULL DEFAULT 'DRAFTED',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT uq_application_job UNIQUE(job_id)
);

-- 5. Approval Requests table: enforces human approval before external actions
CREATE TABLE IF NOT EXISTS approval_requests (
    id TEXT PRIMARY KEY,
    application_id TEXT REFERENCES applications(id) ON DELETE CASCADE,
    proposed_action TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    approval_status TEXT NOT NULL DEFAULT 'PENDING',
    expires_at TEXT,
    created_at TEXT NOT NULL,
    decided_at TEXT
);

-- 6. Audit Events table: complete traceable log of every action
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'system',
    outcome TEXT NOT NULL DEFAULT 'SUCCESS',
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
