# APP-STRUCTURE.md — Application Structure, Deferred Items, and Production Resources

> **Last updated:** Phase 3 scaffold
> **Purpose:** Single reference for what is active, what is deferred, what costs money,
> and how to run the application on available free-tier IBM resources during development.

---

## 1. Current Active Structure

What exists in the scaffold and is in scope for Phase 1 implementation:

```
ibm-earnings-dashboard/
│
├── web/                        ACTIVE — Phase 1
│   └── src/
│       ├── components/         ACTIVE — Phase 1
│       ├── pages/              ACTIVE — Phase 1
│       ├── lib/                ACTIVE — Phase 1  (API client, auth helpers)
│       └── styles/             ACTIVE — Phase 1
│
├── api/                        ACTIVE — Phase 1 (non-negotiable, see Section 3)
│   └── src/
│       ├── routes/             ACTIVE — Phase 1
│       ├── services/           ACTIVE — Phase 1  (extraction, compliance, domain logic)
│       ├── middleware/         ACTIVE — Phase 1  (JWT validation, RBAC, error handling)
│       ├── models/             ACTIVE — Phase 1  (database schema)
│       └── jobs/               DEFERRED — Phase 2  (async ingestion queue)
│
├── infrastructure/             ACTIVE (Dockerfiles) — Phase 1
│                               DEFERRED (Terraform IaC) — Phase 2
│
├── docs/                       ACTIVE — ongoing
├── tests/
│   ├── unit/                   ACTIVE — Phase 1
│   ├── fixtures/               ACTIVE — Phase 1
│   ├── integration/            DEFERRED — Phase 2
│   └── e2e/                    DEFERRED — Phase 4
│
├── scripts/                    DEFERRED — Phase 2
├── .github/workflows/          ACTIVE — Phase 1  (CI from first commit)
│
├── web/src/hooks/              DEFERRED — added when first custom hook is needed
└── (Terraform files)           DEFERRED — Phase 2
```

---

## 2. Deferred Items — Full Register

These items exist as empty folders or are not yet created. They are deferred because
they require scale, a second consumer, or infrastructure that is not needed in Phase 1.

| Item | Deferred To | Trigger for Promotion |
|---|---|---|
| `api/src/jobs/` | Phase 2 | When document ingestion is too slow to run synchronously (> ~5 sec) or needs a retry queue |
| `tests/integration/` | Phase 2 | When the database schema is stable enough to test against |
| `tests/e2e/` | Phase 4 | When primary user flows are stable and a staging environment exists |
| `scripts/` | Phase 2 | When the first seed or migration script is actually needed |
| Terraform IaC in `infrastructure/` | Phase 2 | When cloud resources move beyond a single developer instance |
| `web/src/hooks/` | Phase 1 (add as needed) | When the first reusable hook is extracted from a component |
| Standalone packages (`domain/`, `extraction/`, `compliance-rules/`, `ui/`) | Phase 4+ | Only if a second frontend or service needs to import shared code |
| Standalone ingestion worker container | Phase 3+ | Only if the jobs folder needs independent scaling or deployment |
| Search index (OpenSearch / Watson Discovery) | Phase 4 | When full-text search across documents and transcripts is required |
| Speaker diarization in Live Transcribe | Phase 5 | Requires approved STT provider with speaker-label support |

---

## 3. Why the API Cannot Be Deferred

Manual document uploads via the browser UI still require a backend. The API handles:

- Receiving the uploaded file over HTTPS
- Validating content type, size, and running a malware scan hook
- Storing the file (IBM COS in production; local volume in development)
- Running text extraction and writing results to the database
- Serving extraction results and all application state back to the frontend
- Enforcing authentication (IBM App ID JWT validation) on every request

Keeping uploads browser-only (as in the prototype) means no persistent storage, no auth,
no audit trail, and no sharing between users. The API is load-bearing from Phase 1.

---

## 4. Resources Required for Production

