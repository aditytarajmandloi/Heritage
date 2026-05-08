"""
Audio Service — Phase 3.4

Converts text to speech using Google Text-to-Speech (gTTS).
Generates .mp3 files saved in the static/audio/ directory.
"""

import os
import uuid
from pathlib import Path

from gtts import gTTS


class AudioService:
    """Handles text-to-speech conversion via gTTS."""

    def __init__(self, output_dir: str):
        """Initialize with the output directory for audio files."""
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"   [Audio] Output directory: {self.output_dir}")

    def generate_speech(self, text: str, filename: str = None) -> str:
        """
        Convert text to an .mp3 audio file.

        Args:
            text: The text to convert to speech
            filename: Optional custom filename (without extension)

        Returns:
            The relative URL path to the audio file (e.g., "/static/audio/resp_abc123.mp3")
        """
        if not text or not text.strip():
            return ""

        try:
            # Generate unique filename if not provided
            if not filename:
                filename = f"resp_{uuid.uuid4().hex[:10]}"

            filepath = self.output_dir / f"{filename}.mp3"

            # Use Indian English accent for authenticity
            tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
            tts.save(str(filepath))

            # Return the URL path (relative to static mount)
            return f"/static/audio/{filename}.mp3"

        except Exception as e:
            print(f"   [Audio] gTTS error: {e}")
            return ""

    def cleanup_old_files(self, keep_latest: int = 50):
        """Remove old audio files, keeping only the most recent ones."""
        audio_files = sorted(
            self.output_dir.glob("resp_*.mp3"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        for old_file in audio_files[keep_latest:]:
            try:
                old_file.unlink()
            except OSError:
                pass
