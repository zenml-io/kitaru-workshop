"""Exercise 5 — Fan-out at scale (INSTRUCTOR DEMO).

Theme: synthetic persona panel (archetype: the persona simulator). N persona
agents react to a draft press statement in parallel, each in an ISOLATED
containerized runtime; results aggregate into a sentiment distribution.

Demo-only: needs Docker + an LLM key. Students watch the dashboard.

Verified against kitaru 0.15.0: @checkpoint(runtime=..., retries=..., cache=...)
and .submit() exist (checkpoints also expose .map() and .product() for bulk
fan-out — worth mentioning on stage). REMAINING VERIFY: the handle API returned
by .submit() — confirm .result() (or equivalent) with Docker running.
"""

import kitaru
from kitaru import checkpoint, flow

PERSONAS = [
    "skeptical financial journalist, 25 years covering industrial companies",
    "enthusiastic retail investor active on social media",
    "labor union representative at one of the company's plants",
    "ESG analyst at a mid-size asset manager",
    "local newspaper reader in the town where the factory is located",
    "competitor's head of communications (reads everything cynically)",
]

DRAFT_STATEMENT = (
    "Today we announce the consolidation of our European manufacturing "
    "footprint, concentrating production in two flagship plants. This "
    "positions us for sustainable growth and protects the majority of jobs "
    "while we invest 200M EUR in automation and AI-driven quality systems."
)


@checkpoint(runtime="isolated")
def persona_reaction(persona: str, statement: str) -> dict:
    """Each call runs in its own container — parallel, isolated, durable."""
    reaction = kitaru.llm(
        model="cheap",  # panels are exactly where cheap models earn their keep
        prompt=(
            f"You are: {persona}.\n"
            f"React in 2-3 sentences to this press statement, then give a "
            f"sentiment score from -2 (hostile) to +2 (supportive).\n\n"
            f"STATEMENT:\n{statement}\n\n"
            f"End with a line: SCORE: <number>"
        ),
    )
    score = 0.0
    for line in str(reaction).splitlines():
        if line.strip().upper().startswith("SCORE:"):
            try:
                score = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
    return {"persona": persona, "reaction": str(reaction), "score": score}


@checkpoint
def aggregate(reactions: list[dict]) -> dict:
    scores = [r["score"] for r in reactions]
    distribution = {
        "n": len(scores),
        "mean": sum(scores) / max(len(scores), 1),
        "min": min(scores, default=0),
        "max": max(scores, default=0),
        "hostile_count": sum(1 for s in scores if s <= -1),
    }
    kitaru.log(**distribution)
    return distribution


@flow
def sentiment_panel(statement: str = DRAFT_STATEMENT) -> dict:
    # Fan out: submit all persona checkpoints, then gather.
    handles = [persona_reaction.submit(p, statement) for p in PERSONAS]
    reactions = [h.result() for h in handles]  # VERIFY handle API (.result())

    kitaru.save("panel_reactions", reactions)
    return aggregate(reactions)


if __name__ == "__main__":
    handle = sentiment_panel.run()
    result = handle.wait()
    print("\n--- Sentiment distribution ---")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("\nReplay idea: same panel, swap the statement via overrides —")
    print("compare distributions BEFORE the real press release goes out.")
