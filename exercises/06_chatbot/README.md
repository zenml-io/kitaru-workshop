# Exercise 6 — The durable chatbot (demo thread + take-home)

**The line that lands:** *every chatbot is a long-horizon agent — a session can
last months, and you only pay for the seconds the model is actually thinking.*

This is the official Kitaru `examples/chatbot`, vendored here (plus a streaming
upgrade). One PydanticAI agent with a single `say_and_wait` tool:

- The LLM drives the whole conversation — every assistant turn is the model
  *choosing* to call `say_and_wait`.
- The tool calls `wait_for_input(...)` → the pod **dies** between turns.
  A user replying tomorrow spins up a fresh pod that resumes mid-conversation.
- Every turn snapshots the conversation as a versioned `history` artifact —
  the Gradio UI rehydrates any session from it. Close the browser, reopen,
  it's all there.

## Files

| File | What |
|---|---|
| `chatbot.py` | The flow: one agent, one tool, `wait()` per turn (upstream original) |
| `streaming_demo.py` | **+1 argument**: `event_stream_handler` → live token-delta events (✅ verified live) |
| `watch_stream.py` | Terminal consumer for the SSE event stream (the "typing indicator" feed) |
| `ui.py` | Gradio chat UI — invokes the deployment, pipes replies via `executions.input(...)` |
| `drive_local.py` | Scripted non-interactive driver (flow in background thread, input from foreground) |
| `history_artifacts.py` | Helpers to pick the best `history` artifact for session rehydration |

> **Prerequisite (local *and* deployed):** create the `openai-creds` secret.
> `chatbot.py` sets `secret_environment_from=["openai-creds"]` on its image, and
> Kitaru resolves that secret even for **local** runs — without it the flow fails
> to compile with `No secret found with name 'openai-creds'`. One-time:
> ```bash
> kitaru secrets set openai-creds --OPENAI_API_KEY="$OPENAI_API_KEY"
> ```

## How to run (three ways, from the upstream README)

1. **Deployed + Gradio UI** (production-shaped, what the instructor demos):
   `kitaru deploy chatbot.py:chatbot --tag prod --stack <remote-stack> --exclusive`,
   the `openai-creds` secret for the pod's `OPENAI_API_KEY`, then `python ui.py`.
2. **Direct terminal**: `python chatbot.py` — quick interactive smoke test.
3. **Scripted**: `python drive_local.py` — background flow + foreground driver.
   The driver tolerates the LLM ending the chat early (extra scripted messages
   are ignored) — pass your own messages as args if you want a longer chat.

Anti-pattern to know: `handle.wait()` then `executions.input(...)` in one
thread deadlocks by design — `handle.wait()` waits for the *whole* execution,
which is waiting for the input you haven't sent. Answer waits from a second
actor (UI, CLI, or the driver script).

> **`handle.wait()` on an agent chatbot raises `KitaruAmbiguousFlowResultError`**
> (kitaru 0.16). The adapter emits one terminal checkpoint per model call plus a
> `persist_history` per turn, so Kitaru can't auto-pick a single return value
> (dynamic flows have no static output spec → it falls back to terminal-step
> scanning and finds many). This is **expected for agent flows** — the
> conversation's durable state is the `history` artifact, not a return value.
> `drive_local.py` catches this and the deployed UI rehydrates from `history`.

## The streaming upgrade (verified live, kitaru 0.15.0)

`streaming_demo.py` adds **one argument** to any KitaruAgent:

```python
KitaruAgent(agent, checkpoint_strategy="calls",
            event_stream_handler=passthrough_stream_handler)
```

Having a handler makes the adapter publish `pydantic_ai.stream.*` live events —
`started` / `event` (text deltas in `data["text_delta"]`, clipped to 240 chars)
/ `completed` — onto the server's SSE channel. Consume from anywhere:

```python
for event in client.executions.events(exec_id, kinds=[...]):
    ...
```

Run `python watch_stream.py <EXEC_ID>` in a second terminal and watch the
events tick while the agent runs — attaching late is fine, the SSE cursor
replays missed events. **TypeScript folks:** this SSE endpoint is your
real-time UI feed — no Python needed on the consumer side.

⚠️ **Server requirement:** live events need the streaming broker — enabled on
hosted/managed servers, *absent on bare local servers* ("Streaming is disabled
on the server" → publishes are dropped, durability unaffected). Hence: the
instructor demos this against the hosted workspace.

✅ **Streaming durable chatbot now works (kitaru 0.16.0, verified).** Earlier
versions threw "Nested checkpoint calls are not supported" when you combined
`event_stream_handler` with the flow-scope `say_and_wait`/`persist_history`
pattern. Fixed in 0.16.0 (#431) — add `event_stream_handler=` to the chatbot's
`KitaruAgent` and it streams *and* waits durably (verified: it reaches the
wait, no error). Duplicate stream events are also fixed (#428), so the
`data.source` dedupe in `watch_stream.py` is now just belt-and-suspenders.

## What to look for in the dashboard

- The synthetic model-call checkpoints (replay targets) vs the un-checkpointed
  `say_and_wait` (waits must live at flow scope).
- The `history` artifact, **versioned once per turn**.
- One completed `wait` per user turn — with the question the LLM asked.
- Kill the pod between turns → execution stays `WAITING` indefinitely, resumes
  on the next user message. Durability is the demo.

## Replay tie-in (Module 3 callback)

The conversation's model calls are checkpoints — which means yesterday's chat
session can be **replayed under a cheaper model** and diffed turn by turn.
Chat + replay is the full Kitaru story in one example.
