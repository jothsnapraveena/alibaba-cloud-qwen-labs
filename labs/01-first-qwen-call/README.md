# Lab 1: Resilient Qwen inference gateway

**Level:** Intermediate  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. This series starts beyond basic API calls.

[Series overview](../../README.md) · [Next lab](../02-validated-extraction/README.md)

## Engineering objective

Build an inference boundary that controls concurrent work, retry attempts, deadlines and provider failures.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- A thread-safe semaphore limits in-flight requests before transport calls begin.
- A shared workflow budget counts each network attempt, including retries, rather than just counting user requests.
- Exponential full jitter and numeric Retry-After support reduce immediate retry storms.
- A circuit opens after repeated failed requests, rejects new work during cooldown, and admits one recovery probe.
- Content-free events retain trace IDs, attempt counts and elapsed time, with a bounded 1,000-event buffer.

## Architecture and tradeoffs

Admission happens before circuit checks and network calls. A caller passes one Budget across multiple roles. Retrying consumes that same budget. This prevents a three-role workflow from quietly multiplying its model traffic under repeated throttling. The circuit operates per Gateway instance, so an application should reuse it rather than constructing one per request.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 1
# Optional, real model calls and possible charges
python -m qwenlabs.run 1 --live
```

## Investigate the behavior

Read Gateway.request and Budget.consume. Compare three concurrent logical requests with the observed attempt count. Inject one 429 with Retry-After: 2 and confirm the delay is at least two seconds. Then inject 401 and verify there is only one attempt. Trigger the circuit and advance a fake clock to test recovery without sleeping.

## Failure experiments and acceptance criteria

The admission limit must hold under 16 concurrent requests. A budget of two attempts must stop a provider that keeps timing out. An unauthorized key must fail without retry. A circuit rejection must not consume a model-attempt budget.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# GatewayTests
```

## Build the next version yourself

Add a token-bucket rate limiter per tenant, distinguish queue duration from provider duration, and make admission fairness measurable. Test cancellation and slow streaming responses before describing the deadline as a hard end-to-end limit.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

Deadlines govern admission, retries and the timeout passed to the transport. Python urllib socket timeouts do not provide hard cancellation of an already-running request. Numeric Retry-After is supported, HTTP-date values are not. There is no distributed circuit state or cluster-wide rate limit. Output-token limits are not monetary spending guarantees.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/gateway.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
