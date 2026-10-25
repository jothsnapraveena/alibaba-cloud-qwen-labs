# Validate Qwen output before using it

## What you will build

Turn a support ticket into a small typed classification and reject malformed output.

## Why it works

Prompt instructions cannot enforce application invariants. json.loads parses the response, then application code checks exact keys and allowed values. This sample intentionally rejects Markdown fences and extra fields.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 2

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 2 --live
```

## Walkthrough

Run the offline classification. Read validate_ticket in core.py. Try an invalid priority and an extra key. Run live mode with a supported Qwen model and inspect any schema failures.

## Expected behavior

A dictionary with category billing and priority medium appears in offline mode. Live classifications can vary.

## Limits and troubleshooting

This is prompt-based JSON plus local validation, not guaranteed provider-side structured output. Decide whether to retry, repair, or route failures to a person. Do not silently accept unknown fields.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
