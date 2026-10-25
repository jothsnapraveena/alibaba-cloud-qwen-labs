# Lab 5: Durable workflows, approval pauses and idempotency

**Level:** Advanced  
**Prerequisites:** Python functions, exceptions, JSON, HTTP and SQL. Complete labs 1 through 4 first.

[Previous lab](../04-retrieval-evaluation/README.md) · [Next lab](../06-content-free-observability/README.md)

## Engineering objective

Persist an agent workflow so it can pause, resume and reject stale workers without duplicating local effects.

This lab is one part of a cumulative platform. Work through the implementation and failure cases before treating the guide as material you can teach independently.

## Implemented components

- SQLite persists each run’s state and revision.
- Retrieval checkpoints into awaiting_approval before any action is committed.
- A compare-and-swap revision check rejects stale workers.
- Checkpoint, event record and a local ticket side effect commit in one transaction.
- Repeated completion calls return the completed state without inserting another ticket.

## Architecture and tradeoffs

DurableWorkflow advances one transition at a time. The first step saves selected source IDs and pauses. A trusted host can supply approve=True to commit a local review ticket. Index.save updates only the revision it previously read. If another worker already advanced the run, the transaction fails before its event or side effect can commit. This gives atomic, replay-safe behavior for that local SQLite effect, not universal exactly-once execution.

## Run the implementation

Run from the repository root with Python 3.10 or newer. No third-party packages are needed for the local components. Offline fixtures replace model inference, not the database, protocol process, HTTP server or concurrency controls.

```bash
python -m qwenlabs.run 5
```

Keep state between runs:

```bash
mkdir -p results
python -m qwenlabs.run 5 --db results/workflow.sqlite
```

The demonstration explicitly supplies approval after showing the pause. To study a real pause, call `Index.start` and `DurableWorkflow.advance` separately and stop before passing `approve=True`.

## Investigate the behavior

Use --db results/workflow.sqlite to keep the database. Inspect runs, events and tickets with SQLite. Instantiate a new Index and DurableWorkflow after the pause to simulate losing all in-memory objects. Attempt two writes from the same revision. Observe one success and one conflict. The demo explicitly simulates approval; it does not collect a human approval automatically.

## Failure experiments and acceptance criteria

A stale worker must not create a ticket. A tenant cannot load another tenant’s run. Repeating advance after completion must leave exactly one ticket. A pause without approval must not advance.

```bash
python -m unittest discover -s tests -v
# Focus on the test class or case named below in tests/test_platform.py:
# Storage.test_approval_pause_restart_and_replay
```

## Build the next version yourself

Add an authenticated approver identity, approval expiry, evidence-version hashes and an outbox dispatcher. Inject a crash after the external provider succeeds but before local acknowledgement and show how reconciliation resolves ambiguity.

Document your implementation choices, measurements and failed approaches. Include commands that another developer can reproduce. Add a test that fails before your change and passes afterward.

## Current boundaries

Approval is a trusted-host argument, not an authenticated approval service. The sample stores source IDs but does not snapshot source versions, so source updates can make evidence stale. Local SQLite atomicity does not extend to email, cloud API calls or payments. External effects need an outbox, provider idempotency keys and reconciliation.

## Evidence for a community contribution

Publish a walkthrough using your own reviewed explanation, a live demonstration when relevant, and the failure experiment above. Record model, region, corpus, run date and costs only when observed. Track actual reader questions and improvements in [CONTRIBUTIONS.md](../../CONTRIBUTIONS.md). A local fixture or generated guide is not evidence of hosted-model quality or community impact.

## Code and sources

- [Main implementation](../../qwenlabs/platform.py)
- [Runnable lab](../../qwenlabs/run.py)
- [Behavior tests](../../tests/test_platform.py)
- [Validation record](../../VALIDATION.md)
- [Official Model Studio API](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
