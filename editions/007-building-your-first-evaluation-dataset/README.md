# AI Engineering in Production — Edition 007
## Building Your First Evaluation Dataset

This repository contains the code that accompanies **Edition 007** of the **AI Engineering in Production** newsletter.

In the previous edition, we built evaluators.

Now we answer an even more important question:

> **How do we know our evaluators are actually correct?**

The answer is a **Golden Evaluation Dataset**.

Instead of testing evaluators on random conversations, we evaluate them against carefully curated examples with known expected behavior.

This becomes the baseline for measuring improvement over time.

---

# What You'll Learn

This demo shows how to build a production-ready evaluation dataset.

Each example contains:

- Transcript
- Candidate Answer
- Reference Feedback
- Evaluation Rubric
- Expected Evidence
- Required Actions
- Failure Modes
- Acceptable Score Ranges

These examples allow you to consistently measure whether your AI system is improving or regressing.

---

# Project Structure

```text
dataset.py
    Golden evaluation dataset.

real_inference.py
    Generates interview feedback using an LLM.

evaluators.py
    Evaluates generated feedback against the golden dataset.

llm_utils.py
    LLM helper functions.

config.py
    Environment configuration.
```

---

# Dataset Design

Every dataset example contains:

```text
Transcript
        ↓
Candidate Answer
        ↓
Reference Feedback
        ↓
Rubric
        ↓
Expected Evidence
        ↓
Failure Modes
        ↓
Acceptable Score Range
```

This allows every evaluator to compare generated feedback against a known reference.

---

# Why This Matters

Without a golden dataset:

```text
Run evaluation

↓

Looks good

↓

Ship to production
```

With a golden dataset:

```text
Run evaluation

↓

Compare against known examples

↓

Measure evaluator performance

↓

Improve with confidence
```

Instead of guessing whether your evaluators are improving, you have a stable benchmark.

---

# Install

Using `uv`:

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

# Configure

Create a `.env` file:

```env
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=your-team/ai-engineering-in-production
WANDB_MODEL=meta-llama/Llama-3.1-8B-Instruct
WANDB_INFERENCE_BASE_URL=https://api.inference.wandb.ai/v1
```

---

# Run

Publish the dataset to Weave:

```bash
uv run python real_inference.py --publish-dataset
```

Run the evaluation:

```bash
uv run python real_inference.py \
  --dataset-ref weave:///your-team/ai-engineering-in-production/object/edition_007_golden_interview_evaluation_dataset:latest
```

---

# What to Observe in Weave

After running the evaluation, inspect:

- Each golden dataset example
- Generated AI feedback
- Evaluator scores
- Reasons and evidence
- Token usage
- Latency
- Overall baseline scores

These baseline scores become your reference point.

As you improve prompts, models, or evaluation logic, rerun the same dataset and compare the results.

If the scores improve, your system improved.

If they regress, you'll know exactly when and where the change happened.

---

# Practice

Take one real production failure from your AI system and add it to your golden dataset.

For every new example, define:

- Transcript
- Generated Feedback
- Reference Feedback
- Expected Evidence
- Failure Modes
- Acceptable Score Range

Your golden dataset should evolve as your production system evolves.

---

## Newsletter

This repository accompanies the **AI Engineering in Production** weekly newsletter, where we build production-ready AI systems step by step.

**Read the newsletter:**  
https://www.linkedin.com/newsletters/ai-engineering-in-production-7446540686520348672/