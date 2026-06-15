"""Live event watcher — the consumer side of streaming agents.

Subscribes to an execution's SSE event stream and renders model activity
live in the terminal. This is exactly the channel a TypeScript frontend
would consume for typing indicators / token streaming — same SSE endpoint,
no Python required on the consumer side.

Payload shape (verified live, kitaru 0.15.0): each event carries
``payload["kitaru"]`` (execution/checkpoint correlation) and
``payload["data"]`` (adapter fields: event_kind, part_kind, delta_kind,
display, and text content when transcripts are enabled).

Usage:
    python watch_stream.py <EXEC_ID>            # stream events, deltas inline
    python watch_stream.py <EXEC_ID> --all      # every event kind, raw

Requires a server with the streaming broker (hosted workspace). Attaching
late is fine — the SSE cursor replays missed events.
"""

import argparse
import json
import sys

from kitaru.adapters.pydantic_ai import PYDANTIC_AI_STREAM_EVENT_KINDS
from kitaru.client import KitaruClient


def _delta_text(data: dict) -> str:
    """Best-effort text extraction from a stream event's data payload."""
    for key in ("text_delta", "content_delta", "text", "content"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("exec_id", help="execution ID to watch")
    parser.add_argument("--all", action="store_true",
                        help="dump every event kind as raw JSON")
    args = parser.parse_args()

    client = KitaruClient()
    kinds = None if args.all else list(PYDANTIC_AI_STREAM_EVENT_KINDS)

    print(f"Watching events for {args.exec_id} (Ctrl+C to stop)…\n")
    try:
        for event in client.executions.events(args.exec_id, kinds=kinds):
            payload = event.payload or {}
            data = payload.get("data", payload)
            # With an event_stream_handler configured, the adapter publishes
            # each event from two sources; keep one to avoid duplicates.
            if not args.all and data.get("source") == "event_stream_handler":
                continue
            if args.all:
                print(json.dumps({"kind": event.kind, "data": data}, default=str)[:300])
                continue

            kind = event.kind
            if kind.endswith(".started"):
                agent = data.get("agent_name", "?")
                print(f"\n┌─ model stream started · agent={agent}")
            elif kind.endswith(".completed"):
                print("\n└─ stream completed")
            elif kind.endswith(".failed"):
                print(f"\n└─ stream FAILED: {data.get('display', '')}")
            else:
                text = _delta_text(data)
                if text:
                    sys.stdout.write(text)
                    sys.stdout.flush()
                else:
                    marker = data.get("event_kind") or data.get("category") or "event"
                    detail = data.get("tool_name") or data.get("delta_kind") or ""
                    print(f"  · {marker}{f' ({detail})' if detail else ''}")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
