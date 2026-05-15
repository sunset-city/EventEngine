"""Backward-compatible re-exports — use instagram_scraper.py and scraper_service.py."""
from instagram_scraper import InstagramEventFetcher
from scraper_service import EventLLMParser

__all__ = ["InstagramEventFetcher", "EventLLMParser"]
