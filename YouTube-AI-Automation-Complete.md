# YouTube AI Content Automation — Complete Plan & Antigravity Build Guide

**Channel:** TechZenX (tech/AI/science shorts, Hinglish)
**Niche:** Tech / AI tools / futuristic innovation / mind-blowing tech & science facts / new technology
**Output:** A complete **text content package per video** — NOT a rendered video. The package contains: video overview, scene-by-scene breakdown with camera angle, motion graphics, SFX, and Hinglish voiceover line for each scene (as a ready-to-paste video-generation prompt), plus title options, description, tags, and thumbnail prompt.
**Cadence:** Runs automatically every morning between **8:00–12:00**, researches trending topics, drafts **2–3 full candidate packages**, scores them for viral potential, and outputs only the **single best one** for your review.
**Goal:** You wake up to one ready-to-use script package for your most promising topic of the day — you take that package into your video-generation tool (Google Flow, Midjourney, etc.) yourself.
**Build tool:** Google Antigravity (agentic IDE)

---

## Part 1 — The Plan

### 1.0 Pipeline Overview

```
[Trend Discovery — web browsing + APIs] → [Generate 2-3 Candidate Packages]
        ↓
        [Each candidate scored for viral potential]
        ↓
        [Best candidate selected]
        ↓
        [Full package saved: script + prompts + title/desc/tags + thumbnail prompt]
        ↓
        [You review each morning] → [You generate video/thumbnail yourself in Flow/Midjourney]
```

No voiceover audio, no video rendering, no auto-publishing happens in this pipeline — the output is a **finished text document**, matching the exact format you already use. This keeps the system simple, avoids API costs for audio/video generation you don't need, and keeps you in full creative control of the final render.

### 1.1 Content Pillars & Channel Identity

Lock these down first — they become the "system prompt" for your AI script writer:
- **Content pillars:** AI tools, futuristic innovation, mind-blowing tech facts, science facts, new technology
- **Tone:** Fast-paced, punchy, viral hook-driven, Hinglish (Hindi-English mix)
- **Video length:** 45–60 seconds (Shorts/Reels format)
- **Visual style:** Cinematic — defined camera language (drone shots, macro shots, slow push-ins) rather than static stock footage
- **Channel name/branding, intro sting, consistent thumbnail style** (color palette, font, face/no-face)

### 1.2 Trend Discovery (Data Collection Layer)

Two complementary approaches — use both:

