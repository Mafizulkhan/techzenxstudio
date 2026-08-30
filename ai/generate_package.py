"""
Master Package Generator — TechZenX YouTube Content Package

Generates a complete ready-to-produce text package (overview, scene-by-scene script with
camera angle, SFX, Google Flow video prompt, Hinglish voiceover, titles/metadata, thumbnail prompt)
for a candidate topic using Claude.

Usage:
    python -m ai.generate_package
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, load_prompt

logger = setup_logger("ai.generate_package")


def generate_package(candidate: dict) -> str | None:
    """
    Generate a full ready-to-produce Markdown content package for a candidate topic.

    Args:
        candidate: Dict with topic data (title, description, url, source, etc.)

    Returns:
        Full Markdown package as a string, or None if generation failed.
    """
    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set in .env — cannot generate package")
        return None

    topic_title = candidate.get("title", "Unknown Tech Topic")
    logger.info("Generating master package for: %s", topic_title)

    try:
        system_prompt = load_prompt(config.PROMPTS_DIR / "master_package_generation.md")
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        user_message = f"Trending Topic Details:\n{json.dumps(candidate, indent=2)}"

        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 4096),
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        package_markdown = message.content[0].text.strip()
        logger.info("Successfully generated master package for '%s' (%d chars)",
                    topic_title, len(package_markdown))
        return package_markdown

    except Exception as err:
        logger.exception("Error calling Anthropic API for master package generation: %s", err)
        return None


if __name__ == "__main__":
    dummy_candidate = {
        "title": "Autonomous AI Swarms Build Solar Farm in 48 Hours",
        "description": "Engineers deployed 500 autonomous AI robots that assembled a full solar array without human intervention.",
        "url": "https://techcrunch.com/example",
        "source": "rss",
    }
    result = generate_package(dummy_candidate)
    if result:
        print("Generated Package Preview:\n", result[:500])
