# Validation record

Verified locally on 2026-10-25 with Python 3.12.14.

- 35 unit and integration tests passed.
- All nine offline CLI commands passed.
- MCP initialization, discovery and calls tested over a real stdio subprocess.
- Qwen-to-MCP bridge tested with model-shaped fixtures and real subprocess tool execution.
- HTTP authentication, tenant override rejection and overload tested on localhost.
- Gateway concurrency, budgets, retries, circuit recovery and embedding response contracts tested.
- Durable checkpoint conflict and replay-safe local effects tested with SQLite.
- Model Studio inference and embeddings: not run, no real credentials used.
- Docker build and ACK deployment: not run.
- GitHub Actions: consult the Actions tab for its independent status.

The retrieval evaluation uses 20 synthetic cases. Offline vectors use feature hashing, not pretrained semantic embeddings. Fixture model output and local load timings are not evidence of hosted-model quality or performance.
