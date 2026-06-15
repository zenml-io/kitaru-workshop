"""Exercise 3 — Replay & overrides (the centerpiece).

Theme: brand-visibility extraction (archetype: the fan-out analytics engine).
A flow "queries" an AI search engine about a product category and extracts
which brands were mentioned. Then we REPLAY the extraction step:
  (a) with a hand-edited upstream answer (what-if on the input), and
  (b) with a cheaper model alias (what-if on the model) — and diff the cost.

Requires: an LLM key + registered aliases "strong" and "cheap" (see prework).

Run the baseline:   python replay_demo.py
Replay (SDK):       python replay_demo.py --replay <EXEC_ID>
Replay (CLI):       kitaru executions replay <EXEC_ID> --from extract_mentions \
                        --overrides '{"checkpoint.fetch_answers": "..."}'
"""

import argparse

import kitaru
from kitaru import checkpoint, flow
from kitaru.client import KitaruClient  # verified against kitaru 0.15.0

# Simulated AI-engine answer. In production this would be a live API call —
# part of the point: replays don't re-pay for upstream steps.
CANNED_ANSWER = (
    "For project management software, most teams choose Asana for usability, "
    "Linear for speed, and Jira for enterprise compliance. Notion is a "
    "lightweight alternative; Monday.com targets non-technical teams."
)

EXTRACTION_PROMPT = (
    "Extract every brand/product mentioned in this AI-engine answer. For each, "
    "give: name, sentiment (positive/neutral/negative), and the exact phrase "
    "it appeared in. Answer as a JSON list.\n\nANSWER:\n{answer}"
)


@checkpoint
def fetch_answers(category: str) -> str:
    kitaru.log(category=category, engine="simulated")
    return CANNED_ANSWER


@checkpoint
def extract_mentions(answer: str, model_alias: str) -> str:
    # kitaru.llm routes through a registered alias; tokens + cost auto-logged.
    # Signature: kitaru.llm(prompt, *, model=..., system=..., temperature=...,
    # max_tokens=..., name=...) -> str  (verified against kitaru 0.15.0)
    response = kitaru.llm(
        prompt=EXTRACTION_PROMPT.format(answer=answer),
        model=model_alias,
    )
    return response


@flow
def visibility_scan(category: str = "project management software",
                    model_alias: str = "strong") -> str:
    answer = fetch_answers(category)
    mentions = extract_mentions(answer, model_alias)
    kitaru.save("mentions_report", mentions)
    return mentions


def replay_with_edited_answer(exec_id: str) -> None:
    """What-if (a): same code, same model — but the upstream answer changed.

    Use case: 'a customer says our extractor misses brands in list-style
    answers' → paste the offending answer in, replay ONLY the extraction.
    """
    client = KitaruClient()
    edited = CANNED_ANSWER + " ClickUp rounds out the list for hybrid teams."
    handle = client.executions.replay(
        exec_id,
        from_="extract_mentions",
        overrides={"checkpoint.fetch_answers": edited},
    )
    print(f"Replay started from extract_mentions with edited answer: {handle}")


def replay_with_cheap_model(exec_id: str) -> None:
    """What-if (b): same input — cheaper model. THE cost-cutting question.

    Compare the two executions in the dashboard: output quality side by side,
    and the per-call cost difference. This is regression evidence, not vibes.
    """
    client = KitaruClient()
    # replay signature: replay(exec_id, *, from_, overrides=None, **flow_inputs)
    # — flow params ride along as plain kwargs. (verified, kitaru 0.15.0)
    handle = client.executions.replay(
        exec_id,
        from_="extract_mentions",
        model_alias="cheap",
    )
    print(f"Replay started from extract_mentions with alias 'cheap': {handle}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", metavar="EXEC_ID",
                        help="replay an earlier execution instead of running fresh")
    args = parser.parse_args()

    if args.replay:
        replay_with_edited_answer(args.replay)
        replay_with_cheap_model(args.replay)
        print("\nNow: kitaru executions list  → compare the three executions.")
    else:
        handle = visibility_scan.run()
        result = handle.wait()
        print("\n--- Extracted mentions (model: strong) ---\n")
        print(result)
        print("\nNext:  python replay_demo.py --replay <THE_EXEC_ID_ABOVE>")
