# Evaluate retrieval before judging generation

## What you will build

Measure hit@1 with a tiny transparent test set.

## Why it works

Each synthetic query has one expected source ID. Hit@1 is the fraction where that source appears first. These labels assess retrieval only, not answer correctness, faithfulness, or user usefulness.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 4
```

## Walkthrough

Run the local evaluation. Add ten realistic queries with known source labels. Include ambiguous queries and no-answer cases. Compare ranking changes on a held-out set rather than tuning on every example.

## Expected behavior

The initial four synthetic cases report hit@1 of 1.0. This is a teaching result, not evidence of production quality.

## Limits and troubleshooting

Small and easy datasets inflate confidence. Add separate generation and abstention evaluation before releasing an assistant.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
