"""
Fetchers package — trend data collection from YouTube, Reddit, and RSS feeds.
"""

from fetchers.youtube import fetch_youtube_trends
from fetchers.reddit import fetch_reddit_trends
from fetchers.rss import fetch_rss_trends
from fetchers.score import score_and_rank_trends

__all__ = [
    "fetch_youtube_trends",
    "fetch_reddit_trends",
    "fetch_rss_trends",
    "score_and_rank_trends",
]
