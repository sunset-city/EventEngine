import os

import requests


class InstagramEventFetcher:
    """Pulls recent IG post captions via Apify (or mock data when no token)."""

    def __init__(self):
        self.apify_token = os.getenv("APIFY_TOKEN")
        raw = os.getenv("IG_TARGET_PROFILES", "local_music_curator,phx_hiphop,sunset1k.city")
        self.target_profiles = [p.strip() for p in raw.split(",") if p.strip()]

    def fetch_recent_posts(self) -> list[dict]:
        if not self.apify_token:
            print("APIFY_TOKEN missing — using mock captions for development.")
            return self._mock_posts()

        url = (
            "https://api.apify.com/v2/acts/apify~instagram-post-scraper/"
            "run-sync-get-dataset-items"
            f"?token={self.apify_token}"
        )
        payload = {
            "username": self.target_profiles,
            "resultsLimit": 10,
            "onlyPostsNewerThan": "7 days",
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            posts = response.json()
            return [
                {
                    "caption": p.get("caption") or "",
                    "url": p.get("url") or p.get("inputUrl"),
                    "ig_handle": p.get("ownerUsername"),
                }
                for p in posts
                if p.get("caption")
            ]
        except Exception as exc:
            print(f"Instagram scrape failed: {exc}")
            return []

    def _mock_posts(self) -> list[dict]:
        return [
            {
                "caption": (
                    "PHX Zine vol. 4 release party — May 22, 2026 at Bragg's Pie Factory, "
                    "7pm. Free entry. @phxzine"
                ),
                "url": "https://www.instagram.com/p/mock1/",
                "ig_handle": "phxzine",
            },
            {
                "caption": (
                    "Suns watch party this Friday May 16 at Footprint Center. "
                    "Doors 6pm. #phoenix"
                ),
                "url": "https://www.instagram.com/p/mock2/",
                "ig_handle": "suns",
            },
            {
                "caption": "Throwback to our April show — thanks everyone!",  # should be filtered out
                "url": "https://www.instagram.com/p/mock3/",
                "ig_handle": "phx_hiphop",
            },
        ]
