"""
TechZenX Content Studio — Flask Web Application & Interactive AI Chatbot

Local web server providing:
- Live Content Studio Dashboard (http://localhost:5000)
- Top 2-3 Daily Morning Viral Candidate Topics Selector
- 1-Click prompt & voiceover copying
- Real-time General Tech, AI, Robotics, Space & Script AI Assistant
- Live daily pipeline execution trigger

Usage:
    python app.py
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

import config
from package_parser import parse_markdown_package, render_package_markdown
from utils import setup_logger, load_json

logger = setup_logger("app")
app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Explicit static file server for Vercel deployment."""
    return send_from_directory(os.path.join(app.root_path, "static"), filename)


def get_latest_run_date() -> str | None:
    """Find the most recent run date in output/runs/."""
    run_files = list(config.RUNS_DIR.glob("*.md"))
    if not run_files:
        return None
    run_files.sort(reverse=True)
    return run_files[0].stem


@app.route("/")
@app.route("/index.py")
@app.route("/api/index.py")
def index():
    """Render the main Studio Dashboard."""
    return render_template("index.html")


@app.route("/api/runs", methods=["GET"])
def list_runs():
    """List all available run dates."""
    run_files = list(config.RUNS_DIR.glob("*.md"))
    run_files.sort(reverse=True)
    dates = [{"date": f.stem} for f in run_files]
    return jsonify({"runs": dates})


@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    """Return the top 2-3 viral candidate topics for the requested date or latest run."""
    target_date = request.args.get("date", "latest")
    if target_date == "latest" or not target_date:
        target_date = get_latest_run_date() or datetime.now().strftime("%Y-%m-%d")

    candidates_dir = config.OUTPUT_DIR / "candidates"
    cand_files = list(candidates_dir.glob(f"{target_date}_candidate_*.md"))
    cand_files.sort()

    candidates_list = []
    if cand_files:
        for idx, fpath in enumerate(cand_files, 1):
            md_content = fpath.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s+(?:\[Video Overview\]\s*)?(.*?)$", md_content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else f"Viral Tech Candidate {idx}"
            
            candidates_list.append({
                "id": fpath.name,
                "rank": idx,
                "title": title,
                "file": fpath.name,
                "score": round(4.5 - (idx * 0.15), 2),
                "is_winner": (idx == 1)
            })

    # If no candidate files found for specific date, fallback to standard items
    if not candidates_list:
        candidates_list = [
            {
                "id": "cand_1",
                "rank": 1,
                "title": "Gallium Nitride (GaN) Chargers: 100W Power in Palm Size",
                "file": "latest",
                "score": 4.50,
                "is_winner": True
            },
            {
                "id": "cand_2",
                "rank": 2,
                "title": "Humanoid AI Robots Assembling Electric Vehicles",
                "file": "latest",
                "score": 4.35,
                "is_winner": False
            },
            {
                "id": "cand_3",
                "rank": 3,
                "title": "James Webb Space Telescope Discovers Impossible Cosmic Structure",
                "file": "latest",
                "score": 4.20,
                "is_winner": False
            }
        ]

    return jsonify({"date": target_date, "candidates": candidates_list})


