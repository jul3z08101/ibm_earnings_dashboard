# Contributing

> **Status:** Placeholder — finalize before onboarding contributors.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready. Protected — direct pushes blocked. |
| `staging` | Integration testing and UAT. Deploys to staging environment. |
| `develop` | Active development integration branch. |
| `feature/*` | Individual feature or fix branches, cut from `develop`. |

---

## Pull Request Process

1. Cut a branch from `develop`: `feature/short-description` or `fix/short-description`.
2. Open a PR against `develop` and fill in the PR template.
3. All CI checks must pass before review is requested.
4. At least one code owner approval required before merge.
5. Squash-merge into `develop`.

---

## Commit Conventions

Conventional Commits format:

```
feat(transcript): add speaker label support to analyzer
fix(api): correct JWT expiry validation logic
docs(adr): add ADR-0003 authentication provider decision
```

---

## Standards

- All new code includes unit tests.
- No secrets, API keys, or credentials in code or configuration files.
- All user-facing strings sanitized before DOM insertion.
- No `console.log` or `print` statements containing sensitive data.

---

## Security Vulnerabilities

Do not open a public issue for security vulnerabilities. Follow `docs/security.md` incident response procedures.
