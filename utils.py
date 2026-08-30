"""
Shared utilities for the YouTube AI Automation Pipeline.

Provides logging setup, JSON I/O, and output directory management
used by all modules.
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

import config


def setup_logger(name: str, log_to_file: bool = True) -> logging.Logger:
    """
    Create a configured logger with console + optional file output.

    Args:
        name: Logger name (typically __name__ of the calling module).
        log_to_file: If True, also writes to /tmp/logs/<name>.log.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (INFO+) — guarded for UTF-8 unicode/emojis
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler (DEBUG+) — wrapped in try/except for read-only filesystems (Vercel)
    if log_to_file:
        try:
            log_dir = Path("/tmp/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(
                log_dir / f"{name}.log", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            pass  # Fall back to console-only on read-only filesystems

    return logger


def save_json(data, filepath: Path | str) -> Path:
    """
    Save data as pretty-printed JSON, creating parent dirs as needed.

    Args:
        data: Serializable Python object (dict, list, etc.).
        filepath: Destination path.

    Returns:
        The resolved Path where the file was saved.
    """
    filepath = Path(filepath)
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Silently skip on read-only filesystems (Vercel)
    return filepath


def load_json(filepath: Path | str):
    """
    Load JSON from a file with friendly error handling.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Parsed Python object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file isn't valid JSON.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(prompt_path: Path | str) -> str:
    """
    Read a prompt template from a Markdown file.

    Args:
        prompt_path: Path to the .md prompt template.

    Returns:
        The prompt text as a string.

    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
    """
    prompt_path = Path(prompt_path)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()


def clean_json_text(raw_text: str) -> str:
    """
    Strip markdown code fences (```json ... ```) and leading/trailing text from AI output.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove opening ```json or ```
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def ensure_output_dirs() -> None:
    """Create all required output subdirectories if they don't exist."""
    dirs = [
        config.TRENDS_DIR,
        config.SCRIPTS_DIR,
        config.SHOTLISTS_DIR,
        config.AUDIO_DIR,
        config.RUNS_DIR,
    ]
    for d in dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # Skip on read-only filesystems (Vercel)


def get_run_dir() -> Path:
    """
    Create and return a dated run directory for today's pipeline output.

    Returns:
        Path to /output/runs/YYYY-MM-DD/ directory.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    run_dir = config.RUNS_DIR / today
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass  # Skip on read-only filesystems (Vercel)
    return run_dir
