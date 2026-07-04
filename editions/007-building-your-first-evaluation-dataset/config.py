"""Shared configuration helpers for Edition 005."""

from __future__ import annotations

import os

from dotenv import load_dotenv


WANDB_INFERENCE_BASE_URL = "https://api.inference.wandb.ai/v1"
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
DEMO_PROMPT_VERSION = "demo-fixed-feedback-v1"
LLM_PROMPT_VERSION = "v2"
PLACEHOLDER_VALUES = {
    "your_wandb_api_key",
    "your-team/ai-engineering-in-production",
    "your_wandb_project",
}


def require_environment() -> dict[str, str]:
    """Validate the W&B settings needed by Weave and W&B Inference."""

    load_dotenv()

    wandb_api_key = os.getenv("WANDB_API_KEY", "").strip()
    wandb_project = os.getenv("WANDB_PROJECT", "").strip()

    if not wandb_api_key:
        raise RuntimeError(
            "Missing WANDB_API_KEY. Copy .env.example to .env and add your W&B API key."
        )

    if wandb_api_key in PLACEHOLDER_VALUES:
        raise RuntimeError(
            "WANDB_API_KEY still has the placeholder value from .env.example."
        )

    if (
        not wandb_project
        or wandb_project in PLACEHOLDER_VALUES
        or "/" not in wandb_project
    ):
        raise RuntimeError(
            "WANDB_PROJECT must use entity/project format, for example "
            "edfolmi-andela/ai-engineering-in-production."
        )

    return {
        "wandb_api_key": wandb_api_key,
        "wandb_project": wandb_project,
        "model_name": os.getenv("WANDB_MODEL", DEFAULT_MODEL),
        "inference_base_url": os.getenv(
            "WANDB_INFERENCE_BASE_URL",
            WANDB_INFERENCE_BASE_URL,
        ),
    }
