"""Exercise 4 — Human-in-the-loop + shipping.

Theme: a counter-offer drafter with an approval gate (archetype: the
high-stakes copilot). Nothing legally binding leaves the building without
sign-off — and the infrastructure shouldn't burn compute while a human thinks.

Requires: an LLM key + alias "strong".

Run:      python approval_flow.py
Approve:  kitaru executions input <EXEC_ID> --value true
          kitaru executions resume <EXEC_ID>
Deploy:   python approval_flow.py --deploy
"""

import argparse

import kitaru
from kitaru import checkpoint, flow

SUPPLIER_CONTEXT = (
    "Supplier: Apex Components GmbH. Current quote: 18.40 EUR/unit for 50k "
    "units/yr of part XJ-220. Market benchmark: 16.90-17.60 EUR/unit. "
    "Relationship: 6 years, 99.1% on-time delivery. Their last two quotes "
    "accepted without negotiation. Payment terms: net 30."
)


@checkpoint
def draft_counter_offer(context: str) -> str:
    # kitaru.llm(prompt, *, model=...) — verified against kitaru 0.15.0
    return kitaru.llm(
        model="strong",
        prompt=(
            "You are a procurement negotiation assistant. Draft a concise, "
            "respectful counter-offer email based on this context. Include a "
            "target price with justification from the benchmark.\n\n" + context
        ),
    )


@checkpoint
def finalize(draft: str) -> str:
    kitaru.log(status="approved-and-finalized")
    return draft + "\n\n[Approved via Kitaru HITL gate]"


@flow
def counter_offer(context: str = SUPPLIER_CONTEXT) -> str:
    draft = draft_counter_offer(context)
    kitaru.save("draft_offer", draft)
    print("\n--- DRAFT (awaiting approval) ---\n", draft[:400], "...\n")

    # The magic: this suspends the execution AND releases the compute.
    # The pod is gone. Tomorrow, when someone approves, the execution
    # resumes exactly here — prior checkpoints served from cache.
    # NOTES (verified against kitaru 0.15.0):
    #   - kitaru.wait() is keyword-only.
    #   - schema=bool is REQUIRED to accept `--value true`; without a schema
    #     the wait is a plain continue-gate (resolve with `--value null`).
    approved = kitaru.wait(
        name="approval",
        question="Approve this counter-offer?",
        schema=bool,
    )

    if not approved:
        kitaru.log(status="rejected")
        return "Counter-offer rejected by reviewer."
    return finalize(draft)


def deploy() -> None:
    """Freeze this flow as an immutable, versioned deployment.

    After this, ANY client — including a TypeScript frontend via the REST
    API — invokes it by name. Canary/rollback happens via tags, not redeploys.
    """
    deployment = counter_offer.deploy()  # verified: flows expose .deploy()/.invoke()/.replay()
    print(f"Deployed: {deployment}")
    print("Invoke from anywhere:")
    print('  KitaruClient().deployments.invoke(flow="counter_offer", '
          'inputs={"context": "..."})')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args()

    if args.deploy:
        deploy()
    else:
        handle = counter_offer.run()
        print("Execution started. It will SUSPEND at the approval gate.")
        print("Approve it from another terminal:")
        print("  kitaru executions list           # find the suspended exec ID")
        print("  kitaru executions input <ID> --value true")
        print("  kitaru executions resume <ID>")
        result = handle.wait()
        print("\n--- FINAL ---\n", result)
