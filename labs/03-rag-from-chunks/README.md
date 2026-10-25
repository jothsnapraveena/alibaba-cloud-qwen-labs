# Build a small Qwen RAG pipeline from first principles

## What you will build

Connect word chunking, lexical retrieval, source IDs, and grounded generation.

## Why it works

The example uses three synthetic service descriptions. Chunking demonstrates overlap separately, while retrieval ranks the original short documents with Jaccard word overlap. This keeps source IDs stable and makes ranking inspectable without an embedding service.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 3

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 3 --live
```

## Walkthrough

Inspect the chunks and retrieved scores. Change the question to objects buckets, then to an unrelated string. Run live mode to pass the retrieved source text to Qwen. Read the answer and verify each citation against the retrieved IDs.

## Expected behavior

Offline mode returns chunks and ranked documents. Live mode adds a generated answer.

## Limits and troubleshooting

This is a lexical baseline, without embeddings or a learned reranker. Citation instructions do not prove grounding or prevent all prompt injection. Production RAG needs document authorization, context limits, and factual review.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
