# Lab 4: Retrieval evaluation and regression gates

**Level:** Upper intermediate  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 3 first.

[Previous lab](../03-rag-from-chunks/README.md) · [Next lab](../05-bounded-tool-calling/README.md)

## Engineering objective

Compare a BM25 baseline with a hybrid candidate using labeled evidence, confidence intervals and release checks.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- Twenty synthetic cases include exact matches, paraphrases, multiple relevant sources, no-answer queries and two tenants.
- Per-query recall, reciprocal rank and normalized discounted cumulative gain remain inspectable.
- Source IDs are deduplicated when multiple chunks refer to the same source.
- A seeded bootstrap resamples query scores to estimate an nDCG interval.
- A regression gate rejects candidates that degrade recall, MRR or nDCG beyond the configured tolerance.

## Architecture and tradeoffs

Averages hide failures, so every report retains each query and its retrieved sources. For no-answer cases the implementation rewards returning no evidence and penalizes false retrieval. That convention is explicit rather than pretending standard ranking metrics alone measure abstention. The release gate compares point estimates with a 0.02 tolerance. It is not a statistical significance test, and the bootstrap interval on a small synthetic dataset cannot establish production confidence.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 4
```

## Investigate the behavior

Run the report and inspect the hardest cases instead of focusing only on the aggregate. Change candidate_limit or chunk settings and save both reports. Add a negative query with common stopwords and check false retrieval. Replace some synthetic examples with independently labeled, held-out domain questions. Keep the initial set as a development fixture.

## Failure experiments and acceptance criteria

Set candidate recall to zero and verify the regression gate fails. Preserve deterministic bootstrap intervals with a fixed seed. Check that no-answer cases with irrelevant hits receive zero instead of being dropped from the denominator.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_regression_gate_detects_degradation
```

## Build the next version yourself

Add graded relevance, a separate abstention threshold sweep, paired bootstrap differences, answer-grounding labels and cost per successful task. Save baseline reports by corpus, model and index version and require review when labels change.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

This evaluates retrieval, not answer correctness or judge reliability. Binary relevance is assumed. The fixture set is intentionally small and not representative. Metrics do not prove that hybrid retrieval is better than BM25. A paired confidence test and multiple-comparison correction are not implemented.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/platform.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
