from datetime import datetime
from typing import Optional
# Assuming SQLModel or SQLAlchemy, but Cursor can adapt this to Prisma/Node if needed
from sqlmodel import Field, SQLModel, create_engine

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    summary: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: str
    description: str
    source_url: Optional[str] = None
    submission_type: str # "instagram_scrap" or "user_submitted"
    approval_status: str = Field(default="pending") # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)