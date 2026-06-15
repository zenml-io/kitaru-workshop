# Exercise 1 — Your first durable flow (no API key needed)

**Theme:** bounce-message triage — millions of emails a day, every undelivered
message needs a *reason*, not a statistic.

## Steps

1. Run it: `python flow.py` — note the execution ID it prints (`correlate`
   sleeps ~10s on purpose).
2. Run it again. Watch the logs: `fetch_bounces` and `classify` come back
   **cached** instantly — only `correlate` re-executes. That's durable
   execution. (`correlate` is marked `@checkpoint(cache=False)` so it always
   re-runs and the lesson lands every time.)
3. Bonus — same lesson the hard way: run it and press **Ctrl+C while
   `correlate` is sleeping**, then re-run. The completed checkpoints are still
   cached; you never re-pay for finished work.
4. Explore:
   ```bash
   kitaru executions list
   kitaru executions get <ID>
   kitaru executions logs <ID>
   ```
5. Open the dashboard and find your execution, its checkpoints, and the
   `bounce_summary` artifact.

## Try it (if you're ahead)

- Add a new bounce category to `TAXONOMY` and re-run. Which checkpoints re-execute? Why?
- `kitaru.load("bounce_summary")` from a separate Python REPL — artifacts outlive executions.
- Change `limit` and observe what caching does with different inputs.

> **Stacks** (where a flow runs + where artifacts live) come later, in
> Module 3 — that's where "same code, now on the cloud" pays off, next to
> deployments. Module 1 stays focused on one idea: durable checkpoints.

## The point

Your PoC's pipeline *will* die mid-run — rate limits, OOM, a flaky API.
Checkpoints mean you don't re-pay (in time or tokens) for what already succeeded.
