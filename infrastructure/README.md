# infrastructure — Containers and IaC

> **Status:** Placeholder — implementation begins in Phase 1.

---

## Overview

Dockerfiles and Terraform configuration for all environments. Kept flat until volume justifies sub-folders.

---

## Planned Files

| File | Purpose |
|---|---|
| `Dockerfile.web` | Frontend container — nginx serving the Vite production build |
| `Dockerfile.api` | Backend API container — FastAPI on UBI minimal |
| `main.tf` | Root Terraform configuration — IBM Cloud resources |
| `variables.tf` | Input variable declarations |
| `outputs.tf` | Output value declarations |
| `dev.tfvars` | Development environment variable values |
| `staging.tfvars` | Staging environment variable values |
| `production.tfvars` | Production environment variable values (no secrets — referenced from Secrets Manager) |

---

## IBM Cloud Resources (Terraform)

- Code Engine (web and API containers)
- Cloud Databases for PostgreSQL
- Cloud Databases for Redis
- Cloud Object Storage
- App ID (authentication)
- Secrets Manager
- Log Analysis

---

## Docker Requirements

All images must:
- Use `registry.redhat.io` base images only
- Run as a non-root user (UID 1001)
- Use read-only root filesystem where possible
- Pass vulnerability scanning before registry push

```dockerfile
# Example pattern
FROM registry.redhat.io/ubi9/python-312-minimal:latest

RUN useradd -m -u 1001 appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
USER 1001

CMD ["uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"]
```

---

## Notes

- Terraform state is never committed. Use IBM Cloud remote state backend.
- Variable files containing non-secret values are committed. Secrets are referenced from IBM Secrets Manager at apply time — never stored in `.tfvars` files.
- Split into `terraform/` and `docker/` sub-folders only when file count warrants it.
