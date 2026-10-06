# IBM Earnings Transcript Dashboard — Production Strategy Brainstorm

> **Status:** Awaiting approval before scaffolding begins
> **Prepared:** 2026-09-14
> **Source evaluated:** `dashboard.html` (2,389 lines, single-file prototype)

---

## 1. Tab-by-Tab Evaluation & Visibility Recommendation

### Summary Decision Table

| Tab | Current Role | Stakeholder Visibility | Recommendation |
|---|---|---|---|
| **Overview** | KPI summary, compliance score, flags, activity log | **High** — executives, reviewers, IR | Primary landing page |
| **Live Transcribe** | Real-time speech capture → Transcript Analyzer | **High** — call participants | Primary nav |
| **Transcript Analyzer** | Analyze text vs. reference library | **High** — technical accounting, SEC review team | Primary nav |
| **SEC/Non-GAAP Compliance** | Flag register, Reg G checklist | **Medium** — compliance, legal, IR | Secondary nav, role-gated |
| **KPI Tracker** | Cross-quarter KPI entry, auto-flags | **Medium** — finance team | Secondary nav, role-gated |
| **Document Library** | Upload, extraction, reference library mgmt | Low — operational | Admin panel only |
| **Peer Comparison** | KPI matrix, non-GAAP adoption | Low — data-sparse until populated | Admin panel / report export |
| **Industry Trends** | Theme/sentiment log | Low — fully manual | Admin panel |
| **Companies** | Company registry | None — administrative | Admin panel only |

---

### Detailed Per-Tab Notes

#### Overview — Primary
- Provides the single most important view: IBM compliance score, open high/medium flags,
  peer count, documents loaded.
- Needs real data to be meaningful — score logic (100 − 20×high − 8×medium) is a reasonable
  heuristic but should be documented as indicative only.
- **Production upgrade:** Replace hardcoded score formula with a configurable rules engine.
  Add trend sparklines for flags-over-time and KPI counts.

#### Live Transcribe — Primary
- Core differentiator. The auto-restart loop, elapsed timer, interim display, and
  Send-to-Analyzer flow are all solid for a prototype.
- **Production upgrade:** Replace browser Web Speech API (Google server dependency, Chrome/Edge only)
  with an approved STT provider (IBM Watson Speech-to-Text, or Azure Cognitive Services)
  invoked from a backend service. Add speaker diarization, consent capture, and session
  archival with retention controls.

#### Transcript Analyzer — Primary
- Library-vs-transcript diff is the highest-value analytical function.
- Known / New / Safe Harbor classification works well for the prototype.
- **Critical production fix first:** The `JSON.stringify(f).replace(/"/g,'&quot;')` pattern
  used to pass item objects into inline `onclick` handlers is fragile and an XSS vector.
  Replace with data attributes + event delegation.
- **Production upgrade:** Surface confidence scores, source citations (page/paragraph),
  and a structured review workflow with disposition tracking.

#### SEC/Non-GAAP Compliance — Secondary Nav
- Flag register and Reg G checklist are useful for the compliance review team.
- Not needed by executives or IR — should be role-gated.
- **Production upgrade:** Flag workflow needs status history (not just open/resolved),
  assignee, evidence attachments, and immutable audit trail. Checklist should be versioned
  against SEC guidance effective dates.

#### KPI Tracker — Secondary Nav
- Useful for finance team cross-period analysis.
- Auto-flag generation for definition changes and proxy inconsistency is a valuable feature.
- **Production upgrade:** KPIs should be sourced from the extraction pipeline (not manual entry
  only). Add period-over-period visualization and peer comparison charts.

#### Document Library — Admin Only
- High complexity, low stakeholder value. Uploading documents, reviewing extraction suggestions,
  and managing the reference library are operational tasks, not review tasks.
- The client-side PDF parser (`extractPDFText`) is too fragile for production — it will silently
  fail on most real IBM earnings PDFs (compressed streams, embedded fonts, scanned pages).
