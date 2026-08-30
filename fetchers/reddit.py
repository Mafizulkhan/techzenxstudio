"""
Reddit API — Top Tech Posts Fetcher

Pulls top posts from technology-related subreddits (r/technology,
r/Futurology, r/artificial) from the last 24 hours using PRAW.

Usage:
    python -m fetchers.reddit
"""

from datetime import datetime, timezone
import praw
from prawcore import PrawcoreException

import config
from utils import setup_logger, save_json

logger = setup_logger("fetchers.reddit")


def fetch_reddit_trends(
    time_filter: str = "day",
    limit_per_sub: int = 10,
) -> list[dict]:
    """
    Fetch top posts from configured tech subreddits.

    Uses PRAW (Python Reddit API Wrapper) to pull top posts from
    each subreddit in config.TARGET_SUBREDDITS, filtered by time.

    Args:
        time_filter: Reddit time filter — "hour", "day", "week", "month", "year", "all".
        limit_per_sub: Number of top posts to pull per subreddit.

    Returns:
        List of dicts, each containing:
        - source: "reddit"
        - id: Post ID
        - subreddit: Subreddit display name
        - title: Post title
        - description: Selftext snippet or external link
        - url: Full Reddit permalink
        - external_url: Direct link attached to post
        - score: Upvote score
        - upvote_ratio: Upvote ratio
        - comment_count: Comment count
        - published_at: ISO timestamp
        - fetched_at: When this data was fetched
    """
    if not config.REDDIT_CLIENT_ID or not config.REDDIT_CLIENT_SECRET:
        logger.error("Reddit API credentials not set — skipping Reddit fetch")
        return []

    subreddits = getattr(config, "TARGET_SUBREDDITS", ["technology", "Futurology", "artificial"])
    user_agent = getattr(config, "REDDIT_USER_AGENT", "youtube-ai-automation/1.0")
    fetched_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Fetching Reddit top posts from %s (time_filter=%s, limit=%d)...",
        subreddits,
        time_filter,
        limit_per_sub,
    )

    try:
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=user_agent,
        )
    except Exception as err:
        logger.exception("Failed to initialize Reddit client: %s", err)
        return []

    trends = []

    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.top(time_filter=time_filter, limit=limit_per_sub):
                published_iso = datetime.fromtimestamp(post.created_utc, timezone.utc).isoformat()
                selftext = (post.selftext or "").strip()
                description = selftext[:500] if selftext else post.url

                trends.append(
                    {
                        "source": "reddit",
                        "id": post.id,
                        "subreddit": sub_name,
                        "title": post.title,
                        "description": description,
                        "url": f"https://www.reddit.com{post.permalink}",
                        "external_url": post.url,
                        "score": int(post.score),
                        "upvote_ratio": float(getattr(post, "upvote_ratio", 1.0)),
                        "comment_count": int(post.num_comments),
                        "published_at": published_iso,
                        "fetched_at": fetched_at,
                    }
                )
        except PrawcoreException as err:
            logger.error("PRAW API error fetching r/%s: %s", sub_name, err)
        except Exception as err:
            logger.exception("Error fetching r/%s: %s", sub_name, err)

    logger.info("Successfully fetched %d total Reddit posts", len(trends))
    if trends:
        _save_results(trends)
    return trends


def _save_results(trends: list[dict]) -> None:
    """Save fetched trends to output/trends/reddit_<timestamp>.json."""
    if not trends:
        logger.info("No Reddit trends to save")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.TRENDS_DIR / f"reddit_{timestamp}.json"
    save_json(trends, filepath)
    logger.info("Saved %d Reddit trends to %s", len(trends), filepath)


if __name__ == "__main__":
    results = fetch_reddit_trends()
    _save_results(results)
    print(f"Fetched {len(results)} Reddit trends")
