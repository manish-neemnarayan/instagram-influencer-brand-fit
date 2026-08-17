"""
Replications.

A single 40-case test set is the required deliverable, but 40 cases contain only
a handful of sophisticated fakes - too few to (a) report stable metrics or
(b) supply the five wrong decisions the failure analysis needs.

This runs the same experiment across many seeds. The headline table still comes
from the designated test set; these give confidence intervals and a pool of
failures to examine.

    python experiments/run_replications.py [n_reps]

Outputs
    results/replications.csv        per-policy metrics for every seed
    results/replication_summary.md  mean and spread
    results/failures.csv            every wrong decision, pooled
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import AGENT_PARAMS  # noqa: E402
from simulate import generate_cases  # noqa: E402
from run_experiment import run_arm, N_TEST  # noqa: E402
import policies as P  # noqa: E402


def metrics(g: pd.DataFrame) -> dict:
    clean = g.true_A_authentic & g.true_M_matched & g.true_S_safe
    signed = g.action == P.SIGN
    return {
        "total_cost": g.cost.sum(),
        "signed": int(signed.sum()),
        "signed_unsafe": int((signed & ~g.true_S_safe).sum()),
        "signed_inauthentic": int((signed & ~g.true_A_authentic).sum()),
        "signed_sophisticated": int((signed & g.true_sophisticated).sum()),
        "declined_clean": int(((g.action == P.DECLINE) & clean).sum()),
        "human_review_rate": (g.action == P.ESCALATE).mean(),
        "gift_rate": (g.action == P.GIFT).mean(),
        "analytics_rate": (g.action == P.ANALYTICS).mean(),
    }


def is_failure(row) -> str | None:
    """Name the failure condition, or None if the decision was defensible."""
    clean = row.true_A_authentic and row.true_M_matched and row.true_S_safe
    if row.action == P.SIGN:
        if not row.true_S_safe:
            return "signed_safety_risk"
        if not row.true_A_authentic:
            return ("signed_sophisticated_fake" if row.true_sophisticated
                    else "signed_crude_fake")
        if not row.true_M_matched:
            return "signed_mismatch"
    if row.action == P.DECLINE and clean:
        return "declined_clean"
    return None


def main() -> None:
    n_reps = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    (ROOT / "results").mkdir(exist_ok=True)

    rows, failures = [], []
    for seed in range(1000, 1000 + n_reps):
        cases = generate_cases(N_TEST, seed=seed)
        dec = run_arm(cases, AGENT_PARAMS, "misspecified")
        dec["seed"] = seed

        for policy, g in dec.groupby("policy", sort=False):
            rows.append({"seed": seed, "policy": policy, **metrics(g)})

        for r in dec.itertuples():
            f = is_failure(r)
            if f:
                failures.append(
                    {"seed": seed, "policy": r.policy, "case_id": r.case_id,
                     "failure": f, "action": r.action, "cost": r.cost,
                     "p_authentic": round(r.p_authentic, 3),
                     "p_matched": round(r.p_matched, 3),
                     "p_safe": round(r.p_safe, 3),
                     "max_atom": round(r.max_atom, 3),
                     "sophisticated": r.true_sophisticated}
                )

    reps = pd.DataFrame(rows)
    reps.to_csv(ROOT / "results/replications.csv", index=False)

    fails = pd.DataFrame(failures)
    fails.to_csv(ROOT / "results/failures.csv", index=False)

    agg = reps.groupby("policy").agg(["mean", "std"]).round(3)
    summary = reps.groupby("policy")[
        ["total_cost", "signed_unsafe", "signed_sophisticated",
         "declined_clean", "human_review_rate", "gift_rate", "analytics_rate"]
    ].mean().round(3)

    lines = [
        "# Replication summary",
        "",
        f"{n_reps} independent runs of {N_TEST} cases each, seeds 1000-{1000+n_reps-1}. "
        "Agent uses misspecified parameters throughout (the realistic arm).",
        "",
        "## Mean per run",
        "",
        summary.to_markdown(),
        "",
        "## Cost spread",
        "",
        reps.groupby("policy").total_cost.describe().round(1).to_markdown(),
        "",
        "## Failure conditions (pooled across all runs)",
        "",
        fails.groupby(["policy", "failure"]).size().rename("n").reset_index().to_markdown(index=False),
    ]
    (ROOT / "results/replication_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(summary.to_string())
    print()
    print(fails.groupby(["policy", "failure"]).size().to_string())


if __name__ == "__main__":
    main()
