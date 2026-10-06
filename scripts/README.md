# scripts — Developer Utilities

> **Status:** Placeholder — scripts added as needed through Phase 1 and beyond.

---

## Planned Scripts

| Script | Purpose |
|---|---|
| `seed-dev-data.py` | Populate a development database with representative sample data |
| `migrate.py` | Run pending database schema migrations |
| `export-prototype-state.py` | Convert prototype `localStorage` JSON export to the production schema |
| `hash-fixtures.py` | Compute and record SHA-256 hashes for all files in `tests/fixtures/` |
| `check-deps.sh` | Verify dependencies are current and free of unaddressed critical vulnerabilities |

---

## Rules

- Never run against production without explicit documented approval.
- Scripts that modify data must support a `--dry-run` flag.
- No secrets or credentials hardcoded — use environment variables or IBM Secrets Manager references.
