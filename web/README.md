# web — Frontend Application

> **Stack:** React 18 + TypeScript + Vite
> **Status:** Placeholder — implementation begins in Phase 1.

---

## Overview

The stakeholder-facing single-page application. Handles all UI rendering, client-side routing, authentication flow, and API communication.

The prototype baseline (`dashboard.html`) lives here as the functional reference during Phase 1 decomposition.

---

## Structure

```
src/
├── components/   # Reusable UI primitives — buttons, badges, tables, modals
├── pages/        # Route-level views — Overview, LiveTranscribe, TranscriptAnalyzer, ...
├── hooks/        # Custom React hooks — useAuth, useTranscript, useLibrary, ...
├── lib/          # API client, utilities, constants
└── styles/       # Global styles and design tokens
```

---

## Routes

| Path | View | Access |
|---|---|---|
| `/` | Overview | All authenticated users |
| `/transcribe` | Live Transcribe | All authenticated users |
| `/analyze` | Transcript Analyzer | All authenticated users |
| `/compliance` | Compliance Flags | Compliance, Legal, IR |
| `/kpis` | KPI Tracker | Finance, Compliance |
| `/admin/*` | Admin Panel | Admin only |

---

## Commands

```bash
# First-time setup
npm install

# Development server (proxies /api/* to http://127.0.0.1:8000)
npm run dev        # Opens at http://127.0.0.1:5173

# Production build
npm run build

# Type check
npm run typecheck

# Lint
npm run lint
```

---

## Environment Variables

> All values are non-secret client-side identifiers. No credentials are stored in frontend code.

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API base URL |
| `VITE_APP_ID_CLIENT_ID` | IBM App ID client ID |
| `VITE_APP_ID_DISCOVERY_ENDPOINT` | IBM App ID OIDC discovery endpoint |

---

## Notes

- Auth is handled via IBM App ID (OpenID Connect). The frontend attaches a JWT to all API requests.
- The prototype uses `localStorage` — replaced with authenticated API calls in Phase 1.
- The component library (`src/components/`) absorbs the shared UI primitives for now. Extract to a standalone package only if a second frontend application is introduced.
