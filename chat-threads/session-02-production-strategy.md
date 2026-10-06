# Session 02 — Production Strategy, Scaffold, and Resource Planning

> **Date:** 2026-09-14
> **Status:** Complete — scaffold built, awaiting Phase 0 governance approvals
> **Phase:** Phase 3 scaffold

---

## What Was Decided

### Tab Visibility
Three tabs are stakeholder-facing; the rest are admin or deferred:

| Tab | Decision |
|---|---|
| Overview | Primary nav — landing page |
| Live Transcribe | Primary nav |
| Transcript Analyzer | Primary nav |
| SEC/Non-GAAP Compliance | Secondary nav, role-gated |
| KPI Tracker | Secondary nav, role-gated |
| Document Library | Admin panel only |
| Peer Comparison | Admin panel / report export |
| Industry Trends | Admin panel only |
| Companies | Admin panel only |

### Technology Stack (IBM-only)
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Python 3.12 + FastAPI
- **Auth:** IBM App ID (OIDC / SAML)
- **Database:** IBM Cloud Databases for PostgreSQL (no free tier — requires budget approval)
- **Object Storage:** IBM Cloud Object Storage (Lite: 25 GB free)
- **STT:** IBM Watson Speech-to-Text (Lite: 500 min/month free; requires data classification approval)
- **Containers:** `registry.redhat.io` UBI minimal base images only
- **Secrets:** IBM Secrets Manager
- **Logging:** IBM Cloud Logs
- **Hosting:** IBM Cloud Code Engine (free tier available)

### Scaffold Structure Decision
Initial scaffold was too deep (5 levels, 28 folders, 4 premature packages). Simplified to:
- Max 3 levels deep
- `apps/` wrapper removed — `web/` and `api/` at root
- 4 packages (`domain/`, `extraction/`, `compliance-rules/`, `ui/`) merged into `api/src/services/` and `web/src/components/` — promoted only when a second consumer exists
- `workers/` merged into `api/src/jobs/` — promoted when independent scaling is needed
- `docs/` kept flat — no sub-folders until file count justifies them
- `infrastructure/` kept flat — Dockerfiles only until Terraform is needed (Phase 2)

### Deferred Items
Items intentionally excluded from Phase 1 scope:

| Item | Deferred To | Trigger |
|---|---|---|
| `api/src/jobs/` (async queue) | Phase 2 | Ingestion too slow to run synchronously |
| `tests/integration/` | Phase 2 | Database schema stable |
| `tests/e2e/` | Phase 4 | Stable flows + staging environment |
| `scripts/` | Phase 2 | First real script needed |
| Terraform IaC | Phase 2 | Resources beyond single dev instance |
| Standalone packages | Phase 4+ | Second consumer exists |
| Standalone ingestion worker | Phase 3+ | Independent scaling needed |
| Speaker diarization | Phase 5 | Approved STT provider with label support |

### Development Free-Tier Strategy
Zero-cost local development using IBM-stack substitutes where no free tier exists:

| Production | Dev Substitute |
|---|---|
| IBM Cloud Databases for PostgreSQL | SQLite (swap via `DATABASE_URL`) |
| IBM Cloud Object Storage | Local filesystem (`./data/uploads/`) |
| IBM Secrets Manager | `.env` file (never committed) |
| IBM Watson STT | Browser Web Speech API (existing prototype) |
| IBM Cloud Code Engine | `uvicorn` + `vite dev` on localhost |

---

## What Was Built / Changed

- `dashboard.html` — all emojis removed (34 locations); executive copy tightened on all tabs
- `BRAINSTORM.md` — created; tab evaluation, tech stack, architecture, 5-phase plan, 8 open questions
- `ibm-earnings-dashboard/` — production scaffold created (simplified structure)
- `ibm-earnings-dashboard/APP-STRUCTURE.md` — active vs. deferred map, production resource register, free-tier dev stack, path to production
- `ibm-earnings-dashboard/web/dashboard.html` — cleaned prototype baseline copied into scaffold
- `ibm-earnings-dashboard/chat-threads/` — this folder

