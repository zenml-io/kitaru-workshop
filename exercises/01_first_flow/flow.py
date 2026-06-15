"""Exercise 1 — Your first durable flow.

Theme: email bounce triage (archetype: the batch classifier).
Classify bounce messages into a taxonomy, durably. NO API KEY NEEDED —
the classifier is a deterministic heuristic so everyone can run this.

What you'll see:
  1. A flow made of checkpoints.
  2. Kill it mid-run (Ctrl+C during the slow step), run again — completed
     checkpoints are cached, only the rest re-executes.
  3. Metadata via kitaru.log(), a named artifact via kitaru.save().

Run:  python flow.py
Then: kitaru executions list
"""

import time

import kitaru
from kitaru import checkpoint, flow

# --- fake "production" data: free-text bounce reasons -----------------------

RAW_BOUNCES = [
    "550 5.1.1 The email account that you tried to reach does not exist",
    "421 4.7.0 Try again later, closing connection (throttled)",
    "550 5.7.26 This mail has been blocked because the sender is unauthenticated (DKIM fail)",
    "552 5.2.2 The recipient's inbox is out of storage space",
    "550 5.7.1 Message rejected due to local policy (blacklisted IP)",
    "450 4.2.0 Greylisted, please retry shortly",
    "550 5.1.1 User unknown in virtual mailbox table",
    "554 5.7.9 Message not accepted for policy reasons (SPF softfail)",
]

TAXONOMY = {
    "hard_bounce": ["does not exist", "user unknown"],
    "soft_bounce": ["try again", "greylisted", "storage space"],
    "auth_failure": ["dkim", "spf", "unauthenticated"],
    "reputation": ["blacklisted", "policy reasons", "local policy"],
}


@checkpoint
def fetch_bounces(limit: int) -> list[str]:
    """Pretend this reads from the MTA logs."""
    kitaru.log(source="mta-logs-fake", count=min(limit, len(RAW_BOUNCES)))
    return RAW_BOUNCES[:limit]


@checkpoint
def classify(bounces: list[str]) -> list[dict]:
    """Heuristic classifier. In Exercise 2 we replace brains like this with an LLM."""
    results = []
    for msg in bounces:
        label = "unknown"
        for category, needles in TAXONOMY.items():
            if any(n in msg.lower() for n in needles):
                label = category
                break
        results.append({"message": msg, "label": label})
    return results


@checkpoint(cache=False)
def correlate(classified: list[dict]) -> dict:
    """Aggregate — and pretend it's expensive so you have time to Ctrl+C.

    cache=False keeps this step always re-running, so the lesson lands every
    time: re-run the flow and `fetch_bounces`/`classify` come back from cache
    instantly while `correlate` does its (slow) work again. No need to kill the
    first run for the demo to work — though killing it mid-sleep shows the same
    thing: completed checkpoints are never redone.
    """
    time.sleep(10)
    summary: dict[str, int] = {}
    for row in classified:
        summary[row["label"]] = summary.get(row["label"], 0) + 1

    # A named, versioned artifact: future executions (and other flows) can
    # kitaru.load() it. Think: "the taxonomy report as of this run".
    # NOTE: kitaru.save()/load() must be called INSIDE a @checkpoint.
    kitaru.save("bounce_summary", summary)
    kitaru.log(total=sum(summary.values()))
    return summary


@flow
def bounce_triage(limit: int = 8) -> dict:
    bounces = fetch_bounces(limit)
    classified = classify(bounces)
    return correlate(classified)


if __name__ == "__main__":
    handle = bounce_triage.run(limit=8)
    result = handle.wait()
    print("\nBounce summary:", result)
    print("Now run:  kitaru executions list")
