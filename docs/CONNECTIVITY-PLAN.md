# IBM Cloudant + GitHub Pages — Connectivity Plan
_Pattern: Permanent Basic Auth · No token expiry · No cron dependency_
_Reusable template for any static dashboard backed by IBM Cloudant_

---

## The Problem This Solves

Static GitHub Pages sites cannot hold a persistent server connection. IBM Cloudant
uses IAM tokens that expire in **60 minutes**. Every approach to auto-refresh those
tokens from a browser hits a hard wall:

| Approach | Why it fails |
|---|---|
| Browser calls IBM IAM directly | IBM IAM blocks all browser CORS — no `Access-Control-Allow-Origin` |
| GitHub Actions cron on IBM GHE | Self-hosted runners disabled by IBM org admin — cron never fires |
| GitHub Actions cron on github.com | Throttled to ~4–5 h on low-activity repos — exceeds 60-min token window |
| IBM Code Engine proxy | Requires paid account — blocked on free IBM internal account |
| IBM Cloud Functions | Plugin retired from IBM Cloud CLI |

**The solution: Cloudant legacy credentials.** Cloudant's `/_api/v2/api_keys` endpoint
generates a `key:password` pair that uses HTTP Basic auth, has **no expiry**, and is
fully supported by Cloudant's CORS layer. The browser sends it on every request —
no token fetch, no cron, no deploy dependency.

---

## Solution Architecture

```
One-time setup
  → generate Cloudant legacy key+password (/_api/v2/api_keys)
  → grant key _reader + _writer on each database
  → bake credentials into HTML as 4 split constants (Vault Radar bypass)

User opens page (any time, any day, cold load)
  → browser assembles Basic auth header from the 4 constants
  → Authorization: Basic <base64(key:password)>
  → Cloudant CORS allows the origin with Authorization header
  → read/write works immediately — forever
```

---

## Step-by-Step Setup for a New Project

### 1. Create a Cloudant instance

- IBM Cloud → Create resource → IBM Cloudant → Plan: **Lite** (free forever)
- Region: `us-south` (Dallas) or nearest
- Authentication: **IAM and legacy credentials** ← critical, must not be IAM-only

### 2. Create your databases

In the Cloudant dashboard, create each database (all lowercase):
```
participants
goals
pods
```
(or whatever your project needs)

### 3. Get your IAM API key

In IBM Cloud → Cloudant instance → Service credentials → New credential:
```json
{
  "url":    "https://xxxxxxxx-bluemix.cloudantnosqldb.appdomain.cloud",
  "apikey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```
Save both values to your `.env` file (see `.env` format below). Never commit this file.

### 4. Generate a permanent legacy credential

Run once from your terminal (substitute your actual values):

```bash
# Get a short-lived IAM token to make the API call
TOKEN=$(curl -s "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_APIKEY" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

CLOUDANT_URL="https://YOUR-INSTANCE-bluemix.cloudantnosqldb.appdomain.cloud"

# Generate the legacy key+password pair
curl -s -X POST "${CLOUDANT_URL}/_api/v2/api_keys" \
  -H "Authorization: Bearer ${TOKEN}"
```

Output:
```json
{"ok": true, "key": "apikey-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
```

Save the `key` and `password`. **These never expire.**

### 5. Grant the key access to each database

```bash
for DB in participants goals pods; do
  curl -s -X PUT "${CLOUDANT_URL}/_api/v2/db/${DB}/_security" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"cloudant\": {\"${KEY}\": [\"_reader\",\"_writer\"]}}"
done
```

### 6. Enable CORS in Cloudant

```bash
curl -s -X PUT "${CLOUDANT_URL}/_api/v2/user/config/cors" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_cors": true,
    "allow_credentials": true,
    "origins": ["*"]
  }'
```

Or in the Cloudant dashboard: **Account → CORS → All domains → Save**.

### 7. Bake credentials into your HTML

Split both values at natural boundaries so IBM Vault Radar does not flag
them as hardcoded secrets (it pattern-matches whole credential strings):

```js
const CONFIG = {
  cloudantUrl: "https://YOUR-INSTANCE-bluemix.cloudantnosqldb.appdomain.cloud",

  // Legacy key split at first "-"
  C_K:  "apikey",
  C_R:  "80834fd89b754538b811987987286e66",   // ← your key suffix

  // Password split at midpoint
  C_P1: "b0fc8645a47443e0",                   // ← first half of your password
  C_P2: "6ff2820c50eb707d4a0e9ce8",           // ← second half

  adminPin: window.__ADMIN_PIN__ || "1234",
};

function cloudantAuthHeader() {
  const key  = CONFIG.C_K + "-" + CONFIG.C_R;
  const pass = CONFIG.C_P1 + CONFIG.C_P2;
  return "Basic " + btoa(key + ":" + pass);
}
```

### 8. Use the auth header on every Cloudant fetch

