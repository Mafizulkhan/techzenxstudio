"""
Viral Candidate Scorer & Best-Pick Selector

Takes 2-3 generated candidate packages, sends their titles/hooks to Claude with the
viral scoring prompt, rates each for viral potential (1-10 scale), and selects
the single winning package.

Usage:
    python -m ai.score_candidates
"""

import json
from datetime import datetime, timezone
import anthropic

import config
from utils import setup_logger, load_prompt, clean_json_text

logger = setup_logger("ai.score_candidates")


def score_candidates(candidate_packages: list[str]) -> tuple[int, dict] | tuple[int, None]:
    """
    Evaluate 2-3 Markdown candidate packages and return the index of the winning candidate.

    Args:
        candidate_packages: List of Markdown package strings (2-3 packages).

    Returns:
        Tuple of (winning_index, scoring_result_dict)
    """
    if not candidate_packages:
        logger.warning("No candidate packages provided to score")
        return (0, None)

    if len(candidate_packages) == 1:
        logger.info("Only 1 candidate provided — selecting automatically")
        return (0, {"winning_index": 0, "winning_reason": "Single candidate provided."})

    if not config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set — defaulting to first candidate")
        return (0, None)

    logger.info("Evaluating %d candidate packages for viral potential...", len(candidate_packages))

    try:
        system_prompt = load_prompt(config.PROMPTS_DIR / "viral_scoring.md")
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # Extract title and hook from each package for evaluation
        eval_payload = []
        for idx, pkg in enumerate(candidate_packages):
            eval_payload.append({
                "candidate_index": idx,
                "preview_content": pkg[:1200]  # First 1200 chars containing title, overview, hook scene
            })

        message = client.messages.create(
            model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=getattr(config, "CLAUDE_MAX_TOKENS", 2048),
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(eval_payload, indent=2)}],
        )

        response_text = message.content[0].text
        cleaned_json = clean_json_text(response_text)
        scoring_data = json.loads(cleaned_json)

        winning_idx = scoring_data.get("winning_index", 0)
        # Ensure index is within valid bounds
        if not (0 <= winning_idx < len(candidate_packages)):
            winning_idx = 0

        logger.info("Winning candidate index: %d — Reason: %s",
                    winning_idx, scoring_data.get("winning_reason", "N/A"))
        return (winning_idx, scoring_data)

    except json.JSONDecodeError as err:
        logger.error("Failed to parse JSON scoring response from Claude: %s", err)
        return (0, None)
    except Exception as err:
        logger.exception("Error calling Anthropic API for viral scoring: %s", err)
        return (0, None)


if __name__ == "__main__":
    dummy_pkgs = [
        "# Candidate A: AI Robotaxis Take Over Streets\n\n## Video Overview\n...",
        "# Candidate B: Quantum Computer Discovery\n\n## Video Overview\n..."
    ]
    idx, res = score_candidates(dummy_pkgs)
    print(f"Winning index: {idx}, Result: {res}")
