"""Minimal Weave tracing demo for an AI interview simulation.

This script is intentionally small enough to explain in a few minutes:
run it, inspect the terminal output, then open W&B Weave and inspect the trace.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Any

import weave
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


PROMPT_VERSION = "interview-demo-v1"
WANDB_INFERENCE_BASE_URL = "https://api.inference.wandb.ai/v1"
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
ESTIMATED_COST_PLACEHOLDER = "not_calculated_in_demo"
PLACEHOLDER_VALUES = {
    "your_wandb_api_key",
    "your-team/ai-engineering-in-production",
    "your_wandb_project",
}


@dataclass(frozen=True)
class InterviewScenario:
    """Business context that makes the trace useful later."""

    session_id: str
    scenario_id: str
    persona: str
    role: str
    competency: str
    question: str


def require_environment() -> dict[str, str]:
    """Validate the environment variables the demo needs before doing work."""

    load_dotenv()

    required = ["WANDB_API_KEY", "WANDB_PROJECT"]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )

    wandb_api_key = os.environ["WANDB_API_KEY"].strip()
    wandb_project = os.environ["WANDB_PROJECT"].strip()

    if wandb_api_key in PLACEHOLDER_VALUES:
        raise RuntimeError(
            "WANDB_API_KEY still has the placeholder value from .env.example. "
            "Replace it with your real W&B API key from https://wandb.ai/authorize."
        )

    if wandb_project in PLACEHOLDER_VALUES or "/" not in wandb_project:
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


def init_weave(project_name: str) -> None:
    """Initialize Weave so decorated functions are sent to W&B."""

    try:
        weave.init(project_name)
    except Exception as exc:  # Weave can raise different auth/network errors.
        raise RuntimeError(
            "Could not initialize W&B Weave. Check WANDB_API_KEY and "
            f"WANDB_PROJECT. Original error: {exc}"
        ) from exc


def response_text(response: Any) -> str:
    """Read text from the OpenAI-compatible chat completion result."""

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


@weave.op()
def generate_interviewer_response(
    client: OpenAI,
    scenario: InterviewScenario,
    user_answer: str,
    model_name: str,
) -> dict[str, Any]:
    """Generate a follow-up question and trace the LLM call inputs/outputs."""

    started_at = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise technical interviewer. Ask exactly "
                        "one practical follow-up question based on the "
                        "candidate's answer."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Role: {scenario.role}\n"
                        f"Competency: {scenario.competency}\n"
                        f"Original interview question: {scenario.question}\n"
                        f"Candidate answer: {user_answer}"
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference interviewer call failed. Check that WANDB_API_KEY "
            "contains your W&B API key and WANDB_PROJECT uses "
            f"entity/project format. Original error: {exc}"
        ) from exc

    latency = round(time.perf_counter() - started_at, 3)

    return {
        "interviewer_response": response_text(response),
        "latency": latency,
        "token_usage": usage_to_dict(response),
        "model_name": model_name,
        "estimated_cost_usd": ESTIMATED_COST_PLACEHOLDER,
    }


@weave.op()
def generate_feedback(
    client: OpenAI,
    scenario: InterviewScenario,
    user_answer: str,
    interviewer_response: str,
    model_name: str,
) -> dict[str, Any]:
    """Generate feedback and trace the evidence used to create it."""

    started_at = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an interview coach. Give short, specific "
                        "feedback in three bullets: what worked, what was "
                        "missing, and how to improve."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Role: {scenario.role}\n"
                        f"Competency: {scenario.competency}\n"
                        f"Interview question: {scenario.question}\n"
                        f"Candidate answer: {user_answer}\n"
                        f"Interviewer follow-up: {interviewer_response}"
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference feedback call failed. Check that WANDB_API_KEY "
            "contains your W&B API key and WANDB_PROJECT uses "
            f"entity/project format. Original error: {exc}"
        ) from exc

    latency = round(time.perf_counter() - started_at, 3)

    return {
        "feedback": response_text(response),
        "latency": latency,
        "token_usage": usage_to_dict(response),
        "model_name": model_name,
        "estimated_cost_usd": ESTIMATED_COST_PLACEHOLDER,
    }


@weave.op()
def run_interview_simulation(
    client: OpenAI,
    scenario: InterviewScenario,
    user_answer: str,
    model_name: str,
) -> dict[str, Any]:
    """Run one interview turn.

    This is the main trace for the demo. It records business context
    alongside model inputs, model outputs, latency, token usage, and a cost
    placeholder. That context is what makes later debugging and evaluation
    possible.
    """

    started_at = time.perf_counter()

    interviewer_result = generate_interviewer_response(
        client=client,
        scenario=scenario,
        user_answer=user_answer,
        model_name=model_name,
    )

    feedback_result = generate_feedback(
        client=client,
        scenario=scenario,
        user_answer=user_answer,
        interviewer_response=interviewer_result["interviewer_response"],
        model_name=model_name,
    )

    total_latency = round(time.perf_counter() - started_at, 3)

    # These fields are deliberately explicit so they are easy to find in Weave.
    return {
        "session_id": scenario.session_id,
        "scenario_id": scenario.scenario_id,
        "persona": scenario.persona,
        "prompt_version": PROMPT_VERSION,
        "model_name": model_name,
        "user_answer": user_answer,
        "interviewer_response": interviewer_result["interviewer_response"],
        "feedback": feedback_result["feedback"],
        "latency": {
            "total_seconds": total_latency,
            "interviewer_seconds": interviewer_result["latency"],
            "feedback_seconds": feedback_result["latency"],
        },
        "token_usage": {
            "interviewer": interviewer_result["token_usage"],
            "feedback": feedback_result["token_usage"],
        },
        "estimated_cost_usd": ESTIMATED_COST_PLACEHOLDER,
    }


def print_result(scenario: InterviewScenario, result: dict[str, Any]) -> None:
    """Print a simple terminal view for the newsletter/Loom demo."""

    print("\nAI Engineering In Production - Edition 004 Demo")
    print("=" * 56)
    print(f"Session ID: {result['session_id']}")
    print(f"Scenario ID: {result['scenario_id']}")
    print(f"Persona: {result['persona']}")
    print(f"Prompt version: {result['prompt_version']}")
    print(f"Model: {result['model_name']}")
    print("\nInterview Question:")
    print(scenario.question)
    print("\nCandidate Answer:")
    print(result["user_answer"])
    print("\nInterviewer Follow-up:")
    print(result["interviewer_response"])
    print("\nFeedback:")
    print(result["feedback"])
    print("\nTrace Metadata:")
    print(f"Latency: {result['latency']}")
    print(f"Token usage: {result['token_usage']}")
    print(f"Estimated cost USD: {result['estimated_cost_usd']}")
    print("\nOpen W&B Weave and inspect the run_interview_simulation trace.")


def main() -> int:
    try:
        config = require_environment()
        init_weave(config["wandb_project"])
    except RuntimeError as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 1

    # W&B Inference is OpenAI-compatible, so the OpenAI SDK can call it.
    # The OpenAI SDK parameter is named api_key, but the value is your W&B key.
    client = OpenAI(
        base_url=config["inference_base_url"],
        api_key=config["wandb_api_key"],
        project=config["wandb_project"],
    )

    scenario = InterviewScenario(
        session_id="session-004-demo-001",
        scenario_id="backend-reliability-001",
        persona="early-career backend engineer",
        role="Backend Engineer",
        competency="debugging production incidents",
        question=(
            "Tell me about a time you debugged a production issue. "
            "What signals did you inspect first?"
        ),
    )

    candidate_answer = (
        "I started by checking the error logs and recent deploys. I noticed "
        "timeouts increased after a config change, so I rolled it back and "
        "then added a dashboard for that dependency."
    )

    try:
        result = run_interview_simulation(
            client=client,
            scenario=scenario,
            user_answer=candidate_answer,
            model_name=config["model_name"],
        )
    except RuntimeError as exc:
        print(f"Demo error: {exc}", file=sys.stderr)
        return 1

    print_result(scenario, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
