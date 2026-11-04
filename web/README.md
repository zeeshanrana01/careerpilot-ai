# CareerPilot AI — Next.js Web Frontend

Production web client for CareerPilot AI built with **Next.js 14 (App Router)**, **TypeScript**, **Tailwind CSS**, and **Lucide React**.

## Features

- **Ranked Opportunity Queue**: Real-time opportunity cards displaying AI match scores, executive reasoning, fact-checked strengths citations, and identified gaps.
- **Milestone 3 Application Drafter**: Interactive modal showing tailored CV variants and personalized cover emails with cryptographic draft hashes (`SHA-256`).
- **Human-in-the-Loop Review Gate**: Approve or reject application drafts before any external submission occurs.
- **Untrusted Input Shield Modal**: Live job ingestion modal that tests script neutralization and prompt-injection detection in real-time.
- **Verified Career Profile Explorer**: Review verified skills with years of experience tags and career preferences.
- **Immutable Security Audit Log**: Live audit ledger connecting to the SQLite database.

## Running Locally

1. **Start the FastAPI Backend** (in root directory):
   ```bash
   ..\.venv\Scripts\python.exe scripts/run_web.py
   ```
   Backend runs on `http://localhost:8000`.

2. **Start the Next.js Frontend** (in `web` directory):
   ```bash
   npm run dev
   ```
   Frontend opens on `http://localhost:3000`.
