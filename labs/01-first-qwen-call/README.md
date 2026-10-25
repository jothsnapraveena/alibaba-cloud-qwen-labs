# Your first Qwen call with Alibaba Cloud Model Studio

## What you will build

Configure a regional endpoint, keep the API key out of source control, and inspect a bounded chat response.

## Why it works

The shared client sends an OpenAI-compatible HTTP request using the Python standard library. It requires HTTPS, reads configuration from the environment, sets a 45-second timeout, and caps output at 256 tokens.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 1

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 1 --live
```

## Walkthrough

Inspect client.py. Run the fixture first. Activate Model Studio, choose a supported model, and copy your exact workspace endpoint from the console. Export the three variables below, then run live mode.

## Expected behavior

An offline response explicitly says fixture. A live response contains model-generated text.

## Limits and troubleshooting

A 401 often means the API key and endpoint regions differ. A 404 can indicate the wrong endpoint or model. Never paste a real key into an issue.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
