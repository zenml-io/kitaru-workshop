# Pre-workshop verification checklist

Run this end-to-end against your own server/stack before presenting. The notes
below are **gotchas verified live against kitaru 0.15.0** — pin your version and
re-check, since the SDK moves fast.

## 0. Environment

- [ ] `pip install 'kitaru[local,pydantic-ai]'` in a fresh venv — note versions: ______
      (plain `kitaru` lacks the local server; a standalone latest `pydantic-ai`
      breaks the adapter import — use the extra)
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
      `pip install 's3fs>2022.3.0,!=2025.3.1' boto3`).
- [ ] **Ex 2 (wrap agent):** `kitaru.adapters.pydantic_ai.KitaruAgent`,
      `checkpoint_strategy="calls"`; per-call cost shows in the dashboard.
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
- [ ] **Ex 6 (streaming):** `event_stream_handler=` → `pydantic_ai.stream.*` over
      SSE; `watch_stream.py` consumes it. Needs the server's streaming broker
      (hosted servers; bare local servers drop publishes). With a handler each
      event publishes twice (`model_request_stream` + `event_stream_handler`) —
      dedupe on `data.source`. NOTE: streaming can't combine with the chatbot's
      flow-scope wait tool today — stream a regular agent.
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

- [ ] Fill `<REPO_URL_HERE>` in `prework/PREWORK.md` and the closing slide.
- [ ] Render slides: `npx @marp-team/marp-cli slides/slides.md -o slides/slides.pdf`
- [ ] Send `PREWORK.md` to attendees/organizers ≥3 days before.
- [ ] Workshop API key created, spend-capped, calendar reminder to delete it.
