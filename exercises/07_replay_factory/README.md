# Exercise 7 — The Replay Factory (capstone / advanced track)

> ★★ The thesis of the whole workshop, made runnable. This is the answer to
> "isn't this too simple?" — it's the loop that experienced agent builders
> haven't closed yet.

**The loop:**

```
ingest cases → run baseline + candidate model → LLM-judge good/bad →
aggregate → ship / don't-ship verdict (regressions named)
```

You have a batch of production **cases** (`cases.jsonl` — question + reference
answer). The factory runs each through the agent under two models, an LLM judge
scores both against the reference, and you get a verdict: does the cheaper model
hold up, and if not, *exactly which cases it broke*.

## Run it

```bash
# register two model aliases first (see prework)
kitaru model register strong --model openai/gpt-5.2  --secret <your-openai-secret>
kitaru model register cheap  --model openai/gpt-5-nano --secret <your-openai-secret>

python factory.py
# or: python factory.py --baseline strong --candidate cheap --cases cases.jsonl
```

Real output from the provided batch (verified live, kitaru 0.15.0):

```
=== Replay Factory report ===
  cases:               8
  baseline (strong):   100% pass
  candidate (cheap):   100% pass
  regressions:          0
  VERDICT: SHIP          # the cheaper model held up — cost cut, with evidence
```

When the candidate breaks a case the baseline got right, the verdict flips and
names it (`VERDICT: DO NOT SHIP` + the regression list). Make the candidate a
weaker model, or add harder/adversarial cases to `cases.jsonl`, to see it.

The `replay_factory_report` artifact and per-checkpoint cost are in the dashboard.

## Why this is the capstone

- **The eval loop is itself a Kitaru flow** — three durable checkpoints
  (`load_cases → run_and_judge → aggregate`). Crash during aggregation and the
  expensive LLM batch is **cached**; you don't re-pay. That's the workshop's
  entire thesis applied to evaluation.
- **Eval the eval**: if a judgment looks wrong, `replay` the factory from the
  `aggregate` checkpoint with a better rubric — the runs are cached, only the
  scoring re-executes.
- **Where it goes**: good/bad judgments become your **regression set** → an eval
  dataset → eventually the **reward signal for RL** on a cheaper open model.
  That's the cost endgame the whole "AI spend is the new headcount" story points at.

## Cost is first-class (kitaru 0.16.0)

Tracked `kitaru.llm()` calls record input/output token counts as execution
metadata — split into freshly-incurred vs replay-reused — and you can aggregate
across the batch with `kitaru executions statistics` (or
`KitaruClient().executions.statistics(...)`), grouped by flow/stack/tag/metadata.
So "is the cheaper model actually cheaper?" has a real number behind the verdict,
not just vibes.

## pass^k — reliability, not one-shot

```bash
python factory.py --samples 3      # 3 candidate rollouts per case
```

LLMs are stochastic, so one run is an anecdote. `pass^k` (from τ-bench) = the
chance a case passes on **all** k rollouts; it decays fast (gpt-4o: 61% pass^1 →
<25% pass^8). The report shows `pass^1` and `pass^k`, and a case only counts as a
regression if the candidate fails pass^k — "ship the cheaper model only if it's
*reliably* good." See `instructor/EVALS_PRIMER.md` §4.

## Honest scope & the multi-turn frontier

- **Ingestion is a JSONL stand-in for exported traces.** True one-click import
  from LangFuse / Datadog is the **roadmap edge**, not a shipped button.
- **This capstone is single-turn replay** — same input, compare outputs. That's
  the safe, cheap, high-value case.
- **Multi-turn replay is the open frontier and is NOT what this does.** Replaying
  a conversation under a new agent is *off-policy*: the recorded user turns
  answered the OLD agent, so past the first divergence the recording is invalid.
  User simulators (the literature's fallback) are unreliable (±9pp by simulator
  choice, "easy mode" inflation). The unsolved hybrid is **divergence-gated
  replay**. Full treatment + citations: `instructor/EVALS_PRIMER.md` §2 & §5.
- The judge is a single LLM-as-judge pass with a real cross-turn blind spot
  (~1 in 5 cross-turn defects caught). Production-grade wants juries +
  state-tracking + rubrics derived from defect taxonomies. EVALS_PRIMER §3.

## The kitaru data-flow rule this exercise teaches (learned the hard way)

Inside a `@flow`, a checkpoint's **return value is an artifact handle**, not the
raw value. Two failure modes we hit building this:

- Iterating/subscripting a checkpoint's `list[dict]` output in flow scope →
  silently became tuples (`TypeError: tuple indices must be integers`).
- `json.loads()` on a checkpoint output in flow scope → `the JSON object must be
  str ... not _KitaruOutputArtifact`.

**Fix / pattern:** the flow body only *wires* checkpoint→checkpoint (or returns
a checkpoint output); all parsing/looping happens *inside* checkpoints, and we
pass JSON strings across boundaries. Flow *inputs* are real values (safe to
iterate); checkpoint *outputs* are handles. See `factory.py`.
