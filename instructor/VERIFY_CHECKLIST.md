# Pre-workshop verification checklist

Run this end-to-end against your own server/stack before presenting. The notes
below are **gotchas verified live against kitaru 0.16.0** (core paths + streaming
re-checked on 0.16.0; full suite originally on 0.15.0) — pin via `uv.lock` and
re-check, since the SDK moves fast.

## 0. Environment

- [ ] `uv sync` (from the committed `uv.lock`) → `.venv` with pinned deps
      (kitaru 0.16.0). `source .venv/bin/activate` or use `uv run`. The lock keeps
      the whole room identical — no resolver drift. (Needs Python ≥3.11.)
- [ ] `kitaru init` then `kitaru login` — **`login` starts + connects the local
      server**, `init` only inits the project. `kitaru status` should show it running.
- [ ] `kitaru model register strong --model openai/gpt-5.2 --secret <secret>` and
      a `cheap` alias — model IDs are `provider/model`; aliases ride into runs.
- [ ] Docker running (only for the fan-out and deployed-chatbot demos).

## 1. Per-exercise smoke tests

- [ ] **Ex 1 (first flow):** runs with no API key; Ctrl+C mid-run then re-run →
      earlier checkpoints cached. `kitaru.save()/log()` with artifacts must be
      called **inside a `@checkpoint`** (flow scope raises `KitaruContextError`).
- [ ] **Ex 1 stacks:** `kitaru stack use <remote>` then re-run → same code, remote
      artifacts. Cloud artifact stores need their deps once (e.g. S3:
      `uv pip install 's3fs>2022.3.0,!=2025.3.1' boto3`).
- [ ] **Ex 2 (wrap agent):** `kitaru.adapters.pydantic_ai.KitaruAgent`,
      `checkpoint_strategy="calls"`; per-call cost shows in the dashboard.
      **0.16 gotcha:** `KitaruAgent` now requires a stable `name=` (raises
      `UserError` without it) — pass `name="..."` or set the wrapped agent's name.
- [ ] **Ex 3 (replay) ★:** SDK `client.executions.replay(exec_id, from_=...,
      overrides={"checkpoint.<name>": ...})`; CLI flow inputs via `--args`,
      checkpoint outputs via `--overrides`. `kitaru.llm(prompt, *, model, system,
      temperature, max_tokens, name)`.
- [ ] **Ex 4 (HITL):** `kitaru.wait()` is **keyword-only** and needs `schema=bool`
      to accept `--value true` (schema-less waits resolve with `--value null`);
      `kitaru executions input <id> --value true` resolves AND auto-resumes.
- [ ] **Ex 6 (chatbot, deployed):** `kitaru deploy chatbot.py:chatbot --tag prod
      --stack <remote> --exclusive` → a new immutable version; `python ui.py`
      resolves the `prod` tag per invoke. Pin image deps to
      `requirements=["kitaru[pydantic-ai]", "openai"]` (unpinned pydantic-ai
      breaks the adapter inside the pod). Inline any sibling imports — the deploy
      loader imports the flow file standalone. Flows must live inside the
      `kitaru init` source root.
      **0.16 gotchas:** (1) the `llm-creds` secret must exist or even a
      *local* run fails to compile (`secret_environment_from` is resolved
      locally too): `kitaru secrets set llm-creds --ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"`
      (or `--OPENAI_API_KEY=...`). Model defaults to `anthropic:claude-sonnet-4-5`;
      OpenAI users set `WORKSHOP_MODEL=openai:gpt-4o-mini`.
      (2) `handle.wait()` on the chatbot raises `KitaruAmbiguousFlowResultError`
      — agent flows have many terminal checkpoints (per model call + per-turn
      `persist_history`) and no static output spec, so there's no single result
      to extract. Expected; the conversation lives in the `history` artifact.
      `drive_local.py` catches it and also tolerates the LLM ending early/late.
- [ ] **Ex 6 (streaming):** `event_stream_handler=` → `pydantic_ai.stream.*` over
      SSE; `watch_stream.py` consumes it. Needs the server's streaming broker
      (hosted servers; bare local servers drop publishes). NOTE (0.16.0): the
      streaming **durable chatbot now works** — `event_stream_handler` + the
      flow-scope `say_and_wait`/`persist_history` no longer throws "nested
      checkpoint" (#431, verified — reaches the wait), and duplicate stream events
      are fixed (#428), so the `data.source` dedupe in `watch_stream.py` is now
      belt-and-suspenders, not required.
- [ ] **Ex 7 (Replay Factory):** `python factory.py` → ship/don't-ship report;
      `--samples k` reports pass^k. **Kitaru data-flow rule:** inside a `@flow` a
      checkpoint's return is an artifact *handle* — wire checkpoint→checkpoint or
      return it; never subscript/parse it in flow scope. Parse inside checkpoints;
      pass JSON strings across boundaries. (Confirmed against the kitaru-authoring skill.)
- [ ] **MCP finale (optional/take-home):** `kitaru-mcp`; connect Claude Code/Cursor;
      `kitaru_executions_list` / `kitaru_executions_replay` respond.

## 2. Fix-forward rule

When a check fails: fix the exercise code AND the matching snippet in
`slides/slides.md` — they must stay identical to what participants type.

## 3. Demo insurance

- [ ] 60s screen recording of the deployed chatbot (kill-the-tab rehydration).
- [ ] 60s screen recording of streaming + the MCP finale.

## 4. Final pass

- [x] Repo URL filled in `prework/PREWORK.md` and the closing slide.
- [ ] Render slides: `npx @marp-team/marp-cli slides/slides.md -o slides/slides.pdf`
- [ ] Send `PREWORK.md` to attendees/organizers ≥3 days before.
- [ ] Workshop API key created, spend-capped, calendar reminder to delete it.
