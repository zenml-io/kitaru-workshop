# Exercise 1 — Your first durable flow (no API key needed)

**Theme:** bounce-message triage — millions of emails a day, every undelivered
message needs a *reason*, not a statistic.

## Steps

1. Run it: `python flow.py` — note the execution ID it prints.
2. Run it again, but press **Ctrl+C while `correlate` is sleeping**.
3. Run it a third time. Watch the logs: `fetch_bounces` and `classify` are
   **cached** — only `correlate` re-executes. That's durable execution.
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

## Bonus: same code, different stack (verified live)

A *stack* is where your flow runs and where artifacts live. Swapping it is one
command — the flow code doesn't change:

```bash
kitaru stack list                 # see what's available on your server
kitaru stack use local_remote     # e.g. local runner + S3 artifact store
python flow.py                    # same code — artifacts now land in S3
```

Cloud artifact stores need their integration deps once per environment
(the error message tells you exactly what):

```bash
pip install 's3fs>2022.3.0,!=2025.3.1' boto3 aws-profile-manager   # for S3
```

Caching and replay work identically across stacks — checkpoints cache even
with a remote artifact store. This is how your PoC goes from laptop to cloud
without touching the code.

## The point

Your PoC's pipeline *will* die mid-run — rate limits, OOM, a flaky API.
Checkpoints mean you don't re-pay (in time or tokens) for what already succeeded.
