"""
YouTube Data API v3 — Trending Tech Videos Fetcher

Pulls trending/most-popular videos in the Science & Technology category
using the YouTube Data API v3 (videos.list with chart=mostPopular).

Usage:
    python -m fetchers.youtube
"""

from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config
from utils import setup_logger, save_json

logger = setup_logger("fetchers.youtube")


def fetch_youtube_trends(
    max_results: int = 25,
    region_code: str | None = None,
) -> list[dict]:
    """
    Fetch trending technology videos from YouTube.

    Calls the YouTube Data API v3 `videos.list` endpoint with:
    - chart=mostPopular
    - videoCategoryId=28 (Science & Technology)
    - regionCode=US (configurable)

    Args:
        max_results: Maximum number of trending videos to return (1-50).
        region_code: ISO 3166-1 alpha-2 country code (defaults to config.YOUTUBE_REGION_CODE).

    Returns:
        List of dicts, each containing:
        - source: "youtube"
        - id: Video ID
        - title: Video title
        - description: Video description snippet
        - url: Watch URL
        - channel: Channel name
        - channel_id: Channel ID
        - published_at: ISO timestamp
        - view_count: Number of views
        - like_count: Number of likes
        - comment_count: Number of comments
        - tags: List of video tags
        - fetched_at: When this data was fetched
    """
    if not config.YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not set — skipping YouTube fetch")
        return []

    target_region = region_code or getattr(config, "YOUTUBE_REGION_CODE", "US")
    category_id = getattr(config, "YOUTUBE_CATEGORY_ID", "28")
    fetched_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Fetching YouTube trending tech videos (region=%s, category=%s, max=%d)...",
        target_region,
        category_id,
        max_results,
    )

    try:
        youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            videoCategoryId=category_id,
            regionCode=target_region,
            maxResults=min(max_results, 50),
        )
        response = request.execute()
    except HttpError as err:
        logger.error("YouTube API HTTP error (%d): %s", err.resp.status, err)
        return []
    except Exception as err:
        logger.exception("Unexpected error fetching YouTube trends: %s", err)
        return []

    items = response.get("items", [])
    trends = []

    for item in items:
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        video_id = item.get("id", "")

        trends.append(
            {
                "source": "youtube",
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "tags": snippet.get("tags", []),
                "fetched_at": fetched_at,
            }
        )

    logger.info("Successfully fetched %d trending videos from YouTube", len(trends))
    if trends:
        _save_results(trends)
    return trends


def _save_results(trends: list[dict]) -> None:
    """Save fetched trends to output/trends/youtube_<timestamp>.json."""
    if not trends:
        logger.info("No YouTube trends to save")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.TRENDS_DIR / f"youtube_{timestamp}.json"
    save_json(trends, filepath)
    logger.info("Saved %d YouTube trends to %s", len(trends), filepath)


if __name__ == "__main__":
    results = fetch_youtube_trends()
    _save_results(results)
    print(f"Fetched {len(results)} YouTube trends")
