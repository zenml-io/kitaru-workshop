---
marp: true
theme: default
paginate: true
style: |
  section {
    background: #ffffff;
    color: #1a1a1a;
    font-size: 26px;
    line-height: 1.5;
  }
  h1 { color: #111111; }
  h2 { color: #333333; }
  h6 { color: #888888; text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.6em; }
  strong { color: #000000; }
  section.lead { text-align: left; }
  section.divider h1 { color: #111111; }
---

<!-- _class: lead -->

###### ZENML · KITARU WORKSHOP

# Agents That Earn Production

## Hands-on with Kitaru — the open runtime for Python agents

**Hamza Tahir** · Co-founder & CEO, ZenML

*Python only · everything runs on your laptop: `uv add kitaru`*

---

# Five projects are being built in this room

1. **The batch classifier** — millions of events/day through an LLM
2. **The source-grounded assistant** — 20 years of documents, every answer must cite
3. **The fan-out analytics engine** — N prompts × M engines × every single day
4. **The high-stakes copilot** — drafts things a human must approve
5. **The persona simulator** — hundreds of parallel agents, stochastic outputs

*Recognize yours? Good. Everything today maps back to these five.*

---

# All five will hit the same wall

- The pipeline dies at step **7 of 9** → you re-pay for steps 1–6
- The prompt change that "obviously helped" silently broke last month's numbers
- Finance asks *"why is the AI line bigger than a salary?"* — nobody can answer per-run
- The approval step keeps a pod alive for **14 hours** while a human sleeps
- "It worked yesterday" — and you cannot reproduce yesterday

---

# Agents vs workflows — a spectrum, not a binary

**Workflow** — LLMs orchestrated through *predefined code paths*.
The control flow is yours; the model fills in steps. Predictable, testable, cheap.

**Agent** — the model *dynamically directs its own process* and tool use.
Open-ended. The model decides the path.

> Most "agents" in production are workflows with a few agentic steps —
> and that's the right default. Add agency only where the task demands it.

*Agency buys flexibility — and spends predictability, latency, and money.*

---

# What breaks at the agentic end

- **Non-determinism compounds** — a 95%-reliable step, 10 times, is ~60% end-to-end
- **Cost is unbounded** — the agent decides how many calls. *"Why is the AI line bigger than a salary?"*
- **No reproducibility** — same input, different path. You can't debug *what happened* — let alone *what would have happened*
- **Silent regressions** — swap the model/prompt, the whole trajectory shifts; your evals never saw the new paths
- **The trajectory-eval gap** — unit-testing a workflow step is easy; scoring an agent's *path* (tool choice, multi-turn) is a different problem

---

<!-- _class: lead -->

# Observability tells you *what happened.*

## Agentic systems also need **re-execution**:

# retry · resume · replay · regress

*The more a system decides for itself, the less testing alone can tell you —
you have to be able to re-run it.*

---

# What Kitaru is

- **An open runtime for Python agents** — open source (Apache 2.0), self-hosted
- **Python only.** TypeScript frontend? You call deployed flows over REST (Module 3)
- Sits *underneath* your agent framework — PydanticAI, LangGraph, OpenAI Agents SDK, Claude SDK
- Not a framework. Not a tracing tool. **The runtime your agents run on.**

```bash
uv add 'kitaru[local,pydantic-ai]'   # add it to your own project
kitaru init && kitaru login          # local server — no cloud account needed
```

---

# Setup — do this now (2 min)

Didn't do the prework? Catch up now — everything runs on your laptop:

```bash
git clone https://github.com/zenml-io/kitaru-workshop.git
cd kitaru-workshop
uv sync && source .venv/bin/activate         # pinned env from the lockfile
kitaru init && kitaru login                  # starts a local server
kitaru status                                # should say: running
```

For Modules 2–4 (needs one LLM key — **Anthropic or OpenAI**), register two
aliases pointing at *your* provider:

```bash
# Anthropic (default for this cohort)
kitaru model register strong --model anthropic/claude-sonnet-4-5  --secret llm-creds
kitaru model register cheap  --model anthropic/claude-haiku-4-5   --secret llm-creds
# …or OpenAI
# kitaru model register strong --model openai/gpt-5.2    --secret llm-creds
# kitaru model register cheap  --model openai/gpt-5-nano --secret llm-creds
```

*Tried Kitaru/ZenML before? `kitaru clean all` first to wipe stale local state.*
*Stuck? Flag an instructor — Exercise 1 needs no key, so start there.*

---

<!-- _class: divider -->

###### MODULE 1 OF 4 · HANDS-ON · NO API KEY

# Your first durable flow

Everyone codes along.

---

# Flows and checkpoints

```python
from kitaru import flow, checkpoint

@checkpoint
def classify(bounces: list[str]) -> list[dict]: ...

@flow
def bounce_triage(limit: int = 8) -> dict:
    bounces = fetch_bounces(limit)
    classified = classify(bounces)
    return correlate(classified)

bounce_triage.run(limit=8).wait()
```

`exercises/01_first_flow` — a bounce-triage pipeline, pure Python

---

# The "aha": run it twice

- **Just run it again.** Finished checkpoints come back from cache — instantly.
- `correlate` is marked `cache=False`, so it always re-runs: you *see* the
  cached steps skip while the expensive one works.
- Same thing if it **dies mid-run** (Ctrl+C the slow step): completed work is never re-paid.

```
Kitaru: Checkpoint `fetch_bounces` cached.     ← instant
Kitaru: Checkpoint `classify`      cached.     ← instant
Kitaru: Checkpoint `correlate`     started ... ← cache=False, re-runs
```

Also in there: `kitaru.log()` metadata + `kitaru.save()` versioned artifacts
(*inside* checkpoints — that's the durability boundary).

---

<!-- _class: divider -->

###### MODULE 2 OF 4 · THE CENTERPIECE ★

# Replay & overrides

Don't guess. Don't A/B on your users. Replay your own history.

---

# First: wrap YOUR agent (zero rewrite)

```python
from kitaru.adapters.pydantic_ai import KitaruAgent

agent = Agent("anthropic:claude-sonnet-4-5", system_prompt="...")  # your agent, any provider

durable_agent = KitaruAgent(agent, name="office_assistant", checkpoint_strategy="calls")
```

- **You already have an agent. Wrap *that one*** — provided one is the fallback
- Every model + tool call = a checkpoint, tokens logged per call (and $ cost when the model is priced)
- LangGraph, OpenAI Agents SDK, Claude SDK adapters too — keep your framework
- Granular checkpoints aren't just crash recovery — **they're the replay targets**

*`exercises/02_wrap_agent` + `BRING_YOUR_OWN.md` — wrap your PoC agent live*

---

# Now you: replay with overrides

```python
client.executions.replay(
    "<exec-id>",
    from_="extract_mentions",
    overrides={"checkpoint.fetch_answers": edited_answer},
)
```

1. Run with alias `strong` — your expensive model
2. Replay with an **edited upstream answer** (what-if on the input)
3. Replay with alias `cheap` — outputs side-by-side, **per-call token diff** (cheaper ≠ always fewer tokens!)

Upstream checkpoints: cached, never re-paid. Replay root + descendants: re-executed for real.

`exercises/03_replay_overrides` — HANDS-ON

---

# Honest slide: what a replay is — and isn't

**✓** A counterfactual on the **right data distribution** — your real traffic
**✓** Cost deltas are hard numbers — token math on identical inputs
**✓** Kills bad candidates cheaply, offline

**✗** One replay is an anecdote — LLMs are stochastic, sample n > 1
**✗** Validity decays past the injection point — divergence compounds
**✗** Quality deltas are *evidence, not proof* — confirm winners with a small live test

*Replay is the cheap offline filter. Not the oracle.*

---

# Your replay-regression scenario

| You're building… | Before shipping a change, replay… |
|---|---|
| batch classifier | last week's sample under taxonomy v2 → diff the label shifts |
| source-grounded assistant | your golden questions after every re-index |
| fan-out analytics | new extractor vs old on identical answers |
| high-stakes copilot | a flagged case with the new strategy prompt |
| persona simulator | the same seeded scenario under the new model |

---

<!-- _class: divider -->

###### MODULE 3 OF 4 · DEMO

# Ship it

Deployments, and the chatbot that dies between turns.

---

# Stacks — same code, runs anywhere

A **stack** = where a flow runs + where its artifacts live. Everything you ran
on your laptop in Modules 1–2 ships unchanged:

```bash
kitaru stack list      # default (local) · local_remote (S3) · aws-k8s-stack
kitaru stack use aws-k8s-stack
python flow.py         # same code — now on Kubernetes, artifacts in S3
```

- Laptop → S3 → Kubernetes / Vertex / SageMaker — **zero code changes**
- **Governance lives here**: one controlled place that decides where every agent runs
- Caching & replay work identically on every stack
- Deploys (next slide) are **pinned to a stack** — that's *where* the version runs

---

# Deployments & versions

```bash
kitaru deploy chatbot.py:chatbot --tag prod --stack aws-k8s-stack
#  → chatbot v10        every deploy = a new immutable version
```

- Each deploy is an **immutable, versioned snapshot** — v1, v2, v3 … never mutated
- **Tags route traffic**, versions don't move: `prod` → v10
- **Canary** = point a tag at a new version · **rollback** = point it back —
  `kitaru flow tag`, no rebuild, instant
- Pin a deploy to a **stack** (where it runs) — local, k8s, Vertex …

---

# Invoking a deployment

```python
KitaruClient().deployments.invoke(
    flow="chatbot", tag="prod", inputs={...})      # by name + tag
```

- Decoupled: callers ask for `prod`; you move `prod` across versions underneath
- **TypeScript folks:** your frontend hits this over REST — no Python imports
- *The next demo is exactly that: a Gradio frontend invoking the deployment…*

---

# Demo: the durable chatbot

> *Are modern chatbots just long-horizon async agents? …yes.*

- **One agent, one tool**: every assistant turn is the LLM *choosing* to call `say_and_wait`
- The tool calls `kitaru.wait()` → **the pod dies between turns** — a reply tomorrow
  spins up a fresh pod that resumes mid-conversation
- Every turn versions the `history` artifact → **kill the browser tab, reopen, continue**
- You pay for the seconds the model is thinking — a session can last months

`exercises/06_chatbot` (take it home) · approval gates: `exercises/04_hitl_deploy`

---

<!-- _class: divider -->

###### MODULE 4 OF 4 · CAPSTONE ★★

# The Replay Factory

The thesis, made runnable. "Is this too simple?" — no.

---

# The loop

> ingest cases → run baseline + candidate → judge good/bad →
> aggregate → **ship / don't-ship**

```python
@flow
def replay_factory(cases_path, baseline="strong", candidate="cheap"):
    cases  = load_cases(cases_path)               # ingest (→ exported traces)
    rows   = run_and_judge(cases, baseline, candidate)   # run both, LLM-judge
    return   aggregate(rows, baseline, candidate)         # verdict + regressions
```

- The eval loop is *itself a Kitaru flow* — 3 durable checkpoints. Crash in
  aggregation? The LLM batch is **cached**. Eval the eval by replaying it.
- `exercises/07_replay_factory` — run it on your own cases

---

# The verdict — evidence, not vibes

```
=== Replay Factory report ===          # ← real output, 8 cases
  baseline (strong):   100% pass
  candidate (cheap):   100% pass
  regressions:          0
  VERDICT: SHIP        →  the cheaper model is safe. Cost cut, with proof.
```

The moment a regression appears, the verdict flips and names it:

```
  candidate (cheap):    88% pass   regressions: 1
    - [safety-misuse] suggested an unsafe workaround   →  DO NOT SHIP
```

- Judgments → your **regression set** → eval dataset → eventually the **RL reward
  signal** for a cheaper open model. *The cost endgame.*
- Honest: ingestion is a JSONL stand-in. **Live LangFuse/Datadog trace-import is
  the frontier**, not a button — yet.

---

# Evaluating multi-turn — the honest state of the art

- **Two axes:** *outcome/state* (τ-bench — objective, needs a backend) vs
  *trajectory/judge* (TED "grading notes" — scales, scores the path)
- **n=1 is an anecdote → `pass^k`** (chance it works *every* time). gpt-4o on
  τ-bench: 61% pass^1 → **<25% pass^8**. Our factory takes `--samples k`.
- **The LLM-judge blind spot:** recall *degrades* the more cross-turn the bug is —
  one production study caught **~1 in 5** cross-turn defects. *If it's not in the
  rubric, the judge can't see it.* → panels/juries + state-tracking, not one judge.

---

# The hard part: replaying a *conversation*

- **Single-turn replay is safe & cheap** — same input, compare outputs. That's the factory.
- **Multi-turn replay is off-policy:** the recorded user turns answered the
  **old** agent. Change the agent → past the first divergence, the recording is fiction.
- **User simulators?** Unreliable — simulator choice alone swings success **9 points**;
  they're an "easy mode" (USI 76 vs humans 93). A pre-filter, never truth.
- **The frontier — divergence-gated replay:** replay verbatim until the new agent
  diverges, then hand to a simulator. Kitaru sees divergence *at the checkpoint
  boundary* — something an observability tool structurally cannot. *(see EVALS_PRIMER)*

---

# Also in the box (take-home)

- **Streaming** — one argument (`event_stream_handler`) → live token deltas over
  SSE; `watch_stream.py`. Your real-time UI feed. (`exercises/06_chatbot`)
- **Agents operating the platform** — `kitaru-mcp`: point Claude/Cursor at it and
  let an agent list executions, fetch artifacts, trigger replays
- **Fan-out** at scale — a container per checkpoint (`exercises/05_fanout`)
- **Approval gates** — `kitaru.wait()` for the high-stakes copilot (`exercises/04_hitl_deploy`)

---

<!-- _class: divider -->

###### YOUR TURN · 15 MINUTES

# Map Kitaru onto your PoC

Worksheet — then one insight per team, out loud.

---

# The worksheet

1. **Flow boundaries** — what is *one execution* of your system?
2. **Checkpoint seams** — where would you hate to re-pay?
3. **One `wait()` point** — where must a human sign off?
4. **One replay-regression scenario** — what change scares you most?
5. **One artifact worth versioning** — what will you need to trace back?

> "The thing we were going to build by hand that we now don't have to is ____."

---

# Where this goes

- **Import traces** from the observability tool you already use → replay them
- **Batch replay** → regression reports in CI
- **Curated good/bad traces** → eval datasets → fine-tune open models — *the cost endgame*

### Office hours + Slack for the first teams with a running flow 🚀

---

<!-- _class: lead -->

# Thank you

## github.com/zenml-io/kitaru · docs.zenml.io/kitaru

**hamza@zenml.io** · Slides + exercises: github.com/zenml-io/kitaru-workshop

*The five walls are real. Now you have the tools.*
