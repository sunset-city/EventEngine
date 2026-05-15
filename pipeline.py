"""
Background job: scrape IG → LLM parse → save pending events.

Run on a schedule, e.g.:
  python pipeline.py
  # cron: 0 */6 * * * cd /path/to/Event\ Calendar && python pipeline.py
"""

import os
from datetime import date

from dotenv import load_dotenv
from sqlmodel import Session

from database import Event, engine, event_exists, init_db
from instagram_scraper import InstagramEventFetcher
from scraper_service import EventLLMParser

load_dotenv()


def save_parsed_event(session: Session, data: dict) -> bool:
    if event_exists(session, data["summary"], data["start_time"], data.get("source_url")):
        return False

    event = Event(
        summary=data["summary"],
        start_time=data["start_time"],
        end_time=data.get("end_time"),
        location=data["location"],
        description=data["description"],
        event_type=data.get("event_type", "local"),
        source_url=data.get("source_url"),
        ig_handle=data.get("ig_handle"),
        submission_type="instagram_scrap",
        approval_status="pending",
    )
    session.add(event)
    return True


def run_pipeline(reference_date: date | None = None) -> dict:
    init_db()
    ref = reference_date or date.today()
    fetcher = InstagramEventFetcher()
    parser = EventLLMParser(reference_date=ref)

    posts = fetcher.fetch_recent_posts()
    saved = 0
    skipped = 0

    with Session(engine) as session:
        for post in posts:
            events = parser.parse_caption(
                post.get("caption", ""),
                source_url=post.get("url"),
                ig_handle=post.get("ig_handle"),
            )
            for data in events:
                if save_parsed_event(session, data):
                    saved += 1
                else:
                    skipped += 1
        session.commit()

    summary = {
        "reference_date": ref.isoformat(),
        "posts_scraped": len(posts),
        "events_saved": saved,
        "duplicates_skipped": skipped,
    }
    print(summary)
    return summary


if __name__ == "__main__":
    ref_str = os.getenv("PIPELINE_REFERENCE_DATE")
    ref = date.fromisoformat(ref_str) if ref_str else None
    run_pipeline(reference_date=ref)
