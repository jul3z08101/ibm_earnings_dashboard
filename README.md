# IBM Earnings Transcript Dashboard

> **Status:** Phase 1 — core implementation complete, running locally.
> **Prototype baseline:** `web/dashboard.html`
> **Strategy and planning:** `docs/`

---

## Overview

A browser-based review workspace for IBM earnings materials. Supports live call transcription, transcript analysis against a reference library of known measures, SEC Regulation G / non-GAAP compliance flagging, and KPI tracking across reporting periods and peer companies.

**Target users:** Technical Accounting, SEC Reporting, Investor Relations, Finance, and Legal review teams.

---

## Structure

```
ibm-earnings-dashboard/
├── web/              # React + Vite + TypeScript frontend
├── api/              # Python FastAPI backend
├── docs/             # All project documentation — see docs/README.md
├── tests/            # Unit, integration, E2E, and regression fixtures
├── infrastructure/   # Dockerfiles (Phase 1) and Terraform IaC (Phase 2)
├── scripts/          # Dev utilities, seed scripts, migration helpers (Phase 2)
├── chat-threads/     # Session reference library — decisions, rationale, open items
└── .github/
    └── workflows/    # CI/CD pipeline definitions
```

---

## Getting Started

> To be completed after Phase 1 implementation.

```bash
# Frontend
cd web && npm install && npm run dev

# Backend
cd api && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Development Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Governance, data classification, provider decisions | Pending |
| 1 | Auth, primary views (Overview, Live Transcribe, Transcript Analyzer) | Pending |
| 2 | Secure data platform, RBAC, ingestion pipeline | Pending |
| 3 | Compliance flags, KPI tracker | Pending |
| 4 | Admin panel, peer data, search | Pending |
| 5 | Hardening, accessibility audit, launch | Pending |

---

## Security

- Container images from `registry.redhat.io` only
- Services bind to `127.0.0.1` — never `0.0.0.0`
- All credentials via IBM Secrets Manager — nothing hardcoded
- TLS 1.2 minimum; TLS 1.3 preferred
- Authentication via IBM App ID (SAML / OpenID Connect)
- Structured JSON logging — no secrets, tokens, or PII in log output

See `docs/security.md` for the full threat model and controls.

---

## Contributing

See `CONTRIBUTING.md`. Confirm license with legal before any external publication.