- **Production replacement:** Dedicated backend ingestion service (Python/Apache Tika or
  IBM Watson Discovery) with async job queue, source citations, and confidence scores.
  Stakeholder UI shows "Library Status" read-only panel — no upload controls.

#### Peer Comparison — Admin / Report Export
- Matrix is only useful when KPI data is populated for multiple companies.
- Pre-seeding 22 proxy peers with no data produces an empty, confusing table.
- **Production upgrade:** Auto-populate from a licensed data feed or structured extraction.
  Expose as a read-only report, not an editable matrix.

#### Industry Trends — Admin Only
- Entirely manual, no extraction backing, low signal-to-noise ratio early on.
- Valuable eventually for longitudinal research but not a stakeholder-facing priority.
- **Production upgrade:** Semi-automate using NLP sentiment on analyzed transcripts.
  Surface as a curated report rather than a manual log.

#### Companies — Admin Only
- Pure registry management — no stakeholder value.
- Should be an admin-only settings page accessible from an admin panel, not the main nav.

---

## 2. Recommended Stakeholder Navigation (Production)

```
Primary Nav (all authenticated users)
  ├── Overview          (landing page)
  ├── Live Transcribe   (active earnings calls)
  └── Transcript Analyzer

Secondary Nav (compliance / finance roles)
  ├── Compliance Flags
  └── KPI Tracker

Admin Panel (admin role only, separate route)
  ├── Document Library & Ingestion
  ├── Reference Library Management
  ├── Company Registry
  ├── Peer Comparison
  └── Industry Trends
```

---

## 3. Technology Stack Recommendation

### Guiding Principles
- IBM security policy compliance (container images from `registry.redhat.io`, no 0.0.0.0 binding,
  TLS 1.2+, no hardcoded secrets, RBAC, structured logging)
- Minimize operational surface area for a small team
- IBM-first tooling where available and appropriate
- Clear separation between frontend, backend API, ingestion workers, and data stores

### Frontend
| Concern | Recommendation | Why |
|---|---|---|
| Framework | **React 18 + TypeScript** | Component model maps well to tab/module structure; strong ecosystem |
| Build | **Vite** | Fast dev experience, simple config, modern ESM output |
| Styling | **Tailwind CSS** or keep current custom CSS | Current CSS system is clean — either is fine |
| State | **Zustand** or **React Query** | Lightweight; avoids Redux overhead for this use case |
| Auth UI | **SAML / OpenID Connect** (IBM SSO) | Required by IBM security policy |
| Hosting | **IBM Cloud Code Engine** or static CDN behind IBM AppID | Serverless, IBM-native |

### Backend API
| Concern | Recommendation | Why |
|---|---|---|
| Runtime | **Node.js 22 (LTS) + Express** or **Python 3.12 + FastAPI** | Both well-supported; FastAPI preferred if ingestion team uses Python |
| Auth | **IBM App ID** (OIDC/SAML) + JWT validation middleware | IBM-native, satisfies RBAC requirement |
| Container | `registry.redhat.io/ubi9/nodejs-22-minimal` or `python-312-minimal` | IBM security policy requires Red Hat registry |
| Secrets | **IBM Secrets Manager** | IBM Key Protect / Secrets Manager for all credentials |
| Logging | **Structured JSON** to IBM Log Analysis (LogDNA) | Required by security policy; no sensitive data in logs |

### Data Layer
| Store | Use | Technology |
|---|---|---|
| Relational DB | Companies, flags, KPIs, reviews, audit events | **PostgreSQL 16** on IBM Cloud Databases |
| Object Storage | Source PDFs, audio recordings, export archives | **IBM Cloud Object Storage** (encrypted, lifecycle policies) |
| Search Index | Documents, transcript sections, library items | **Elasticsearch / OpenSearch** or IBM Watson Discovery |
| Session / Cache | Auth sessions, job status | **Redis 7** on IBM Cloud Databases |

