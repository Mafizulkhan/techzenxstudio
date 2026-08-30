"""
Package Parser & Markdown Renderer — TechZenX Content Package

Parses Markdown content packages (output/runs/YYYY-MM-DD.md) into structured dicts
for the web UI, and renders updated dicts back into Markdown format.
"""

import re


def parse_markdown_package(md_text: str) -> dict:
    """Parse a Markdown content package into a structured dictionary."""
    pkg = {
        "title": "",
        "overview": {
            "target_duration": "45-60 Seconds",
            "format": "Vertical 9:16",
            "visual_style": "",
            "bgm": "",
        },
        "scenes": [],
        "metadata": {
            "best_title": "",
            "alt_titles": [],
            "description": "",
            "tags": [],
        },
        "thumbnail": {
            "prompt": "",
            "text_overlay": "",
        },
        "raw_markdown": md_text,
    }

    # Extract Main Title
    title_match = re.search(r"^#\s+(?:\[Video Overview\]\s*)?(.*?)$", md_text, re.MULTILINE)
    if title_match:
        pkg["title"] = title_match.group(1).strip()

    # Extract Video Overview fields
    dur_match = re.search(r"-\s*Target Duration:\s*(.*?)$", md_text, re.MULTILINE | re.IGNORECASE)
    if dur_match:
        pkg["overview"]["target_duration"] = dur_match.group(1).strip()

    fmt_match = re.search(r"-\s*Format:\s*(.*?)$", md_text, re.MULTILINE | re.IGNORECASE)
    if fmt_match:
        pkg["overview"]["format"] = fmt_match.group(1).strip()

    style_match = re.search(r"-\s*Visual Style:\s*(.*?)$", md_text, re.MULTILINE | re.IGNORECASE)
    if style_match:
        pkg["overview"]["visual_style"] = style_match.group(1).strip()

    bgm_match = re.search(r"-\s*BGM:\s*(.*?)$", md_text, re.MULTILINE | re.IGNORECASE)
    if bgm_match:
        pkg["overview"]["bgm"] = bgm_match.group(1).strip()

    # Extract Scenes
    scene_blocks = re.findall(
        r"###\s+Scene\s+(\d+):\s*(.*?)\s*\((.*?)\)\s*\n([\s\S]*?)(?=###\s+Scene|##\s+|$)",
        md_text,
    )

    for num_str, name, timestamp, body in scene_blocks:
        camera = _extract_field(body, r"\*\*Camera Angle & Motion:\*\*\s*(.*?)$")
        sfx = _extract_field(body, r"\*\*SFX:\*\*\s*(.*?)$")
        flow_prompt = _extract_field(body, r"\*\*Google Flow Prompt:\*\*\s*(.*?)$")
        voiceover = _extract_field(body, r"\*\*Voiceover \(Hinglish\):\*\*\s*\"?(.*?)\"?$")

        pkg["scenes"].append(
            {
                "number": int(num_str),
                "name": name.strip(),
                "timestamp": timestamp.strip(),
                "camera_angle": camera,
                "sfx": sfx,
                "flow_prompt": flow_prompt,
                "voiceover": voiceover,
            }
        )

    # Extract Metadata
    best_t = _extract_field(md_text, r"\*\*Best YouTube Shorts Title:\*\*\s*(.*?)$")
    pkg["metadata"]["best_title"] = best_t or pkg["title"]

    alt_block = re.search(r"\*\*Alternative Titles:\*\*\s*\n([\s\S]*?)(?=\*\*YouTube Shorts Description:|\*\*Targeted Tags:|$)", md_text)
    if alt_block:
        alts = re.findall(r"^\d+\.\s*(.*?)$", alt_block.group(1), re.MULTILINE)
        pkg["metadata"]["alt_titles"] = [a.strip() for a in alts]

    desc = _extract_field(md_text, r"\*\*YouTube Shorts Description:\*\*\s*([\s\S]*?)(?=\*\*Targeted Tags:|##\s+|$)")
    pkg["metadata"]["description"] = desc.strip()

    tags_str = _extract_field(md_text, r"\*\*Targeted Tags:\*\*\s*(.*?)$")
    if tags_str:
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        pkg["metadata"]["tags"] = tags

    # Extract Thumbnail
    thumb_prompt = _extract_field(md_text, r"\*\*Thumbnail Prompt:\*\*\s*(.*?)$")
    text_overlay = _extract_field(md_text, r"\*\*Text Overlay Concept:\*\*\s*(.*?)$")
    pkg["thumbnail"]["prompt"] = thumb_prompt
    pkg["thumbnail"]["text_overlay"] = text_overlay

    return pkg


def render_package_markdown(pkg: dict) -> str:
    """Render a structured package dictionary into standard Markdown format."""
    title = pkg.get("title", "Untitled Video Package")
    overview = pkg.get("overview", {})
    metadata = pkg.get("metadata", {})
    thumbnail = pkg.get("thumbnail", {})
    scenes = pkg.get("scenes", [])

    lines = [
        f"# [Video Overview] {title}",
        "",
        "## Video Overview",
        f"- Target Duration: {overview.get('target_duration', '~45-60 Seconds')}",
        f"- Format: {overview.get('format', 'Vertical 9:16 (YouTube Shorts / Instagram Reels)')}",
        f"- Visual Style: {overview.get('visual_style', 'Cinematic, dynamic push-in')}",
        f"- BGM: {overview.get('bgm', 'Fast-paced dark synthwave')}",
        "",
        "## Scene-by-Scene Script & Video Generation Prompts",
        "",
    ]

    for sc in scenes:
        lines.append(f"### Scene {sc.get('number', 1)}: {sc.get('name', 'Scene')} ({sc.get('timestamp', '0:00 - 0:10')})")
        lines.append(f"**Camera Angle & Motion:** {sc.get('camera_angle', 'Dynamic push-in')}")
        lines.append(f"**SFX:** {sc.get('sfx', 'Whoosh SFX')}")
        lines.append(f"**Google Flow Prompt:** {sc.get('flow_prompt', '')}")
        lines.append(f'**Voiceover (Hinglish):** "{sc.get("voiceover", "")}"')
        lines.append("")

    lines.extend([
        "## Best Title, Description & Tags",
        f"**Best YouTube Shorts Title:** {metadata.get('best_title', title)}",
        "**Alternative Titles:**",
    ])

    for idx, alt in enumerate(metadata.get("alt_titles", []), 1):
        lines.append(f"{idx}. {alt}")

    lines.extend([
        f"**YouTube Shorts Description:** {metadata.get('description', '')}",
        f"**Targeted Tags:** {', '.join(metadata.get('tags', []))}",
        "",
        "## Thumbnail Prompt (For Google Flow / Midjourney / DALL-E)",
        f"**Thumbnail Prompt:** {thumbnail.get('prompt', '')}",
        f"**Text Overlay Concept:** {thumbnail.get('text_overlay', '')}",
        "",
    ])

    return "\n".join(lines)


def _extract_field(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""