Everything below requires provisioning, approval, or has a recurring cost.
Review each item with your team before Phase 1 deployment.

### 4.1 IBM Cloud Services

| Service | Purpose | Requires Approval | Estimated Cost |
|---|---|---|---|
| **IBM Cloud Account** | Root account for all IBM Cloud resources | Yes — IBM internal provisioning process | Internal |
| **IBM App ID** | User authentication (OIDC/SAML), JWT issuance | Yes — confirm with security team | Lite: free up to 1,000 users/month; Standard: pay-per-use |
| **IBM Cloud Code Engine** | Serverless container hosting for `web` and `api` | No — self-service | Free tier: 400 vCPU-seconds and 100 GB-seconds per month; pay-per-use beyond |
| **IBM Cloud Object Storage** | Store uploaded PDFs, audio files, exports | No — self-service | Lite: 25 GB storage + 20 GB egress/month free; Standard: pay-per-use |
| **IBM Cloud Databases for PostgreSQL** | Persistent relational storage for all application state | No — self-service | **No Lite plan — paid only.** Cheapest tier: ~$48/month (multi-zone, 1 vCPU, 4 GB RAM). Verify current pricing in IBM Cloud catalog. |
| **IBM Cloud Container Registry** | Store Docker images | No — self-service | Free tier: 0.5 GB storage; Standard: ~$0.07/GB/month |
| **IBM Secrets Manager** | Store and rotate all credentials | No — self-service | Trial: 5 secrets free; Standard: pay-per-secret/month |
| **IBM Cloud Logs** | Structured log ingestion and search | No — self-service | Lite: 500 MB/day with 3-day retention; Standard: pay-per-GB |
| **IBM Watson Speech-to-Text** | Live Transcribe backend (replaces browser Web Speech API) | Yes — data classification review required | Lite: 500 minutes/month free; Plus: pay-per-minute |

### 4.2 Development Tooling (External Services)

| Service | Purpose | Requires Approval | Cost |
|---|---|---|---|
| **GitHub** (or IBM GitHub Enterprise) | Source control, CI/CD via GitHub Actions | Yes — confirm whether IBM GitHub Enterprise is required or public GitHub is permitted | IBM GHE: internal; Public GitHub: free for private repos (Teams plan for branch protection: ~$4/user/month) |
| **GitHub Actions** | CI/CD pipeline execution | Follows GitHub account | Free tier: 2,000 minutes/month for private repos; pay-per-minute beyond |

### 4.3 Items Requiring Explicit Sign-Off

These are not just cost items — they require a decision or approval before use:

| Item | Why Sign-Off Is Required |
|---|---|
| IBM Watson Speech-to-Text | Audio from earnings calls may be MNPI. Confirm data classification, retention policy, and whether audio leaves IBM infrastructure. |
| IBM App ID vs. existing enterprise SSO | IBM may have an existing SSO that must be used instead of provisioning a new App ID instance. Confirm with IT/security. |
| GitHub (public) vs. IBM GitHub Enterprise | Confirm which is permitted for this project's data classification. |
| IBM Cloud account and billing owner | Someone must own the IBM Cloud account and accept billing responsibility. |
| PostgreSQL paid tier | No free option exists — requires budget approval before any production data is stored. |

---

## 5. How to Run With Free Tier Resources (Development Only)

This is the lowest-cost path to get a working development environment using IBM
free/Lite tiers and local substitutes where IBM has no free option.

> **These substitutes are for development only. Do not use local storage or SQLite
> with real earnings data. Replace all local substitutes before any stakeholder access.**

### Development Stack (Zero Cost)

