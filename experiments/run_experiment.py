"""
Main experiment.

Writes everything to data/ and results/ so that every number in the paper has a
file behind it and the run can be repeated exactly.

    python experiments/run_experiment.py

Outputs
    data/tuning_cases.csv      200 cases, used ONLY to choose thresholds
    data/test_cases.csv        40 cases, untouched until scoring
    results/decisions.csv      every belief, action and realised cost
    results/summary.md         headline table
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import AGENT_PARAMS, TRUE_PARAMS  # noqa: E402
from simulate import generate_cases, observable_only  # noqa: E402
from agent import update_beliefs  # noqa: E402
import policies as P  # noqa: E402

N_TUNING = 200
N_TEST = 40
SEED_TUNING = 11
SEED_TEST = 42


def run_arm(cases: pd.DataFrame, params, label: str) -> pd.DataFrame:
    """Score all three policies on one set of cases under one parameter set."""
    beliefs = update_beliefs(observable_only(cases), params)
    merged = beliefs.merge(cases, on="case_id")

    rows = []
    for b in merged.itertuples():
        for name, action in [
            ("v0_threshold", P.policy_threshold(b)),
            ("v0_expected_cost", P.policy_expected_cost(b)),
            ("engagement_baseline", P.policy_engagement_baseline(b)),
        ]:
            rows.append(
                {
                    "arm": label,
                    "policy": name,
                    "case_id": b.case_id,
                    "action": action,
                    "cost": P.realised_cost(action, b),
                    "p_authentic": b.p_authentic,
                    "p_matched": b.p_matched,
                    "p_safe": b.p_safe,
                    "p_clean": b.p_clean,
                    "max_atom": b.max_atom,
                    "true_A_authentic": b.true_A_authentic,
                    "true_M_matched": b.true_M_matched,
                    "true_S_safe": b.true_S_safe,
                    "true_sophisticated": b.true_sophisticated,
                }
            )
    return pd.DataFrame(rows)


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (arm, policy), g in df.groupby(["arm", "policy"], sort=False):
        clean = g.true_A_authentic & g.true_M_matched & g.true_S_safe
        signed = g.action == P.SIGN

        out.append(
            {
                "arm": arm,
                "policy": policy,
                "total_cost": g.cost.sum(),
                "mean_cost": g.cost.mean(),
                "signed": int(signed.sum()),
                "signed_unsafe": int((signed & ~g.true_S_safe).sum()),
                "signed_inauthentic": int((signed & ~g.true_A_authentic).sum()),
                "signed_sophisticated": int((signed & g.true_sophisticated).sum()),
                "declined_clean": int(((g.action == P.DECLINE) & clean).sum()),
                "human_review_rate": (g.action == P.ESCALATE).mean(),
                "probe_rate": g.action.isin([P.GIFT, P.ANALYTICS]).mean(),
            }
        )
    return pd.DataFrame(out)


def main() -> None:
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "results").mkdir(exist_ok=True)

    tuning = generate_cases(N_TUNING, seed=SEED_TUNING)
    test = generate_cases(N_TEST, seed=SEED_TEST)
    tuning.to_csv(ROOT / "data/tuning_cases.csv", index=False)
    test.to_csv(ROOT / "data/test_cases.csv", index=False)

    # two arms: agent guessing at the parameters, and agent handed the truth
    frames = [
        run_arm(test, AGENT_PARAMS, "misspecified"),
        run_arm(test, TRUE_PARAMS, "oracle"),
    ]
    decisions = pd.concat(frames, ignore_index=True)
    decisions.to_csv(ROOT / "results/decisions.csv", index=False)

    summary = summarise(decisions)
    summary.to_csv(ROOT / "results/summary.csv", index=False)

    lines = [
        "# Experiment summary",
        "",
        f"Test set: {N_TEST} cases, seed {SEED_TEST}. Thresholds chosen on a separate "
        f"{N_TUNING}-case tuning set (seed {SEED_TUNING}).",
        "",
        "`misspecified` = agent guesses the parameters (realistic). "
        "`oracle` = agent is handed the true generating parameters (impossible in "
        "practice; included to show how much the results depend on being right).",
        "",
        summary.round(3).to_markdown(index=False),
        "",
        "## Ground truth in the test set",
        "",
        f"- inauthentic: {(~test.true_A_authentic).sum()}",
        f"- of those, sophisticated: {test.true_sophisticated.sum()}",
        f"- mismatched: {(~test.true_M_matched).sum()}",
        f"- safety risk: {(~test.true_S_safe).sum()}",
        f"- clean: {(test.true_A_authentic & test.true_M_matched & test.true_S_safe).sum()}",
    ]
    (ROOT / "results/summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(summary.round(3).to_string(index=False))
    print(f"\nwrote data/ and results/ under {ROOT}")


if __name__ == "__main__":
    main()
