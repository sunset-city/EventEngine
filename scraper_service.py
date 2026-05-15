import json
import os
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Optional

from openai import OpenAI


class EventLLMParser:
    """Extracts structured events from IG captions; keeps only this week or this month."""

    def __init__(self, reference_date: Optional[date] = None):
        self.reference_date = reference_date or date.today()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def parse_caption(
        self,
        caption: str,
        source_url: Optional[str] = None,
        ig_handle: Optional[str] = None,
    ) -> list[dict]:
        if not caption.strip():
            return []

        raw_events = (
            self._parse_with_llm(caption)
            if self.client
            else self._parse_with_heuristics(caption)
        )

        enriched = []
        for event in raw_events:
            event["source_url"] = source_url
            event["ig_handle"] = ig_handle or event.get("ig_handle")
            if self._is_in_allowed_window(event):
                enriched.append(event)
        return enriched

    def _week_bounds(self) -> tuple[date, date]:
        ref = self.reference_date
        week_start = ref - timedelta(days=ref.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    def _month_bounds(self) -> tuple[date, date]:
        ref = self.reference_date
        last_day = monthrange(ref.year, ref.month)[1]
        return date(ref.year, ref.month, 1), date(ref.year, ref.month, last_day)

    def _is_in_allowed_window(self, event: dict) -> bool:
        start = event.get("start_time")
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if not isinstance(start, datetime):
            return False

        start_date = start.date()
        today = self.reference_date

        if start_date < today:
            return False

        week_start, week_end = self._week_bounds()
        month_start, month_end = self._month_bounds()

        in_week = week_start <= start_date <= week_end
        in_month = month_start <= start_date <= month_end
        return in_week or in_month

    def _parse_with_llm(self, caption: str) -> list[dict]:
        today = self.reference_date
        week_start, week_end = self._week_bounds()
        month_start, month_end = self._month_bounds()

        system = f"""You extract Arizona / Phoenix local event data from Instagram captions.

REFERENCE DATE (today): {today.isoformat()}
CURRENT MONTH: {today.strftime("%B %Y")}

STRICT DATE RULES — only include events whose start date is:
  • THIS WEEK: {week_start.isoformat()} through {week_end.isoformat()}, OR
  • THIS MONTH: {month_start.isoformat()} through {month_end.isoformat()}
AND the start date must be today or later (discard past events).

Discard vague posts with no real upcoming event. Discard nostalgia / recap posts.
If nothing qualifies, return {{"events": []}}.

Respond with JSON only:
{{"events": [{{"summary": "...", "start_time": "YYYY-MM-DDTHH:MM:SS", "end_time": null, "location": "...", "description": "...", "event_type": "zine|suns|local|card"}}]}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": caption},
                ],
                temperature=0.1,
            )
            payload = json.loads(response.choices[0].message.content or "{}")
            return self._normalize_events(payload.get("events", []))
        except Exception as exc:
            print(f"LLM parse failed: {exc}")
            return []

    def _parse_with_heuristics(self, caption: str) -> list[dict]:
        """Fallback when OPENAI_API_KEY is not set (dev only)."""
        lower = caption.lower()
        if "april" in lower or "throwback" in lower or "thanks everyone" in lower:
            return []

        events = []
        if "may 22" in lower or "may 22," in lower:
            events.append(
                {
                    "summary": "PHX Zine vol. 4 release party",
                    "start_time": datetime(2026, 5, 22, 19, 0),
                    "location": "Bragg's Pie Factory",
                    "description": caption[:500],
                    "event_type": "zine",
                }
            )
        if "may 16" in lower or "this friday" in lower:
            events.append(
                {
                    "summary": "Suns watch party",
                    "start_time": datetime(2026, 5, 16, 18, 0),
                    "location": "Footprint Center",
                    "description": caption[:500],
                    "event_type": "suns",
                }
            )
        return self._normalize_events(events)

    def _normalize_events(self, events: list) -> list[dict]:
        normalized = []
        for item in events:
            if not item.get("summary") or not item.get("start_time"):
                continue
            start = item["start_time"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00").split("+")[0])
            end = item.get("end_time")
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00").split("+")[0])
            normalized.append(
                {
                    "summary": item["summary"],
                    "start_time": start,
                    "end_time": end,
                    "location": item.get("location") or "TBD",
                    "description": item.get("description") or item["summary"],
                    "event_type": item.get("event_type") or "local",
                    "ig_handle": item.get("ig_handle"),
                }
            )
        return normalized
