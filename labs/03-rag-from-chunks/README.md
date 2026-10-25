# Lab 3: Hybrid RAG with BM25, embeddings and rank fusion

**Level:** Upper intermediate  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 2 first.

[Previous lab](../02-validated-extraction/README.md) · [Next lab](../04-retrieval-evaluation/README.md)

## Engineering objective

Build inspectable hybrid retrieval and pass authorized evidence to Qwen.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- BM25 calculates term frequency, document frequency and document-length normalization.
- A vector channel ranks the same authorized chunks with cosine similarity.
- Reciprocal rank fusion combines candidate ranks without equating incompatible raw scores.
- Tenant filtering runs before either channel, including before text is sent to a cloud embedding model.
- Live mode uses Model Studio text-embedding-v4, followed by a Qwen generation request.

## Architecture and tradeoffs

search first reads only the tenant’s rows. It ranks up to eight candidates from each channel, combines them with RRF constant 60, then returns top-k chunks. Offline vectors use signed feature hashing to exercise vector plumbing without model downloads. That baseline is lexical and must not be presented as semantic retrieval. Live embeddings replace it with hosted vectors. Ranking all authorized chunks is deliberately transparent but costs more as the corpus grows.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 3
# Optional, real model calls and possible charges
python -m qwenlabs.run 3 --live
```

## Investigate the behavior

Compare mode=bm25, vector and hybrid for the same query. Inspect chunk IDs, source IDs and fused scores. Run live mode only after configuring a supported regional embedding model. Change k and candidate_limit independently and explain why a larger candidate pool can help even when the answer context stays small. Verify every generated citation against retrieved source IDs.

## Failure experiments and acceptance criteria

A beta-only source must never reach alpha’s embedding request. Unknown query words should return no evidence in offline mode. Mismatched embedding counts or dimensions must raise errors rather than silently corrupt ranking.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_tenant_filter_before_embedding
```

## Build the next version yourself

Persist embeddings keyed by tenant, chunk hash, model and dimensions. Add a genuine cross-encoder or Model Studio reranking adapter. Evaluate recall before reranking and nDCG afterward. Report cloud embedding cost separately from generation cost.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

RRF fuses rankings; it is not a cross-encoder reranker. There is no trained local semantic embedding, persistent vector cache or ANN index. Live mode re-embeds the authorized corpus on each run. The tiny corpus fits one request; a production adapter needs batch and token limits. Prompts do not prove factual grounding or eliminate prompt injection.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/platform.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
