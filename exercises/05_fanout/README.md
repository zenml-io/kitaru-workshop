# Exercise 5 — Fan-out at scale (instructor demo)

> 🏠 **Take-home** — gets one sentence + a recording in the 2h session.

**Theme:** a synthetic persona panel reacting to a draft press statement —
six personas here, hundreds in production. Stochastic outputs, parallel
execution, and the cost meter running the whole time.

## What the demo shows

1. `@checkpoint(runtime="isolated")` — each persona reaction runs in its own
   container. One persona OOMs or hangs → the other five don't care.
2. `.submit()` / gather — fan-out parallelism without writing a thread pool.
3. The dashboard during the run: six parallel checkpoints, each with its own
   logs, cost, and output. Then the aggregate.
4. **The replay kicker:** rerun the *same seeded panel* against a new statement
   (or a new model) via overrides and compare sentiment distributions —
   regression testing for a simulator.

## Why `cheap` and not `strong`?

Panels multiply: personas × rounds × scenarios. This is exactly the workload
where the "can we run this on a smaller/cheaper model?" question pays for
itself — and where you want per-call cost in a dashboard rather than a
surprise invoice. (Cheap model + many samples often beats expensive model +
few samples for distribution-shaped outputs.)

## Finale: agent-native operations

The instructor points Claude/Cursor at `kitaru-mcp` and asks it to:
list the latest executions → fetch the panel artifact → trigger a replay.
No UI, no docs lookup — an agent operating the platform that runs agents.
