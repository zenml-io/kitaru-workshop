# Workshop Agenda — 2 hours (120 min)

> Audience: teams who **already have agents and pipelines** built (real PoCs:
> batch classifiers, RAG assistants, fan-out analytics, copilots, simulators). This is NOT "learn to build an agent." It is
> the production layer they haven't added yet: replay, cost, durability, eval.
> Students run TWO things live (Ex 1, Ex 3) and wrap their OWN agent (Ex 2).
> Protect the peaks: the theory frame, replay (Module 2), and the capstone.

## The five archetypes (anonymized — never name the companies on stage)

1. **The batch classifier** — millions of events/day through an LLM
2. **The source-grounded assistant** — 20 years of documents, answers must cite
3. **The fan-out analytics engine** — N prompts × M engines × daily, costs explode
4. **The high-stakes copilot** — drafts things a human must approve
5. **The persona simulator** — hundreds of parallel agents, reproducibility is the product

---

## 0. Agents vs workflows, and what breaks in production — 15 min (talk)

The altitude-setter. Earn their respect before touching a keyboard.

- **The spectrum, not a binary.** Workflows = LLMs orchestrated through predefined
  code paths (deterministic control flow, model fills steps). Agents = the model
  dynamically directs its own process and tool use. Most "agents" in production
  are workflows with a few agentic steps — and that's the right default.
- **The engineering trade.** Agency buys flexibility at the cost of predictability,
  latency, and money. You add agency only where the task demands it.
- **What breaks at the agentic end** (the five archetypes recognize themselves):
  - Non-determinism **compounds** — a 95%-reliable step, 10 times, is ~60% end-to-end.
  - Cost is **unbounded** — the agent decides how many calls. "Why is the AI line
    bigger than a salary?"
  - **No reproducibility** — same input, different path; you can't debug *what
    happened*, let alone *what would have happened*.
  - **Silent regressions** — swap the model/prompt and the whole trajectory shifts;
    your evals never covered the new paths.
  - **The trajectory-eval gap** — you can unit-test a workflow step; scoring an
    agent's *path* (tool choice, multi-turn) is a different problem.
- **The bridge / thesis:** workflows you can mostly *test*. Agents you must
  **observe → replay → regress**. Deterministic code got production discipline for
  free; agentic systems need to be re-runnable (replay/regress) to earn it. That
  re-execution layer — the open runtime your agents run on — is Kitaru.

## 1. The substrate — 12 min (HANDS-ON, no API key)

`exercises/01_first_flow/` — fast. "This is the floor; then we get to your code."

- `@flow` + `@checkpoint`, run it, **run it again → cached** (the "aha"). The
  slow step is `@checkpoint(cache=False)` so it always re-runs while the rest
  serves from cache — the lesson lands without needing a mid-run Ctrl+C (which
  shows the same thing, as a bonus).
- `kitaru.log()` + `kitaru.save()` (inside checkpoints).
- Don't dwell on flows/checkpoints — they know what a pipeline is. The point is
  the durability boundary. (Stacks/portability moved to Module 3, where deploy
  needs them.)

## 2. Wrap YOUR agent, then replay — 33 min ★ THE CENTERPIECE

- **Wrap it (13 min, HANDS-ON, bring your own)** — `exercises/02_wrap_agent`: two
  lines wrap a PydanticAI/LangGraph/OpenAI/Claude agent; every model + tool call
  becomes a checkpoint with cost. **Invite them to wrap their own PoC agent** —
  provided agent is the fallback. Granular checkpoints = replay targets.
  (See `exercises/02_wrap_agent/BRING_YOUR_OWN.md`.)
- **Replay (20 min, HANDS-ON)** — `exercises/03_replay_overrides`: run with `strong`,
  replay with an edited upstream value, replay with `cheap`, diff cost in the dashboard.
- Honest framing: replay = cheap offline regression filter on your real traffic.
  Cost deltas are hard numbers; quality deltas need n>1; confirm winners live.

