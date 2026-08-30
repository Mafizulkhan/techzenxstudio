"""
YouTube AI Content Automation — Daily Pipeline Orchestrator (TechZenX)

Runs the complete daily automation chain:
  1. Fetch trending topics (YouTube, Reddit, RSS)
  2. Score and rank topics → select top 2-3 candidate topics
  3. Draft full content package (Markdown) for top 2-3 candidates
  4. Run viral scoring to select the single winning package
  5. Output final package to output/runs/YYYY-MM-DD.md for morning review

Usage:
    python run_pipeline.py [--demo]
"""

import sys
from datetime import datetime
from pathlib import Path

import config
from utils import setup_logger, ensure_output_dirs, get_run_dir, save_json

logger = setup_logger("pipeline")


def run_pipeline(demo_mode: bool = False):
    """Execute the full TechZenX YouTube content automation pipeline."""
    start_time = datetime.now()
    today_str = start_time.strftime("%Y-%m-%d")
    logger.info("=" * 60)
    logger.info("TECHZENX YOUTUBE AUTOMATION PIPELINE — STARTING%s", " (DEMO MODE)" if demo_mode else "")
    logger.info("=" * 60)

    # Ensure output directories exist
    ensure_output_dirs()
    candidates_dir = config.OUTPUT_DIR / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Fetch Trends ─────────────────────────────────────
    logger.info("-" * 40)
    logger.info("Step 1/5: Fetching trending tech topics...")
    logger.info("-" * 40)

    from fetchers.youtube import fetch_youtube_trends
    from fetchers.reddit import fetch_reddit_trends
    from fetchers.rss import fetch_rss_trends

    youtube_trends = fetch_youtube_trends()
    reddit_trends = fetch_reddit_trends()
    rss_trends = fetch_rss_trends()

    total_trends = len(youtube_trends) + len(reddit_trends) + len(rss_trends)
    logger.info("Fetched %d total trends (YT: %d, Reddit: %d, RSS: %d)",
                total_trends, len(youtube_trends), len(reddit_trends), len(rss_trends))

    # ── Step 2: Score & Pick Top 2-3 Candidates ─────────────────
    logger.info("-" * 40)
    logger.info("Step 2/5: Scoring and ranking trend topics...")
    logger.info("-" * 40)

    from fetchers.score import score_and_rank_trends

    top_candidates = score_and_rank_trends(top_n=3)
    if not top_candidates:
        logger.warning("No candidates scored — pipeline cannot continue")
        return

    logger.info("Selected top %d candidate topics for package drafting:", len(top_candidates))
    for idx, c in enumerate(top_candidates):
        logger.info("  Candidate %d: '%s' (Score: %.2f)", idx + 1, c.get("title"), c.get("score", 0.0))

    # ── Step 3: Draft Full Packages for Candidates ──────────────
    logger.info("-" * 40)
    logger.info("Step 3/5: Drafting 2-3 full candidate content packages...")
    logger.info("-" * 40)

    from ai.generate_package import generate_package

    candidate_packages = []
    for idx, candidate in enumerate(top_candidates):
        topic_title = candidate.get("title", f"Topic_{idx}")
        logger.info("Drafting package %d/%d for '%s'...", idx + 1, len(top_candidates), topic_title)

        pkg_md = generate_package(candidate)
        if not pkg_md and demo_mode:
            logger.info("[DEMO MODE] Generating sample Markdown package for simulation...")
            pkg_md = _create_demo_package_markdown(candidate)

        if pkg_md:
            candidate_packages.append(pkg_md)
            # Save candidate package to output/candidates/
            slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in topic_title[:30]).strip("_")
            cand_path = candidates_dir / f"{today_str}_candidate_{idx+1}_{slug}.md"
            cand_path.write_text(pkg_md, encoding="utf-8")
            logger.info("Saved candidate package -> %s", cand_path)

    if not candidate_packages:
        logger.error("Failed to generate any candidate packages — pipeline stopping")
        return

    # ── Step 4: Viral Scoring & Winner Selection ─────────────────
    logger.info("-" * 40)
    logger.info("Step 4/5: Running viral scoring on candidates...")
    logger.info("-" * 40)

    from ai.score_candidates import score_candidates

    winning_idx, scoring_info = score_candidates(candidate_packages)
    winning_package = candidate_packages[winning_idx]
    winning_topic = top_candidates[winning_idx].get("title", "Selected Candidate")

    logger.info("WINNER SELECTED: Candidate %d ('%s')", winning_idx + 1, winning_topic)
    if scoring_info and scoring_info.get("winning_reason"):
        logger.info("Winning Reason: %s", scoring_info["winning_reason"])

    # ── Step 5: Save Daily Package to output/runs/YYYY-MM-DD.md ──
    logger.info("-" * 40)
    logger.info("Step 5/5: Outputting final package to output/runs/%s.md...", today_str)
    logger.info("-" * 40)

    final_run_file = config.RUNS_DIR / f"{today_str}.md"
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    final_run_file.write_text(winning_package, encoding="utf-8")

    # Also save run summary JSON
    summary_path = config.RUNS_DIR / f"{today_str}_summary.json"
    summary_data = {
        "date": today_str,
        "status": "completed",
        "winning_candidate_index": winning_idx,
        "winning_topic": winning_topic,
        "total_candidates_drafted": len(candidate_packages),
        "viral_scoring": scoring_info,
        "output_file": str(final_run_file),
        "duration_seconds": (datetime.now() - start_time).total_seconds(),
    }
    save_json(summary_data, summary_path)

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE — Today's Package Ready: %s", final_run_file)
    logger.info("Duration: %s", datetime.now() - start_time)
    logger.info("=" * 60)


