from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: NoteCreate) -> NoteResponse:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    if note is None:
        # The insert succeeded but the row could not be read back.
        raise HTTPException(status_code=500, detail="database error")
    return NoteResponse(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("")
def list_all_notes() -> list[NoteResponse]:
    """Return all saved notes, newest first."""
    rows = db.list_notes()
    return [
        NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])
        for row in rows
    ]


@router.get("/{note_id}")
def get_single_note(note_id: int) -> NoteResponse:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])
