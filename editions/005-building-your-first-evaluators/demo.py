"""Controlled Weave evaluation demo for building your first evaluators.

This script uses deterministic feedback so the video can focus on evaluator
mechanics without model randomness.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any

import weave
from weave import Evaluation

from config import DEMO_PROMPT_VERSION, require_environment
from dataset import load_dataset, print_dataset_story
from evaluators import (
    actionability_rule_evaluator,
    groundedness_rule_evaluator,
    rubric_alignment_evaluator,
    specificity_evaluator,
    trust_rule_evaluator,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the controlled Edition 005 evaluator demo.",
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
    return parser.parse_args()


@weave.op()
def generate_demo_interview_feedback(
    case_id: str,
    transcript: str,
    candidate_answer: str,
    rubric: list[str],
) -> dict[str, Any]:
    """Return deterministic feedback for explaining evaluator mechanics."""

    if case_id == "strong-feedback-001":
        feedback = (
            "Strong answer: you checked logs, compared the timeout spike against "
            "the last deploy, identified the config change, rolled it back, and "
            "added a dashboard. To improve, explain the user impact and describe "
            "which monitoring alert you would add next."
        )
    elif case_id == "vague-feedback-001":
        feedback = (
            "Good answer overall. You communicated well, but you should improve "
            "clarity and be more structured next time."
        )
    else:
        feedback = (
            "You showed ownership, but the answer missed database sharding, cache "
            "eviction, and incident command handoff. Next time, explain how you "
            "would define alert thresholds and connect reliability metrics to "
            "user impact."
        )

    return {
        "case_id": case_id,
        "generator": "demo",
        "feedback": feedback,
        "rubric_used": rubric,
        "source_answer": candidate_answer,
        "transcript_excerpt": transcript[:180],
        "prompt_version": DEMO_PROMPT_VERSION,
    }


def print_dashboard_story() -> None:
    """Print where to click in Weave after the run completes."""

    print("\nIn W&B Weave:")
    print("1. Open the project from WANDB_PROJECT.")
    print("2. Find the Evaluation.evaluate call named Edition 005 - Demo Evaluators.")
    print("3. Open a predict_and_score child row to inspect one dataset example.")
    print("4. Compare the deterministic feedback with scorer results.")
    print("5. Click scorer calls to show score, reason, and evidence.")


def print_summary(results: Any) -> None:
    """Print the evaluation result returned by Weave."""

    print("\nAI Engineering In Production - Edition 005 Demo")
    print("=" * 56)
    print("Mode: controlled demo")
    print("Feedback generator: generate_demo_interview_feedback")
    print("Actionability scorer: actionability_rule_evaluator")
    print_dataset_story()
    print("\nScorers sent to W&B Weave:")
    print("- specificity_evaluator")
    print("- actionability_rule_evaluator")
    print("- groundedness_rule_evaluator")
    print("- rubric_alignment_evaluator")
    print("- trust_rule_evaluator")
    print("\nWeave evaluation result:")
    print(results)
    print_dashboard_story()


async def run_demo(
    publish_dataset: bool = False,
    dataset_ref: str | None = None,
) -> Any:
    dataset = load_dataset(dataset_ref=dataset_ref, publish_dataset=publish_dataset)

    evaluation = Evaluation(
        dataset=dataset,
        scorers=[
            specificity_evaluator,
            actionability_rule_evaluator,
            groundedness_rule_evaluator,
            rubric_alignment_evaluator,
            trust_rule_evaluator,
        ],
        evaluation_name="edition-005-demo-evaluators-rule-based",
    )

    return await evaluation.evaluate(
        generate_demo_interview_feedback,
        __weave={"display_name": "Edition 005 - Demo Evaluators"},
    )


def main() -> int:
    args = parse_args()

    try:
        config = require_environment()
        weave.init(config["wandb_project"])
        results = asyncio.run(
            run_demo(
                publish_dataset=args.publish_dataset,
                dataset_ref=args.dataset_ref,
            )
        )
    except RuntimeError as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Demo error: {exc}", file=sys.stderr)
        return 1

    print_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
