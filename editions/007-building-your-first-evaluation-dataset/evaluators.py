"""Shared evaluators for Edition 005."""

from __future__ import annotations

import json
from typing import Any

import weave
from openai import OpenAI, OpenAIError

from llm_utils import (
    clamp_score,
    count_phrase_matches,
    parse_json_object,
    response_text,
    usage_to_dict,
)


JUDGE_CLIENT: OpenAI | None = None
JUDGE_MODEL_NAME = ""


def configure_judge_client(client: OpenAI, model_name: str) -> None:
    """Configure the optional LLM-as-a-judge evaluator client."""

    global JUDGE_CLIENT, JUDGE_MODEL_NAME
    JUDGE_CLIENT = client
    JUDGE_MODEL_NAME = model_name


@weave.op()
def specificity_evaluator(
    expected_evidence: list[str],
    output: dict[str, Any],
) -> dict[str, Any]:
    """Score whether the feedback references concrete moments."""

    feedback = output["feedback"]
    matches = count_phrase_matches(feedback, expected_evidence)
    score = clamp_score(len(matches) / max(len(expected_evidence), 1))

    return {
        "score": score,
        "reason": f"Referenced {len(matches)} of {len(expected_evidence)} expected evidence points.",
        "evidence": matches,
    }


@weave.op()
def actionability_rule_evaluator(
    required_actions: list[str],
    output: dict[str, Any],
) -> dict[str, Any]:
    """Cheap baseline scorer for whether feedback gives usable next steps.

    This is intentionally simple and deterministic. It is useful for teaching
    rule-based evaluators, but it can miss semantically good feedback that uses
    different wording.
    """

    feedback = output["feedback"]
    matched_actions = count_phrase_matches(feedback, required_actions)
    improvement_language = [
        phrase
        for phrase in ["to improve", "next time", "would add", "define", "connect"]
        if phrase in feedback.lower()
    ]
    score = clamp_score(
        (0.65 * len(matched_actions) / max(len(required_actions), 1))
        + (0.35 if improvement_language else 0.0)
    )

    return {
        "score": score,
        "reason": (
            "Rule-based baseline: measured exact action phrases and common "
            "improvement language. This can miss semantically similar wording."
        ),
        "evidence": {
            "matched_actions": matched_actions,
            "improvement_language": improvement_language,
            "required_actions": required_actions,
        },
    }


