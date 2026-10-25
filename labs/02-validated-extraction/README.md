# Lab 2: Incremental tenant-aware document ingestion

**Level:** Intermediate  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 1 first.

[Previous lab](../01-first-qwen-call/README.md) · [Next lab](../03-rag-from-chunks/README.md)

## Engineering objective

Build a transactional SQLite index with stable provenance, incremental updates and tenant isolation.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- Source checksums include document content and chunk configuration.
- Unchanged sources skip reindexing.
- Changed sources replace their old chunks within one transaction.
- Chunks retain source ID and word offsets, with content-derived chunk IDs.
- Tenant and source IDs form composite identities; deletes cannot remove another tenant’s documents.

## Architecture and tradeoffs

A document update must never leave a mixture of old and new chunks. Index.ingest validates the full batch before opening its transaction, compares checksums, then replaces affected chunks and source metadata together. A SQLite rollback protects the previous index on failure. Chunking uses word windows with overlap, not the model tokenizer. Those offsets describe the normalized word sequence, not byte offsets in a PDF.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 2
```

## Investigate the behavior

Run the same corpus twice and observe unchanged_sources_reindexed=0. Update the Model Studio source and inspect the new chunk IDs. Change size from 45 to 8 and overlap to 2, then check that the configuration change invalidates the old checksum. Delete the same source ID from alpha and verify beta remains intact.

## Failure experiments and acceptance criteria

A batch containing an invalid document must not partially insert earlier documents. Changing a source must remove stale chunks. Reingesting the same content must preserve the exact chunk rows.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage
```

## Build the next version yourself

Implement an OSS ingestion adapter with object version IDs, deletion events and a persisted ingestion manifest. Test duplicate events and out-of-order updates. Keep external object retrieval separate from trusted tenant assignment.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

This is a local text ingestion pipeline. It does not fetch OSS objects, extract PDFs, handle OCR, or maintain a distributed vector store. It does not automatically tombstone sources missing from an ingestion batch because a batch is treated as a partial update. Explicit delete is required. Source IDs and tenant assignments come from a trusted host.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/platform.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
