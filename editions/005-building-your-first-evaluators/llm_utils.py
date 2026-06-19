"""Small helpers for LLM responses and evaluator scoring."""

from __future__ import annotations

import json
from typing import Any


def response_text(response: Any) -> str:
    """Read text from an OpenAI-compatible chat completion result."""

    choices = getattr(response, "choices", []) or []
    if choices:
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if content:
            return content.strip()

    return ""


def usage_to_dict(response: Any) -> dict[str, int | None]:
    """Convert token usage metadata to a small trace-friendly dictionary."""

    usage = getattr(response, "usage", None)
    if usage is None:
        return {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from an LLM response."""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    return json.loads(cleaned)


def count_phrase_matches(text: str, phrases: list[str]) -> list[str]:
    """Find expected phrases that appear in an output."""

    lower_text = text.lower()
    return [phrase for phrase in phrases if phrase.lower() in lower_text]


def clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 2)
