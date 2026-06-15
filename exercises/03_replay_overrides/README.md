# Exercise 3 — Replay & overrides ★

**Theme:** brand-visibility extraction. You run the same prompts daily across
AI engines; your extractor prompt and model choice silently move customer-facing
metrics. Before any change ships, you want *evidence*.

## Steps

1. Baseline: `python replay_demo.py` → note the execution ID.
2. Replay twice: `python replay_demo.py --replay <EXEC_ID>`
   - Replay (a): same model, **edited upstream answer** injected via
     `overrides={"checkpoint.fetch_answers": ...}`
   - Replay (b): same input, **cheaper model alias**.
3. `kitaru executions list` → open all three in the dashboard. Compare:
   - which checkpoints were cached vs re-executed (only the replay root + descendants run)
   - per-call token cost: `strong` vs `cheap`
   - output quality, side by side
4. Same thing from the CLI:
   ```bash
   kitaru executions replay <EXEC_ID> --from extract_mentions \
     --overrides '{"checkpoint.fetch_answers": "…your edited answer…"}'
   ```

## Rules of the road (these will be on the exam — i.e., in your PoC)

- Overrides use the `checkpoint.<name>` prefix and target single-output checkpoints.
- `from_` accepts checkpoint names / invocation IDs; ambiguity raises an error — name your checkpoints deliberately.
- In the CLI, **flow input** overrides go via `--args '{"model_alias": "cheap"}'`,
  **checkpoint output** overrides via `--overrides '{"checkpoint.x": ...}'`.
  In the SDK, flow inputs ride along as plain kwargs on `replay()`.
- You can't pre-populate `wait()` results (humans aren't replayable — Exercise 4).

## Honest framing (really)

A replay is a **counterfactual on the right data distribution** — your actual
production inputs — but it is not an oracle:

- LLMs are stochastic: one replay is an anecdote. Run several before believing a quality delta.
- The further past the injection point, the less the comparison means (divergence compounds).
- **Cost deltas are the hardest number** (token math on identical inputs).
  Quality deltas are evidence, not proof. Use replay to *kill bad candidates
  cheaply*; confirm winners with a small live test.

## Map this to YOUR PoC

| If you're building… | Your replay-regression scenario |
|---|---|
| batch classifier | re-classify last week's sample under taxonomy/prompt v2, diff label shifts |
| source-grounded assistant | replay your golden questions after every re-index |
| fan-out analytics | new extractor prompt vs old, same answers, before customers see it |
| high-stakes copilot | replay a flagged negotiation with a changed strategy prompt |
| persona simulator | same seeded scenario, new model, compare trajectory distributions |
