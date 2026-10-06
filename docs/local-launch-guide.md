# IBM Earnings Dashboard — Local Launch Guide

Two processes, one terminal each. Total setup time: approximately 5 minutes on a clean machine.

---

## Prerequisites

| Tool | Minimum Version | Check |
|---|---|---|
| Python | 3.12+ | `python3 --version` |
| Node.js | 20 LTS+ | `node --version` |
| npm | 10+ | `npm --version` |

> **Browser note:** Live Transcribe requires the Web Speech API. Use Chrome or Edge — it is not supported in Firefox or Safari.

---

## Terminal A — API (FastAPI + SQLite)

**1. Navigate to the API directory.**

```bash
cd ibm-earnings-dashboard/api
```

**2. Create and activate a Python virtual environment.**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows: `.venv\Scripts\activate`

**3. Install Python dependencies.**

```bash
pip install -r requirements.txt
```

**4. Create your local environment file.**

No values need to change for a first run — the defaults use SQLite and bypass auth.

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | SQLite file — created automatically on first start |
| `STORAGE_BACKEND` | `local` | Stores uploaded files on disk under `./data/uploads/` |
| `AUTH_MODE` | `dev` | Bypasses JWT validation — remove before staging |

**5. Start the API server.**

The database tables are created automatically on first startup.

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

You should see: `Application startup complete.`

---

## Terminal B — Web (React + Vite)

**1. In a second terminal, navigate to the web directory.**

```bash
cd ibm-earnings-dashboard/web
```

**2. Install Node dependencies.**

Skip this step if `node_modules/` already exists.

```bash
npm install
```

**3. Start the Vite dev server.**

```bash
npm run dev
```

You should see: `Local: http://127.0.0.1:5173/`

> **Proxy is automatic.** All `/api/*` requests from the browser are silently forwarded to `http://127.0.0.1:8000` by Vite — no additional configuration needed.

**4. Open the app in Chrome or Edge.**

```
http://127.0.0.1:5173
```

---

## Verify Both Services Are Up

| Service | URL | Expected |
|---|---|---|
| API health check | `http://127.0.0.1:8000/health` | `{"status": "ok"}` |
| API interactive docs | `http://127.0.0.1:8000/docs` | FastAPI Swagger UI — all endpoints browsable |

---

## API Endpoints — Quick Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/documents` | List all uploaded documents |
| `POST` | `/documents` | Upload a PDF or text file |
| `POST` | `/documents/{id}/extract` | Run extraction on a document |
| `DELETE` | `/documents/{id}` | Remove a document |
| `POST` | `/transcripts` | Save a transcript |
| `GET` | `/transcripts` | List all saved transcripts |
| `DELETE` | `/transcripts/{id}` | Delete a transcript |
| `GET` | `/library` | List all library items |
| `POST` | `/library` | Add or merge a library item |
| `DELETE` | `/library/{id}` | Remove a library item |

---

## Troubleshooting

**Port 8000 already in use**
Run `lsof -i :8000` and kill the conflicting process, or start uvicorn on a different port and update `web/vite.config.ts` to match.

**ModuleNotFoundError on uvicorn start**
Confirm the virtualenv is activated (`which python` should point inside `.venv/`), then re-run `pip install -r requirements.txt`.

**API calls fail with CORS error in browser**
Ensure the frontend is running on `127.0.0.1:5173`, not `localhost:5173`. Both origins are allow-listed in `api/src/main.py`.

**Live Transcribe shows no microphone button or fails silently**
Web Speech API requires Chrome or Edge. Confirm the browser has microphone permission granted for `127.0.0.1`.

**npm install fails with peer dependency errors**
Run `npm install --legacy-peer-deps`. The project targets Node 20 LTS — downgrading to an older Node version can cause this.
