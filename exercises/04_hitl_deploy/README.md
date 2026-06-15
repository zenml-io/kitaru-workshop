# Exercise 4 — Human-in-the-loop + shipping

> 🏠 **Take-home exercise** — in the 2h workshop the chatbot demo (Module 3) shows `wait()` in action; run this yourself to build an approval gate.

**Theme:** counter-offer drafting with an approval gate. The draft involves
money and a legal relationship: a human signs off, full stop.

## Part A — the wait() gate

1. `python approval_flow.py` — the execution suspends at `kitaru.wait("approval")`.
2. **Key observation:** check your process list / the dashboard. The execution
   is *suspended*, not *running*. No compute is burning while the reviewer thinks.
   (Compare: a `while not approved: sleep(60)` loop in a pod — paying for nothing.)
3. From a second terminal:
   ```bash
   kitaru executions list                     # find the ID with status "waiting"
   kitaru executions logs <ID>                # read the DRAFT before you decide
   kitaru executions input <ID> --value true  # resolves AND resumes automatically
   ```
   (The draft is generated inside a checkpoint, so its preview shows in
   `executions logs` / the dashboard — and is saved as the `draft_offer`
   artifact — rather than in the terminal that launched the run.)
   (`kitaru executions resume <ID>` exists for runs that didn't continue on
   their own. Note: `--value true` works because the wait declares `schema=bool`;
   a schema-less `kitaru.wait(name=...)` is a plain continue-gate resolved with
   `--value null`.)
4. Watch it resume *exactly where it left off* — the draft checkpoint is cached,
   only `finalize` runs.
5. Run it again and reject it (`--value false`). Different path, same durability.

## Part B — ship it

Deploy straight from the CLI — no script needed (the `<file>:<flow>` target is
the same pattern as the chatbot in Module 3):

```bash
kitaru deploy approval_flow.py:counter_offer --tag prod --stack <remote-stack> --exclusive
```

(Equivalent in-script path if you prefer: `python approval_flow.py --deploy`,
which just calls `counter_offer.deploy()`.)

- Deployments are **immutable, versioned snapshots** of your flow.
- Tag-based canary/rollback: point the `production` tag at v2; if it misbehaves,
  point it back. No redeploy, no rebuild.
- **TypeScript folks, this is your slide:** your frontend never imports Python —
  it calls a deployed flow by name over the REST API:
  ```python
  KitaruClient().deployments.invoke(flow="counter_offer", inputs={...})
  ```

## Try it

- Add a second `wait()` for a "legal review" after finalize. Two gates, still zero idle compute.
- What happens if you `replay` an execution that contains a `wait()`? (Hint:
  wait results can't be pre-populated — humans aren't replayable. Discuss why
  that's a feature.)
