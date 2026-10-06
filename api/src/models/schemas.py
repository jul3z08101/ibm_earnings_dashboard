from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from src.models.database import Base


class Document(Base):
    """A source document uploaded by a user."""
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, index=True)
    company     = Column(String(16), nullable=False, index=True)
    period      = Column(String(16), nullable=False)       # e.g. "Q2 2026"
    doc_type    = Column(String(32), nullable=False)       # transcript | press-release | ...
    file_name   = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)     # local path or COS key
    char_count  = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Transcript(Base):
    """A saved transcript section (live or pasted)."""
    __tablename__ = "transcripts"

    id          = Column(Integer, primary_key=True, index=True)
    company     = Column(String(16), nullable=False, index=True)
    period      = Column(String(16), nullable=False)
    section     = Column(String(255), nullable=False, default="Unnamed Section")
    body        = Column(Text, nullable=False)
    source      = Column(String(32), default="manual")    # manual | live
    created_at  = Column(DateTime, default=datetime.utcnow)


class LibraryItem(Base):
    """A measure or KPI extracted from a document and accepted to the reference library."""
    __tablename__ = "library_items"

    id           = Column(Integer, primary_key=True, index=True)
    company      = Column(String(16), nullable=False, index=True)
    name         = Column(String(255), nullable=False)
    measure_type = Column(String(16), nullable=False)     # nongaap | kpi | gaap
    category     = Column(String(32), nullable=False)     # cashflow | profitability | ...
    periods      = Column(String(512), default="")        # comma-separated list of periods
    context      = Column(Text, default="")               # representative snippet
    source_file  = Column(String(255), default="")
    first_seen   = Column(String(16), default="")
    confidence   = Column(Float, default=1.0)
    created_at   = Column(DateTime, default=datetime.utcnow)
