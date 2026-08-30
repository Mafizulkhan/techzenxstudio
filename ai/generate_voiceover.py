"""
Voiceover Generator — TTS-powered Hinglish Audio

Takes the finalized script text and generates voiceover audio using
ElevenLabs (primary) or Google Cloud TTS (fallback).

Usage:
    python -m ai.generate_voiceover
"""

from datetime import datetime, timezone
from pathlib import Path
import requests

import config
from utils import setup_logger

logger = setup_logger("ai.generate_voiceover")

# Default ElevenLabs voice ID (Adam - clear, energetic global voice)
DEFAULT_ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def generate_voiceover(
    script_text: str,
    voice_id: str = DEFAULT_ELEVENLABS_VOICE_ID,
    title: str = "voiceover",
) -> Path | None:
    """
    Generate Hinglish voiceover audio from script text.

    Uses ElevenLabs REST API to synthesize speech from script text using
    the `eleven_multilingual_v2` model (ideal for Hinglish / multilingual audio).

    Args:
        script_text: The full script text to convert to speech.
        voice_id: ElevenLabs voice ID.
        title: Title prefix for saved audio file.

    Returns:
        Path to the generated .mp3 file, or None if generation failed.
    """
    if not script_text.strip():
        logger.warning("Empty script text provided — skipping voiceover generation")
        return None

    if not config.ELEVENLABS_API_KEY:
        logger.error("ELEVENLABS_API_KEY not set in .env — cannot generate voiceover")
        return None

    logger.info("Generating voiceover audio (%d characters)...", len(script_text))

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": config.ELEVENLABS_API_KEY,
        }
        payload = {
            "text": script_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            audio_bytes = response.content
            saved_path = _save_audio(audio_bytes, title=title)
            logger.info("Successfully generated voiceover audio: %s", saved_path)
            return saved_path
        else:
            logger.error(
                "ElevenLabs API HTTP error (%d): %s", response.status_code, response.text
            )
            return None

    except Exception as err:
        logger.exception("Unexpected error generating voiceover: %s", err)
        return None


def _save_audio(audio_bytes: bytes, title: str = "voiceover") -> Path:
    """Save audio bytes to output/audio/<title>_<timestamp>.mp3."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
    safe_title = safe_title.strip().replace(" ", "_")[:50] or "voiceover"
    filepath = config.AUDIO_DIR / f"{safe_title}_{timestamp}.mp3"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(audio_bytes)
    logger.info("Saved voiceover to %s", filepath)
    return filepath


if __name__ == "__main__":
    dummy_text = "Hello, this is a test of the voiceover generator."
    result = generate_voiceover(dummy_text)
    print(f"Voiceover result: {result}")