def _create_demo_package_markdown(candidate: dict) -> str:
    title = candidate.get("title", "Tech Innovation 2026")
    return f"""# [Video Overview] The Truth About {title}

## Video Overview
- Target Duration: ~45-60 Seconds
- Format: Vertical 9:16 (YouTube Shorts / Instagram Reels)
- Visual Style: Photorealistic product macro, dual-neon thermal contrast, 3D molecular lattice, IMAX 70mm lens, Unreal Engine 5.4 render
- BGM: Fast-paced dark synthwave pulse beat with explosive sub-bass drops on transitions

## Scene-by-Scene Script & Video Generation Prompts

### Scene 1: Hook & The Shrinking Charger (0:00 - 0:08)
**Camera Angle & Motion:** High-angle macro shot, fast dynamic 35mm push-in comparing a giant old laptop charging brick side-by-side with a tiny 100W GaN charger with motion blur.
**SFX:** Electric surge ZAP! + heavy glass bass drop.
**Google Flow Prompt:** Vertical 9:16, 8k resolution, photorealistic IMAX 70mm cinematic comparison shot. On the left, a giant black bulky vintage laptop power brick with warning heat waves. On the right, a ultra-sleek white phone-sized 100W GaN charger emitting intense electric blue plasma sparks from its prongs. Dual neon cyan and hyper-amber rim lighting, volumetric fog, dramatic fast camera push-in zoom with motion blur, 4k studio photography.
**Voiceover (Hinglish):** "Itna chhota sa charger aapke laptop aur phone ko bina over-heat hue 100 Watt ki super-fast speed se kaise charge kar deta hai? Subscribe TechZenX and learn about it! Aao iski Gallium Nitride chemistry dekhte hain!"

### Scene 2: Inside the GaN Crystal — Atomic Level (0:08 - 0:20)
**Camera Angle & Motion:** Smooth 3D orbital tracking shot diving inside the GaN microchip, camera spiraling through a glowing atomic lattice structure.
**SFX:** Deep sub-bass hum + crystalline shimmer resonance.
**Google Flow Prompt:** Vertical 9:16, 8k resolution, hyper-detailed 3D render of a Gallium Nitride crystal lattice at atomic scale. Glowing electric blue-white hexagonal molecular bonds, translucent crystalline semiconductor layers, volumetric light beams slicing through the lattice, 35mm anamorphic lens flare, sharp focal depth, smooth orbital camera movement, dark space background with floating energy particles, Unreal Engine 5.4 quality.
**Voiceover (Hinglish):** "Yeh hai Gallium Nitride — ek aisa semiconductor crystal jiska bandgap silicon se 3 guna zyada hai. Iska matlab? Electrons itni speed se switch karte hain ki energy waste hona almost impossible ho jata hai!"

### Scene 3: Silicon vs GaN — The Heat Battle (0:20 - 0:35)
**Camera Angle & Motion:** Split-screen thermal camera comparison shot, camera slowly panning left to right across both chargers under maximum load.
**SFX:** Intense electrical buzzing on silicon side + calm cool digital chime on GaN side.
**Google Flow Prompt:** Vertical 9:16, 8k photorealistic split-screen thermal imaging view. Left half shows a traditional silicon charger glowing intense fiery red-orange on thermal camera (75°C+), heat ripples rising. Right half shows a GaN charger staying cool emerald-blue on thermal camera (35°C), ultra-compact. Glowing digital telemetry readout showing live temp comparison, sleek dark studio desk background, cinematic rim lighting.
**Voiceover (Hinglish):** "Dekho silicon charger kitna garam ho raha hai — 75 degrees! Aur GaN? Bilkul cool at 35 degrees. Kyunki GaN mein energy heat mein waste nahi hoti, directly power delivery mein jaati hai. Yeh hai real efficiency!"

### Scene 4: The 100W Speed Test — Live Charging Race (0:35 - 0:48)
**Camera Angle & Motion:** Dynamic low-angle tracking shot, speed-ramp dolly zoom between two smartphones charging side-by-side, battery percentage counters racing upward.
**SFX:** Racing countdown timer beeps + power surge whoosh on each 10% jump.
**Google Flow Prompt:** Vertical 9:16, 8k resolution, cinematic low-angle action shot of two flagship smartphones side by side on a reflective black glass desk. Left phone on regular 20W charger with slow battery counter at 15%. Right phone on 100W GaN charger with battery counter blazing upward 40%... 60%... 80% with glowing green lightning beam animations flowing through cable. 120fps motion blur, dramatic dual neon backlight.
**Voiceover (Hinglish):** "20 Watt charger abhi 15% par hai aur GaN charger ne already 80% cross kar liya! Bhai yeh speed real hai — 0 se 100 sirf 25 minutes mein. Game over for slow charging!"

### Scene 5: Outro & Call to Action — Future of Charging (0:48 - 0:58)
**Camera Angle & Motion:** Static medium studio shot with animated TechZenX subscribe graphics floating in, camera slowly pulling back to reveal the tiny GaN charger powering a laptop, phone, and tablet simultaneously.
**SFX:** Upbeat synth resolution + satisfying click + notification bell SFX.
**Google Flow Prompt:** Vertical 9:16, premium studio product shot of one tiny white GaN charger with three braided cables running out — simultaneously charging a MacBook Pro, iPhone 16, and iPad Pro. Glowing neon 3D subscribe button animation overlaid, TechZenX branding, dark premium background with soft blue ambient lighting.
**Voiceover (Hinglish):** "Ek charger — teen devices — zero overheating. GaN technology future nahi hai bhai, yeh already present hai! Agar aapko yeh video pasand aayi toh subscribe karo TechZenX ko aur bell icon dabao — daily aisi tech reveals milegi!"

## Best Title, Description & Tags
**Best YouTube Shorts Title:** This TINY Charger Has 100W POWER! 🔌🔥
**Alternative Titles:**
1. How Does a Charger THIS Small Charge SO Fast? ⚡😱
2. GaN vs Silicon: The Charging Revolution EXPLAINED 🧪🔋
3. 100W in Your Pocket — The Science Behind GaN Chargers 🚀
**YouTube Shorts Description:** How does a charger smaller than your palm deliver 100 Watts of power without overheating? The secret is Gallium Nitride (GaN) — a crystal semiconductor that's 3x more efficient than silicon!\n\nSubscribe to TechZenX for daily mind-blowing tech & science reveals! 🔔\n\n#TechZenX #GaNCharger #TechShorts #FutureTech #Shorts
**Targeted Tags:** #TechZenX, #GaN, #GalliumNitride, #FastCharging, #100W, #TechShorts, #ChargingTech, #GaNCharger, #FutureTech, #Shorts, #ScienceFacts, #TechExplained, #HinglishTech, #Innovation, #Gadgets

## Thumbnail Prompt (For Google Flow / Midjourney / DALL-E)
**Thumbnail Prompt:** Vertical 9:16, 8k resolution, ultra high-contrast dramatic split-screen thumbnail. Left half: giant ugly black laptop charger glowing with red warning heat aura and 75°C badge. Right half: tiny sleek white GaN charger glowing with electric blue plasma lightning bolts and 100W badge. Bold neon yellow arrow pointing from big to small. Photorealistic product photography, octane render, dramatic studio rim lighting, 35mm lens.
**Text Overlay Concept:** 100W THIS SMALL?!
"""


if __name__ == "__main__":
    try:
        is_demo = "--demo" in sys.argv or "-d" in sys.argv
        if not is_demo and not config.ANTHROPIC_API_KEY:
            logger.info("ANTHROPIC_API_KEY not found in .env — enabling Demo/Simulation mode automatically")
            is_demo = True

        run_pipeline(demo_mode=is_demo)
    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Pipeline failed with error: %s", e)
        sys.exit(1)
