from __future__ import annotations

from pydantic import BaseModel, ConfigDict

# Request models
#
# Required-looking fields default to "" so that a missing value still reaches the
# route's own emptiness check (HTTP 400) instead of failing validation (HTTP 422).
# coerce_numbers_to_str keeps the old str(payload.get(...)) behavior for numbers.


class NoteCreate(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    content: str = ""


class ExtractRequest(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    text: str = ""
    save_note: bool = False


class MarkDoneRequest(BaseModel):
    done: bool = True


# Response models


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str


class ExtractedItem(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: int | None
    items: list[ExtractedItem]


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
