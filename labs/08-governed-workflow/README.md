# Lab 8: Tenant-isolated HTTP API and operational metrics

**Level:** Advanced capstone, part 1  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 7 first.

[Previous lab](../07-transient-failure-recovery/README.md) · [Next lab](../09-benchmark-and-container/README.md)

## Engineering objective

Serve the retrieval subsystem through a bounded authenticated API with readiness and observable failures.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- API keys map to tenants on the server; callers cannot submit a tenant override.
- Admission rejects excess connections before a worker thread is spawned.
- Request bodies and queries have size limits, and sockets have a read timeout.
- Separate /live and /ready endpoints distinguish process health from storage availability.
- Authenticated /metrics exposes aggregate request counts, errors and recent latency without prompt or credential logging.

## Architecture and tradeoffs

The API serves retrieval only, keeping inference billing outside the HTTP exercise. /search derives its tenant from LAB_API_KEYS_JSON and rejects unknown input keys. Four workers are allowed by default. Extra connections receive 503 immediately. This creates a measurable overload behavior instead of accumulating unlimited request threads. The metrics buffer keeps only the most recent 1,000 durations while cumulative counts continue to increase.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 8
```

Start a local demo API:

```bash
export LAB_API_KEYS_JSON='{"local-alpha-demo":"alpha","local-beta-demo":"beta"}'
python -m qwenlabs.operations serve --db results/platform.sqlite --seed-demo --port 8080
```

The keys above are public demonstration values. Use fresh secret values before deploying. Do not expose the standard-library demo server directly to the internet.

## Investigate the behavior

Start the server in one terminal and use the load command from lab 9 in another. Query with alpha and beta keys and verify different source visibility. Send an invalid key, an oversized body and a tenant field. Force all worker slots to be busy and confirm 503. Delete or lock the database and inspect readiness behavior.

## Failure experiments and acceptance criteria

Tenant spoofing must return 400, an invalid bearer token must return 401, and a full admission pool must return 503. Metrics must not include query text, authorization headers or credentials.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_api_auth_and_tenant_spoofing
```

## Build the next version yourself

Move the handler into an ASGI service, preserve the behavior tests, add verified workload identity and export metrics to a collector. Design readiness and admission so overloaded replicas can recover without oscillating traffic. Define a tenant-specific SLO.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

The standard-library HTTP server is a learning boundary, not a hardened internet-facing application server. No TLS, token rotation service, distributed quotas or identity provider integration is included. Readiness probes share the admission pool and may fail during overload. Metrics are process-local and require authentication. This is not Alibaba SLS or managed monitoring integration.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/operations.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
