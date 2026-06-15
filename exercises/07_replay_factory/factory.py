"""Capstone — the Replay Factory loop (advanced track).

The thesis of the whole workshop, made runnable:

    ingest cases  →  run under baseline + candidate  →  judge good/bad  →
    aggregate  →  ship / don't-ship verdict

You have a batch of production CASES (here a JSONL of question + reference
answer — an honest stand-in for *exported traces*; true LangFuse/Datadog
import is the roadmap edge, see README). The loop runs each case through your
agent under two model aliases, has an LLM judge score each answer against the
reference, and reports whether the cheaper model holds up — with the
regressions named, so the decision is evidence, not vibes.

The eval loop is *itself a Kitaru flow*: three durable checkpoints
(ingest → run+judge → aggregate). Crash during aggregation and you DON'T
re-pay the LLM batch — it's cached. That's the workshop's whole point applied
to evaluation.

KITARU DATA-FLOW RULE (learned the hard way — see README): inside a @flow, a
checkpoint's return value is an artifact *handle*, not the raw value. Wire
handles checkpoint→checkpoint or return them; never subscript/parse a
checkpoint output in flow scope. All real work happens inside checkpoints.

Requires: aliases `strong` and `cheap` (see prework), an LLM key.

Run:  python factory.py
      python factory.py --cases cases.jsonl --candidate cheap --baseline strong
"""

import argparse
import json
import os

import kitaru
from kitaru import checkpoint, flow

HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = (
    "You are a support agent for a home-improvement retailer. Be concise, "
    "accurate, and safe. Never invent stock numbers, prices, order status, or "
    "delivery dates you don't have."
)

JUDGE_RUBRIC = (
    "You are a strict QA reviewer. Given a customer QUESTION, a REFERENCE answer "
    "describing the correct behavior, and a CANDIDATE answer from an agent, "
    "decide whether the candidate is acceptable.\n"
    "Acceptable = it follows the same policy/behavior as the reference (it may "
    "be worded differently). Unacceptable = it contradicts the reference, "
    "invents facts it shouldn't, or is unsafe.\n"
    "Reply with exactly two lines:\n"
    "VERDICT: good   (or)   VERDICT: bad\n"
    "REASON: <one short sentence>"
)


def _judge_one(question: str, reference: str, candidate: str) -> dict:
    """One LLM-as-judge call (plain helper, runs inside the run_batch checkpoint)."""
    verdict_text = kitaru.llm(
        prompt=f"QUESTION:\n{question}\n\nREFERENCE:\n{reference}\n\nCANDIDATE:\n{candidate}",
        system=JUDGE_RUBRIC,
        model="strong",  # always judge with the strong model
        temperature=0.0,
    )
    good, reason = False, ""
    for line in str(verdict_text).splitlines():
        low = line.strip().lower()
        if low.startswith("verdict:"):
            good = "good" in low
        elif low.startswith("reason:"):
            reason = line.split(":", 1)[1].strip()
    return {"good": good, "reason": reason}


@checkpoint
def load_cases(path: str) -> str:
    """Ingest the batch → JSON string. In production this is where a trace
    adapter maps LangFuse/Datadog observations into replay cases (roadmap)."""
    full = path if os.path.isabs(path) else os.path.join(HERE, path)
    with open(full) as f:
        cases = [json.loads(line) for line in f if line.strip()]
    kitaru.log(case_count=len(cases), source=os.path.basename(full))
    return json.dumps(cases)


@checkpoint
def run_and_judge(cases_json: str, baseline: str, candidate: str,
                  samples: int) -> str:
    """Run each case under both models and judge. The candidate runs `samples`
    times so we can compute pass^k (the field-standard reliability metric —
    LLMs are stochastic, one run is an anecdote; see EVALS_PRIMER §4).
    The expensive checkpoint — cached on replay so aggregation tweaks are free."""
    cases = json.loads(cases_json)
    rows = []
    for case in cases:
        q, ref = case["question"], case["reference"]
        base_ans = kitaru.llm(prompt=q, system=SYSTEM, model=baseline)
        # k independent candidate rollouts → list of good/bad
        cand_runs = []
        for _ in range(max(1, samples)):
            cand_ans = kitaru.llm(prompt=q, system=SYSTEM, model=candidate)
            cand_runs.append(_judge_one(q, ref, cand_ans))
        rows.append({
            "id": case["id"],
            "baseline": _judge_one(q, ref, base_ans),
            "candidate_runs": cand_runs,
        })
    return json.dumps(rows)


