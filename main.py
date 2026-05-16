import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from dashboard_routes import router as admin_router
from database import Event, EventCreate, engine, event_exists, get_session, init_db

load_dotenv()

app = FastAPI(title="Sunset City Event Calendar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

_static_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/admin-static", StaticFiles(directory=_static_dir), name="admin-static")

WORK_WITH_US_URL = os.getenv(
    "WORK_WITH_US_URL",
    "https://sunset-city.com/work-with-us/",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/events")
def list_public_events(
    status: str = "approved",
    db: Session = Depends(get_session),
):
    """Approved events for the public calendar widget."""
    statement = (
        select(Event)
        .where(Event.approval_status == status)
        .order_by(Event.start_time.asc())
    )
    return db.exec(statement).all()


@app.post("/api/events/submit")
def submit_event(payload: EventCreate, db: Session = Depends(get_session)):
    """
    Public endpoint for zine / event submissions.
    Stored as user_submitted + pending until an admin approves.
    """
    if event_exists(db, payload.summary, payload.start_time, payload.source_url):
        raise HTTPException(status_code=409, detail="This event was already submitted.")

    event = Event(
        **payload.model_dump(),
        submission_type="user_submitted",
        approval_status="pending",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "status": "pending",
        "message": "Thanks! Your event is queued for review.",
        "event_id": event.id,
        "work_with_us_url": WORK_WITH_US_URL,
        "work_with_us_note": (
            "Want help promoting your event? See our digital media and zine services."
        ),
    }


@app.get("/api/config")
def public_config():
    return {"work_with_us_url": WORK_WITH_US_URL}


@app.get("/admin")
def admin_page():
    path = os.path.join(_static_dir, "admin_dashboard.html")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Admin dashboard not found")
    return FileResponse(path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
@app.get("/calendar")
def calendar_page():
    path = os.path.join(_static_dir, "arizona_events_calendar_widget.html")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Calendar not found")
    return FileResponse(path)
