# Agents That Earn Production — Kitaru Workshop

A hands-on, reusable workshop (run it at a meetup, internal training, or course).
Participants make their agents replayable, cost-observable, and shippable with
[Kitaru](https://github.com/zenml-io/kitaru) — ZenML's open-source, self-hosted
**runtime for Python agents**.

**Python only** (that's the runtime). TypeScript frontends call deployed flows
over REST — see Module 3.

**Audience:** teams who *already have agents/pipelines built*
(batch classification, RAG assistants, fan-out analytics, HITL copilots,
multi-agent simulation). This is the production layer they haven't added yet:
stacks, replay, cost, evals, deployment versions.

## Repo layout

| Path | What it is | In the 2h session |
|---|---|---|
| `AGENDA.md` | Full 2-hour agenda with timings and per-module goals | — |
| `prework/PREWORK.md` | Setup instructions to send to students beforehand | — |
| `slides/slides.md` | Slide deck (Marp — `npx @marp-team/marp-cli slides/slides.md -o slides.pdf`) | — |
| `exercises/01_first_flow` | Durable flows: `@flow`, `@checkpoint`, caching, artifacts | 🟢 **HANDS-ON** (no key) |
| `exercises/02_wrap_agent` | Wrap a PydanticAI agent with zero rewrite | 🎬 instructor demo / take-home |
| `exercises/03_replay_overrides` | **Centerpiece**: replay with overrides, model swap, cost diff | 🟢 **HANDS-ON** |
| `exercises/04_hitl_deploy` | `kitaru.wait()` approval gates + deployments | 🏠 take-home |
| `exercises/05_fanout` | Isolated-runtime fan-out | 🏠 take-home |
| `exercises/06_chatbot` | Durable chatbot (deployed, Gradio UI) + streaming demo | 🎬 instructor demo / take-home |
| `exercises/07_replay_factory` | **Capstone**: ingest → run baseline/candidate → LLM-judge → ship verdict | 🎬 capstone demo / take-home |
| `team_mapping/MAPPING_WORKSHEET.md` | Closing exercise: teams map Kitaru onto their own PoC | 🟢 15 min |
| `instructor/SPEAKER_NOTES.md` | Talking points, per-team tailoring, honesty caveats | — |
| `instructor/EVALS_PRIMER.md` | Multi-turn eval SOTA (cited): user-sim crisis, judge blind spot, pass^k, off-policy replay | — |
| `instructor/VERIFY_CHECKLIST.md` | **Run before the workshop** — smoke-test every API call | — |

## Quick start (instructor)

```bash
pip install 'kitaru[local,pydantic-ai]'
kitaru init
kitaru login                       # starts + connects to a local server
kitaru status
python exercises/01_first_flow/flow.py
```

Then work through `instructor/VERIFY_CHECKLIST.md` — a few API surfaces were
written against docs as of June 2026 and must be smoke-tested against the
installed Kitaru version before going on stage.

## The one-sentence pitch

> Tracing tells you what happened. Production agents need re-execution:
> retry, resume, replay, regress — and a cost report your CFO can read.