@checkpoint
def aggregate(rows_json: str, baseline: str, candidate: str, samples: int) -> str:
    rows = json.loads(rows_json)
    n = len(rows)
    k = max(1, samples)
    base_pass = sum(1 for r in rows if r["baseline"]["good"])
    # pass^1: average single-rollout pass rate across all candidate runs.
    # pass^k: a case "passes" only if ALL k rollouts are judged good (reliability).
    total_runs = sum(len(r["candidate_runs"]) for r in rows) or 1
    cand_pass1 = sum(run["good"] for r in rows for run in r["candidate_runs"]) / total_runs
    cand_passk = sum(1 for r in rows if all(run["good"] for run in r["candidate_runs"])) / n if n else 0
    # Regressions = baseline got it right, candidate fails pass^k (not reliably good).
    regressions = [
        {"id": r["id"], "why": next((run["reason"] for run in r["candidate_runs"]
                                     if not run["good"]), "")}
        for r in rows
        if r["baseline"]["good"] and not all(run["good"] for run in r["candidate_runs"])
    ]
    # Per-case breakdown so the report shows WHICH cases moved, not just totals.
    per_case = [
        {
            "id": r["id"],
            "baseline": "good" if r["baseline"]["good"] else "bad",
            "candidate": "good" if all(run["good"] for run in r["candidate_runs"]) else "bad",
        }
        for r in rows
    ]
    report = {
        "cases": n,
        "samples": k,
        "baseline_model": baseline,
        "candidate_model": candidate,
        "baseline_pass_rate": round(base_pass / n, 3) if n else 0,
        "candidate_pass1": round(cand_pass1, 3),
        "candidate_passk": round(cand_passk, 3),
        "regressions": regressions,
        "per_case": per_case,
        # Decision rule: ship the cheaper model only if it adds no regressions
        # at pass^k. Cost lives in the dashboard (per-call, auto-logged).
        "verdict": "SHIP" if not regressions else "DO NOT SHIP",
    }
    kitaru.save("replay_factory_report", report)
    kitaru.log(verdict=report["verdict"], regressions=len(regressions), samples=k)
    return json.dumps(report)


@flow
def replay_factory(cases_path: str = "cases.jsonl",
                   baseline: str = "strong",
                   candidate: str = "cheap",
                   samples: int = 1) -> str:
    # Flow body = pure wiring. Each checkpoint output flows into the next
    # checkpoint (handles), never inspected in flow scope.
    cases_json = load_cases(cases_path)
    rows_json = run_and_judge(cases_json, baseline, candidate, samples)
    return aggregate(rows_json, baseline, candidate, samples)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--cases", default="cases.jsonl")
    p.add_argument("--baseline", default="strong")
    p.add_argument("--candidate", default="cheap")
    p.add_argument("--samples", type=int, default=1,
                   help="candidate rollouts per case → pass^k reliability (default 1)")
    args = p.parse_args()

    report = json.loads(replay_factory.run(
        cases_path=args.cases, baseline=args.baseline,
        candidate=args.candidate, samples=args.samples
    ).wait())

    k = report["samples"]
    print("\n=== Replay Factory report ===")
    print(f"  cases:               {report['cases']}  (candidate samples k={k})")
    print(f"  baseline ({report['baseline_model']}):  "
          f"{report['baseline_pass_rate']:.0%} pass")
    if k > 1:
        cand = (f"pass^1 {report['candidate_pass1']:.0%}  |  "
                f"pass^{k} {report['candidate_passk']:.0%}")
    else:
        cand = f"{report['candidate_pass1']:.0%} pass"
    print(f"  candidate ({report['candidate_model']}): {cand}")
    print(f"  regressions:         {len(report['regressions'])}")
    for r in report["regressions"]:
        print(f"    - [{r['id']}] {r['why']}")

    # Per-case breakdown — see which cases moved, not just the totals.
    print("\n  Per-case (baseline → candidate):")
    for c in report["per_case"]:
        moved = "  ⚠ REGRESSED" if (c["baseline"] == "good" and c["candidate"] == "bad") else ""
        print(f"    [{c['id']:<22}] {c['baseline']:>4} → {c['candidate']:<4}{moved}")

    print(f"\n  VERDICT: {report['verdict']}")

    # This demo judges one dimension (policy correctness) on a model swap.
    # In production you'd run this SAME replay-and-judge loop on more changes,
    # and score more dimensions — that's the real "factory":
    print(
        "\n  In production, replay-regress more than a model swap:\n"
        "    • prompt edits · model-version bumps · provider/open-model swaps\n"
        "    • RAG re-index (new chunking/embeddings) · tool/schema changes\n"
        "    • temperature/params · new guardrails · changed business rules\n"
        "  …and score beyond pass/fail:\n"
        "    • outcome/state checks & correct tool calls (more trustworthy than a judge)\n"
        "    • safety/hallucination · grounding/citations · output/JSON validity\n"
        "    • cost & latency · reliability via pass^k (not n=1)\n"
        "  Tip: every 'bad' the judge catches → add it to cases.jsonl (your growing\n"
        "  regression set). Replay kills bad candidates cheaply; confirm winners live."
    )