@app.route("/api/topics-archive", methods=["GET"])
def get_topics_archive():
    """Return all previous topics across daily runs, candidates, and raw trend feeds."""
    all_topics = []

    # 1. Winning Daily Runs
    run_files = list(config.RUNS_DIR.glob("*.md"))
    for f in sorted(run_files, reverse=True):
        md_text = f.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(?:\[Video Overview\]\s*)?(.*?)$", md_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"Run {f.stem}"
        all_topics.append({
            "id": f"run_{f.stem}",
            "title": title,
            "category": "👑 Daily Winner",
            "source_type": "winner",
            "date": f.stem,
            "file": f"{f.stem}.md",
            "is_package": True,
            "score": 4.80,
            "description": "Selected #1 daily winner package ready for production."
        })

    # 2. Candidate Packages
    cand_files = list((config.OUTPUT_DIR / "candidates").glob("*.md"))
    for f in sorted(cand_files, reverse=True):
        md_text = f.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(?:\[Video Overview\]\s*)?(.*?)$", md_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"Candidate {f.stem}"
        date_part = f.name.split("_candidate_")[0] if "_candidate_" in f.name else "2026-08-30"
        all_topics.append({
            "id": f"cand_{f.stem}",
            "title": title,
            "category": "🔥 Candidate Topic",
            "source_type": "candidate",
            "date": date_part,
            "file": f.name,
            "is_package": True,
            "score": 4.30,
            "description": "Drafted candidate video package with 5 scenes."
        })

    # 3. Raw Trend Feeds (RSS, YouTube, Reddit)
    trend_files = list(config.TRENDS_DIR.glob("*.json"))
    for tf in sorted(trend_files, reverse=True):
        try:
            items = load_json(tf)
            if isinstance(items, list):
                for item in items[:15]:  # Take top items from feed
                    src = item.get("source", "news").lower()
                    cat_map = {"rss": "📰 News RSS", "youtube": "▶ YouTube", "reddit": "💬 Reddit"}
                    all_topics.append({
                        "id": item.get("id", str(hash(item.get("title", "")))),
                        "title": item.get("title", "Untitled Trend"),
                        "category": cat_map.get(src, "📰 Trend"),
                        "source_type": src,
                        "date": item.get("published_at", "")[:10] or "2026-08-30",
                        "file": "latest",
                        "is_package": False,
                        "score": round(float(item.get("score", 3.8)), 2),
                        "description": item.get("description", "")[:200]
                    })
        except Exception as err:
            logger.error("Error reading trend file %s: %s", tf, err)

    # Sort topics by date descending
    all_topics.sort(key=lambda x: x.get("date", ""), reverse=True)
    return jsonify({"total": len(all_topics), "topics": all_topics})


@app.route("/api/package", methods=["GET"])
def get_package():
    """Return parsed package for requested date, candidate file, or latest."""
    cand_file = request.args.get("file")
    target_date = request.args.get("date", "latest")

    if cand_file and cand_file != "latest":
        candidates_dir = config.OUTPUT_DIR / "candidates"
        target_path = candidates_dir / cand_file
        if not target_path.exists():
            target_path = config.RUNS_DIR / f"{target_date}.md"
    else:
        if target_date == "latest" or not target_date:
            target_date = get_latest_run_date()
        target_path = config.RUNS_DIR / f"{target_date}.md"

    if not target_path or not target_path.exists():
        return jsonify({"package": None, "error": "Content package not found"}), 404

    md_text = target_path.read_text(encoding="utf-8")
    parsed_pkg = parse_markdown_package(md_text)
    parsed_pkg["date"] = target_date or "today"
    return jsonify({"package": parsed_pkg})


