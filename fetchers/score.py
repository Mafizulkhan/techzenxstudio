"""
Trend Scorer — Merge, Deduplicate, and Rank Trend Candidates

Reads all trend JSON files from output/trends/, merges them into a single
list, removes near-duplicates, scores by recency + keyword relevance,
and outputs the top 5 candidates.

Usage:
    python -m fetchers.score
"""

import re
from datetime import datetime, timezone
from pathlib import Path

import config
from utils import setup_logger, save_json, load_json

logger = setup_logger("fetchers.score")


def _normalize_title(title: str) -> set[str]:
    """Extract normalized word tokens for title comparison."""
    words = re.findall(r"\w+", title.lower())
    # Exclude common stop words
    stop_words = {"a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of", "is", "it", "this", "that"}
    return {w for w in words if w not in stop_words and len(w) > 2}


def _is_similar(title1: str, title2: str, threshold: float = 0.65) -> bool:
    """Check Jaccard token similarity between two titles."""
    tokens1 = _normalize_title(title1)
    tokens2 = _normalize_title(title2)
    if not tokens1 or not tokens2:
        return False
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    similarity = len(intersection) / len(union)
    return similarity >= threshold


def score_and_rank_trends(top_n: int = 5) -> list[dict]:
    """
    Merge all fetched trends, deduplicate, score, and return top candidates.

    Scoring formula:
    - Recency score: Linear decay from 1.0 (just published) to 0.0 (48h old)
    - Keyword score: Points for keywords matched in title (x1.5) and description (x1.0)
    - Engagement score: Additional points based on view counts or Reddit upvotes
    - Total score = (recency * 3.0) + keyword_score + engagement_score

    Deduplication uses Jaccard token similarity on normalized title words.

    Args:
        top_n: Number of top candidates to return.

    Returns:
        List of top_n dicts with score details added.
    """
    logger.info("Scoring and ranking trends from %s...", config.TRENDS_DIR)

    # 1. Load all JSON files from output/trends/
    json_files = list(config.TRENDS_DIR.glob("*.json"))
    if not json_files:
        logger.warning("No trend files found in %s", config.TRENDS_DIR)
        return []

    all_trends = []
    for filepath in json_files:
        try:
            data = load_json(filepath)
            if isinstance(data, list):
                all_trends.extend(data)
        except Exception as err:
            logger.error("Failed to load trend file %s: %s", filepath, err)

    logger.info("Loaded %d raw trends across %d JSON files", len(all_trends), len(json_files))
    if not all_trends:
        return []

    # 2. Deduplicate near-duplicate titles
    deduped_trends = []
    for item in all_trends:
        title = item.get("title", "")
        if not title:
            continue
        duplicate = False
        for existing in deduped_trends:
            if _is_similar(title, existing.get("title", "")):
                duplicate = True
                break
        if not duplicate:
            deduped_trends.append(item)

    logger.info("Deduplicated from %d to %d unique trends", len(all_trends), len(deduped_trends))

    now_utc = datetime.now(timezone.utc)
    keywords = [k.lower() for k in getattr(config, "SCORING_KEYWORDS", [])]

    scored_items = []

    # 3. Compute score for each trend
    for item in deduped_trends:
        title = item.get("title", "")
        description = item.get("description", "")
        published_str = item.get("published_at", "")

        # Recency calculation (0.0 to 1.0 over 48 hours)
        recency_score = 0.5
        if published_str:
            try:
                pub_time = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                hours_old = max(0.0, (now_utc - pub_time).total_seconds() / 3600.0)
                recency_score = max(0.0, 1.0 - (hours_old / 48.0))
            except Exception:
                recency_score = 0.5

        # Keyword matching
        matched_kw = set()
        title_lower = title.lower()
        desc_lower = description.lower()
        keyword_score = 0.0

        for kw in keywords:
            if kw in title_lower:
                matched_kw.add(kw)
                keyword_score += 1.5
            elif kw in desc_lower:
                matched_kw.add(kw)
                keyword_score += 0.8

        # Engagement score (views/upvotes)
        engagement_score = 0.0
        if item.get("source") == "youtube":
            views = item.get("view_count", 0)
            engagement_score = min(3.0, views / 100000.0)
        elif item.get("source") == "reddit":
            score_val = item.get("score", 0)
            engagement_score = min(3.0, score_val / 1000.0)

        total_score = round((recency_score * 3.0) + keyword_score + engagement_score, 2)

        scored_item = dict(item)
        scored_item["score"] = total_score
        scored_item["matched_keywords"] = sorted(list(matched_kw))
        scored_item["score_components"] = {
            "recency": round(recency_score, 2),
            "keyword": round(keyword_score, 2),
            "engagement": round(engagement_score, 2),
        }
        scored_items.append(scored_item)

    # 4. Sort by score descending
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    top_candidates = scored_items[:top_n]

    logger.info("Scored %d items — top candidate: '%s' (score: %.2f)",
                len(scored_items),
                top_candidates[0]["title"] if top_candidates else "N/A",
                top_candidates[0]["score"] if top_candidates else 0.0)

    return top_candidates


def _save_results(candidates: list[dict]) -> None:
    """Save top candidates to output/top-candidates.json."""
    if not candidates:
        logger.info("No candidates to save")
        return

    filepath = config.OUTPUT_DIR / "top-candidates.json"
    save_json(candidates, filepath)
    logger.info("Saved %d top candidates to %s", len(candidates), filepath)


if __name__ == "__main__":
    results = score_and_rank_trends()
    _save_results(results)
    print(f"Scored and ranked — {len(results)} top candidates")
