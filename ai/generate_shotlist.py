"""
Shot List Generator — Claude-powered Scene-by-Scene Breakdown

Takes a generated script and produces a timestamped shot list
formatted for the Higgsfield video generation workflow.

Usage:
    python -m ai.generate_shotlist
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, load_prompt

logger = setup_logger("ai.generate_shotlist")


def generate_shotlist(script: dict) -> str | None:
    """
    Generate a timestamped shot list from a script.

    Sends the script to Claude with the shotlist generation prompt.
    Expects output in this exact format (one line per scene):

        [M:SS] Scene description — camera: ..., lighting: ..., sound: ..., duration: Ns

    This format feeds directly into the Higgsfield shot-list workflow.

    Args:
        script: Generated script dict from generate_script().

    Returns:
        Shot list as a string (multi-line text), or None if generation failed.
    """
    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set — cannot generate shot list")
        return None

    script_title = script.get("title", "Untitled Video")
    logger.info("Generating shot list for: %s", script_title)

    try:
        system_prompt = load_prompt(config.SHOTLIST_PROMPT_PATH)
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 4096),
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(script, indent=2)}],
        )

        shotlist_text = message.content[0].text.strip()
        logger.info("Successfully generated shot list for '%s' (%d lines)",
                    script_title, len(shotlist_text.splitlines()))
        return shotlist_text

    except Exception as err:
        logger.exception("Error calling Anthropic API for shot list: %s", err)
        return None


def _save_result(shotlist: str | None, title: str = "untitled") -> None:
    """Save generated shot list to output/shotlists/<title>_<timestamp>.txt."""
    if not shotlist:
        logger.info("No shot list to save")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
    safe_title = safe_title.strip().replace(" ", "_")[:50] or "shotlist"
    filepath = config.SHOTLISTS_DIR / f"{safe_title}_{timestamp}.txt"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(shotlist, encoding="utf-8")
    logger.info("Saved shot list to %s", filepath)


if __name__ == "__main__":
    dummy_script = {"title": "Test Script", "sections": []}
    result = generate_shotlist(dummy_script)
    _save_result(result, "test")
