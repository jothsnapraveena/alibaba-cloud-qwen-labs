# Let Qwen use a read-only tool safely

## What you will build

Complete the assistant-tool-assistant message cycle with application-enforced limits.

## Why it works

Qwen can request lookup_service. Code validates the name and exact arguments against a three-service allowlist. Tool results use the original tool_call_id. The final response disables tools, so a run uses at most two model requests and three local tool executions.

## Before you start

Use Python 3.10 or newer. Run from the repository root. Offline mode needs no account, API key, GPU, or additional packages. For cloud mode, follow the root README configuration instructions. Lab 9 sends five requests; other live labs send one request, except lab 5 which sends at most two.

## Run

```bash
python -m qwenlabs.run 5

# Optional: real cloud calls, may incur charges
python -m qwenlabs.run 5 --live
```

## Walkthrough

Run the offline tool fixture. Inspect TOOL and execute_tool. Try an unknown name and a path traversal string. In live mode inspect the count of requested calls and the final response.

## Expected behavior

Offline mode returns the local OSS glossary entry. Live mode may request the tool or answer without it.

## Limits and troubleshooting

This is function calling, not MCP. A real MCP integration also needs protocol transport, authorization, and server trust. Do not extend this allowlist to shell execution or resource creation without separate controls.

## Your contribution exercise

Run the example yourself, explain the design in your own words, add one meaningful failure case, and publish what you learned with reproducible commands. Record actual observations, including failures. A fixture run is not proof of Alibaba Cloud usage.

## Source and implementation

- [Runnable implementation](../../qwenlabs/run.py)
- [Shared client](../../qwenlabs/client.py)
- [Core helpers](../../qwenlabs/core.py)
- [Tests](../../tests/test_labs.py)
- [Alibaba Cloud Model Studio API documentation](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
