"""Turn a Bengali voice recording into casual Banglish text.

One call to Google's Gemini model: it listens to the audio and writes
what was said in Banglish (Bengali words in English letters).
"""

import os
from pathlib import Path

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PROMPT_FILE = Path(__file__).parent / "prompts" / "banglish_style.md"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        _client = genai.Client(api_key=api_key)
    return _client


def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def clean_output(text: str) -> str:
    """Remove quotes, labels or extra blank lines the model sometimes adds."""
    text = (text or "").strip()
    for label in ("Banglish:", "Output:", "Text:"):
        if text.lower().startswith(label.lower()):
            text = text[len(label):].strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'`":
        text = text[1:-1].strip()
    return "\n".join(line.rstrip() for line in text.splitlines() if line.strip())


def voice_to_banglish(audio: bytes, mime_type: str = "audio/ogg") -> str:
    """Send the audio to Gemini and return the Banglish text."""
    response = _get_client().models.generate_content(
        model=MODEL,
        contents=[
            load_prompt(),
            types.Part.from_bytes(data=audio, mime_type=mime_type),
        ],
    )
    return clean_output(response.text)