---

## Key Rationale

- Emoji removal: executive stakeholder audience; clean text is more professional and accessible.
- Scaffold simplification: don't create folders to anticipate scale that doesn't exist yet. Promote when there's a real forcing function.
- API is non-negotiable even for manual uploads: file storage, auth, extraction, and audit trail all require a backend.
- PostgreSQL has no free IBM Cloud tier — this is the only Phase 1 item that requires budget approval before proceeding.
- SQLite is a legitimate Phase 1 dev substitute because SQLAlchemy abstracts the difference; switching to PostgreSQL requires only a `DATABASE_URL` change.

---

## Open Items / Carry-Forward to Session 03

### Governance (Phase 0 — blockers before Phase 1 coding)
- [ ] Confirm whether live earnings call transcripts are classified as MNPI
- [ ] Select approved STT provider and confirm data-residency requirements
- [ ] Confirm identity provider: IBM App ID vs. existing enterprise SSO
- [ ] Confirm GitHub type: public GitHub vs. IBM GitHub Enterprise
- [ ] Identify billing owner for IBM Cloud account
- [ ] Get budget approval for PostgreSQL paid tier (~$48/month minimum)
- [ ] Get legal sign-off on peer data sourcing strategy
- [ ] Confirm whether Q1/Q2 2026 reference PDFs can be used as regression test fixtures

### Technical (Phase 1 — first implementation tasks)
- [ ] Fix P0 XSS: replace all `innerHTML` interpolation of user text with `textContent` or DOMPurify
- [ ] Fix P0 XSS: replace `JSON.stringify(f).replace(/"/g,'&quot;')` inline onclick pattern with `data-*` + event delegation
- [ ] Replace `localStorage` with authenticated API + PostgreSQL (or SQLite in dev)
- [ ] Implement IBM App ID authentication end-to-end (or dev-mode JWT stub)
- [ ] Port Overview, Live Transcribe, Transcript Analyzer as React components
- [ ] Wire `uvicorn` API with file upload endpoint (local filesystem in dev)
- [ ] Set up CI pipeline (`.github/workflows/ci.yml`) from first commit

---

## File Index

| File | Action |
|---|---|
| `dashboard.html` | Modified — 34 emoji removed, tab/button/alert copy tightened |
| `BRAINSTORM.md` | Created — strategy, stack, phases, open questions |
| `ibm-earnings-dashboard/README.md` | Created |
| `ibm-earnings-dashboard/APP-STRUCTURE.md` | Created |
| `ibm-earnings-dashboard/CONTRIBUTING.md` | Created |
| `ibm-earnings-dashboard/CHANGELOG.md` | Created |
| `ibm-earnings-dashboard/LICENSE` | Created (placeholder) |
| `ibm-earnings-dashboard/gitignore.txt` | Created (rename to .gitignore on git init) |
| `ibm-earnings-dashboard/web/README.md` | Created |
| `ibm-earnings-dashboard/web/dashboard.html` | Copied — cleaned prototype baseline |
| `ibm-earnings-dashboard/api/README.md` | Created |
| `ibm-earnings-dashboard/infrastructure/README.md` | Created |
| `ibm-earnings-dashboard/docs/README.md` | Created |
| `ibm-earnings-dashboard/tests/README.md` | Created |
| `ibm-earnings-dashboard/scripts/README.md` | Created |
| `ibm-earnings-dashboard/.github/workflows/README.md` | Created |
| `ibm-earnings-dashboard/chat-threads/README.md` | Created |
| `ibm-earnings-dashboard/chat-threads/session-01-prototype-and-live-transcribe.md` | Created |
| `ibm-earnings-dashboard/chat-threads/session-02-production-strategy.md` | Created (this file) |
