import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.database import init_db
from src.routes import documents, library, transcripts

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="IBM Earnings Dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the Vite dev server and any localhost origin during development.
# Tighten to specific origins before staging/production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
app.include_router(library.router, prefix="/library", tags=["library"])


@app.get("/health")
def health():
    return {"status": "ok"}