@weave.op()
def actionability_judge_evaluator(
    transcript: str,
    candidate_answer: str,
    required_actions: list[str],
    output: dict[str, Any],
) -> dict[str, Any]:
    """Semantic actionability scorer using an LLM-as-a-judge."""

    if JUDGE_CLIENT is None:
        raise RuntimeError(
            "Judge client is not configured. Run real_inference.py or configure "
            "the judge client before using actionability_judge_evaluator."
        )

    feedback = output["feedback"]
    required_actions_text = "\n".join(f"- {action}" for action in required_actions)

    try:
        response = JUDGE_CLIENT.chat.completions.create(
            model=JUDGE_MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Score whether interview "
                        "feedback gives concrete, useful next steps. Accept "
                        "semantic matches and paraphrases. Do not require exact "
                        "wording. Return only a JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Evaluate the feedback's actionability.\n\n"
                        f"Transcript:\n{transcript}\n\n"
                        f"Candidate answer:\n{candidate_answer}\n\n"
                        f"Expected improvement themes:\n{required_actions_text}\n\n"
                        f"Feedback:\n{feedback}\n\n"
                        "Scoring guide:\n"
                        "- 1.0: feedback gives concrete, specific next steps "
                        "that a candidate can act on.\n"
                        "- 0.7: feedback gives a useful next step, but it is "
                        "somewhat incomplete or generic.\n"
                        "- 0.4: feedback hints at improvement but lacks a clear "
                        "action.\n"
                        "- 0.0: feedback gives no actionable next step.\n\n"
                        "Return only JSON with these keys:\n"
                        "- score: number from 0.0 to 1.0 that you choose from "
                        "the scoring guide\n"
                        "- reason: short explanation\n"
                        "- evidence: array of quoted or paraphrased actionable "
                        "parts from the feedback\n\n"
                        "Do not copy placeholder values. Choose the score based "
                        "on the feedback."
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference actionability judge call failed. Check WANDB_API_KEY, "
            "WANDB_PROJECT, WANDB_MODEL, and WANDB_INFERENCE_BASE_URL. "
            f"Original error: {exc}"
        ) from exc

    judge_text = response_text(response)

    try:
        judged = parse_json_object(judge_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(
            "Actionability judge did not return valid JSON. "
            f"Original response: {judge_text}"
        ) from exc

    return {
        "score": clamp_score(float(judged.get("score", 0.0))),
        "reason": str(judged.get("reason", "")),
        "evidence": judged.get("evidence", []),
        "raw_judge_response": judge_text,
        "judge_model": JUDGE_MODEL_NAME,
        "required_actions": required_actions,
        "token_usage": usage_to_dict(response),
    }


@weave.op()
def groundedness_rule_evaluator(
    transcript: str,
    output: dict[str, Any],
) -> dict[str, Any]:
    """Rule-based scorer for known unsupported claims."""

    feedback = output["feedback"].lower()
    transcript_lower = transcript.lower()
    unsupported_claims = [
        claim
        for claim in ["database sharding", "cache eviction", "incident command handoff"]
        if claim in feedback and claim not in transcript_lower
    ]
    score = 0.0 if unsupported_claims else 1.0

    return {
        "score": score,
        "reason": (
            "Found unsupported claims."
            if unsupported_claims
            else "No known unsupported claims were found."
        ),
        "evidence": unsupported_claims,
    }


@weave.op()
def groundedness_judge_evaluator(
    transcript: str,
    output: dict[str, Any],
) -> dict[str, Any]:
    """Semantic groundedness scorer using an LLM-as-a-judge."""

    if JUDGE_CLIENT is None:
        raise RuntimeError(
            "Judge client is not configured. Run real_inference.py or configure "
            "the judge client before using groundedness_judge_evaluator."
        )

    feedback = output["feedback"]

    try:
        response = JUDGE_CLIENT.chat.completions.create(
            model=JUDGE_MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Score whether feedback "
                        "claims are supported by the transcript. Identify any "
                        "unsupported claims. Return only a JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Evaluate groundedness.\n\n"
                        f"Transcript:\n{transcript}\n\n"
                        f"Feedback:\n{feedback}\n\n"
                        "Scoring guide:\n"
                        "- 1.0: all substantive feedback claims are supported "
                        "by the transcript.\n"
                        "- 0.7: mostly supported, with minor unsupported or "
                        "over-interpreted claims.\n"
                        "- 0.4: several claims go beyond the transcript.\n"
                        "- 0.0: feedback is mostly unsupported or invented.\n\n"
                        "Return only JSON with these keys:\n"
                        "- score: number from 0.0 to 1.0\n"
                        "- reason: short explanation\n"
                        "- unsupported_claims: array of unsupported claims, or "
                        "an empty array if none\n\n"
                        "Choose the score based on the feedback and transcript."
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference groundedness judge call failed. Check WANDB_API_KEY, "
            "WANDB_PROJECT, WANDB_MODEL, and WANDB_INFERENCE_BASE_URL. "
            f"Original error: {exc}"
        ) from exc

    judge_text = response_text(response)

    try:
        judged = parse_json_object(judge_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(
            "Groundedness judge did not return valid JSON. "
            f"Original response: {judge_text}"
        ) from exc

    return {
        "score": clamp_score(float(judged.get("score", 0.0))),
        "reason": str(judged.get("reason", "")),
        "evidence": judged.get("unsupported_claims", []),
        "raw_judge_response": judge_text,
        "judge_model": JUDGE_MODEL_NAME,
        "token_usage": usage_to_dict(response),
    }


@weave.op()
def rubric_alignment_evaluator(
    rubric: list[str],
    output: dict[str, Any],
) -> dict[str, Any]:
    """Score whether the feedback touches the required rubric dimensions."""

    feedback = output["feedback"]
    matched_dimensions = count_phrase_matches(feedback, rubric)
    score = clamp_score(len(matched_dimensions) / max(len(rubric), 1))

    return {
        "score": score,
        "reason": f"Covered {len(matched_dimensions)} of {len(rubric)} rubric dimensions.",
        "evidence": matched_dimensions,
    }


@weave.op()
def trust_rule_evaluator(output: dict[str, Any]) -> dict[str, Any]:
    """Rule-based scorer for known trust-damaging criticism patterns."""

    feedback = output["feedback"].lower()
    risky_phrases = [
        phrase
        for phrase in ["missed database sharding", "cache eviction", "incident command"]
        if phrase in feedback
    ]
    score = 0.25 if risky_phrases else 1.0

    return {
        "score": score,
        "reason": "Checks whether criticism sounds supported and trustworthy.",
        "evidence": risky_phrases,
    }


@weave.op()
def trust_judge_evaluator(
    transcript: str,
    output: dict[str, Any],
) -> dict[str, Any]:
    """Semantic trust scorer using an LLM-as-a-judge."""

    if JUDGE_CLIENT is None:
        raise RuntimeError(
            "Judge client is not configured. Run real_inference.py or configure "
            "the judge client before using trust_judge_evaluator."
        )

    feedback = output["feedback"]

    try:
        response = JUDGE_CLIENT.chat.completions.create(
            model=JUDGE_MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Score whether interview "
                        "feedback avoids unsupported, unfair, overconfident, "
                        "or harsh personal criticism that could reduce user "
                        "trust. Return only a JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Evaluate trust risk.\n\n"
                        f"Transcript:\n{transcript}\n\n"
                        f"Feedback:\n{feedback}\n\n"
                        "Scoring guide:\n"
                        "- 1.0: feedback is fair, appropriately scoped, and "
                        "does not make unsupported personal criticism.\n"
                        "- 0.7: mostly fair, with slightly overconfident or "
                        "under-supported wording.\n"
                        "- 0.4: contains noticeable unfair, harsh, or "
                        "unsupported criticism.\n"
                        "- 0.0: contains serious trust-damaging criticism.\n\n"
                        "Return only JSON with these keys:\n"
                        "- score: number from 0.0 to 1.0\n"
                        "- reason: short explanation\n"
                        "- risky_claims: array of trust-risky claims, or an "
                        "empty array if none\n\n"
                        "Choose the score based on the feedback and transcript."
                    ),
                },
            ],
        )
    except OpenAIError as exc:
        raise RuntimeError(
            "W&B Inference trust judge call failed. Check WANDB_API_KEY, "
            "WANDB_PROJECT, WANDB_MODEL, and WANDB_INFERENCE_BASE_URL. "
            f"Original error: {exc}"
        ) from exc

    judge_text = response_text(response)

    try:
        judged = parse_json_object(judge_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(
            "Trust judge did not return valid JSON. "
            f"Original response: {judge_text}"
        ) from exc

    return {
        "score": clamp_score(float(judged.get("score", 0.0))),
        "reason": str(judged.get("reason", "")),
        "evidence": judged.get("risky_claims", []),
        "raw_judge_response": judge_text,
        "judge_model": JUDGE_MODEL_NAME,
        "token_usage": usage_to_dict(response),
    }
