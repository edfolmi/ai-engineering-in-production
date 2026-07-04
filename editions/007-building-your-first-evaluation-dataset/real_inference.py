"""Real W&B Inference evaluation demo for Edition 005.

This script evaluates real LLM-generated feedback against the same shared
dataset used by demo.py.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from typing import Any

import weave
from openai import OpenAI, OpenAIError
from weave import Evaluation

from config import LLM_PROMPT_VERSION, require_environment
from dataset import load_dataset
from evaluators import (
    actionability_judge_evaluator,
    configure_judge_client,
    groundedness_judge_evaluator,
    rubric_alignment_evaluator,
    specificity_evaluator,
    trust_judge_evaluator,
)
from llm_utils import response_text, usage_to_dict


LLM_CLIENT: OpenAI | None = None
LLM_MODEL_NAME = ""
LLM_INFERENCE_BASE_URL = ""
ACTIVE_PROMPT_VERSION = LLM_PROMPT_VERSION

LLM_PROMPTS = {
    "v1": {
        "label": "Generic feedback prompt",
        "system": (
            "You are an interview coach. Give helpful feedback on the "
            "candidate's answer."
        ),
        "user_template": (
            "Transcript:\n{transcript}\n\n"
            "Candidate answer:\n{candidate_answer}\n\n"
            "Give short feedback."
        ),
    },
    "v2": {
        "label": "Grounded rubric-aware feedback prompt",
        "system": (
            "You are an interview coach. Give concise feedback on a candidate "
            "answer. Use only evidence from the transcript. Include what "
            "worked, what was missing, and one next step. Do not invent "
            "details."
        ),
        "user_template": (
            "Case ID: {case_id}\n"
            "Rubric dimensions: {rubric_text}\n\n"
            "Transcript:\n{transcript}\n\n"
            "Candidate answer to score:\n{candidate_answer}\n\n"
            "Write the feedback in 3 short bullets. Reference concrete "
            "evidence from the transcript when possible."
        ),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the real W&B Inference Edition 005 evaluation.",
    )
    parser.add_argument(
        "--publish-dataset",
        action="store_true",
        help="Publish the demo dataset as a Weave Dataset before running the evaluation.",
    )
    parser.add_argument(
        "--dataset-ref",
        help=(
            "Use an existing Weave dataset ref instead of the in-memory dataset, "
            "for example weave:///entity/project/object/edition_005_evaluation_dataset:latest."
        ),
    )
    parser.add_argument(
        "--prompt-version",
        choices=sorted(LLM_PROMPTS),
        default=LLM_PROMPT_VERSION,
        help="Prompt version to use for the feedback generator.",
    )
    return parser.parse_args()


def configure_llm_client(config: dict[str, str], prompt_version: str) -> None:
    """Configure the OpenAI-compatible W&B Inference client."""

    global LLM_CLIENT, LLM_MODEL_NAME, LLM_INFERENCE_BASE_URL, ACTIVE_PROMPT_VERSION

    LLM_MODEL_NAME = config["model_name"]
    LLM_INFERENCE_BASE_URL = config["inference_base_url"]
    ACTIVE_PROMPT_VERSION = prompt_version
    LLM_CLIENT = OpenAI(
        base_url=config["inference_base_url"],
        api_key=config["wandb_api_key"],
        project=config["wandb_project"],
    )
    configure_judge_client(LLM_CLIENT, LLM_MODEL_NAME)


@weave.op()
def generate_llm_interview_feedback(
    case_id: str,
    transcript: str,
    candidate_answer: str,
    rubric: list[str],
) -> dict[str, Any]:
    """Call a real LLM through W&B Inference to generate feedback."""

    if LLM_CLIENT is None:
        raise RuntimeError("LLM client is not configured. Use configure_llm_client first.")

    started_at = time.perf_counter()
    rubric_text = ", ".join(rubric)
    prompt = LLM_PROMPTS[ACTIVE_PROMPT_VERSION]

    try:
        response = LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL_NAME,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": prompt["system"],
                },
                {
                    "role": "user",
                    "content": prompt["user_template"].format(
                        case_id=case_id,
                        rubric_text=rubric_text,
                        transcript=transcript,
                        candidate_answer=candidate_answer,
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference feedback call failed. Check WANDB_API_KEY, "
            "WANDB_PROJECT, WANDB_MODEL, and WANDB_INFERENCE_BASE_URL. "
            f"Original error: {exc}"
        ) from exc

    return {
        "case_id": case_id,
        "generator": "llm",
        "feedback": response_text(response),
        "rubric_used": rubric,
        "source_answer": candidate_answer,
        "transcript_excerpt": transcript[:180],
        "prompt_version": ACTIVE_PROMPT_VERSION,
        "prompt_label": prompt["label"],
        "system_prompt": prompt["system"],
        "model_name": LLM_MODEL_NAME,
        "inference_base_url": LLM_INFERENCE_BASE_URL,
        "latency_seconds": round(time.perf_counter() - started_at, 3),
        "token_usage": usage_to_dict(response),
    }


def print_dashboard_story() -> None:
    """Print where to click in Weave after the run completes."""

    print("\nIn W&B Weave:")
    print("1. Open the project from WANDB_PROJECT.")
    print("2. Find the Evaluation.evaluate call named Edition 005 - Real Inference.")
    print("3. Open a predict_and_score child row to inspect one dataset example.")
    print("4. Compare the LLM feedback with scorer results.")
    print("5. Compare prompt_version v1 and v2 evaluation runs.")


def print_summary(
    results: Any,
    prompt_version: str,
) -> None:
    """Print the evaluation result returned by Weave."""

    print("\nAI Engineering In Production - Edition 005 Real Inference")
    print("=" * 64)
    print("Mode: real W&B Inference")
    print("Feedback generator: generate_llm_interview_feedback")
    print(f"Model: {LLM_MODEL_NAME}")
    print(f"Prompt version: {prompt_version} - {LLM_PROMPTS[prompt_version]['label']}")
    print("Semantic scorers: actionability_judge, groundedness_judge, trust_judge")
    print(f"Inference base URL: {LLM_INFERENCE_BASE_URL}")

    print("\nScorers sent to W&B Weave:")
    print("- specificity_evaluator")
    print("- actionability_judge_evaluator")
    print("- groundedness_judge_evaluator")
    print("- rubric_alignment_evaluator")
    print("- trust_judge_evaluator")
    print("\nWeave evaluation result:")
    print(results)
    print_dashboard_story()


async def run_evaluation(
    publish_dataset: bool = False,
    dataset_ref: str | None = None,
    prompt_version = LLM_PROMPT_VERSION,
) -> Any:
    dataset = load_dataset(dataset_ref=dataset_ref, should_publish_dataset=publish_dataset)

    evaluation = Evaluation(
        dataset=dataset,
        scorers=[
            specificity_evaluator,
            actionability_judge_evaluator,
            groundedness_judge_evaluator,
            rubric_alignment_evaluator,
            trust_judge_evaluator,
        ],
        evaluation_name=(
            "edition-007-real-inference-"
            f"prompt-{prompt_version}-semantic-judges"
        ),
    )

    return await evaluation.evaluate(
        generate_llm_interview_feedback,
        __weave={
            "display_name": (
                "Edition 007 - Real Inference "
                f"(prompt {prompt_version}, semantic judges)"
            )
        },
    )


def main() -> int:
    args = parse_args()

    print(f"args: {args}")
    print(f"publish_dataset type: {type(args.publish_dataset)}")

    print(f"publish_dataset: {args.publish_dataset}")
    print(f"dataset_ref: {args.dataset_ref}")
    print(f"prompt_version: {args.prompt_version}")

    try:
        config = require_environment()
        weave.init(config["wandb_project"])
        configure_llm_client(config, prompt_version=args.prompt_version)
        results = asyncio.run(
            run_evaluation(
                publish_dataset=args.publish_dataset,
                dataset_ref=args.dataset_ref,
                prompt_version=args.prompt_version,
            )
        )
    except RuntimeError as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Demo error: {exc}", file=sys.stderr)
        return 1

    print_summary(
        results,
        prompt_version=args.prompt_version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
