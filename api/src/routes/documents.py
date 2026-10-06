import os
import shutil
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import Document
from src.services.extraction import extract_measures

router = APIRouter()

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
LOCAL_UPLOAD_DIR = os.getenv("LOCAL_UPLOAD_DIR", "./data/uploads")

ALLOWED_TYPES = {"text/plain", "application/pdf", "text/html"}
MAX_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class DocumentOut(BaseModel):
    id: int
    company: str
    period: str
    doc_type: str
    file_name: str
    char_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


def _save_local(upload: UploadFile, dest_dir: str) -> tuple[str, int]:
    """Save an uploaded file to local disk. Returns (storage_path, char_count)."""
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, upload.filename)
    content = upload.file.read()
    with open(dest, "wb") as f:
        f.write(content)
    # Attempt UTF-8 decode for char count; fall back gracefully for binary PDFs
    try:
        char_count = len(content.decode("utf-8", errors="replace"))
    except Exception:
        char_count = len(content)
    return dest, char_count


@router.post("", response_model=DocumentOut, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    company: str = Form(...),
    period: str = Form(...),
    doc_type: str = Form(...),
    db: Session = Depends(get_db),
):
    # Content-type validation
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: txt, pdf, html.",
        )

    # Size check
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")

    # Store file
    if STORAGE_BACKEND == "local":
        storage_path, char_count = _save_local(file, LOCAL_UPLOAD_DIR)
    else:
        # COS adapter — placeholder for Phase 2
        raise HTTPException(status_code=501, detail="COS storage not yet implemented.")

    doc = Document(
        company=company,
        period=period,
        doc_type=doc_type,
        file_name=file.filename,
        storage_path=storage_path,
        char_count=char_count,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=List[DocumentOut])
def list_documents(
    company: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Document)
    if company:
        q = q.filter(Document.company == company)
    return q.order_by(Document.uploaded_at.desc()).all()


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    # Remove from local storage if it exists
    if STORAGE_BACKEND == "local" and os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)
    db.delete(doc)
    db.commit()


@router.post("/{doc_id}/extract")
def extract_document(doc_id: int, db: Session = Depends(get_db)):
    """Run extraction on a previously uploaded document and return suggested items."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="Source file not found on disk.")
    with open(doc.storage_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    suggestions = extract_measures(text, doc.company, doc.period, doc.file_name)
    return {"doc_id": doc_id, "suggestions": suggestions}
