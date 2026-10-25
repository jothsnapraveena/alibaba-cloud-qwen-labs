# Alibaba Cloud Qwen Engineering Labs

A progressive intermediate-to-advanced series that builds a small tenant-aware AI knowledge and operations platform. The focus is on engineering behavior: recovery, retrieval quality, authorization, durable state, MCP boundaries, multi-agent contracts and measurable serving limits.

Independent educational work for Jothsna Praveena Pendyala's community learning and teaching. Not affiliated with or endorsed by Alibaba Cloud. Prepared with AI assistance and locally tested. Author review, live cloud verification and community publication remain separate steps.

## The progression

| Lab | What you build | Level |
| --- | --- | --- |
| 1 | [Resilient Qwen inference gateway](labs/01-first-qwen-call/README.md) | Intermediate |
| 2 | [Incremental tenant-aware document ingestion](labs/02-validated-extraction/README.md) | Intermediate |
| 3 | [Hybrid RAG with BM25, embeddings and rank fusion](labs/03-rag-from-chunks/README.md) | Upper intermediate |
| 4 | [Retrieval evaluation and regression gates](labs/04-retrieval-evaluation/README.md) | Upper intermediate |
| 5 | [Durable workflows, approval pauses and idempotency](labs/05-bounded-tool-calling/README.md) | Advanced |
| 6 | [MCP runbook server and Qwen tool bridge](labs/06-content-free-observability/README.md) | Advanced |
| 7 | [Contract-driven multi-agent evidence review](labs/07-transient-failure-recovery/README.md) | Advanced |
| 8 | [Tenant-isolated HTTP API and operational metrics](labs/08-governed-workflow/README.md) | Advanced capstone, part 1 |
| 9 | [Load, chaos and ACK deployment capstone](labs/09-benchmark-and-container/README.md) | Advanced capstone, part 2 |

The old directory names remain stable so existing links still work. Their content and the runnable commands now implement this progression. The original `client.py` and `core.py` remain as introductory helper examples and legacy regression coverage. The new platform uses `gateway.py`, `platform.py`, `mcp_stdio.py` and `operations.py`.

## Quick start

```bash
git clone https://github.com/jothsnapraveena/alibaba-cloud-qwen-labs.git
cd alibaba-cloud-qwen-labs
python -m unittest discover -s tests -v
python -m qwenlabs.run 1
python -m qwenlabs.run 6
python -m qwenlabs.run 9
```

Use Python 3.10+. The local components use the standard library. Model inference is explicitly replaced by fixtures in offline mode. SQLite transactions, BM25, rank fusion, the MCP subprocess, HTTP serving and concurrent load are real local code paths.

## Optional Model Studio execution

Activate Model Studio, obtain a regional API key and copy the exact workspace base URL from your console. Verify the available chat and embedding models in that region.

```bash
export DASHSCOPE_API_KEY='YOUR_KEY'
export DASHSCOPE_BASE_URL='https://YOUR_WORKSPACE_ID.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1'
export QWEN_MODEL='qwen-plus'
export QWEN_EMBED_MODEL='text-embedding-v4'
python -m qwenlabs.run 3 --live
```

Live mode is supported in labs 1, 3, 6 and 7. It can incur charges. Lab 1 has a six-attempt shared budget for three concurrent calls. Lab 3 permits up to three attempts across embeddings and generation. Lab 6 permits up to four attempts across tool selection and final generation, with at most three local tool calls. Lab 7 permits six attempts across three roles. These are request limits, not currency budgets. Chat output is capped at 512 tokens per request. `.env.example` is a reference and is not loaded automatically.

Live lab 3 uses Model Studio embeddings. Offline vectors use signed feature hashing and are not a pretrained semantic model. The MCP implementation is pinned to the 2025-06-18 protocol subset. It is not a claim of compatibility with every current client or the latest revision.

## Cumulative architecture

The gateway contains provider failures and budgets. Ingestion writes tenant-scoped source versions and chunks. Retrieval combines lexical and vector channels. Evaluation checks ranking changes. Durable workflows persist approval boundaries and local effects. MCP exposes authorized retrieval to a host. Multi-agent roles operate under contracts and a shared budget. The HTTP boundary and capstone exercise load, failures and deployment constraints.

## Run the API and load test

```bash
export LAB_API_KEYS_JSON='{"local-alpha-demo":"alpha","local-beta-demo":"beta"}'
python -m qwenlabs.operations serve --db results/platform.sqlite --seed-demo
```

In another terminal:

```bash
export LAB_API_KEY='local-alpha-demo'
python -m qwenlabs.operations load --requests 100 --workers 8
```

These public demo keys are suitable only for local experiments. The API serves retrieval and does not invoke Qwen. See [ACK deployment instructions](deploy/README.md) for the container and manifest boundaries.

## Validation and contribution evidence

See [VALIDATION.md](VALIDATION.md) for the exact checks and unverified cloud steps. Behavior tests cover concurrency limits, retries, circuit recovery, tenant prefiltering, stale checkpoint conflicts, replay-safe local effects, protocol lifecycle, tool argument rejection, role output contracts, API authorization and overload.

[CONTRIBUTIONS.md](CONTRIBUTIONS.md) tracks the nine teaching artifacts. Publishing a repository does not automatically establish nine accepted MVP contributions. Add your reviewed explanations, real experiments, public teaching and community feedback before making an award claim.

## Sources

- [Alibaba Cloud Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
- [Model Studio embeddings](https://www.alibabacloud.com/help/en/model-studio/embedding)
- [MCP 2025-06-18 transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [MCP 2025-06-18 tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Alibaba Cloud MVP program](https://mvp.alibabacloud.com/)
