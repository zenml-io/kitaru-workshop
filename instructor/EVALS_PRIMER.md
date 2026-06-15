# Evals Primer — multi-turn conversational agents, with replay

> Instructor depth for the evals questions this audience *will* ask. Sourced
> from a verified literature sweep (mostly Jan–Jun 2026 — fast-moving, several
> preprints; treat specific percentages as illustrative, directions as solid).
> Doubles as product intel for the replay-from-traces thesis.

## TL;DR for the stage

- Two eval axes have won: **outcome/state-based** (objective, needs a backend)
  and **trajectory/turn-aware LLM-judge** (no backend, scores the path).
- The honest landmines, in order of how much they matter to a *replay* product:
  1. **User simulators are unreliable** — the central validity threat.
  2. **LLM-judges have a cross-turn blind spot** — weakest exactly where
     multi-turn matters.
  3. **n=1 is an anecdote** — the field standard is **pass^k**.
  4. **Off-policy replay** — recorded user turns answered the *old* agent;
     past the first divergence the recording is invalid. The open frontier.

---

## 1. The two axes

### Outcome / state-based (the trusted one)
τ-bench (Sierra, ICLR 2025) scores success by **deterministically comparing the
final database state to an annotated goal state** — not by judging text. An LLM
simulates the user, so the conversation is stochastic, but the reward is
objective. τ²-bench (Jun 2025) extends this to **dual-control** (both agent *and*
user act on a shared environment, a Dec-POMDP) — agents drop ~20pp moving from
no-user to dual-control, showing "coordinate with a user" is a distinct, harder
skill than solo tool use.

- **Valid when:** you have an executable backend and a definable goal state.
- **Limit:** most production agents don't have a clean goal-state oracle; and
  pure state-checking misses *how* the agent got there.

### Trajectory / turn-aware (the scalable one)
TED ("Talk, Evaluate, Diagnose", ICLR 2026) scores a trajectory against
**"grading notes"** — NL checklists of subgoals (tool calls, tool-call *order*,
key responses) judged by an LLM **without environment/state access**. Introduces
turn-aware metrics (MaxProgressRate@k, MaxAUC@k rewarding *early* progress)
beyond final-success-only (MINT) and pass@k.

- **Proxy state-based eval** (PayPal, Feb 2026) bridges the two: an LLM "state
  tracker" infers a structured proxy state from the trace, then judges verify
  goal completion + hallucinations against it — final-state evaluation *without*
  a deterministic backend. Self-reported agreement is contested (headline ">90%"
  but only 82.7% three-way on goal completion; a "this proves reliability"
  framing was refuted in our sweep). Promising, not settled.

---

## 2. The user-simulator validity crisis (read this twice)

This is THE finding for a replay/simulation eval product.

- **Simulator choice alone moves agent success up to 9 percentage points**
  ("Lost in Simulation", arXiv 2601.17087, 451 real humans across US/India/
  Kenya/Nigeria).
- LLM simulators are an **"easy mode"** — excessively cooperative, stylistically
  uniform, front-load information, lack frustration/ambiguity/pushback. Best
  simulator User-Sim Index **76.0 vs humans 92.9** ("Mind the Sim2Real Gap",
  2603.11245).
- **Systematically miscalibrated by difficulty** — underestimate on hard tasks,
  overestimate on moderate ones. They blame the agent for failures 48.9% of the
  time vs humans' 24.5%, and surface *different failure modes* than real users.
- Miscalibration varies by **dialect/demographic** (AAVE ECE 20.3 vs SAE 11.7) —
  a fairness landmine if you ship simulator-based eval as ground truth.

**Implication for the product:** never present a simulator score as truth.
Position it as a *cheap pre-filter*; the human/production signal is the anchor.
Ensemble simulators to bound the variance, and always report which simulator
produced a number.

---

## 3. LLM-as-judge for multi-turn

- **The cross-turn blind spot** ("Catching One in Five", 2606.10315, production
  food/bev agent): judge recall **degrades monotonically with how cross-turn a
  problem is**. Turn-local surface errors (fabricated stats, wrong language) get
  caught; cross-turn state issues (confirm-gate state, cart contents, escalation
  flags, stale referents) get missed. One batch: **22% recall**; another: a judge
  flagged **zero** failures against **23 human-confirmed defects**. Half of defect
  patterns fell into dimensions the rubric **had no category for**.
