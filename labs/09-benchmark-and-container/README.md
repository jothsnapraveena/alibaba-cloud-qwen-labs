# Lab 9: Load, chaos and ACK deployment capstone

**Level:** Advanced capstone, part 2  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 8 first.

[Previous lab](../08-governed-workflow/README.md) · [Series overview](../../README.md)

## Engineering objective

Run concurrent load, inject failures, interpret SLOs and prepare a constrained Kubernetes deployment for ACK.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- A configurable thread pool issues 100 requests by default with bounded concurrency.
- Latency percentiles are calculated for successful requests and errors are reported separately.
- Throughput, error rate and an explicit error-and-latency SLO are reported.
- The offline chaos scenario injects five failures and should fail the error SLO.
- The deployment example includes a PVC, resource limits, security context, probes and a secret reference rather than embedded keys.

## Architecture and tradeoffs

Success latency and failure counts must be interpreted together. Fast errors must not make latency look healthy. The synthetic run calls the real local retrieval path and injects one timeout every 20 requests. A separate HTTP load mode tests the actual serving boundary from lab 8. Docker and ACK examples use one replica because the teaching implementation stores shared state in local SQLite on one PVC. This is not a horizontally scalable state architecture.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 9
```

With lab 8 running in another terminal:

```bash
export LAB_API_KEY='local-alpha-demo'
python -m qwenlabs.operations load --requests 100 --workers 8

docker build -t qwen-community-labs:0.2 .
docker run --rm qwen-community-labs:0.2
```

For API serving in a container, mount `/data`, pass `LAB_API_KEYS_JSON` from your environment, and override the entry point:

```bash
docker run --rm -p 8080:8080 --env LAB_API_KEYS_JSON --mount type=volume,source=qwen-labs-data,target=/data --entrypoint python qwen-community-labs:0.2 -m qwenlabs.operations serve --host 0.0.0.0 --db /data/platform.sqlite --seed-demo
```

For ACK, read [deploy/README.md](../../deploy/README.md) before using [ack.yaml](../../deploy/ack.yaml). These are deployment instructions and manifests, not a claim of a completed cloud deployment.

## Investigate the behavior

Run the offline chaos scenario and verify exactly five failures. Start the API and run HTTP load at 1, 4, 8 and 16 workers. Compare errors, successful p95 and throughput. Build the Docker image. Review deploy/ack.yaml, replace its image placeholder and configure a compatible StorageClass before applying it to an authorized cluster. Preserve raw reports with environment metadata.

## Failure experiments and acceptance criteria

Injected 5 percent faults must make the 1 percent error SLO fail. All-failure runs must report null latency rather than crash. A read-only container root must still allow SQLite writes only on the mounted data volume.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# GatewayTests.test_load_harness_counts_failures
```

## Build the next version yourself

Replace SQLite with a transactional service and persistent vector index, then add multiple replicas, HPA or KEDA based on queue pressure, secret rotation, backup recovery and failure-domain tests. Benchmark Qwen with actual prompt lengths, token counts, warmup and provider rate limits separately from this retrieval-only load.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

The 500 ms p95 and 99 percent success thresholds are demonstration targets, not recommended SLAs. A 100-request local run does not prove GPU throughput or hosted-model capacity. Docker and ACK deployment have not been executed here. The YAML has no public ingress, TLS, autoscaling, backup or network policy. PVC-backed SQLite is single-instance teaching storage.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/operations.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
