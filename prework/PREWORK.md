# Pre-work — do this BEFORE the workshop (15 minutes)

You'll be running everything live on your own laptop. Please complete these
steps beforehand so we don't spend workshop time on installs.

## 1. Requirements

- Python **3.10+** (`python --version`)
- A terminal and your editor of choice
- ~1 GB free disk (local Kitaru server + Docker images for the demo modules)
- Optional but recommended: Docker Desktop running (needed only for Module 5)

## 2. Get the materials + install (uv)

```bash
git clone https://github.com/zenml-io/kitaru-workshop.git
cd kitaru-workshop
uv sync                        # creates .venv with the exact pinned deps (kitaru 0.16.0)
source .venv/bin/activate      # or prefix later commands with `uv run`
```

`uv sync` reads the committed `uv.lock`, so the whole room ends up on identical,
known-good versions — no resolver drift. (No uv yet? `curl -LsSf
https://astral.sh/uv/install.sh | sh`. Prefer plain pip? `python -m venv .venv &&
source .venv/bin/activate && pip install 'kitaru[local,pydantic-ai]'` — but the
lockfile path is the reliable one.)

## 3. Initialize and start the local server

```bash
kitaru init       # initialize the project in your working directory
kitaru login      # starts AND connects to a local server (default port 8383)
kitaru status
```

`kitaru status` should report `Local server: running`. If it doesn't, ask in
the workshop Slack channel **before** the day.

## 4. Model API key

Exercise 1 needs **no API key**. For Exercises 2–4 you'll need one LLM provider key.
Either bring your own (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` exported in your
shell), or use the workshop key we'll hand out on the day (rate-limited, deleted after).

Register two model aliases once you have a key (we use these names in all
exercises). Model IDs use `provider/model` format:

```bash
kitaru model register strong --model openai/gpt-5.2
kitaru model register cheap --model openai/gpt-5-nano
```

(Any two models of different cost tiers work — the point is the price gap.
Ollama users: `ollama/qwen3.5` works too.)

## 5. Smoke test

With your venv active (from step 2):

```bash
python exercises/01_first_flow/flow.py   # should complete and print an execution ID
```

If that prints an execution ID, you're ready. 🎉

## Already installed an older Kitaru/ZenML? Start clean.

If you tried Kitaru (or ZenML) before, an old local database/config can clash
with this version and throw confusing errors (stale stack, schema mismatch).
Wipe local state and re-init:

```bash
kitaru clean all      # resets project + global local Kitaru/ZenML state
# then: kitaru init && kitaru login
```

`kitaru clean` has `all` / `global` / `project` — `all` is the clean slate.
(Equivalent older command: `zenml clean`.) This only touches *local* state on
your machine; it doesn't delete anything on a remote server.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `kitaru: command not found` | Venv not active — `source .venv/bin/activate` (or use `uv run`) |
| Stale stack / schema / DB error | `kitaru clean all`, then `kitaru init && kitaru login` (see above) |
| Server won't start | Port conflict — `kitaru status` for details; nothing else on the default port |
| Corporate laptop blocks Docker | Modules 1–2 need no Docker; the deploy/fan-out demos are instructor-run |

Questions → workshop Slack channel. See you there!
