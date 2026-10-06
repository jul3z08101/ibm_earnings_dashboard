# Operations

> This document is a placeholder. Complete before Phase 5 launch.

---

## Environments

| Environment | Purpose | Deployment Trigger |
|---|---|---|
| `local` | Active development | Manual — `uvicorn` + `vite dev` |
| `dev` | Shared integration testing | Push to `develop` branch |
| `staging` | UAT and pre-production validation | Merge to `staging` branch |
| `production` | Live stakeholder access | Approved PR merged to `main` |

---

## Health Checks

| Endpoint | Service | Expected Response |
|---|---|---|
| `GET /health` | API | `{"status": "ok"}` |
| Frontend root | Web | HTTP 200 |

---

## Runbooks (Placeholders)

| Scenario | File |
|---|---|
| API will not start | `runbook-api-startup.md` — to be written |
| Document upload failing | `runbook-upload-failure.md` — to be written |
| Database connection error | `runbook-db-connection.md` — to be written |
| Auth / IBM App ID outage | `runbook-auth-outage.md` — to be written |

---

## Deployment

> Step-by-step deployment procedures to be written when Code Engine configuration is complete (Phase 2).

---

## Monitoring

> Alert definitions and dashboard configuration to be written when IBM Cloud Logs is provisioned (Phase 2).

Planned alerts:
- API error rate > 1% over 5 minutes
- Document ingestion failures
- Authentication failure spike
- Disk/storage approaching capacity limit
