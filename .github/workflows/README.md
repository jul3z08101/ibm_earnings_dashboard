# .github/workflows — CI/CD Pipelines

> **Status:** Placeholder — pipeline definitions written in Phase 1.

---

## Planned Workflows

| File | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push / PR to any branch | Lint, typecheck, unit and integration tests |
| `e2e.yml` | PR to `staging` or `main` | End-to-end tests against a preview environment |
| `deploy-dev.yml` | Push to `develop` | Build and deploy to dev |
| `deploy-staging.yml` | Merge to `staging` | Build, test, deploy to staging |
| `deploy-production.yml` | Approved PR merged to `main` | Build, test, deploy to production |
| `dependency-scan.yml` | Scheduled daily | Scan dependencies for known vulnerabilities |
| `container-scan.yml` | On Dockerfile change | Scan images before registry push |

---

## Quality Gates

All must pass before a PR can merge:

- Lint and type check
- Unit tests with minimum coverage threshold
- Integration tests
- Dependency vulnerability scan — no unaddressed critical or high CVEs
- Container scan (for PRs touching infrastructure files)

---

## Secrets

Pipeline secrets are stored as GitHub Actions encrypted secrets and sourced from IBM Secrets Manager at deploy time. No credentials are written into workflow YAML files.
