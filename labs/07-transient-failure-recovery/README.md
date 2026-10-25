# Lab 7: Contract-driven multi-agent evidence review

**Level:** Advanced  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 6 first.

[Previous lab](../06-content-free-observability/README.md) · [Next lab](../08-governed-workflow/README.md)

## Engineering objective

Coordinate planner, writer and reviewer roles with explicit schemas, evidence boundaries and a shared model budget.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- The planner emits a bounded query and top-k rather than executing tools.
- The host performs tenant-scoped retrieval using the plan.
- The writer emits an answer and source IDs, which code validates against actual retrieved evidence.
- A separate reviewer call receives the draft and evidence and returns accept or revise.
- All three roles share a six-attempt budget, including gateway retries.

## Architecture and tradeoffs

Role separation is implemented as three model calls with distinct instructions and structured contracts. Application code validates exact output keys, types, lengths and allowed citation IDs. The writer cannot add a source simply by naming it. If retrieval finds nothing the workflow abstains before writer and reviewer calls. Accepting a reviewer verdict still leaves the final status at human_review rather than automatically taking a business action.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 7
# Optional, real model calls and possible charges
python -m qwenlabs.run 7 --live
```

## Investigate the behavior

Run offline mode to inspect deterministic role fixtures. Run live mode to see genuine planner, writer and reviewer outputs. Change the reviewer to return revise and confirm the workflow stops with revision_required. Return an unknown citation from the writer and ensure execution fails before review. Return invalid JSON and decide which errors warrant a bounded repair call.

## Failure experiments and acceptance criteria

Three successful roles should consume exactly three model attempts. A writer citation outside the retrieved allowlist must fail. An empty source set must abstain. A planner cannot return a Boolean top_k or an unbounded query.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_writer_unknown_citation_is_rejected
```

## Build the next version yourself

Add claim-level evidence spans, an independent reviewer model, a revision budget and quality measurements against human labels. Compare the three-role workflow with a single model baseline at equal cost before assuming the extra roles improve outcomes.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

The agents share one model family and evidence, so reviewer errors can correlate with writer errors. Schema validity and allowed citations do not prove the claim is supported. There is no recursive planning, autonomous shell access or unbounded debate. Model JSON output is prompt-based and can fail validation. No automatic JSON-repair loop is included.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/platform.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
