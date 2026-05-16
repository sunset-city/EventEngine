import os
from datetime import datetime
from typing import Optional, Generator

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///events.db")
engine = create_engine(DATABASE_URL, echo=False)


# ── Models ────────────────────────────────────────────────────

class Event(SQLModel, table=True):
    id:                  Optional[int]      = Field(default=None, primary_key=True)
    summary:             str
    start_time:          datetime
    end_time:            Optional[datetime] = None
    location:            str
    description:         str
    event_type:          str                = Field(default="local")
    source_url:          Optional[str]      = None
    ig_handle:           Optional[str]      = None
    submission_type:     str
    approval_status:     str                = Field(default="pending")
    submitter_name:      Optional[str]      = None
    submitter_email:     Optional[str]      = None
    marketing_budget:    Optional[str]      = None
    digital_media_notes: Optional[str]      = None
    created_at:          datetime           = Field(default_factory=datetime.utcnow)


class EventCreate(SQLModel):
    summary:             str
    start_time:          datetime
    end_time:            Optional[datetime] = None
    location:            str
    description:         str
    event_type:          str                = "local"
    source_url:          Optional[str]      = None
    submitter_name:      Optional[str]      = None
    submitter_email:     Optional[str]      = None
    marketing_budget:    Optional[str]      = None
    digital_media_notes: Optional[str]      = None


# ── DB helpers ────────────────────────────────────────────────

def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def event_exists(
    session: Session,
    summary: str,
    start_time: datetime,
    source_url: Optional[str] = None,
) -> bool:
    if source_url:
        url_match = session.exec(
            select(Event).where(Event.source_url == source_url)
        ).first()
        if url_match:
            return True

    text_match = session.exec(
        select(Event).where(
            Event.summary == summary,
            Event.start_time == start_time,
        )
    ).first()

    return text_match is not None
