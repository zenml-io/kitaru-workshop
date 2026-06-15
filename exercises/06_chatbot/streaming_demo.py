"""Streaming demo — live token events from any KitaruAgent, in one argument.

VERIFIED LIVE against a hosted Kitaru server (kitaru 0.15.0, 2026-06-10):
adding ``event_stream_handler`` to the adapter makes every model request emit
``pydantic_ai.stream.started`` / ``.event`` (incl. deltas) / ``.completed``
live events over the server's SSE channel. Watch them from another terminal:

    python streaming_demo.py                 # prints EXEC: <id>
    python watch_stream.py <EXEC_ID>         # tokens tick in live (or replayed
                                             # via cursor if you attach late)

NOTE (kitaru 0.16.0): you can also stream a *durable chatbot* now —
``event_stream_handler`` combined with the flow-scope ``say_and_wait`` pattern
(``allow_sync_tool_body_waits``) works as of 0.16.0 (#431; verified — it reaches
the wait instead of throwing "Nested checkpoint calls"). This file streams a
plain agent for simplicity; add ``event_stream_handler=`` to ``chatbot.py`` for
a streaming durable chat.

SERVER REQUIREMENT: live events need the server's streaming broker — present
on hosted/managed servers, absent on bare `kitaru login` local servers
("Streaming is disabled on the server" → publishes dropped, durability fine).
"""

from pydantic_ai import Agent

from kitaru import flow
from kitaru.adapters.pydantic_ai import KitaruAgent

agent = Agent(
    "openai:gpt-5.2",
    name="streaming_writer",
    system_prompt=(
        "You are a concise product copywriter. Use the word_count tool to "
        "check your draft, then return the final text."
    ),
)


@agent.tool_plain
def word_count(text: str) -> int:
    """Count words in TEXT."""
    return len(text.split())


async def passthrough_stream_handler(ctx, stream) -> None:
    """Drain the PydanticAI event stream.

    The body is intentionally trivial: KitaruAgent wraps any configured
    handler with its live-event publisher, so just *having* a handler makes
    every streamed model event flow onto the server's SSE channel.
    """
    async for _event in stream:
        pass


durable_agent = KitaruAgent(
    agent,
    checkpoint_strategy="calls",
    event_stream_handler=passthrough_stream_handler,  # ← the one-line upgrade
)


@flow
def streaming_writer(topic: str = "a durable-execution platform for agents") -> str:
    result = durable_agent.run_sync(
        f"Write a punchy two-sentence product blurb about {topic}."
    )
    output = result.output
    # KitaruAgent may hand back the framework's run result; unwrap to plain text.
    return output.output if hasattr(output, "output") else str(output)


if __name__ == "__main__":
    handle = streaming_writer.run()
    exec_id = getattr(handle, "exec_id", None) or getattr(handle, "id", None)
    print(f"EXEC: {exec_id}")
    print("In another terminal:  python watch_stream.py", exec_id, "\n")
    result = handle.wait()
    print("\n--- Final blurb ---\n", result)
