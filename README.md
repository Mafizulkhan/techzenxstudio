# YouTube AI Automation Pipeline

Automated content pipeline that discovers trending tech/AI topics, generates YouTube-ready scripts, metadata, shot lists, and voiceovers using AI — then packages everything for video production.

## 🏗 Project Structure

```
youtube-ai-automation/
├── config.py              # Central configuration (API keys, constants, paths)
├── utils.py               # Shared utilities (logging, JSON I/O, output dirs)
├── run_pipeline.py        # Full pipeline orchestrator
│
├── fetchers/              # Trend data collection
│   ├── youtube.py         # YouTube Data API trending fetcher
│   ├── reddit.py          # Reddit top posts fetcher
│   ├── rss.py             # RSS feed parser (TechCrunch, Verge, etc.)
│   └── score.py           # Trend merger, deduplicator, scorer
│
├── ai/                    # AI-powered content generation
│   ├── generate_script.py          # Claude → YouTube script
│   ├── generate_metadata.py        # Claude → title, description, tags
│   ├── generate_thumbnail_prompt.py # Claude → image-gen prompt
│   ├── generate_shotlist.py        # Claude → scene-by-scene shot list
│   └── generate_voiceover.py       # TTS → Hinglish voiceover audio
│
├── prompts/               # Prompt templates (Markdown — edit without touching code)
│   ├── script_generation.md
│   ├── metadata_generation.md
│   ├── thumbnail_prompt.md
│   └── shotlist_generation.md
│
└── output/                # Generated content (git-ignored)
    ├── trends/            # Raw + scored trend data
    ├── scripts/           # Generated scripts (JSON)
    ├── shotlists/         # Scene-by-scene shot lists
    ├── audio/             # TTS voiceover files
    └── runs/              # Full daily content packages (YYYY-MM-DD/)
```

## 🚀 Setup

### 1. Clone & enter the project
```bash
git clone <repo-url>
cd youtube-ai-automation
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
```bash
cp .env.example .env
# Edit .env and fill in your real API keys
```

## 📖 Usage

### Run the full pipeline
```bash
python run_pipeline.py
```
This runs the complete chain: fetch trends → score → generate script → metadata → thumbnail prompt → shot list → voiceover. Output is saved to `output/runs/<today's date>/`.

### Run individual modules
```bash
# Fetch trends from YouTube
python -m fetchers.youtube

# Fetch trends from Reddit
python -m fetchers.reddit

# Fetch trends from RSS
python -m fetchers.rss

# Score and rank all fetched trends
python -m fetchers.score
```

### Edit AI prompts
Prompt templates live in `/prompts/*.md` — edit the Markdown files directly to tune script quality, tone, format, etc. No code changes required.

## 🔑 Required API Keys

| Service | Purpose | Get it at |
|---------|---------|-----------|
| Anthropic (Claude) | Script/metadata/shot list generation | [console.anthropic.com](https://console.anthropic.com/) |
| YouTube Data API v3 | Trending video discovery | [Google Cloud Console](https://console.cloud.google.com/) |
| Reddit API | Trending post discovery | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| ElevenLabs | Hinglish TTS voiceover | [elevenlabs.io](https://elevenlabs.io/) |
| Image Gen (optional) | Programmatic thumbnail creation | Varies by provider |

## 📋 Daily Workflow

1. Pipeline runs automatically (or manually via `python run_pipeline.py`)
2. Review outputs in `output/runs/<date>/`
3. Take the shot list into Higgsfield for video generation
4. Use the voiceover `.mp3` in your video editor
5. Apply the generated metadata when publishing to YouTube
