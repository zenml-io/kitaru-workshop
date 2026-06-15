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

## Troubleshooting

| Symptom | Fix |
|---|---|
| `kitaru: command not found` | `pip show kitaru` — check your PATH / venv is active |
| Server won't start | Port conflict — check nothing else owns the default port; `kitaru status` for details |
| Corporate laptop blocks Docker | You can do Modules 1–4 without Docker; Module 5 is demo-only |

Questions → workshop Slack channel. See you there!
