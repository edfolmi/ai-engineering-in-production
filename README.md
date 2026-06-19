# AI Engineering In Production

This repository supports the newsletter **AI Engineering In Production** with small, practical code examples for each edition.

Each folder under `editions/` maps to a specific newsletter edition. The goal is to make production AI engineering ideas easier to understand by pairing the writing with runnable demos.

These examples are intentionally small. They are not full applications or frameworks. They are learning artifacts for practicing concepts such as tracing, evaluation, monitoring, reliability, cost awareness, and debugging in realistic AI workflows.

## Setup

This repo supports `uv` for faster installs:

```bash
uv sync
```

Individual edition folders may also include a `requirements.txt` file for readers who prefer `pip`.

## Editions

- `editions/004-tracing-before-evaluation/` - A minimal Python demo showing why tracing should come before evaluation, using W&B Weave and W&B Inference through the OpenAI-compatible Python SDK.
- `editions/005-building-your-first-evaluators/` - A W&B Weave evaluation demo showing how to score AI behavior with separate evaluator functions for specificity, actionability, groundedness, rubric alignment, and trust.
