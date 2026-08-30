"""
Thumbnail Prompt Generator — Claude-powered Image Generation Prompts

Takes a script and metadata, then generates an image-gen prompt suitable
for creating a YouTube thumbnail using DALL-E, Midjourney, or Ideogram.

Usage:
    python -m ai.generate_thumbnail_prompt
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, save_json, load_prompt, clean_json_text

logger = setup_logger("ai.generate_thumbnail_prompt")


def generate_thumbnail_prompt(script: dict, metadata: dict | None = None) -> dict | None:
    """
    Generate an image-generation prompt for a YouTube thumbnail.

    Sends the script (and optionally metadata) to Claude with the
    thumbnail prompt template. Expects output with:
    - primary_prompt: The image-gen prompt (for DALL-E / Midjourney / Ideogram)
    - style_notes: Suggested style, colors, composition
    - text_overlay: Suggested text overlay
    - alt_prompts: 2-3 alternative prompt variations

    Args:
        script: Generated script dict.
        metadata: Optional metadata dict for context (title, tags).

    Returns:
        Thumbnail prompt dict, or None if generation failed.
    """
    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set — cannot generate thumbnail prompt")
        return None

    script_title = script.get("title", "Untitled Video")
    logger.info("Generating thumbnail prompt for: %s", script_title)

    try:
        system_prompt = load_prompt(config.THUMBNAIL_PROMPT_PATH)
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        payload = {"script": script}
        if metadata:
            payload["metadata"] = metadata

        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 4096),
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(payload, indent=2)}],
        )

        response_text = message.content[0].text
        cleaned_json = clean_json_text(response_text)
        result = json.loads(cleaned_json)

        result["generated_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Successfully generated thumbnail prompt for '%s'", script_title)
        return result

    except json.JSONDecodeError as err:
        logger.error("Failed to parse JSON thumbnail prompt response from Claude: %s", err)
        return None
    except Exception as err:
        logger.exception("Error calling Anthropic API for thumbnail prompt: %s", err)
        return None


def _save_result(result: dict | None) -> None:
    """Save generated thumbnail prompt to output/scripts/thumbnail_prompt_<timestamp>.json."""
    if not result:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.SCRIPTS_DIR / f"thumbnail_prompt_{timestamp}.json"
    save_json(result, filepath)
    logger.info("Saved thumbnail prompt to %s", filepath)


if __name__ == "__main__":
    dummy_script = {"title": "Test Script", "sections": []}
    result = generate_thumbnail_prompt(dummy_script)
    _save_result(result)
