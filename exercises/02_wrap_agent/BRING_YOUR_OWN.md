# Bring Your Own Agent

You already have an agent. The whole point of this module is to make **yours**
durable and replayable — not the toy one. Here's how, in ~5 minutes.

## If your agent is PydanticAI

```python
from kitaru import flow, checkpoint
from kitaru.adapters.pydantic_ai import KitaruAgent

# your existing agent — unchanged. (The model must be bound at construction.)
my_agent = Agent("openai:gpt-5.2", system_prompt="...", tools=[...])

durable = KitaruAgent(my_agent, name="my_agent", checkpoint_strategy="calls")

@flow
def run_my_agent(prompt: str) -> str:
    result = durable.run_sync(prompt)
    out = result.output
    return out.output if hasattr(out, "output") else str(out)

run_my_agent.run(prompt="...").wait()
```

That's it. Every model call and tool call is now a checkpoint with cost — open
the dashboard and look. Those checkpoints are your replay targets in Module 3.

## If your agent is LangGraph / OpenAI Agents SDK / Claude SDK

Same idea, different adapter — your graph/agent stays untouched:

- LangGraph: `from kitaru.adapters.langgraph import ...` (strategies: `graph_call`
  coarse vs `calls` granular)
- OpenAI Agents SDK / Claude SDK: see `docs.zenml.io/kitaru/adapters`

## If your agent is "just code that calls an LLM" (no framework)

Even simpler — no adapter needed. Put `kitaru.llm()` calls inside `@checkpoint`s
and orchestrate with a `@flow`. See `exercises/01_first_flow` and
`exercises/07_replay_factory` for the plain-`kitaru.llm` pattern.

## The two rules that will bite you (learned live)

1. **`kitaru.llm()`, `@checkpoint`, `@flow` only — register your model alias first:**
   `kitaru model register strong --model openai/gpt-5.2 --secret <your-secret>`
2. **Don't inspect a checkpoint's return value in flow scope.** Inside a `@flow`,
   a checkpoint's output is an artifact *handle* — wire it into the next
   checkpoint or return it; do the parsing/looping *inside* checkpoints. (Flow
   *inputs*, by contrast, are real values you can iterate.)

## What to try once it's wrapped

- Run it, kill it mid-run, re-run → cached checkpoints (durability).
- In Module 3, replay one execution under a cheaper model and diff the cost.
- Stuck? Grab an instructor — this is exactly what office hours are for.
