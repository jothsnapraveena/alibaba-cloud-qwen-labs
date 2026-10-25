# Build a bounded draft-review workflow with Qwen

## What you will build

Separate generation, deterministic review, and a human decision.

## Why it works

Qwen drafts a short explanation. A deterministic review checks for a citation-related word and always requires human review. The code records the sequence instead of presenting a weak heuristic as an AI judge.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 8

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 8 --live
```

## Walkthrough

Run the fixture and inspect the review object. Try a draft containing the word citation but false claims. Explain why the check passes even though the content is wrong. Run live mode and manually assess evidence and usefulness.

## Expected behavior

The output contains a draft, a limited review, and requires_human_review=true.

## Limits and troubleshooting

This is one model step plus deterministic review, not a multi-agent implementation or factual verification. A reviewer agent would need independent evidence, its own evaluation, and a strict execution budget.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
