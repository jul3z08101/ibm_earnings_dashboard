from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import LibraryItem

router = APIRouter()


class LibraryItemIn(BaseModel):
    company: str
    name: str
    measure_type: str           # nongaap | kpi | gaap
    category: str
    periods: str = ""           # comma-separated: "Q1 2026,Q2 2026"
    context: str = ""
    source_file: str = ""
    first_seen: str = ""
    confidence: float = 1.0


class LibraryItemOut(BaseModel):
    id: int
    company: str
    name: str
    measure_type: str
    category: str
    periods: str
    context: str
    source_file: str
    first_seen: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=LibraryItemOut, status_code=201)
def add_library_item(payload: LibraryItemIn, db: Session = Depends(get_db)):
    # Upsert: if the same company+name already exists, merge the period in
    existing = (
        db.query(LibraryItem)
        .filter(
            LibraryItem.company == payload.company,
            LibraryItem.name == payload.name,
        )
        .first()
    )
    if existing:
        # Merge periods
        current = set(p.strip() for p in existing.periods.split(",") if p.strip())
        new = set(p.strip() for p in payload.periods.split(",") if p.strip())
        existing.periods = ",".join(sorted(current | new))
        if payload.context and payload.context not in existing.context:
            existing.context = existing.context + "\n" + payload.context if existing.context else payload.context
        db.commit()
        db.refresh(existing)
        return existing

    item = LibraryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=List[LibraryItemOut])
def list_library(
    company: str | None = None,
    measure_type: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(LibraryItem)
    if company:
        q = q.filter(LibraryItem.company == company)
    if measure_type:
        q = q.filter(LibraryItem.measure_type == measure_type)
    return q.order_by(LibraryItem.company, LibraryItem.name).all()


@router.delete("/{item_id}", status_code=204)
def delete_library_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(LibraryItem).filter(LibraryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found.")
    db.delete(item)
    db.commit()
