"""
Script Generator — Claude-powered YouTube Script Writing

Takes a trend candidate and generates a structured YouTube script
using the Claude API with the script_generation.md prompt template.

Usage:
    python -m ai.generate_script
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, save_json, load_prompt, clean_json_text

logger = setup_logger("ai.generate_script")


def generate_script(trend_candidate: dict) -> dict | None:
    """
    Generate a YouTube script for the given trend candidate.

    Sends the trend data to Claude with the script generation system prompt.
    Expects a structured JSON response with:
    - title: Working title
    - hook: Attention-grabbing opening (first 10 seconds)
    - sections: List of {heading, content, duration_seconds}
    - cta: Call-to-action closing
    - estimated_duration: Total video length estimate
    - tone: Conversational Hinglish-friendly

    Args:
        trend_candidate: Dict with trend data (title, source, url, etc.)

    Returns:
        Generated script as a dict, or None if generation failed.
    """
    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set — cannot generate script")
        return None

    topic_title = trend_candidate.get("title", "Unknown Tech Topic")
    logger.info("Generating script for candidate: %s", topic_title)

    try:
        system_prompt = load_prompt(config.SCRIPT_PROMPT_PATH)
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        user_content = json.dumps(trend_candidate, indent=2)
        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 4096),
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )

        response_text = message.content[0].text
        cleaned_json = clean_json_text(response_text)
        script_data = json.loads(cleaned_json)

        # Attach metadata about generation
        script_data["generated_at"] = datetime.now(timezone.utc).isoformat()
        script_data["source_candidate"] = {
            "title": topic_title,
            "url": trend_candidate.get("url", ""),
            "source": trend_candidate.get("source", ""),
        }

        logger.info("Successfully generated script for '%s' (%d sections)",
                    topic_title, len(script_data.get("sections", [])))
        return script_data

    except json.JSONDecodeError as err:
        logger.error("Failed to parse JSON script response from Claude: %s", err)
        return None
    except Exception as err:
        logger.exception("Error calling Anthropic API for script generation: %s", err)
        return None


def _save_result(script: dict | None) -> None:
    """Save generated script to output/scripts/script_<timestamp>.json."""
    if not script:
        logger.info("No script to save")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.SCRIPTS_DIR / f"script_{timestamp}.json"
    save_json(script, filepath)
    logger.info("Saved script to %s", filepath)


if __name__ == "__main__":
    # Test with a dummy candidate
    dummy = {"title": "Test Trend", "source": "manual", "url": ""}
    result = generate_script(dummy)
    _save_result(result)
