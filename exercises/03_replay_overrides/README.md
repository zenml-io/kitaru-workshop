# Exercise 3 — Replay & overrides ★

**Theme:** brand-visibility extraction. You run the same prompts daily across
AI engines; your extractor prompt and model choice silently move customer-facing
metrics. Before any change ships, you want *evidence*.

## Steps

> **Run these from the project root** (the `kitaru init` source root), not from
> inside this folder — replay re-imports the flow module and can't resolve it
> from the exercise directory (`KitaruRuntimeError: Failed to import replay
> source module`).

1. Baseline: `python exercises/03_replay_overrides/replay_demo.py` → note the execution ID.
2. Replay twice: `python exercises/03_replay_overrides/replay_demo.py --replay <EXEC_ID>`
   - Replay (a): same model, **edited upstream answer** injected via
     `overrides={"checkpoint.fetch_answers": ...}`
   - Replay (b): same input, **cheaper model alias**.
3. **The token diff prints right in the replay output** — each line shows
   `model=… tokens in/out/total=…` (e.g. `strong` 96/201/297 vs `cheap`
   86/1971/2057; the cheaper model often *rambles*, so cheaper ≠ fewer tokens).
   Then `kitaru executions list` → open all three in the dashboard to compare:
   - which checkpoints were **cached vs re-executed** (only the replay root +
     descendants run — `fetch_answers` is skipped)
   - **per-call tokens** on the `extract_mentions` checkpoint, `strong` vs `cheap`
   - output quality, side by side

   > 💲 Dollar cost shows only when Kitaru has pricing for the model. For
   > unpriced models (e.g. `gpt-5.2`/`gpt-5-nano`) cost is blank — **tokens** are
   > the reliable comparison, and they're always tracked.
4. Same override from the CLI (put **real** text in the override, not the
   placeholder!):
   ```bash
   kitaru executions replay <EXEC_ID> --from extract_mentions --overrides '{"checkpoint.fetch_answers": "Asana and Linear lead; ClickUp is rising fast for hybrid teams."}'
   ```
   The CLI `replay` **launches a new execution and returns — it does not print
   the result.** See the output via the dashboard, or:
   ```bash
   kitaru executions logs <NEW_EXEC_ID>     # the run's logs
   kitaru executions get  <NEW_EXEC_ID>     # status + the mentions_report artifact
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
- **Watch out — "cheaper" model ≠ fewer tokens.** In a sample run, `cheap`
  emitted ~1900 output tokens vs `strong`'s ~200 (it rambled), so the cheaper
  *per-token* model was the more expensive *call*. That's exactly why you
  measure instead of assuming. (Dollar cost shows only when Kitaru has pricing
  for the model; tokens are always tracked, so the token diff is what you
  compare here.)

## Map this to YOUR PoC

| If you're building… | Your replay-regression scenario |
|---|---|
| batch classifier | re-classify last week's sample under taxonomy/prompt v2, diff label shifts |
| source-grounded assistant | replay your golden questions after every re-index |
| fan-out analytics | new extractor prompt vs old, same answers, before customers see it |
| high-stakes copilot | replay a flagged negotiation with a changed strategy prompt |
| persona simulator | same seeded scenario, new model, compare trajectory distributions |