- **Known biases** (MT-Bench lineage, 2306.05685 and follow-ons): position,
  verbosity, self-enhancement. Mitigations: pairwise > pointwise for stability;
  randomize position; **panels/juries of cheaper diverse judges** (2404.18796)
  often beat a single strong judge and cut cost.
- **Rubric design is the lever**: the blind-spot study's root cause was a rubric
  exposing only 3 coarse axes (intent, brand-voice, personalization) — so it
  *structurally could not see* state-tracking/guardrails/recovery/safety. If a
  dimension isn't in the rubric, the judge is blind to it. Derive rubric
  categories from real defect taxonomies, not from intuition.

**Implication:** a single rubric'd judge is a turn-local smoke detector, not a
multi-turn oracle. For cross-turn correctness, pair it with state-tracking
(proxy-state) and a panel, and validate recall against human-labeled cross-turn
defects specifically — not aggregate agreement (headline agreement % hides the
cross-turn collapse).

---

## 4. Stochasticity: pass^k, not n=1

- **pass^k** = probability that **all** k i.i.d. trials succeed (p^k — decays
  exponentially). Measures *reliability*, the opposite of pass@k (≥1 of k).
- gpt-4o on τ-bench: pass^1 ~61% retail → **pass^8 < 25%**. The agent that "works"
  one-shot is wildly inconsistent across runs.
- **Implication:** one replay is an anecdote. A decision-grade verdict needs
  k samples and a pass^k threshold. The capstone (`07_replay_factory`) supports
  `--samples k` and reports pass^k for exactly this reason.

---

## 5. The off-policy replay problem (the open frontier — and Kitaru's core problem)

When you replay a *multi-turn* conversation under a new/cheaper agent:

> the recorded user turns were responses to the **old** agent's replies.

So the moment the new agent says something different, every recorded user turn
after that is answering a message that no longer exists — **off-policy, invalid**.
Naive teacher-forced replay silently scores fiction.

- **Single-turn replay is safe** (the cheap, high-value case — and what the
  capstone does today): inject the same first input, compare outputs. The off-
  policy problem only bites *past the first divergence*.
- The literature's implicit answer is to abandon teacher-forcing for
  **free-running simulated rollouts** — but §2 says simulators are unreliable.
  So you trade one validity problem for another.
- **The unsolved hybrid: divergence-gated replay.** Replay recorded turns
  verbatim *until* the new agent's reply diverges from the recorded one; from
  that turn on, hand off to a user simulator (clearly flagged as lower-confidence
  past the gate). Nobody has nailed this; there's little empirical work on how
  fast divergence compounds over turns.

**Why this matters for the product:** this is precisely the gap between "replay a
single trace" (shipped, easy) and "replay a multi-turn conversation under a new
model" (hard, unsolved, valuable). Kitaru already has the runtime to detect
divergence at a checkpoint boundary — divergence-gated replay is a natural,
defensible thing to build that observability tools structurally cannot.

---

## 6. Frameworks the founder will be asked about

τ-bench / τ²-bench (the academic gold standard, needs backends), LangSmith
trajectory evals, DeepEval / Confident AI conversational metrics, Braintrust,
Langfuse experiments, Ragas multi-turn, MINT, MT-Bench successors.

**Honest gap from the sweep:** none of the *production* tools surfaced verified
human-agreement data for their multi-turn metrics. They're widely used; their
correlation with human judgment is largely unestablished in public. Don't quote
their numbers as validated — say "widely adopted, validity self-reported."

---

## Soundbites for Q&A

- "Single-turn replay is safe and cheap. Multi-turn replay is off-policy past the
  first divergence — that's the frontier, and it's exactly where we're pointed."
- "Simulator choice alone swings scores 9 points. So we never call a simulator
  score truth — it's a pre-filter; production traces are the anchor."
- "LLM judges catch one in five cross-turn defects. A judge is a smoke detector,
  not an oracle — pair it with state-tracking and a panel."
- "If it's not in the rubric, the judge is blind to it. Rubrics come from defect
  taxonomies, not vibes."
- "n=1 is an anecdote. We report pass^k — the chance it works *every* time."

## Sources (verified)
τ-bench 2406.12045 · τ²-bench 2506.07982 · Lost in Simulation 2601.17087 ·
Sim2Real Gap 2603.11245 · TED 2603.15483 · Proxy-State 2602.16246 ·
Catching One in Five 2606.10315 · MT-Bench/judge 2306.05685 · juries 2404.18796.
(2026 arXiv IDs use the YYMM scheme; search by title if re-verifying.)