## 3. Ship it — 27 min (instructor demo)

- **Stacks (1 slide, ~2 min):** a stack = where a flow runs + where artifacts
  live. `kitaru stack use aws-k8s-stack` → the same code from Modules 1–2 on k8s,
  artifacts in S3. Laptop → Vertex/SageMaker, zero code changes. This is the
  governance/portability story (the one Siemens & Adeo cared about), and it sets
  up deploy — deploys are pinned to a stack. Verified across default + local_remote(S3).
- **Deployments & versions (2 slides, ~7 min)**: `kitaru deploy ... --tag prod
  --stack aws-k8s-stack` → a new **immutable version** (v1, v2 …, never mutated).
  **Tags route, versions don't move**: `prod` → v10; canary = point a tag at a new
  version, rollback = point it back (`kitaru flow tag`, no rebuild). Deploys are
  pinned to a **stack** (where they run). Invoke by name+tag —
  `deployments.invoke(flow="chatbot", tag="prod")`; callers ask for `prod` while
  you move it across versions underneath. TS folks: REST, no Python. (All verified
  live — chatbot v9→v10 on aws-k8s-stack.)
- **The durable chatbot (15 min)** — `exercises/06_chatbot` deployed on k8s, Gradio UI:
  every chatbot is a long-horizon agent; one `say_and_wait` tool; **the pod dies
  between turns**; `history` artifact rehydrates — kill the tab, reopen, continue.
  While the cold pod boots (~60s), narrate `kitaru.wait()` + point at
  `exercises/04_hitl_deploy` (take-home, the copilot archetype).
- **Buffer (5 min)**.

## 4. Capstone: the Replay Factory — 15 min (advanced; demo, then take-home)

`exercises/07_replay_factory/` — the thesis made runnable, and the answer to "is
this too simple." The loop:

> ingest cases → run baseline + candidate model → LLM-judge good/bad →
> aggregate → **ship / don't-ship verdict** (regressions named)

- The eval loop is *itself a Kitaru flow* — durable, checkpointed, replayable.
  "Eval the eval": replay the factory from the judge checkpoint with a better rubric.
- Be honest: ingestion here is a provided JSONL (an *exported-traces* stand-in).
  **True LangFuse/Datadog trace-import is the roadmap edge** — name it as the frontier.
- Where it goes: good/bad judgments become your regression set → eval dataset →
  eventually the reward signal for RL on a cheaper open model. The cost endgame.
- **Eval depth (2 slides) — the part this audience will grill you on:** the two
  axes (outcome/state vs trajectory/judge); **pass^k not n=1** (factory takes
  `--samples k`); the LLM-judge **cross-turn blind spot** (~1 in 5); and the
  frontier — **off-policy multi-turn replay** (recorded user turns answered the
  OLD agent) → divergence-gated replay. Full depth + citations in
  `instructor/EVALS_PRIMER.md` — read it before the workshop; it's the Q&A armory.
- If time is short: 3-min demo of the report output; it's the take-home that
  matters most for teams who already have agents.

## 5. Map your PoC + close — 15 min

- `team_mapping/MAPPING_WORKSHEET.md`: flow boundary, checkpoint seams, one wait
  point, one replay-regression scenario, one versioned artifact. One insight per team.
- Close: Slack, office hours for the first teams with a running flow.

---

### Timing ledger

| Block | Min | Cumulative |
|---|---|---|
| 0 Agents vs workflows (theory) | 13 | 13 |
| 1 Substrate (hands-on) | 12 | 25 |
| 2 Wrap your agent + replay ★ | 33 | 58 |
| 3 Ship it (stacks + deploy/versions + chatbot) | 27 | 85 |
| 4 Capstone: Replay Factory | 15 | 100 |
| 5 Mapping + close | 20 | 120 |

### If running late, cut in this order
1. Capstone → 3-min report demo + "go build it" (saves ~12)
2. Buffer in Module 3 (saves 5)
3. NEVER cut: the theory frame, the replay hands-on, the mapping exercise.
