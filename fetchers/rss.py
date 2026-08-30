"""
RSS Feed Parser — Tech/AI News Fetcher

Parses RSS feeds from TechCrunch, The Verge, and Google News (AI tools)
to discover trending topics.

Usage:
    python -m fetchers.rss
"""

import time
import re
from datetime import datetime, timezone
import feedparser

import config
from utils import setup_logger, save_json

logger = setup_logger("fetchers.rss")


def _clean_html(raw_html: str) -> str:
    """Strip HTML tags from string to leave clean text."""
    if not raw_html:
        return ""
    clean_text = re.sub(r"<[^>]+>", "", raw_html)
    return " ".join(clean_text.split())


def fetch_rss_trends(limit_per_feed: int = 15) -> list[dict]:
    """
    Fetch recent articles from configured RSS feeds.

    Uses feedparser to pull and parse entries from each feed in
    config.RSS_FEEDS, extracting title, link, summary, and publish date.

    Args:
        limit_per_feed: Max items to fetch per feed URL.

    Returns:
        List of dicts, each containing:
        - source: "rss"
        - id: Link or entry ID
        - feed_url: Origin feed URL
        - title: Article title
        - url: Article URL
        - summary: Short text excerpt
        - author: Author name (if available)
        - published_at: ISO timestamp
        - fetched_at: When this data was fetched
    """
    feeds = getattr(config, "RSS_FEEDS", [])
    fetched_at = datetime.now(timezone.utc).isoformat()
    logger.info("Fetching RSS trends from %d feeds...", len(feeds))

    trends = []

    for feed_url in feeds:
        try:
            logger.debug("Parsing RSS feed: %s", feed_url)
            parsed = feedparser.parse(feed_url)

            if parsed.bozo and not parsed.entries:
                logger.warning("Failed to parse RSS feed %s: %s", feed_url, getattr(parsed, "bozo_exception", "unknown error"))
                continue

            for entry in parsed.entries[:limit_per_feed]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                link = entry.get("link", "")
                entry_id = entry.get("id", link)

                # Parse publication time
                published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                if published_parsed:
                    published_iso = datetime.fromtimestamp(time.mktime(published_parsed), timezone.utc).isoformat()
                else:
                    published_iso = fetched_at

                raw_summary = entry.get("summary") or entry.get("description") or ""
                clean_summary = _clean_html(raw_summary)[:500]

                trends.append(
                    {
                        "source": "rss",
                        "id": entry_id,
                        "feed_url": feed_url,
                        "title": title,
                        "description": clean_summary,
                        "url": link,
                        "author": entry.get("author", ""),
                        "published_at": published_iso,
                        "fetched_at": fetched_at,
                    }
                )

        except Exception as err:
            logger.exception("Error parsing RSS feed %s: %s", feed_url, err)

    logger.info("Successfully fetched %d total RSS articles", len(trends))
    if trends:
        _save_results(trends)
    return trends


def _save_results(trends: list[dict]) -> None:
    """Save fetched trends to output/trends/rss_<timestamp>.json."""
    if not trends:
        logger.info("No RSS trends to save")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.TRENDS_DIR / f"rss_{timestamp}.json"
    save_json(trends, filepath)
    logger.info("Saved %d RSS trends to %s", len(trends), filepath)


if __name__ == "__main__":
    results = fetch_rss_trends()
    _save_results(results)
    print(f"Fetched {len(results)} RSS trends")
