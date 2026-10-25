# Alibaba Cloud Qwen Community Labs

Nine practical Python labs for learning Qwen and Alibaba Cloud Model Studio, with runnable offline exercises, optional live inference, and guides that explain the limits of each example.

Created for Jothsna Praveena Pendyala's community learning and teaching work. Independent educational project. Not affiliated with or endorsed by Alibaba Cloud. Prepared with AI assistance and checked locally. Live cloud verification and independent author review are still required.

## Start here

```bash
git clone https://github.com/jothsnapraveena/alibaba-cloud-qwen-labs.git
cd alibaba-cloud-qwen-labs
python -m qwenlabs.run 1
python -m unittest discover -s tests -v
```

Python 3.10+ is sufficient. All examples use the standard library. Offline mode never calls a model or simulates a measured cloud result.

## Nine labs

1. [Your first Qwen call with Alibaba Cloud Model Studio](labs/01-first-qwen-call/README.md)
2. [Validate Qwen output before using it](labs/02-validated-extraction/README.md)
3. [Build a small Qwen RAG pipeline from first principles](labs/03-rag-from-chunks/README.md)
4. [Evaluate retrieval before judging generation](labs/04-retrieval-evaluation/README.md)
5. [Let Qwen use a read-only tool safely](labs/05-bounded-tool-calling/README.md)
6. [Observe Qwen calls without logging prompts](labs/06-content-free-observability/README.md)
7. [Recover from transient failures with bounded retries](labs/07-transient-failure-recovery/README.md)
8. [Build a bounded draft-review workflow with Qwen](labs/08-governed-workflow/README.md)
9. [Benchmark and containerize a Qwen learning application](labs/09-benchmark-and-container/README.md)

## Optional live cloud configuration

Activate Alibaba Cloud Model Studio. Obtain an API key for the same region as your workspace endpoint, then select a model available in that region. Copy the exact HTTPS OpenAI-compatible base URL from the console and current documentation. Do not guess endpoint names across regions.

```bash
export DASHSCOPE_API_KEY='YOUR_KEY'
export DASHSCOPE_BASE_URL='https://YOUR_WORKSPACE_ID.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1'
export QWEN_MODEL='qwen-plus'
python -m qwenlabs.run 1 --live
```

The URL above illustrates a Singapore workspace. Replace YOUR_WORKSPACE_ID and verify model availability. Variables are read from the environment. The .env.example file is a reference and is not loaded automatically. Never commit keys. Cloud requests may cost money. Output is capped at 256 tokens per request. Lab 5 makes at most two model requests, lab 9 makes five, and the other cloud-enabled labs make one. Labs 4 and 7 are local only.

## What has been verified

Local tests and all nine offline commands are exercised during preparation. The API request construction is tested with a mocked HTTP response. No real cloud credentials were used. No claims of hosted inference performance, cloud deployment, upstream acceptance, or MVP eligibility are made. See [VALIDATION.md](VALIDATION.md).

## From labs to community contributions

Each lab is a starting point for an original tutorial or workshop. Run the live steps where applicable, review and revise the explanation yourself, and publish useful observations. Record public links, publication dates, reader questions, and fixes in [CONTRIBUTIONS.md](CONTRIBUTIONS.md). Nine folders or commits do not automatically equal nine accepted MVP contributions. This repository is your own educational contribution, not a contribution accepted into Alibaba's upstream repositories.

## References

- [Official Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
- [Alibaba Cloud MVP program](https://mvp.alibabacloud.com/)
- [Published nomination categories](https://www.alibabacloud.com/en/mvp/nominate)

Documentation and availability change. Verify current program terms and model configuration before applying or running live exercises.
