from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str
    pinned: bool = False


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    pinned: bool | None = None


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    pinned: bool

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True
