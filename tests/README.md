# tests — Test Suite

> **Status:** Placeholder — framework and first fixtures established in Phase 1.

---

## Structure

| Folder | Scope |
|---|---|
| `unit/` | Pure function and module tests — no I/O, no network |
| `integration/` | Tests against real database, queue, and storage in an isolated environment |
| `e2e/` | Full browser tests against a running application (Playwright) |
| `fixtures/` | Approved sample documents for extraction and compliance regression |

---

## Frameworks

| Scope | Framework |
|---|---|
| Unit — Python | pytest |
| Unit — TypeScript | Vitest |
| Integration | pytest + testcontainers |
| End-to-end | Playwright |

---

## Coverage Requirements

- Unit tests required for all extraction patterns, compliance rule logic, and service methods.
- Integration tests required for all API routes, database operations, and ingestion flow.
- E2E tests required for all primary user flows: login, live transcription, transcript analysis, flag creation, KPI entry, export.

---

## Fixtures

Files in `fixtures/` are used for extraction regression testing. Each file must be:
- Reviewed and approved for inclusion by a legal or compliance stakeholder.
- Stored with provenance metadata (source, retrieval date, reporting period, SHA-256 hash).
- Treated as immutable after initial commit.

The Q1/Q2 2026 IBM reference PDFs in `../reference-pdfs/` are candidates pending governance approval.

---

## Commands

> To be completed after Phase 1 scaffolding.

```bash
pytest tests/unit/
pytest tests/integration/    # Requires Docker for testcontainers
npx playwright test          # E2E
```
