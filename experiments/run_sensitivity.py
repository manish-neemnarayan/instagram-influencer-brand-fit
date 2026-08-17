"""
Sensitivity analysis.

Three numbers in this model are guesses, and no source measures any of them:

  p_A_false      base rate of inauthentic audiences among SHORTLISTED influencers.
                 Published figures (37% vendor, 15-49% meta-analysis) measure what
                 fraction of an AUDIENCE is fake, which is a different quantity.
  sign_unsafe    cost of signing a latent brand-safety risk. Set to 200 on the
                 assumption that one such failure costs about ten wasted fees.
  decline_good   cost of passing on someone who would have worked. Invisible in
                 practice, so intuition sets it low. Two practitioners on
                 r/advertising argued it should exceed the cost of signing a fake.

Rather than pick values and defend them, the whole experiment is re-run across a
range of each. If the agent's behaviour is stable, the guesses do not matter and
that can be said with evidence. If it flips somewhere, that location is itself a
finding - it identifies the number worth going and measuring.

Method suggested by efrique (PhD statistics) on r/AskStatistics: you cannot know
the bias without information you do not have, but you can explore sensitivity to
a range of possible circumstances by simulation.

    python experiments/run_sensitivity.py [n_reps_per_setting]
"""

from __future__ import annotations

import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import AGENT_PARAMS, TRUE_PARAMS, COSTS  # noqa: E402
from simulate import generate_cases, observable_only  # noqa: E402
from agent import update_beliefs  # noqa: E402
import policies as P  # noqa: E402
from metrics import confusion  # noqa: E402

N_CASES = 40
V0_POLICIES = ["v0_threshold", "v0_expected_cost", "engagement_baseline"]


def score(cases, agent_params, costs) -> pd.DataFrame:
    beliefs = update_beliefs(observable_only(cases), agent_params)
    merged = beliefs.merge(cases, on="case_id")
    rows = []
    for b in merged.itertuples():
        for name, action in [
            ("v0_threshold", P.policy_threshold(b)),
            ("v0_expected_cost", P.policy_expected_cost(b, costs=costs)),
            ("engagement_baseline", P.policy_engagement_baseline(b)),
        ]:
            rows.append(
                {
                    "policy": name,
                    "action": action,
                    "cost": P.realised_cost(action, b, costs),
                    "p_clean": b.p_clean,
                    "true_A_authentic": b.true_A_authentic,
                    "true_M_matched": b.true_M_matched,
                    "true_S_safe": b.true_S_safe,
                    "true_sophisticated": b.true_sophisticated,
                }
            )
    return pd.DataFrame(rows)


def sweep(param_name, values, n_reps) -> pd.DataFrame:
    out = []
    for v in values:
        true_p, agent_p, costs = TRUE_PARAMS, AGENT_PARAMS, deepcopy(COSTS)

        if param_name == "p_A_false":
            true_p = replace(TRUE_PARAMS, p_A_false=v)
            # the agent keeps its own (wrong) belief about the base rate - it does
            # not get told when the world changes
        else:
            costs[param_name] = v

        for seed in range(2000, 2000 + n_reps):
            cases = generate_cases(N_CASES, params=true_p, seed=seed)
            df = score(cases, agent_p, costs)
            for policy, g in df.groupby("policy", sort=False):
                out.append({"param": param_name, "value": v, "seed": seed,
                            "policy": policy, **confusion(g)})
    return pd.DataFrame(out)


def main() -> None:
    n_reps = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    (ROOT / "results").mkdir(exist_ok=True)

    sweeps = {
        "p_A_false": [0.10, 0.20, 0.25, 0.30, 0.40],
        "sign_unsafe": [50, 100, 200, 350, 500],
        "decline_good": [5, 10, 20, 30, 40],
    }

    frames = [sweep(k, v, n_reps) for k, v in sweeps.items()]
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(ROOT / "results/sensitivity.csv", index=False)

    keep = ["total_cost", "false_positive", "false_negative",
            "fp_safety_risk", "fp_sophisticated", "human_review_rate", "precision", "recall"]
    agg = (df.groupby(["param", "value", "policy"])[keep]
             .mean().round(3).reset_index())

    lines = ["# Sensitivity analysis", "",
             f"{n_reps} runs of {N_CASES} cases at each setting. "
             "Only the swept quantity changes; everything else is held fixed.", ""]

    for param, block in agg.groupby("param", sort=False):
        lines += [f"## {param}", "",
                  block.drop(columns="param").to_markdown(index=False), ""]

        # where does the ordering of the two agent policies flip?
        piv = block.pivot(index="value", columns="policy", values="total_cost")
        if {"v0_threshold", "v0_expected_cost"} <= set(piv.columns):
            better = (piv["v0_expected_cost"] < piv["v0_threshold"])
            if better.nunique() > 1:
                lines += [f"**Policy ordering flips within this range.**", ""]
            else:
                who = "expected_cost" if better.iloc[0] else "threshold"
                lines += [f"Ordering stable across the range: {who} wins throughout.", ""]

    (ROOT / "results/sensitivity.md").write_text("\n".join(lines), encoding="utf-8")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
