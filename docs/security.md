# Security Controls

> Must be completed and reviewed before any Phase 1 deployment that involves real data.
> See IBM security policy requirements in `../BRAINSTORM.md` Section 3.

---

## Data Classification

> To be completed in Phase 0.

| Data Type | Classification | Notes |
|---|---|---|
| Live earnings call transcripts | TBD — likely MNPI | Requires legal ruling before STT provider is selected |
| Uploaded earnings documents | TBD | Confirm whether source PDFs are public or confidential |
| Extracted measures and KPIs | TBD | Derived from earnings documents — classification inherits |
| User credentials | Confidential | Managed via IBM App ID / Secrets Manager |

---

## Threat Model

> STRIDE-based threat model to be completed before Phase 1 deployment.

Surfaces to cover:
- Document upload endpoint (spoofing, tampering, malicious files)
- Transcript save endpoint (injection, data exfiltration)
- Authentication flow (token forgery, session fixation)
- Local file storage in development (unauthorized access)
- Browser Web Speech API (audio interception, data residency)

---

## Control Mapping

| Requirement | Control | Status |
|---|---|---|
| Authentication | IBM App ID OIDC (production) / dev-mode stub (local only) | Dev mode implemented; production pending |
| Authorization | RBAC middleware on all API routes | Placeholder — implement in Phase 1 |
| Data in transit | TLS 1.2+ enforced at load balancer | Phase 2 — not applicable for localhost dev |
| Data at rest | AES-256 encryption via IBM COS | Phase 2 — local filesystem in dev |
| Secrets | IBM Secrets Manager (production) / `.env` (local dev only) | `.env.example` committed; `.env` excluded |
| Logging | Structured JSON, no PII or secrets | FastAPI stdout logging in dev; IBM Cloud Logs in production |
| Input validation | Content-type and size checks on upload | Implemented in `api/src/routes/documents.py` |
| Container security | Red Hat UBI minimal base images, non-root user | Pending — Dockerfiles not yet written |

---

## Incident Response

> Procedure to be written before Phase 1 deployment.

Steps: detect → contain → assess → notify → remediate → post-mortem.
Contact list, escalation path, and notification requirements to be defined with the security team.
