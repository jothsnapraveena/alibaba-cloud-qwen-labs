# Recover from transient failures with bounded retries

## What you will build

Inject two timeouts and verify that retries stop after a fixed budget.

## Why it works

The retry helper retries timeouts, URL failures, HTTP 429, and selected server errors. It fails immediately for authentication and other non-transient HTTP errors. The exercise records intended delays instead of sleeping.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 7
```

## Walkthrough

Run the fault injection. Inspect attempts=3 and scheduled delays [1,2]. Change the operation to fail permanently and confirm exhaustion. Read the unit test for 401 fast failure.

## Expected behavior

The local synthetic operation reports recovered after three attempts.

## Limits and troubleshooting

This helper is educational and is not automatically attached to every client call. Production clients should honor Retry-After, add jitter, and enforce an overall deadline. Retrying inference can incur duplicate charges. Retrying writes can duplicate side effects.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
