"""Exercise 2 — Wrap a real agent with zero rewrite.

Theme: a source-grounded office-knowledge assistant (archetype: the
source-grounded assistant). A PydanticAI agent answers questions over a small
"project archive" and MUST cite its sources. We wrap it in Kitaru's adapter so
every model call and tool call becomes a durable, costed checkpoint.

Requires: an LLM key (see prework). IMPORTANT: install the pinned adapter
dependency with `pip install 'kitaru[pydantic-ai]'` — a standalone latest
pydantic-ai is too new and breaks the adapter import.
(Verified against kitaru 0.15.0 / pydantic-ai-slim 1.103.0)
"""

import os

from pydantic_ai import Agent

from kitaru.adapters.pydantic_ai import KitaruAgent

# Provider-neutral: defaults to Anthropic (this cohort), override for OpenAI etc.
# e.g. export WORKSHOP_MODEL=openai:gpt-5.2
MODEL = os.getenv("WORKSHOP_MODEL", "anthropic:claude-sonnet-4-5")

# --- a tiny "20 years of project knowledge" archive --------------------------

ARCHIVE = {
    "project_alpha_2019.md": (
        "Project Alpha (2019): 4,200 sqm office fit-out for a fintech tenant. "
        "Acoustic ceiling rafts were chosen over baffles due to a 2.9m clear "
        "height constraint. Budget: 6.1M EUR. Lesson: involve building physics "
        "consultant before space planning, not after."
    ),
    "project_beam_2022.md": (
        "Project Beam (2022): revitalization of a 1970s concrete office block. "
        "Existing slab loads limited raised-floor options; cable management "
        "moved to furniture-integrated trunking. DGNB Gold achieved. "
        "Budget: 14.8M EUR."
    ),
    "office_handbook.md": (
        "Office handbook: all tender documents (Leistungsverzeichnisse) follow "
        "the 2021 template. Meeting minutes are filed per project per quarter. "
        "Standard workplace ratio assumption since 2023: 0.7 desks per employee."
    ),
}


agent = Agent(
    MODEL,  # any provider; set WORKSHOP_MODEL to switch. Alias routing shown in Ex. 3
    system_prompt=(
        "You answer questions about the firm's past projects. Use the "
        "search_archive tool. Every claim MUST cite the source filename in "
        "[brackets]. If the archive doesn't contain the answer, say so."
    ),
)


@agent.tool_plain
def search_archive(query: str) -> str:
    """Naive keyword search over the archive. Returns matching docs with names."""
    query_words = {w.lower().strip("?.,") for w in query.split()}
    hits = []
    for name, content in ARCHIVE.items():
        score = sum(1 for w in query_words if w in content.lower())
        if score > 0:
            hits.append((score, name, content))
    hits.sort(reverse=True)
    if not hits:
        return "No matching documents."
    return "\n\n".join(f"[{name}]\n{content}" for _, name, content in hits[:2])


# --- the only Kitaru-specific lines in this file ------------------------------

durable_agent = KitaruAgent(
    agent,
    name="office_assistant",  # stable name — required (0.16+) so replay/lookup is unambiguous
    checkpoint_strategy="calls",  # every model call + tool call = a checkpoint
    # (the other option is "turn"; per-name tool checkpoint configs also exist)
)

if __name__ == "__main__":
    question = (
        "What did we learn about acoustics in past fit-outs, and what's our "
        "current desk ratio assumption?"
    )
    result = durable_agent.run_sync(question)  # wrapper proxies run/run_sync
    print("\n--- Answer ---\n")
    print(result.output if hasattr(result, "output") else result)
    print("\nNow check the dashboard: every LLM call and the search_archive")
    print("tool call is a checkpoint, with tokens and cost logged per call.")