### Ingestion & AI Services
| Concern | Recommendation |
|---|---|
| PDF parsing | **Apache Tika** (server-side) or **AWS Textract / IBM Watson Discovery** for OCR |
| Speech-to-Text | **IBM Watson Speech-to-Text** (on-prem option available; IBM-native; data-residency controls) |
| NLP / extraction | **IBM Watson NLP** or fine-tuned HuggingFace model for measure classification |
| Background jobs | **Bull / BullMQ** (Node) or **Celery** (Python) with Redis queue |

---

## 4. Production Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        IBM Cloud                                │
│                                                                 │
│  ┌──────────────┐     ┌────────────────┐     ┌──────────────┐  │
│  │   React SPA   │────▶│   API Service  │────▶│  PostgreSQL  │  │
│  │ (Code Engine) │     │ (FastAPI/Node) │     │  (IBM CDB)   │  │
│  └──────────────┘     └───────┬────────┘     └──────────────┘  │
│          │                    │                                 │
│     IBM App ID           ┌────▼──────┐     ┌──────────────┐    │
│     (Auth/RBAC)          │  Workers  │────▶│  Object Store│    │
│                          │ (BullMQ)  │     │  (COS/PDFs)  │    │
│                          └────┬──────┘     └──────────────┘    │
│                               │                                 │
│                    ┌──────────▼──────────┐                      │
│                    │  IBM Watson STT      │                      │
│                    │  + NLP Ingestion     │                      │
│                    └─────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Critical Prototype Issues to Fix Before Any Production Work

These are must-fix before the prototype is used with real sensitive data:

| Priority | Issue | Fix |
|---|---|---|
| **P0** | XSS: `innerHTML` interpolation of user text throughout render functions | Sanitize all user content; use `textContent` or a sanitizer library (DOMPurify) |
| **P0** | XSS: `JSON.stringify(f).replace(/"/g,'&quot;')` in onclick attrs (lines ~1895, ~1923) | Replace with `data-*` attributes + event delegation |
| **P0** | `localStorage` only — no access control, no backup | For any real data, move to authenticated server-side persistence immediately |
| **P1** | PDF extraction silently fails on real IBM earnings PDFs | Replace with server-side Tika/OCR pipeline |
| **P1** | `switchTab` uses implicit browser `event` global | Pass `event` explicitly or restructure |
| **P1** | No CSP header — inline scripts throughout | Add Content-Security-Policy; externalize JS |
| **P2** | `alert()` / `confirm()` for all user feedback | Replace with non-blocking toast/modal notifications |
| **P2** | README path discrepancy (`../dashboard.html` vs actual location) | Correct README §2 and §10 |

---

## 6. Phased Development Plan

### Phase 0 — Governance & Decisions (2 weeks, no code)
- Define data classification: are live earnings call transcripts MNPI? Who can access?
- Determine consent/recording-notice requirements for Live Transcribe.
- Select approved STT provider and confirm data-residency requirements.
- Define user roles: Admin, Reviewer, Viewer — and what each can see/do.
- Confirm IBM App ID as the identity provider.
- Get legal sign-off on peer data sourcing strategy.

### Phase 1 — Repository Foundation (2 weeks)
- Initialize Git repo, branch protection, CI/CD skeleton (GitHub Actions or IBM Toolchain).
- Scaffold frontend (React + Vite + TS) and backend API (FastAPI or Express + TS).
- Add linting (ESLint, Prettier), type checks, and unit test framework (Vitest / pytest).
- Implement IBM App ID authentication end-to-end (login → JWT → protected route).
- Port Overview, Live Transcribe, and Transcript Analyzer tabs as React components.
- Wire Live Transcribe to IBM Watson STT backend endpoint (stub if STT not yet approved).
- Replace `localStorage` with authenticated API endpoints and PostgreSQL.
- Fix all P0 XSS issues before first deploy.