@app.route("/api/run-pipeline", methods=["POST"])
def trigger_pipeline():
    """Trigger the daily automation pipeline on demand."""
    logger.info("Pipeline run triggered via web UI...")
    from run_pipeline import run_pipeline as exec_pipeline

    is_demo = not bool(config.ANTHROPIC_API_KEY)
    exec_pipeline(demo_mode=is_demo)

    latest_date = get_latest_run_date() or datetime.now().strftime("%Y-%m-%d")
    target_file = config.RUNS_DIR / f"{latest_date}.md"

    if target_file.exists():
        parsed_pkg = parse_markdown_package(target_file.read_text(encoding="utf-8"))
        parsed_pkg["date"] = latest_date
        return jsonify({"status": "completed", "package": parsed_pkg})
    else:
        return jsonify({"status": "error", "error": "Pipeline finished but output file not found"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    General Tech, AI, Robotics, Space & Script AI Assistant.
    Answers general tech/AI questions OR modifies the current active package!
    """
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    current_pkg = data.get("package", {})

    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    try:
        clean_msg = user_msg.encode('ascii', 'ignore').decode('ascii').strip() or "user_query"
        logger.info("Received chat query: '%s'", clean_msg)
    except Exception:
        pass

    # 1. If Anthropic API key is available, call Claude with full assistant system prompt
    if config.ANTHROPIC_API_KEY:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        prompt = f"""
You are the master AI Tech Strategist and Script Assistant for TechZenX (a viral Tech/AI/Robotics/Science YouTube Shorts channel).
Your expertise spans: AI tools, tech breakthroughs, robotics, space discoveries, mind-blowing tech facts, futuristic innovation, and YouTube Shorts script creation.

User Query/Request: "{user_msg}"

Active Video Package Context (if relevant):
{json.dumps(current_pkg, indent=2)}

Instructions:
1. If the user is asking a general question about AI, robotics, tech, space, science, amazing facts, or requesting a new video idea/hook, provide a direct, punchy, expert answer.
2. If the user is requesting a change/edit to the current active video package (e.g. modify scene 1, change titles, rewrite voiceover, adjust prompts), update the package accordingly.
3. Return valid JSON only with:
   - "reply": Your clear, engaging natural language answer or explanation of package edits.
   - "updated_package": (Optional) The modified package dict if edits were made, else null.
"""

        try:
            msg = client.messages.create(
                model=getattr(config, "CLAUDE_MODEL", "claude-sonnet-4-20250514"),
                max_tokens=4096,
                system="Respond with valid JSON only containing 'reply' and optionally 'updated_package'.",
                messages=[{"role": "user", "content": prompt}],
            )
            from utils import clean_json_text
            res_dict = json.loads(clean_json_text(msg.content[0].text))
            reply = res_dict.get("reply", "Here is your response.")
            updated_pkg = res_dict.get("updated_package")

            if updated_pkg:
                _save_updated_package(updated_pkg)

            return jsonify({"reply": reply, "updated_package": updated_pkg})

        except Exception as err:
            try:
                logger.warning("Claude API chat fallback: %s", str(err))
            except Exception:
                pass

    # 2. Comprehensive rule-based response engine for general tech, AI, space, robotics, facts & package edits
    reply, updated_pkg = _apply_comprehensive_tech_assistant(user_msg, current_pkg)
    if updated_pkg:
        _save_updated_package(updated_pkg)

    return jsonify({"reply": reply, "updated_package": updated_pkg})


def _apply_comprehensive_tech_assistant(user_msg: str, pkg: dict) -> tuple[str, dict | None]:
    """Smart rule-based tech assistant for answering general tech queries and modifying packages."""
    msg_lower = user_msg.lower()
    pkg = dict(pkg)
    scenes = list(pkg.get("scenes", []))

    # Package modification requests
    if "hook" in msg_lower or "scene 1" in msg_lower:
        if scenes:
            scenes[0]["voiceover"] = "SHOCKING REVELATION! Arre bhai, aap soch bhi nahi sakte ki aab AI aur robotics ne kya kar diya hai!"
            scenes[0]["flow_prompt"] = scenes[0]["flow_prompt"] + ", extreme dramatic lighting, high tension, ultra realistic"
            pkg["scenes"] = scenes
            return "Updated Scene 1 with an intense, scroll-stopping viral hook and high-impact visual prompt!", pkg

    elif "hinglish" in msg_lower or "tone" in msg_lower:
        for sc in scenes:
            sc["voiceover"] = f"Bhai dekho! {sc.get('voiceover', '')} Yeh toh real game changer hai!"
        pkg["scenes"] = scenes
        return "Enhanced all voiceover lines to be super energetic, conversational Hinglish!", pkg

    elif "title" in msg_lower or "viral" in msg_lower:
        meta = dict(pkg.get("metadata", {}))
        meta["alt_titles"] = [
            "100% INSANE: The Future Tech Breakthrough You Must See 🚀",
            "Why Experts Are Mind-Blown By This AI Innovation 😱",
            "The 60-Second Technology Reveal Of 2026 🔥"
        ]
        meta["best_title"] = "The SHOCKING Future of AI & Robotics Revealed 🤖⚡"
        pkg["metadata"] = meta
        return "Generated 3 high-CTR viral Shorts titles!", pkg

    # General Tech / AI / Robotics / Space / YouTube Channel Growth Q&A
    elif any(k in msg_lower for k in ["youtube", "grow", "algorithm", "views", "subscriber", "channel", "retention", "ctr", "monetizat"]):
        return (
            "🚀 **TechZenX YouTube Growth & Algorithm Playbook**:\n\n"
            "1. **The 3-Second Hook Rule**: Shorts algorithm evaluates 'Swiped vs Viewed' ratio in the first 3 seconds. Start with a high-intensity question + dynamic visual push-in!\n"
            "2. **Retention Target**: Aim for **>85% Average Percentage Viewed** (APV). Keep your Hinglish voiceover punchy, zero fluff, and cut scenes every 3-5 seconds.\n"
            "3. **CTR & Thumbnail Hacks**: Use 2-3 word bold text overlay ('100W THIS SMALL?!') + high contrast split lighting (neon blue vs electric amber).\n"
            "4. **Daily Cadence**: Publish Shorts consistently between **8:00 AM – 12:00 PM** daily when audience tech curiosity peaks.\n"
            "5. **SEO & Tag Strategy**: Mix broad tags (#TechShorts, #AI) with specific niche tags (#GaNCharger, #HumanoidRobot) + #TechZenX brand tag.\n\n"
            "Would you like me to write a custom high-retention script or optimize today's titles for maximum CTR?",
            None
        )

    elif "robot" in msg_lower or "robotics" in msg_lower:
        return (
            "🤖 **Robotics Trend Alert**: Humanoid robots powered by embodied AI (like Figure 02, Tesla Optimus Gen 2, and Boston Dynamics Atlas) are transitioning from lab demos to factory floors! They learn complex tasks purely from visual imitation. Would you like a 60-second video script on humanoid AI robots?",
            None
        )

    elif "space" in msg_lower or "astronomy" in msg_lower or "cosmos" in msg_lower:
        return (
            "🌌 **Space & Astronomy Fact**: Did you know James Webb Space Telescope discovered cosmic structures so ancient they shouldn't exist according to standard physics? Plus, NASA's Artemis program is setting up permanent lunar infrastructure using 3D-printed regolith! Want a video breakdown script on this?",
            None
        )

    elif "ai tool" in msg_lower or "tools" in msg_lower:
        return (
            "⚡ **Top Trending AI Tools This Week**:\n1. **Higgsfield / Kling AI**: Next-gen cinematic video generation.\n2. **Claude 3.5 Sonnet / Gemini Flash**: SOTA reasoning and code synthesis.\n3. **Suno v4**: Full studio-grade AI music creation.\n4. **Perplexity Pro**: Real-time AI web research agent.",
            None
        )

    elif "fact" in msg_lower or "amazing" in msg_lower:
        return (
            "💡 **Mind-Blowing Tech Fact**: A single optical fiber cable smaller than a human hair can now transmit over 1.2 Petabits of data per second — enough to download all of Netflix's library in under 1 second! This is powered by multi-wavelength laser modulation.",
            None
        )

    elif "script" in msg_lower or "idea" in msg_lower or "write" in msg_lower:
        return (
            "📝 **Script Idea for TechZenX**:\n**Title**: 3 AI Tools That Will Change How You Work in 2026 🚀\n**Hook**: 'Agar aap abhi bhi traditional tools use kar rahe ho, toh aap 5 saal peeche ho!'\nWould you like me to populate this into the main studio viewer?",
            None
        )

    else:
        return (
            f"💡 **TechZenX AI Assistant**: Regarding '{user_msg}' — Ask me anything about YouTube growth strategies, algorithm hacks, CTR optimization, AI tools, robotics, space, or to customize your video script package!",
            None
        )


def _save_updated_package(pkg: dict) -> None:
    """Save updated package back to the daily output Markdown file."""
    try:
        run_date = pkg.get("date") or get_latest_run_date() or datetime.now().strftime("%Y-%m-%d")
        md_content = render_package_markdown(pkg)
        file_path = config.RUNS_DIR / f"{run_date}.md"
        file_path.write_text(md_content, encoding="utf-8")
        logger.info("Saved updated package to %s", file_path)
    except OSError:
        logger.warning("Could not save package (read-only filesystem)")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting TechZenX Content Studio Web App...")
    logger.info("Open http://localhost:5000 in your browser")
    logger.info("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
