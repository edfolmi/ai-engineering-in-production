# Edition 004 - Why Tracing Comes Before Evaluation

This demo supports **Edition 004** of the **AI Engineering In Production** newsletter.

It shows how to trace a simple AI interview simulation with W&B Weave before trying to evaluate the quality of the AI system.

## What Tracing Means

Tracing means recording what happened inside an AI workflow while it runs.

For an LLM-powered product, a useful trace can include the prompt, model name, user input, generated output, latency, token usage, errors, and business context such as a session ID or scenario ID.

Instead of only seeing the final answer, tracing lets you inspect the steps that produced it.

## Why Tracing Comes Before Evaluation

Evaluation asks, "Was this good?"

Tracing helps you answer, "What actually happened?"

Before you can design meaningful evaluations, you need visibility into the system behavior. Traces show which prompts were used, what the user said, how the model responded, how long it took, whether token usage changed, and where failures happened.

Without traces, evaluation results are hard to debug. With traces, failures become inspectable examples you can turn into better prompts, tests, datasets, and metrics.

## What This Demo Does

The script simulates one interview turn:

1. Defines an interview scenario.
2. Defines a candidate answer.
3. Calls W&B Inference through the OpenAI-compatible Python SDK to generate an interviewer follow-up question.
4. Calls W&B Inference again to generate short feedback on the candidate answer.
5. Prints the result in the terminal.
6. Sends a trace to W&B Weave.

The trace includes fields such as:

- `session_id`
- `scenario_id`
- `persona`
- `prompt_version`
- `model_name`
- `user_answer`
- `interviewer_response`
- `feedback`
- `latency`
- `token_usage`
- `estimated_cost_usd`

## Install Dependencies

From this edition folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you prefer `uv`, you can install the same requirements with:

```bash
uv venv
uv pip install -r requirements.txt
```

If you already have a `uv` project with a `pyproject.toml`, you can also add the dependencies with:

```bash
uv add -r requirements.txt
```

## Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then fill in:

```text
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=your-team/ai-engineering-in-production
```

Use your W&B API key as the value for `WANDB_API_KEY`. The same key is used for both W&B Weave tracing and W&B Inference.

W&B Inference is OpenAI-compatible, so the Python code uses the OpenAI SDK as a client library. The SDK parameter is named `api_key`, but the value passed to it is your W&B API key. No other API key is required for this demo.

Use an entity/project path, such as `your-team/ai-engineering-in-production`, for `WANDB_PROJECT`. W&B Inference uses this for usage tracking, and Weave uses it for traces.

Optional settings:

```text
WANDB_MODEL=meta-llama/Llama-3.1-8B-Instruct
WANDB_INFERENCE_BASE_URL=https://api.inference.wandb.ai/v1
```

## Run The Demo

```bash
python demo.py
```

You should see:

- the scenario
- the candidate answer
- the generated interviewer follow-up
- the generated feedback
- latency and token usage metadata

## What To Look For In W&B Weave

After running the script, open your W&B Weave project and inspect the trace.

Look for:

- the full `run_interview_simulation` trace
- nested calls for the interviewer response and feedback generation
- the input fields that describe the interview context
- the model outputs
- latency for each W&B Inference call
- token usage when returned by the OpenAI-compatible API
- the estimated cost placeholder

This is the key lesson: before evaluating whether the interviewer or feedback is good, first make the system behavior visible.
