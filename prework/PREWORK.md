# Pre-work — do this BEFORE the workshop (15 minutes)

You'll be running everything live on your own laptop. Please complete these
steps beforehand so we don't spend workshop time on installs.

## 1. Requirements

- Python **3.10+** (`python --version`)
- A terminal and your editor of choice
- ~1 GB free disk (local Kitaru server + Docker images for the demo modules)
- Optional but recommended: Docker Desktop running (needed only for Module 5)

## 2. Install

```bash
pip install 'kitaru[local,pydantic-ai]'
```

The extras matter: `local` brings the local-server dependencies; `pydantic-ai`
pins a compatible adapter version so the agent and chatbot exercises work too —
use the extra, **not** a standalone `pip install pydantic-ai` (latest is too
new and breaks the adapter import).

(Use a fresh virtualenv if you prefer: `python -m venv .venv && source .venv/bin/activate`)

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

## 5. Get the materials

```bash
git clone <REPO_URL_HERE>   # filled in before the workshop
cd kitaru-workshop
python exercises/01_first_flow/flow.py   # should complete and print an execution ID
```

If that last command prints an execution ID, you're ready. 🎉

## Troubleshooting

| Symptom | Fix |
|---|---|
| `kitaru: command not found` | `pip show kitaru` — check your PATH / venv is active |
| Server won't start | Port conflict — check nothing else owns the default port; `kitaru status` for details |
| Corporate laptop blocks Docker | You can do Modules 1–4 without Docker; Module 5 is demo-only |

Questions → workshop Slack channel. See you there!
