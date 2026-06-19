# Edition 005 - Building Your First Evaluators

This demo supports **Edition 005** of the **AI Engineering In Production** newsletter.

It shows how to move from vague quality judgment to measurable evaluation dimensions using W&B Weave.

## Article

In the previous editions, we covered:

```text
What to evaluate
↓
Evaluation architecture
↓
Tracing
```

Now we reach the point where quality becomes measurable.

The question is:

> How do we actually score AI behavior?

Many teams make the same mistake.

They ask:

```text
Is this response good?
```

That sounds reasonable.

But it does not scale.

Instead, strong evaluation systems break quality into dimensions.

For example:

- Specificity
- Actionability
- Groundedness
- Rubric Alignment

Each dimension gets its own evaluator.

## What Is An Evaluator?

An evaluator is simply:

> A function that measures one quality dimension.

Examples:

```text
specificity_evaluator()
actionability_evaluator()
groundedness_evaluator()
rubric_alignment_evaluator()
```

Each evaluator typically returns:

- score
- reason
- evidence

Instead of one vague judgment, you get measurable signals.

## Three Types Of Evaluators

### 1. Rule-Based Evaluators

These are deterministic.

Examples:

- Is the JSON valid?
- Are all rubric sections present?
- Is evidence included?
- Is the response long enough?

These evaluators are fast, cheap, and reliable. They should usually be your first evaluators.

### 2. LLM-As-A-Judge

This is where another model evaluates the output.

For example:

Input:

```text
Transcript
Feedback
```

Question:

```text
Did the feedback reference specific moments from the transcript?
```

Output:

```json
{
  "score": 4,
  "reason": "Referenced customer objection handling."
}
```

This approach is flexible and widely used in production systems.

### 3. Human Evaluation

Humans are still the gold standard.

Especially for evaluating:

- realism
- usefulness
- trustworthiness
- conversational quality

Strong evaluation systems often combine human evaluation with automated evaluators.

## Example Evaluators

### Specificity

Question:

> Did the feedback reference concrete moments?

Good:

```text
You interrupted the customer twice while they explained the issue.
```

Bad:

```text
Improve communication.
```

### Actionability

Question:

> Can the user improve from this feedback?

Good:

```text
Use the STAR framework when answering behavioral questions.
```

Bad:

```text
Need better communication.
```

### Groundedness

Question:

> Is the feedback supported by transcript evidence?

Good evaluators catch unsupported claims before users do.

This is critical because hallucinated criticism destroys trust.

### Rubric Alignment

Question:

> Did the feedback evaluate all required dimensions?

For example:

```text
Clarity
Structure
Confidence
Empathy
```

If one category is missing, the evaluator should detect it.

## The Mistake Most Beginners Make

Never trust a single evaluator.

Instead:

```text
Specificity
+
Actionability
+
Groundedness
+
Rubric Alignment
```

Together they create confidence.

One score is fragile. Multiple dimensions create reliability.

## The Most Important Principle

Do not ask:

```text
Is this output good?
```

Ask:

```text
How specific is it?
How actionable is it?
How grounded is it?
How aligned is it?
```

Breaking quality into dimensions is one of the most important skills in evaluation engineering.

## What This Demo Does

This edition has two runnable scripts:

1. `demo.py` is the controlled teaching demo.
   - It uses deterministic feedback.
   - It uses rule-based evaluators for actionability, groundedness, and trust.
   - Use this first when explaining how evaluators work.
2. `real_inference.py` is the production-like demo.
   - It calls W&B Inference through the OpenAI-compatible SDK.
   - It supports prompt versions `v1` and `v2`.
   - It uses LLM-as-a-judge evaluators for actionability, groundedness, and trust.

Shared files:

- `dataset.py` contains the evaluation dataset.
- `evaluators.py` contains the evaluator functions.
- `config.py` contains W&B environment configuration.
- `llm_utils.py` contains small LLM response helpers.

The important teaching point is that each evaluator returns:

- `score`
- `reason`
- `evidence`

## Install Dependencies

From this edition folder, the fastest path is `uv`:

```bash
uv sync
```

Then run the demo with:

```bash
uv run python demo.py
```

For a video demo, publish the dataset before running the evaluation:

```bash
uv run python demo.py --publish-dataset
```

You only need `--publish-dataset` when you want to create or update the dataset in Weave. After the dataset already exists, reuse it with:

```bash
uv run python demo.py --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_005_evaluation_dataset:latest
```

To evaluate real LLM-generated feedback through W&B Inference:

```bash
uv run python real_inference.py --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_005_evaluation_dataset:latest
```

To compare prompt versions, run the same dataset with V1 and V2:

```bash
uv run python real_inference.py --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_005_evaluation_dataset:latest --prompt-version v1
uv run python real_inference.py --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_005_evaluation_dataset:latest --prompt-version v2
```

Prompt V1 is intentionally generic. Prompt V2 is more grounded and rubric-aware, so the evaluator scores should make the improvement easier to inspect in Weave.

In `demo.py`, actionability, groundedness, and trust are intentionally rule-based so you can explain the simplest evaluator pattern first.

In `real_inference.py`, actionability, groundedness, and trust use LLM-as-a-judge evaluators because real LLM feedback may use many valid phrasings and may fail in ways that exact phrase checks miss.

If you prefer `pip`, the `requirements.txt` file is still available:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Then fill in:

```text
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=your-team/ai-engineering-in-production
WANDB_MODEL=meta-llama/Llama-3.1-8B-Instruct
WANDB_INFERENCE_BASE_URL=https://api.inference.wandb.ai/v1
```

Use an entity/project path, such as `your-team/ai-engineering-in-production`, for `WANDB_PROJECT`.

`WANDB_API_KEY` is used for both W&B Weave and W&B Inference. The code calls W&B Inference with the OpenAI-compatible Python SDK, so the SDK parameter is named `api_key`, but the value is your W&B API key.

## Run The Demo

```bash
python demo.py --publish-dataset
```

You should see the evaluation result in the terminal.

For the real inference version:

```bash
python real_inference.py --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_005_evaluation_dataset:latest --prompt-version v2
```

## What To Look For In W&B Weave

After running the script, open your W&B Weave project and inspect the evaluation run.

Look for:

- the `Edition 005 - Building Your First Evaluators` evaluation run
- each dataset row
- the generated feedback output
- each scorer call
- the `score`, `reason`, and `evidence` returned by every evaluator
- the row where groundedness and trust fail because unsupported claims appear
- in real inference mode, the `generate_llm_interview_feedback` call with model name, token usage, and latency
- the `prompt_version` and `prompt_label` fields when comparing V1 and V2
- the difference between rule evaluators in `demo.py` and judge evaluators in `real_inference.py`

This is the core lesson: do not evaluate AI behavior with one vague score. Break quality into dimensions, then score each dimension separately.

For a presenter-friendly walkthrough, use [VIDEO_GUIDE.md](VIDEO_GUIDE.md).

## Practice This Like An AI Engineer

Design 3 additional evaluators for an AI interview simulation platform.

Beyond:

- Specificity
- Actionability
- Groundedness
- Rubric Alignment

Choose evaluators that support:

- realism
- trust
- consistency
- assessment quality

For each one define:

- name
- what it measures
- why it matters
- how it would be scored

In the next edition, we will look at evaluation datasets.

Because even the best evaluators are useless without good test cases.
