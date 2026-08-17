"""
Calibration, pooled across replications.

Two practitioners raised calibration independently, and both were right that it
cannot be assessed on 40 cases - the bins would hold two or three items each and
you would be reading noise. This pools many runs so the bins mean something.

The question: when the agent says "80% likely to be clean", does that come true
80% of the time?

    python experiments/run_calibration.py [n_reps]
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import AGENT_PARAMS, TRUE_PARAMS  # noqa: E402
from simulate import generate_cases  # noqa: E402
from run_experiment import run_arm, N_TEST  # noqa: E402
from metrics import calibration, expected_calibration_error, confusion  # noqa: E402


def main() -> None:
    n_reps = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    (ROOT / "results").mkdir(exist_ok=True)

    frames = []
    for seed in range(3000, 3000 + n_reps):
        cases = generate_cases(N_TEST, seed=seed)
        for params, arm in [(AGENT_PARAMS, "misspecified"), (TRUE_PARAMS, "oracle")]:
            d = run_arm(cases, params, arm)
            d["seed"] = seed
            frames.append(d)
    pooled = pd.concat(frames, ignore_index=True)

    # beliefs are identical across policies within an arm, so one policy is enough
    lines = ["# Calibration", "",
             f"Pooled over {n_reps} runs of {N_TEST} cases "
             f"({n_reps * N_TEST} cases per arm). Bins on P(clean).", ""]

    for arm, g in pooled[pooled.policy == "v0_expected_cost"].groupby("arm", sort=False):
        cal = calibration(g, n_bins=5)
        ece = expected_calibration_error(cal)
        lines += [f"## {arm} (ECE = {ece:.3f})", "",
                  cal.round(3).to_markdown(index=False), ""]
        cal.to_csv(ROOT / f"results/calibration_{arm}.csv", index=False)
        print(f"--- {arm}  ECE={ece:.3f}")
        print(cal.round(3).to_string(index=False))

    # headline metrics pooled, for stable precision/recall
    rows = []
    for (arm, policy), g in pooled.groupby(["arm", "policy"], sort=False):
        rows.append({"arm": arm, "policy": policy, **confusion(g)})
    pooled_metrics = pd.DataFrame(rows)
    pooled_metrics.to_csv(ROOT / "results/pooled_metrics.csv", index=False)

    keep = ["arm", "policy", "precision", "recall", "false_positive", "false_negative",
            "fp_safety_risk", "fp_sophisticated", "human_review_rate", "mean_cost"]
    lines += ["## Pooled metrics", "",
              pooled_metrics[keep].round(3).to_markdown(index=False), ""]

    (ROOT / "results/calibration.md").write_text("\n".join(lines), encoding="utf-8")
    print()
    print(pooled_metrics[keep].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
