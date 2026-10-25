# Observe Qwen calls without logging prompts

## What you will build

Capture request duration and token usage while excluding prompt content.

## Why it works

The example measures wall-clock request duration with perf_counter and emits a random trace ID. Live mode includes the provider usage object if available. Offline mode measures local retrieval and labels that distinction explicitly.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 6

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 6 --live
```

## Walkthrough

Run offline mode and inspect the JSON. Run live mode and record model, total request duration, and token usage. Simulate a timeout and design an error event that omits credentials and prompt bodies.

## Expected behavior

A JSON event contains trace_id, operation, duration_ms, model, usage, and content_logged=false.

## Limits and troubleshooting

This is a local event example, not an SLS or OpenTelemetry integration. Duration includes network and provider queue time. It is not isolated GPU inference time or streaming time-to-first-token.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
