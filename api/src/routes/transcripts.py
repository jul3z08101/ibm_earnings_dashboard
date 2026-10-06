from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import Transcript
from src.services.extraction import extract_measures

router = APIRouter()


class TranscriptIn(BaseModel):
    company: str
    period: str
    section: str = "Unnamed Section"
    body: str
    source: str = "manual"


class TranscriptOut(BaseModel):
    id: int
    company: str
    period: str
    section: str
    body: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=TranscriptOut, status_code=201)
def save_transcript(payload: TranscriptIn, db: Session = Depends(get_db)):
    if not payload.body.strip():
        raise HTTPException(status_code=422, detail="Transcript body cannot be empty.")
    record = Transcript(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[TranscriptOut])
def list_transcripts(
    company: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Transcript)
    if company:
        q = q.filter(Transcript.company == company)
    return q.order_by(Transcript.created_at.desc()).all()


@router.get("/{transcript_id}", response_model=TranscriptOut)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    record = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    return record


@router.delete("/{transcript_id}", status_code=204)
def delete_transcript(transcript_id: int, db: Session = Depends(get_db)):
    record = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    db.delete(record)
    db.commit()


class ExtractionSuggestionOut(BaseModel):
    name: str
    measure_type: str
    category: str
    contexts: List[str]
    company: str
    period: str
    source_file: str
    operating_reclassified: bool


class TranscriptExtractionOut(BaseModel):
    transcript_id: int
    has_safe_harbor: bool
    has_fwd_looking: bool
    suggestions: List[ExtractionSuggestionOut]


@router.post("/{transcript_id}/extract", response_model=TranscriptExtractionOut)
def extract_transcript(transcript_id: int, db: Session = Depends(get_db)):
    record = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    result = extract_measures(
        text=record.body,
        company=record.company,
        period=record.period,
        source_file=f"transcript:{record.id}",
    )
    return TranscriptExtractionOut(
        transcript_id=record.id,
        has_safe_harbor=result.has_safe_harbor,
        has_fwd_looking=result.has_fwd_looking,
        suggestions=[
            ExtractionSuggestionOut(
                name=item.name,
                measure_type=item.measure_type,
                category=item.category,
                contexts=item.contexts,
                company=item.company,
                period=item.period,
                source_file=item.source_file,
                operating_reclassified=item.operating_reclassified,
            )
            for item in result.items
        ],
    )