| Production Resource | Development Substitute | Notes |
|---|---|---|
| IBM Cloud Databases for PostgreSQL | **SQLite** (local file) | SQLAlchemy supports both. Switch by changing `DATABASE_URL`. Zero cost, zero setup. |
| IBM Cloud Object Storage | **Local filesystem** (`/tmp/uploads/` or `./data/uploads/`) | Store uploaded files locally during dev. Replace COS client with a local file adapter. |
| IBM Secrets Manager | **`.env` file** (local only, never committed) | Use `python-dotenv` to load env vars locally. `.env` is in `.gitignore`. |
| IBM Cloud Logs | **Console logging** (stdout) | FastAPI logs to stdout by default. Structured JSON locally; forward to IBM Cloud Logs in production. |
| IBM App ID (authentication) | **Local JWT stub** or skip auth in dev | Implement a dev-mode flag that accepts a hardcoded test token. Remove before staging deploy. |
| IBM Cloud Code Engine | **`uvicorn` locally** + **`vite dev`** locally | Run API and frontend directly on localhost. No container needed in dev. |
| IBM Cloud Container Registry | **Local Docker build** | Build and run containers locally with `docker build` + `docker run`. Push to registry only for staging/production. |
| IBM Watson Speech-to-Text | **Browser Web Speech API** (existing prototype behavior) | Keep the current browser-based transcription for development. Replace with Watson STT when approved. |

### Minimal Setup Steps (Development)

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd ibm-earnings-dashboard

# 2. Start the API (Python + SQLite, no cloud dependencies)
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Copy and edit environment file — never commit this
cp .env.example .env
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Start the frontend
cd ../web
npm install
npm run dev
# Opens at http://localhost:5173
```

### Example `.env.example` (committed — no real values)

```
# Database — use SQLite for local dev
DATABASE_URL=sqlite:///./dev.db

# File storage — use local filesystem for local dev
STORAGE_BACKEND=local
LOCAL_UPLOAD_DIR=./data/uploads

# Auth — set to "dev" to skip JWT validation locally
AUTH_MODE=dev

# IBM Cloud — leave blank locally, populated via Secrets Manager in production
IBM_APP_ID_JWKS_URI=
COS_ENDPOINT=
COS_BUCKET=
SECRETS_MANAGER_URL=
```

---

## 6. IBM Cloud Free Tier Summary

> **Note:** IBM Cloud pricing and plan limits change. Verify all figures in the
> [IBM Cloud catalog](https://cloud.ibm.com/catalog) before committing to a budget.
> The figures below reflect known plan structures at time of writing.

| Service | Free / Lite Tier | Hard Limit Before Cost |
|---|---|---|
| IBM App ID | Lite plan available | 1,000 authentication events/month |
| IBM Cloud Code Engine | Free tier included | 400 vCPU-seconds + 100 GB-seconds/month |
| IBM Cloud Object Storage | Lite plan available | 25 GB storage + 20 GB outbound/month |
| IBM Cloud Container Registry | Free tier included | 0.5 GB image storage |
| IBM Watson Speech-to-Text | Lite plan available | 500 minutes/month |
| IBM Cloud Logs | Lite plan available | 500 MB/day, 3-day retention |
| IBM Secrets Manager | Trial available | 5 secrets |
| **IBM Cloud Databases for PostgreSQL** | **No free tier** | **Paid from first instance** |

**Bottom line:** A development environment costs nothing if using local SQLite and local
file storage. The only IBM Cloud costs begin when you move to a shared or staging
environment and provision PostgreSQL. Everything else has a usable free tier for low-volume
development and early testing.

---

## 7. Path From Development to Production

```
Local dev (free)
  SQLite + local files + .env + localhost
        |
        v
IBM Cloud dev instance (low cost)
  PostgreSQL Lite-equivalent (smallest paid tier) + COS Lite + App ID Lite
  Code Engine (free tier likely sufficient for low traffic)
        |
        v
Staging
  Full IBM Cloud stack, real auth, real STT (if approved)
  All Lite tiers upgraded to Standard as needed
        |
        v
Production
  Standard/paid tiers for all services
  Secrets Manager, full audit logging, monitoring
  Pen test and compliance review complete
```
