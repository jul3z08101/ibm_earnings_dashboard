# Architecture Decision Records

> Each significant technical decision is appended below as a numbered entry.
> Decisions are permanent — supersede rather than delete.

---

## ADR Format

```
## ADR-NNNN — Title
Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by ADR-XXXX

### Context
### Decision
### Consequences
```

---

## Pending — Required Before Phase 1 Deployment

The following decisions must be documented before implementation advances:

| # | Decision |
|---|---|
| ADR-0001 | Frontend framework (React 18 + Vite — confirm) |
| ADR-0002 | Backend language and framework (Python 3.12 + FastAPI — confirm) |
| ADR-0003 | Authentication provider (IBM App ID vs. existing enterprise SSO) |
| ADR-0004 | Database selection (PostgreSQL — confirm tier and region) |
| ADR-0005 | Object storage approach (IBM COS vs. local for Phase 1) |
| ADR-0006 | Speech-to-text provider and data classification ruling |
| ADR-0007 | PDF ingestion approach (synchronous extraction vs. async worker) |
| ADR-0008 | Source control (public GitHub vs. IBM GitHub Enterprise) |

---

<!-- Add accepted ADRs below this line -->
