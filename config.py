"""
Central configuration for the YouTube AI Automation Pipeline.

All API keys and constants are loaded here from environment variables.
Every module imports from this file — single source of truth.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

# ── API Keys ─────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "youtube-ai-automation/1.0")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY", "")
IMAGE_GEN_API_KEY = os.getenv("IMAGE_GEN_API_KEY", "")

# ── Claude Model Config ─────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096

# ── Trend Fetcher Settings ───────────────────────────────────────────
# Subreddits to scrape for tech trends
TARGET_SUBREDDITS = [
    "technology",
    "Futurology",
    "artificial",
]

# RSS feeds for tech/AI news
RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://news.google.com/rss/search?q=AI+tools&hl=en-US&gl=US&ceid=US:en",
]

# YouTube trending settings
YOUTUBE_CATEGORY_ID = "28"  # Science & Technology
YOUTUBE_REGION_CODE = os.getenv("YOUTUBE_REGION_CODE", "US")

# ── Scoring Keywords ─────────────────────────────────────────────────
SCORING_KEYWORDS = [
    "AI", "artificial intelligence", "technology", "innovation",
    "science", "future", "tech tool", "machine learning",
    "robotics", "automation", "startup", "gadget",
]

# ── Output Paths ─────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "output"
TRENDS_DIR = OUTPUT_DIR / "trends"
SCRIPTS_DIR = OUTPUT_DIR / "scripts"
SHOTLISTS_DIR = OUTPUT_DIR / "shotlists"
AUDIO_DIR = OUTPUT_DIR / "audio"
RUNS_DIR = OUTPUT_DIR / "runs"

# ── Prompt Template Paths ────────────────────────────────────────────
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SCRIPT_PROMPT_PATH = PROMPTS_DIR / "script_generation.md"
METADATA_PROMPT_PATH = PROMPTS_DIR / "metadata_generation.md"
THUMBNAIL_PROMPT_PATH = PROMPTS_DIR / "thumbnail_prompt.md"
SHOTLIST_PROMPT_PATH = PROMPTS_DIR / "shotlist_generation.md"