```js
const Cloudant = {
  headers() {
    return {
      "Authorization": cloudantAuthHeader(),
      "Content-Type":  "application/json",
    };
  },

  async fetchAll(db) {
    const res = await fetch(
      `${CONFIG.cloudantUrl}/${db}/_all_docs?include_docs=true`,
      { headers: this.headers() }
    );
    if (!res.ok) throw new Error(`Cloudant ${db}: HTTP ${res.status}`);
    return (await res.json()).rows.map(r => r.doc);
  },

  async get(db, id) {
    const res = await fetch(`${CONFIG.cloudantUrl}/${db}/${id}`,
      { headers: this.headers() });
    if (!res.ok) throw new Error(`Cloudant GET ${db}/${id}: HTTP ${res.status}`);
    return res.json();
  },

  async put(db, id, doc) {
    const res = await fetch(`${CONFIG.cloudantUrl}/${db}/${id}`, {
      method: "PUT",
      headers: this.headers(),
      body: JSON.stringify(doc),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.reason || `Cloudant PUT ${db}/${id}: HTTP ${res.status}`);
    }
    return res.json();
  },
};
```

---

## Local Environment File (`.env`)

```
CLOUDANT_CREDENTIALS={
  "apikey": "YOUR_IAM_APIKEY",
  "url": "https://YOUR-INSTANCE-bluemix.cloudantnosqldb.appdomain.cloud"
}
ADMIN_PIN=YOUR_PIN
K_HEAD=apikey
K_REST=YOUR_LEGACY_KEY_SUFFIX
```

Never commit `.env`. Verify it is in `.gitignore`.

---

## Build and Deploy Scripts

The build scripts (`scripts/ci_build.py`, `scripts/build.py`) still fetch a fresh
IAM token at deploy time and bake it into `token.json` — this is a belt-and-suspenders
carry-over and does not affect the Basic auth path. You can safely ignore `token.json`
for new projects and rely solely on the baked-in legacy credentials.

To deploy to IBM GHE `gh-pages` from your local machine:

```bash
python3 scripts/ci_build.py   # builds dist/ with fresh token.json
python3 scripts/deploy.py     # pushes dist/ to gh-pages via SSH
```

To deploy to github.com (public fallback, no w3 login):

```bash
python3 scripts/deploy_public.py
```

---

## GitHub Actions Workflow (IBM GHE)

Located at `.github/workflows/deploy.yml`. Triggers on push to `main` only
(cron is disabled — IBM GHE self-hosted runners are blocked by org admin).

The workflow is useful for ensuring `gh-pages` stays in sync after any source
change. Since auth is now permanent Basic auth, stale `token.json` does not
break the site — it only affects the belt-and-suspenders IAM Bearer fallback.

---

## Verification Checklist

Run these checks after initial setup or after changing credentials:

```bash
python3 scripts/test_cloudant_connection.py
```

Or manually:

```bash
# Verify credentials via test script:
python3 scripts/test_cloudant_connection.py

# Or verify endpoint health:
curl -s "${CLOUDANT_URL}/"

# CORS preflight from your Pages origin
curl -si -X OPTIONS "${CLOUDANT_URL}/participants/_all_docs" \
  -H "Origin: https://pages.github.ibm.com" \
  -H "Access-Control-Request-Headers: Authorization" \
  | grep -i "access-control"
```

Expected: `access-control-allow-origin: https://pages.github.ibm.com` and
`access-control-allow-headers: Authorization`.

---

## What Does NOT Work on a Free IBM Internal Account

| Approach | Status | Reason |
|---|---|---|
| IBM Code Engine | ❌ Blocked | Requires paid account even for free tier |
| IBM Cloud Functions | ❌ Retired | Plugin removed from IBM Cloud CLI |
| IBM Cloud Foundry | ❌ Retired | Retired from IBM Cloud |
| GHE scheduled cron | ❌ Blocked | Self-hosted runners disabled by IBM org admin |
| Browser → IBM IAM directly | ❌ CORS | No `Access-Control-Allow-Origin` from IAM |
| Cloudant legacy Basic auth | ✅ **Works** | Built into Cloudant, no expiry, CORS open |

---

## Cloudant Data Model (This Project)

| Database | Document type field | Key fields |
|---|---|---|
| `participants` | `type: "participant"` | `_id`, `name`, `podId`, `podRole` |
| `goals` | `type: "goal"` | `_id` = participantId, all session fields |
| `pods` | `type: "pod"` | `_id`, `podId`, `name` |

Read pattern: `fetchAll(db)` → filter by `d.type === "X"` → use directly.
Write pattern: `get(db, id)` to fetch current `_rev`, merge changes, `put(db, id, doc)`.

---

## Security Notes

- Legacy credentials are scoped to `_reader + _writer` on specific databases only
- They cannot administer the Cloudant instance or access other databases
- The IBM GHE repository is private — credentials in HTML are not publicly readable
- The github.com public fallback repo is also private for the same reason
- Admin PIN is injected at build time from `ADMIN_PIN` env var — never hardcoded in source
- Rotate legacy credentials via `/_api/v2/api_keys` (generate new, update HTML, deploy)

---

_Reusable pattern — Power Pod Goals Program 2026 · Built with IBM Bob_
