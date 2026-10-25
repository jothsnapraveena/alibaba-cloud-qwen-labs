# Lab 6: MCP runbook server and Qwen tool bridge

**Level:** Advanced  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 5 first.

[Previous lab](../05-bounded-tool-calling/README.md) · [Next lab](../07-transient-failure-recovery/README.md)

## Engineering objective

Expose tenant-scoped retrieval over a real stdio subprocess and optionally connect discovered tools to Qwen.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- A subprocess exchanges newline-delimited JSON-RPC messages on stdin and stdout.
- The session requires initialize followed by the initialized notification before tool discovery.
- tools/list advertises a JSON input schema and read-only tool annotation.
- tools/call validates query size, top-k, tool name and extra arguments on the server.
- Optional live mode maps discovered schemas into Qwen function tools, executes selected requests through MCP, then returns tool results using the original tool_call_id.

## Architecture and tradeoffs

The host starts a server with a trusted --tenant argument. Tool callers cannot select a different tenant. The server applies that scope before ranking. Discovery metadata describes capabilities but does not grant authorization. The live bridge permits at most three tool calls and at most two logical model requests. Each tool invocation starts a fresh, initialized subprocess session to keep this teaching implementation small and avoid hidden process state.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 6
# Optional, real model calls and possible charges
python -m qwenlabs.run 6 --live
```

Start the MCP server directly after seeding a persistent database:

```bash
mkdir -p results
python -m qwenlabs.run 2 --db results/mcp.sqlite
python -m qwenlabs.mcp_stdio --db results/mcp.sqlite --tenant alpha
```

A host must send valid protocol messages over stdin. Never put informational print statements on stdout. See the pinned [transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) and [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) specifications.

## Investigate the behavior

Run lab 6 and inspect the three actual protocol responses: initialization, discovery and tool result. Send tools/list before initialization and expect rejection. Add tenant=beta to tool arguments and verify schema validation rejects it. In live mode inspect whether Qwen requested the tool, the MCP result and the final answer. Some models may answer without a tool call.

## Failure experiments and acceptance criteria

Malformed JSON should produce a parse error. Unknown methods and tools should produce protocol errors. Invalid tool arguments must not reach retrieval. Notifications must not generate response lines. stdout must contain JSON protocol messages only.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_mcp_process_transport_roundtrip
```

## Build the next version yourself

Replace the small protocol handler with a pinned maintained MCP SDK, preserve these contract tests, add cancellation and integrate a persistent session lifecycle. Separate tool discovery, authorization and audit policy. Do not treat readOnlyHint from an untrusted server as permission.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

This is an educational subset pinned to MCP revision 2025-06-18, not the newest protocol or a general-purpose SDK. No HTTP transport, resources, prompts, cancellation, pagination or conformance certification is claimed. The local subprocess trusts its host and OS boundary. For remote multi-user deployment use a maintained SDK and authenticated transport.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/mcp_stdio.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