**A. Direct web research via the agent's browser** — Antigravity's agent can browse the web directly (trending pages, tech news homepages, YouTube's trending tab, subreddit front pages) as part of its research step, without you wiring up every API individually. Fastest way to get this running.

**B. Structured API feeds (more reliable/repeatable long-term)** — layer these in afterward for consistency:

| Platform | How to pull trend data |
|---|---|
| **YouTube** | YouTube Data API v3 — `videos.list` with `chart=mostPopular`, filtered by tech category |
| **Google** | Google Trends (via `pytrends` unofficial library, or Google Trends RSS for "Technology") |
| **Reddit** | Reddit API (free tier) — top posts from r/technology, r/Futurology, r/artificial, r/gadgets |
| **News aggregation (best ROI)** | RSS feeds from TechCrunch, The Verge, Ars Technica, MIT Tech Review, Google News RSS for "AI tools," "new technology," "science discovery" |
| **Instagram/Facebook** | Skip direct scraping (against ToS, fragile) — the web-browsing agent reading public tech-news pages covers this gap adequately |

**Practical recommendation:** Start with the agent's own web-browsing research (fast, flexible), layer in YouTube/Reddit/RSS APIs afterward for repeatable, rate-limit-safe daily runs.

### 1.3 The Master Generation Prompt (single AI call produces the whole package)

This is the core of the whole system — one detailed prompt that generates the entire content package in your exact reference format, in one shot, per candidate topic:

```
SYSTEM PROMPT:
You are the AI scriptwriter for TechZenX, a tech/AI/science YouTube Shorts
channel. Audience: Hindi-English bilingual, tech-curious, aged 16-35.
Tone: fast-paced, punchy, viral-hook-driven, explained like a "wow, I didn't
know that!" reveal.

Given a trending tech/AI/science topic and a short research summary, generate
a COMPLETE ready-to-produce content package in EXACTLY this structure:

# [Video working title]

## Video Overview
- Target Duration: ~XX Seconds (45-60s)
- Format: Vertical 9:16 (YouTube Shorts)
- Visual Style: [2-4 descriptive keywords, e.g. "3D microscopic visualization,
  thermal comparison, high-speed particle simulation"]
- BGM: [one line describing the background music/sound mood]

## Scene-by-Scene Script & Video Generation Prompts

For each scene (aim for 4-6 scenes: Hook, 2-4 explanation beats, Outro/CTA),
output:

### Scene N: [Scene Name] (start-end timestamp)
**Camera Angle & Motion:** [specific camera direction, e.g. "high-angle macro
shot, fast dynamic push-in" or "3D atomic lattice orbit shot"]
**SFX:** [specific sound effect cue for this scene]
**Google Flow Prompt:** [a full, detailed, ready-to-paste video-generation
prompt — vertical 9:16, cinematic, photorealistic or 3D-render style,
describing exactly what's on screen, lighting, and camera motion]
**Voiceover (Hinglish):** "[natural Hindi-English code-switched line for this
scene, NOT a literal translation — written the way a real bilingual creator
would speak it]"

## Best Title, Description & Tags
**Best YouTube Shorts Title:** [one strong title with 1-2 emoji]
**Alternative Titles:** [3 more options]
**YouTube Shorts Description:** [2-3 sentence hook + subscribe CTA]
**Targeted Tags:** [15-20 comma-separated tags mixing broad + specific + channel name]

## Thumbnail Prompt (For Google Flow / Midjourney / DALL-E)
[one detailed thumbnail image-generation prompt: vertical 9:16, high-contrast,
dramatic lighting/color split, bold text overlay concept, hyper-detailed]

Style rules:
- Hinglish must read naturally, the way a real creator talks — not stiff translation
- Every "Google Flow Prompt" must be detailed enough to paste directly into a
  video generation tool with no further editing needed
- Keep total voiceover word count fitting the target duration at natural pace
- Do not invent false/misleading facts — if unsure of a specific number or
  claim, phrase it more generally rather than guessing a fake statistic
```

Feed this + each candidate topic's research summary to Claude, and you get the full package back in the exact format you're already using — no separate title/description/thumbnail/shot-list calls needed.

### 1.4 Daily Batch: Generate 2–3 Candidates, Score, Keep the Best One

Every morning between 8:00–12:00, the pipeline should:

1. **Research** 4–6 trending tech/AI/science topics (via web browsing + APIs from 1.2)
2. **Generate a full package** (1.3's prompt) for the **top 2–3** topics — not just one, so you have a real comparison
3. **Score each candidate** for viral potential using a second, smaller AI call:

```
Given these 2-3 video title+description+hook combinations, rate each for
viral potential on a 1-10 scale considering: hook strength (does it stop
scroll in the first 2 seconds?), curiosity gap, topic novelty/trendiness
today, and clarity of the "wow factor." Return the highest-scoring one with
a one-line reason why it wins.
```

4. **Keep only the winning package**, discard (or archive) the others
5. Save the final package as a single Markdown file, e.g. `/output/runs/2026-08-31.md`, in the exact format from 1.3

You wake up to one file: today's best script, ready to take into your video-generation tool.

### 1.5 What You Do With the Output

Since this pipeline generates **text only** (no rendering), your manual steps after each morning's package lands are:
1. Read through the package (2-minute check — verify no factual errors, tone feels right)
2. Copy each scene's "Google Flow Prompt" into Google Flow (or Midjourney/whichever tool you use) to generate visuals
3. Copy the thumbnail prompt into your image tool
4. Record/generate the Hinglish voiceover yourself (not automated in this version — you only need the prompts, not rendered audio)
5. Assemble and publish as usual

### 1.6 Performance Feedback Loop (later optimization)

Once live, periodically pull view/retention stats via YouTube Analytics API and feed back into 1.4's scoring — topics/formats that performed well should get weighted higher in future topic selection, closing the loop into a self-improving system.

### 1.7 Legal & Policy Notes (important)

- **Don't scrape Instagram/Facebook directly** — their ToS restricts this heavily; rely on the agent's general web browsing of public pages plus official APIs/RSS rather than aggressive scraping.
- **Fact-check "science facts" content** — your 2-minute daily review step protects you from spreading misinformation and the credibility damage that follows. The master prompt in 1.3 also explicitly instructs the AI not to invent false statistics.
- **Respect API rate limits/quotas** (especially YouTube Data API's daily quota) if/when you add the structured API layer alongside web browsing.
- Since no video is auto-generated or auto-published by this pipeline, YouTube's synthetic-content disclosure requirements apply based on however *you* ultimately produce and label the final video — check current policy once you're rendering and uploading.

### 1.8 Suggested Build Timeline

| Phase | What gets built | Est. duration |
|---|---|---|
| 1. Research layer | Web-browsing research task + YouTube/Reddit/RSS API connectors | 1 week |
| 2. Master generation prompt | Claude API integration with the full package prompt (1.3) | 3–5 days |
| 3. Multi-candidate + viral scoring | Generate 2-3 candidates per run, scoring call, best-pick selection | 3–5 days |
| 4. Orchestration & scheduling | `run_pipeline.py` wired end-to-end, scheduled for 8:00-12:00 daily | 3–5 days |
| 5. Output formatting | Save final package as clean Markdown matching your reference format | 2–3 days |
| 6. Review routine | Your daily 2-minute read-through habit | Ongoing from day 1 |
| 7. Feedback loop (later) | Pull performance data back into topic/scoring logic | Ongoing, add after ~1 month of data |

---

## Part 2 — Building It in Antigravity, Step by Step

### 2.0 How Antigravity Works (quick orientation)

- You don't write code line-by-line — you give the **Agent** a task in plain language, it plans, writes code, runs it in a terminal, tests it (even in a browser if needed), and reports back with **Artifacts** (task list, implementation plan, walkthrough) for you to review and approve.
- Three autonomy modes: **full autonomy** (agent just does it — good for scaffolding), **checkpoint mode** (agent pauses at key decisions — best for most of this project), and **step-approval mode** (you approve every step — best for parts touching API keys/publishing).
- You can run **multiple independent agents in parallel** once the foundation is built.

**Recommendation:** use **checkpoint mode** for most tasks so Antigravity pauses and shows you the plan before writing code.

### 2.1 Install & Set Up

1. Download Antigravity IDE from antigravity.google and install it
2. Sign in with your Google account
3. Create a new empty project folder, e.g. `youtube-ai-automation`
4. Open it in Antigravity — this becomes your one workspace for the whole pipeline

### 2.2 Gather Your API Keys First

Before giving the agent any tasks, get accounts + keys ready (the agent references these as environment variables — never paste raw keys into chat prompts):
- **ANTHROPIC_API_KEY** (console.anthropic.com — script/package generation)
- **YOUTUBE_API_KEY** (Google Cloud Console → enable "YouTube Data API v3" — trend fetching)
- **REDDIT_CLIENT_ID** + secret (reddit.com/prefs/apps, "script" type app — trend fetching)

Store them in a `.env` file — tell the agent to always read secrets from `.env`, never hardcode them. Support a **demo mode** (runs with sample data when keys are absent, e.g. `python run_pipeline.py --demo`) and a **live mode** (auto-switches to real API calls once real keys are present) — this lets you test pipeline logic safely before spending on real API calls.

### 2.3 Give Antigravity the First Task (project scaffold)

```
Set up a Python project for a YouTube content automation pipeline. Create
this folder structure:
- /fetchers (for trend research/data collection scripts)
- /ai (for Claude API package generation and scoring)
- /prompts (for stored prompt templates)
- /output/candidates (generated candidate packages)
- /output/runs (final daily-selected package, one .md file per date)
- .env.example (list required env vars, no real values)
- README.md (explain the project structure)

Use environment variables for all API keys, never hardcode secrets. Build in
a --demo flag that uses sample data with no real API calls, and a live mode
that activates automatically once real keys are found in .env. Set up basic
error handling and logging for each module.
```

Let it plan, review the plan Artifact, then approve.

**Scope reminder:** this build outputs a **text file per day** (video overview, scene-by-scene camera/SFX/Hinglish-voiceover script, title/description/tags, thumbnail prompt) — it does not render video or audio, or publish anything. You take the finished package into Google Flow/Midjourney yourself. This keeps the build simple and avoids paying for generation APIs you don't need here.

### 2.4 Build the Trend Research Step

```
Task: Give the agent a browsing research task — e.g. "Browse YouTube's
trending tech videos, r/technology's top posts today, and 2-3 tech news
homepages, and summarize the 5 most interesting tech/AI/science trending
topics right now, saving results as JSON to /output/trends/."
```

This uses Antigravity's browser-use capability directly and gets you a working version fast. Optionally, add structured API fetchers afterward for reliability:

```
Task: Build a YouTube Data API fetcher in /fetchers/youtube.py that pulls
trending tech-category videos (chart=mostPopular), and a Reddit API fetcher
in /fetchers/reddit.py pulling top posts from r/technology, r/Futurology,
r/artificial from the last 24 hours. Save both in the same JSON format to
/output/trends/. Test by running each and showing me real output.
```

Ask the agent to **run each step and show you real results** before moving on — this is exactly the self-verification loop Antigravity is built for.

### 2.5 Build the Trend Scorer

```
Task: Build a scoring script in /fetchers/score.py that reads all researched
topics, scores each by: recency (newer = higher), keyword match against
["AI", "technology", "innovation", "science", "future", "tech tool"], and
removes near-duplicate topics. Output the top 4-6 scored candidates to
/output/top-candidates.json.
```

### 2.6 Build the Master Package Generator

The core AI step — paste in the full master prompt from Section 1.3:

```
Task: Build /ai/generate_package.py that takes ONE trend candidate and sends
it to the Claude API with this exact system prompt: [paste the full master
generation prompt from Section 1.3]. Save the returned Markdown-formatted
package to /output/candidates/[topic-slug].md. Make it callable so it can be
run once per candidate topic.
```

Run it against 2–3 real fetched topics and read the actual generated packages closely — **this is the single most important checkpoint in the whole build**, since script quality is what determines whether this is actually useful day to day.

### 2.7 Build the Viral Scorer & Best-Pick Selector

```
Task: Build /ai/score_candidates.py that takes 2-3 generated packages from
/output/candidates/, sends their titles+hooks+descriptions to Claude with
this scoring prompt: [paste the scoring prompt from Section 1.4], and picks
the highest-scoring one. Copy the winning package to
/output/runs/[today's date].md as the final output, and archive the others
in /output/candidates/archive/.
```

### 2.8 Chain It Into One Daily Pipeline

```
Task: Build /run_pipeline.py that runs the full chain in order: research
trending topics → score/select top 4-6 → generate a full package for the
top 2-3 → run viral scoring → save the winning package to
/output/runs/[date].md. Log progress at each stage clearly in the terminal.
Support both --demo mode (sample data, no real API calls) and live mode
(real API keys from .env).
```

Run once manually in demo mode, review the fake output for structural correctness, then run once live and read the real generated package end to end.

### 2.9 Schedule It for 8:00–12:00 Daily

```
Task: Add scheduling so /run_pipeline.py runs automatically once every
morning between 8:00 and 12:00 (e.g. pick 9:00 AM), using Python's schedule
library or a system cron job. Make sure it only runs once per day even if
the machine is on for the whole window.
```

*(Antigravity 2.0's standalone app also has built-in scheduled task support — you can alternatively schedule the whole agent run from within Antigravity itself rather than writing your own cron logic.)*

### 2.10 Your Daily Review Routine

Each morning, open `/output/runs/[today's date].md` — your one finished package: video overview, scene-by-scene camera/SFX/Hinglish voiceover script, title/description/tags, and thumbnail prompt, matching your reference format. Do a 2-minute read-through (factual accuracy + tone check), then copy each "Google Flow Prompt" into your video-generation tool.

### 2.11 Working Style Tips for Antigravity

- **Give one clear task per agent turn** — Antigravity works best when it can plan → execute → verify → report for a scoped chunk, then you review the Artifact before the next chunk.
- **Use checkpoint mode** on anything touching API keys, publishing, or external calls — full autonomy is fine for pure scaffolding.
- **Ask it to actually run and show real output**, not just write code — lean on Antigravity's terminal execution for verification at every step.
- **Run parallel agents for independent pieces** once the foundation (2.3) is done — e.g. one agent on the scorer while another works on the master generator, since these don't depend on each other.
- **Keep prompt templates in files, not inline strings** — store each prompt in `/prompts/*.md` and have the code read from there, so you can iterate on prompt wording without touching code.

### 2.12 Suggested Order of Operations (summary)

1. Install Antigravity, set up project, gather API keys (Anthropic + optionally YouTube/Reddit)
2. Task: project scaffold with demo/live mode switch
3. Task: web-browsing research step → verify real topics come back
4. Task (optional): YouTube/Reddit API fetchers for reliability → verify
5. Task: trend scorer → verify top candidates look right
6. Task: master package generator (1.3 prompt) → **review script quality closely, this is the key checkpoint**
7. Task: viral scorer & best-pick selector → verify it picks sensibly
8. Task: chain into `run_pipeline.py` with demo/live modes → run once, review full package
9. Task: add scheduling for 8:00–12:00 daily
10. Daily 2-minute review of `/output/runs/[date].md` → copy prompts into Google Flow/Midjourney yourself
