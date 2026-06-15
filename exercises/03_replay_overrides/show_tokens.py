"""Show per-checkpoint model + token usage for a Kitaru execution.

`kitaru executions list` and the dashboard summary don't surface per-call
tokens — they live in each checkpoint's `llm_calls` metadata. This reads them
out so you can compare `strong` vs `cheap` from the terminal.

Usage:
    python exercises/03_replay_overrides/show_tokens.py <EXEC_ID>

NOTE: dollar cost is populated only when Kitaru has pricing for the model.
Unpriced models (e.g. gpt-5.2 / gpt-5-nano) show "$— (unpriced)"; tokens are
always tracked, so the token counts are the reliable comparison.
"""

import sys

from kitaru.client import KitaruClient


def main(exec_id: str) -> None:
    ex = KitaruClient().executions.get(exec_id)
    print(f"Execution {exec_id} — {ex.status}")
    found = False
    for cp in ex.checkpoints:
        for call in (cp.metadata or {}).get("llm_calls", {}).values():
            found = True
            cost = (call.get("cost") or {}).get("estimated_cost_usd")
            cost_s = f"${cost}" if cost is not None else "$— (unpriced model)"
            print(
                f"  {cp.name}: {call['resolved_model']}  "
                f"tokens in/out/total="
                f"{call['tokens_input']}/{call['tokens_output']}/{call['total_tokens']}"
                f"  {cost_s}"
            )
    if not found:
        print("  (no LLM calls recorded on this execution)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python exercises/03_replay_overrides/show_tokens.py <EXEC_ID>")
    main(sys.argv[1])
