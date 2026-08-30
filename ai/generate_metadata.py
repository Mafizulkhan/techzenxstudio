"""
Metadata Generator — Claude-powered YouTube Title/Description/Tags

Takes a generated script and produces SEO-optimized metadata for YouTube.

Usage:
    python -m ai.generate_metadata
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, save_json, load_prompt, clean_json_text

logger = setup_logger("ai.generate_metadata")


def generate_metadata(script: dict) -> dict | None:
    """
    Generate YouTube metadata (title, description, tags) for a script.

    Sends the script to Claude with the metadata generation system prompt.
    Expects a structured JSON response with:
    - title: SEO-optimized title (max 70 characters)
    - description: Full description with timestamps placeholder, links, hashtags
    - tags: List of 15-20 relevant tags
    - category: YouTube category suggestion

    Args:
        script: Generated script dict from generate_script().

    Returns:
        Metadata dict, or None if generation failed.
    """
    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set — cannot generate metadata")
        return None

    script_title = script.get("title", "Untitled Script")
    logger.info("Generating metadata for script: %s", script_title)

    try:
        system_prompt = load_prompt(config.METADATA_PROMPT_PATH)
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 4096),
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(script, indent=2)}],
        )

        response_text = message.content[0].text
        cleaned_json = clean_json_text(response_text)
        metadata = json.loads(cleaned_json)

        metadata["generated_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Successfully generated metadata (title: '%s', tags: %d)",
                    metadata.get("title", ""), len(metadata.get("tags", [])))
        return metadata

    except json.JSONDecodeError as err:
        logger.error("Failed to parse JSON metadata response from Claude: %s", err)
        return None
    except Exception as err:
        logger.exception("Error calling Anthropic API for metadata generation: %s", err)
        return None


def _save_result(metadata: dict | None) -> None:
    """Save generated metadata to output/scripts/metadata_<timestamp>.json."""
    if not metadata:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.SCRIPTS_DIR / f"metadata_{timestamp}.json"
    save_json(metadata, filepath)
    logger.info("Saved metadata to %s", filepath)


if __name__ == "__main__":
    dummy_script = {"title": "Test Script", "sections": []}
    result = generate_metadata(dummy_script)
    _save_result(result)