### Phase 2 — Data Platform (3 weeks)
- Define PostgreSQL schema: companies, periods, documents, library_items, flags, kpis,
  transcripts, audit_events.
- Implement RBAC middleware: role-check on every API route.
- Build document upload API: type validation, malware scan hook, COS storage, provenance metadata.
- Build async ingestion worker: Tika PDF parsing → NLP extraction → library upsert.
- Build audit log: every state-changing action records user, timestamp, before/after.
- Add structured logging (no PII/secrets) to IBM Log Analysis.

### Phase 3 — Compliance & KPI Workflows (2 weeks)
- Port Compliance Flags and KPI Tracker as role-gated secondary nav.
- Add flag assignment, evidence attachments, and disposition history.
- Implement versioned Reg G checklist tied to SEC guidance effective dates.
- Add KPI period-over-period comparison charts.
- Add JSON export and CSV report download.

### Phase 4 — Admin Panel & Peer Data (2 weeks)
- Build admin-only panel: Document Library, Company Registry, Reference Library mgmt,
  Industry Trends, Peer Comparison.
- Implement peer data ingestion strategy (manual upload or licensed feed).
- Add search index for documents and transcript sections.
- Conduct accessibility audit (WCAG 2.1 AA) and performance review.

### Phase 5 — Hardening & Launch (3 weeks)
- Threat model review and penetration test.
- Privacy impact assessment for STT / transcript data.
- Add E2E tests (Playwright) for primary user flows.
- Add monitoring, alerting, and runbooks.
- Load test ingestion pipeline.
- Stakeholder UAT, change-management communications, and launch.

---

## 7. Folder Structure Preview (for Phase 3 scaffold approval)

```
ibm-earnings-dashboard/
├── apps/
│   ├── web/                    # React + Vite + TypeScript frontend
│   └── api/                    # FastAPI or Express backend service
├── packages/
│   ├── domain/                 # Shared TypeScript/Python types & business rules
│   ├── extraction/             # Document parsing & measure-detection logic
│   ├── compliance-rules/       # Versioned Reg G / SEC rule definitions
│   └── ui/                     # Shared accessible React component library
├── workers/
│   └── ingestion/              # Async PDF/OCR/NLP ingestion worker
├── infrastructure/
│   ├── terraform/              # IaC for IBM Cloud resources
│   └── docker/                 # Dockerfiles (registry.redhat.io base images)
├── docs/
│   ├── adr/                    # Architecture Decision Records
│   ├── security/               # Threat model, security controls
│   └── operations/             # Runbooks, monitoring, deployment
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/               # Approved sample documents for regression
├── scripts/                    # Dev utilities, seed scripts, migration helpers
├── .github/
│   └── workflows/              # CI/CD pipeline definitions
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

---

## 8. Open Questions Requiring Stakeholder Input

| # | Question | Why It Matters |
|---|---|---|
| 1 | Are live earnings call transcripts classified as MNPI? | Drives access control, retention, and storage architecture |
| 2 | Which IBM-approved STT provider should be used? | Determines Live Transcribe backend architecture |
| 3 | Is IBM App ID the correct identity provider, or is there an existing enterprise SSO? | Determines auth integration path |
| 4 | What is the intended deployment environment? (IBM Cloud, on-prem, hybrid) | Drives infrastructure choices |
| 5 | Who are the named roles? (e.g. Technical Accounting, IR, Legal, Admin) | Determines RBAC model |
| 6 | Is peer data sourced manually or from a licensed financial data feed? | Determines Peer Comparison architecture |
| 7 | What are the document retention and legal-hold requirements? | Drives COS lifecycle policy and deletion workflow |
| 8 | Is the Q1/Q2 2026 reference PDF corpus approved for use as regression test fixtures? | Determines whether existing PDFs can be committed to the test repo |

---

*This document is a brainstorm artifact — not a binding specification. All technology, architecture,
and sequencing decisions remain subject to stakeholder review, governance approvals, and security
sign-off before implementation begins.*
