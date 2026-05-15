from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import Event, get_session

router = APIRouter(prefix="/api/admin/events", tags=["admin"])


@router.get("/pending")
def get_pending_events(db: Session = Depends(get_session)):
    """Events awaiting review (Instagram scrapes and user submissions)."""
    statement = (
        select(Event)
        .where(Event.approval_status == "pending")
        .order_by(Event.created_at.desc())
    )
    return db.exec(statement).all()


@router.post("/{event_id}/approve")
def approve_event(event_id: int, db: Session = Depends(get_session)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.approval_status = "approved"
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"status": "success", "message": f"Event {event_id} approved.", "event": event}


@router.post("/{event_id}/reject")
def reject_event(event_id: int, db: Session = Depends(get_session)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.approval_status = "rejected"
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"status": "success", "message": f"Event {event_id} rejected.", "event": event}
