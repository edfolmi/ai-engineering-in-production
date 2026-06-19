"""Shared evaluation dataset for Edition 005."""

from __future__ import annotations

from typing import Any

import weave


EVALUATION_DATASET = [
    {
        "case_id": "strong-feedback-001",
        "transcript": (
            "Interviewer: Tell me about a time you debugged a production issue.\n"
            "Candidate: I checked logs first, then compared the failure rate "
            "against the last deploy. The timeout spike started after a config "
            "change, so I rolled it back and added a dashboard for that service."
        ),
        "candidate_answer": (
            "I checked logs first, compared the failure rate against the last "
            "deploy, rolled back the config change, and added a dashboard."
        ),
        "rubric": ["specific evidence", "root cause", "user impact", "next step"],
        "expected_evidence": [
            "checked logs",
            "last deploy",
            "timeout spike",
            "config change",
            "dashboard",
        ],
        "required_actions": ["explain impact", "add monitoring"],
    },
    {
        "case_id": "vague-feedback-001",
        "transcript": (
            "Interviewer: How do you handle ambiguous project requirements?\n"
            "Candidate: I ask stakeholders to define the user problem, write "
            "down assumptions, and share a short proposal before implementation."
        ),
        "candidate_answer": (
            "I ask stakeholders to define the user problem, document assumptions, "
            "and share a proposal before building."
        ),
        "rubric": ["specific evidence", "clarity", "collaboration", "next step"],
        "expected_evidence": [
            "stakeholders",
            "user problem",
            "assumptions",
            "proposal",
        ],
        "required_actions": ["ask follow-up questions", "confirm success criteria"],
    },
    {
        "case_id": "unsupported-feedback-001",
        "transcript": (
            "Interviewer: Describe how you improve API reliability.\n"
            "Candidate: I add integration tests, monitor p95 latency, and review "
            "error budgets during weekly reliability reviews."
        ),
        "candidate_answer": (
            "I add integration tests, monitor p95 latency, and review error "
            "budgets each week."
        ),
        "rubric": ["specific evidence", "reliability metric", "process", "next step"],
        "expected_evidence": [
            "integration tests",
            "p95 latency",
            "error budgets",
            "weekly reliability reviews",
        ],
        "required_actions": ["define alert threshold", "connect metric to user impact"],
    },
]

CASE_EXPLANATIONS = {
    "strong-feedback-001": (
        "Good output: the feedback should mention concrete evidence and useful next steps."
    ),
    "vague-feedback-001": (
        "Weak output: the feedback sounds polite but does not reference enough specific evidence."
    ),
    "unsupported-feedback-001": (
        "Risky output: the feedback invents criticism that is not supported by the transcript."
    ),
}


def publish_demo_dataset() -> Any:
    """Publish the demo rows as a named Weave Dataset."""

    dataset = weave.Dataset(
        name="edition_005_evaluation_dataset",
        rows=EVALUATION_DATASET,
    )
    dataset_ref = weave.publish(dataset)
    print(f"\nPublished Weave dataset: {dataset_ref}")
    return dataset


def load_dataset(dataset_ref: str | None, publish_dataset: bool) -> Any:
    """Choose the dataset source for this evaluation run."""

    if dataset_ref:
        print(f"\nUsing existing Weave dataset: {dataset_ref}")
        return weave.ref(dataset_ref).get()

    if publish_dataset:
        return publish_demo_dataset()

    return EVALUATION_DATASET


def print_dataset_story() -> None:
    """Print a short presenter-friendly explanation of the evaluation rows."""

    print("\nDataset rows:")
    for row in EVALUATION_DATASET:
        print(f"- {row['case_id']}: {CASE_EXPLANATIONS[row['case_id']]}")

    print("\nWhat the evaluators inspect:")
    print("- transcript: raw conversation context for groundedness")
    print("- candidate_answer: clean answer the feedback system responds to")
    print("- rubric: dimensions the feedback should cover")
    print("- expected_evidence: concrete moments the feedback should mention")
    print("- required_actions: improvement steps the feedback should recommend")
