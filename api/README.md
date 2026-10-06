# api — Backend Service

> **Stack:** Python 3.12 + FastAPI
> **Status:** Placeholder — implementation begins in Phase 1.

---

## Overview

The backend API service. Handles authentication enforcement, business logic, database access, document upload, and coordination of background ingestion jobs.

Domain models, extraction logic, and compliance rules live in `src/services/` for now. They are promoted to standalone packages only when a second consumer (e.g. a second service or shared library) requires it.

---

## Structure

```
src/
├── routes/      # API route handlers — flags, kpis, transcripts, library, documents, companies
├── services/    # Business logic — extraction, compliance scoring, library management,
│                #   domain types, and Reg G rule definitions
├── middleware/  # JWT validation, RBAC, request logging, error handling
├── models/      # Database models and schema (SQLAlchemy)
└── jobs/        # Background ingestion jobs — promoted to a standalone worker when
                 #   independent scaling is required
```

---

## Key Responsibilities

- Validate IBM App ID JWTs and enforce role-based access on every route.
- Accept document uploads: content-type validation, size limit, malware scan hook, IBM COS storage.
- Expose REST endpoints for the frontend SPA.
- Enqueue and process ingestion jobs (PDF parsing, NLP extraction, library upsert).
- Write structured audit events for every state-changing operation.

---

## Commands

```bash
# First-time setup
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Edit .env — never commit it

# Run development server (SQLite, local file storage — no cloud needed)
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# Run tests
pytest tests/unit/ -v

# Interactive API docs (dev only)
# Open http://127.0.0.1:8000/docs in a browser
```

---

## Environment Variables

Copy `.env.example` to `.env` and edit. All production values are sourced from IBM Secrets Manager — never hardcoded.

| Variable | Default (dev) | Production |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | PostgreSQL connection string |
| `STORAGE_BACKEND` | `local` | `cos` |
| `LOCAL_UPLOAD_DIR` | `./data/uploads` | — |
| `AUTH_MODE` | `dev` | `production` |
| `IBM_APP_ID_JWKS_URI` | _(blank)_ | IBM App ID JWKS endpoint |
| `COS_ENDPOINT` | _(blank)_ | IBM Cloud Object Storage endpoint |
| `COS_BUCKET` | _(blank)_ | Object storage bucket name |
| `SECRETS_MANAGER_URL` | _(blank)_ | IBM Secrets Manager URL |

---

## Security Requirements

- Bind to `127.0.0.1` only.
- Validate JWT on every request before any processing.
- Parameterized queries only — no string interpolation in database statements.
- No sensitive data in logs.
- Uploaded files validated for content type, size, and malware before storage.
