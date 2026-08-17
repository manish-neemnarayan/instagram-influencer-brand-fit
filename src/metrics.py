"""
Metrics.

The brief is explicit that accuracy alone is not acceptable. Reported here:
confusion matrix, precision, recall, false positives and negatives, human-review
rate, decision cost, and calibration.

The classification framing: the agent's terminal decision is SIGN or not-SIGN,
and the ground truth is whether the influencer was actually clean (authentic,
matched and safe). Probes and escalations are not classification errors - they
are the agent declining to classify yet - so they are reported separately rather
than being forced into the matrix.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import policies as P


def confusion(g: pd.DataFrame) -> dict:
    """2x2 over SIGN vs not, against 'was actually clean'."""
    clean = g.true_A_authentic & g.true_M_matched & g.true_S_safe
    signed = g.action == P.SIGN

    tp = int((signed & clean).sum())      # signed someone worth signing
    fp = int((signed & ~clean).sum())     # signed someone who was not
    fn = int((~signed & clean).sum())     # passed on someone worth signing
    tn = int((~signed & ~clean).sum())

    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")

    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        # FP broken out by which latent was actually false - they do not cost
        # remotely the same, which is the whole point of the cost matrix
        "fp_safety_risk": int((signed & ~g.true_S_safe).sum()),
        "fp_inauthentic": int((signed & ~g.true_A_authentic).sum()),
        "fp_sophisticated": int((signed & g.true_sophisticated).sum()),
        "fp_mismatch_only": int(
            (signed & g.true_A_authentic & ~g.true_M_matched & g.true_S_safe).sum()
        ),
        # the agent declining to classify
        "human_review_rate": float((g.action == P.ESCALATE).mean()),
        "probe_rate": float(g.action.isin([P.GIFT, P.ANALYTICS]).mean()),
        "total_cost": float(g.cost.sum()),
        "mean_cost": float(g.cost.mean()),
    }


def calibration(g: pd.DataFrame, n_bins: int = 5) -> pd.DataFrame:
    """
    Does 'this one is 80% likely to be clean' actually come true 80% of the time?

    Two practitioners raised calibration independently, and both were right that
    it cannot be assessed on 40 cases. This is meant to be run on POOLED
    replications (30 runs x 40 cases = 1200) where the bins have enough in them
    to mean something.
    """
    clean = (g.true_A_authentic & g.true_M_matched & g.true_S_safe).astype(int)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(g.p_clean, edges) - 1, 0, n_bins - 1)

    rows = []
    for b in range(n_bins):
        m = idx == b
        if m.sum() == 0:
            continue
        rows.append(
            {
                "bin": f"{edges[b]:.1f}-{edges[b+1]:.1f}",
                "n": int(m.sum()),
                "mean_predicted": float(g.p_clean[m].mean()),
                "observed_clean": float(clean[m].mean()),
                "gap": float(g.p_clean[m].mean() - clean[m].mean()),
            }
        )
    return pd.DataFrame(rows)


def expected_calibration_error(cal: pd.DataFrame) -> float:
    """Weighted mean absolute gap between predicted and observed."""
    if cal.empty:
        return float("nan")
    w = cal.n / cal.n.sum()
    return float((w * cal.gap.abs()).sum())
