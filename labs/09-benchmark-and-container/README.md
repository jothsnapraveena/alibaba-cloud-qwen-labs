# Benchmark and containerize a Qwen learning application

## What you will build

Compare local retrieval timings with sequential hosted-model request timings.

## Why it works

The benchmark records five samples and computes nearest-rank p50 and p95. Offline mode measures retrieval. Live mode makes five sequential Qwen calls. The Docker image runs offline by default, with no cloud keys baked into the image.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 9

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 9 --live
```

## Walkthrough

Run the benchmark locally. Build the Docker image and run its default command. For a live run pass configuration as environment variables and explicitly add --live. Record region, model, date, request count, and failures beside timings.

## Expected behavior

Output reports sample count, raw durations, p50, and p95, with a clear mode label.

## Limits and troubleshooting

Five samples cannot establish capacity or tail latency. There is no concurrency, warmup, or GPU profiling. The container is ready for local use, but has not been deployed or verified on ECS, ACK, or Function Compute.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
