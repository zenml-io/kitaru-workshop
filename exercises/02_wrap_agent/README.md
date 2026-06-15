# Exercise 2 — Wrap a real agent, zero rewrite

> 🎬 **In the 2h workshop this is an instructor demo** — take it home and run it yourself afterwards.

**Theme:** an office-knowledge assistant over a (tiny) 20-year project archive.
The agent must cite sources — a wrong citation about a building spec is worse
than no answer.

## The pitch

You already have an agent — PydanticAI, LangGraph, OpenAI Agents SDK, Claude SDK.
Kitaru doesn't replace it. Two added lines:

```python
from kitaru.adapters.pydantic_ai import KitaruAgent
durable_agent = KitaruAgent(agent, name="office_assistant", checkpoint_strategy="calls")
```

Now every model call and every tool call is a durable checkpoint with
tokens/cost logged.

## Steps

1. Export your API key (or use the workshop key).
2. `python agent.py`
3. Dashboard: find the execution. Count the checkpoints — one per LLM call,
   one per `search_archive` tool call. Click into each: inputs, outputs, cost.
4. Ask a question the archive can't answer. Does the agent admit it? Find the
   exact tool call in the trace that came back empty.

## Try it

- Switch `checkpoint_strategy` to a coarser granularity and compare what the
  dashboard shows (see the adapters docs for your framework's options).
- LangGraph users: the LangGraph adapter has `graph_call` (coarse) vs `calls`
  (granular) strategies — same idea, your graph stays untouched.

## The point

Granular checkpoints aren't just for crash recovery — they're the **replay
targets** for Exercise 3. No checkpoints, no counterfactuals.
