"""
Case generator.

Two steps per influencer:
  1. flip three weighted coins (the priors) -> her sealed true label (A, M, S)
  2. draw her six signals from whichever distribution matches that label

The labels are stored alongside the signals but MUST NOT be shown to the agent
at decision time. scoring.py is the only module allowed to read them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from model import Params, TRUE_PARAMS, beta_ab


def _beta(rng: np.random.Generator, spec: tuple[float, float]) -> float:
    a, b = beta_ab(*spec)
    return float(rng.beta(a, b))


def _blend(fake: tuple[float, float], auth: tuple[float, float], pull: float):
    """
    A sophisticated operator moves every signal toward the authentic range.
    pull=0 leaves it crude, pull=1 makes it indistinguishable from authentic.

    One hidden cause shifting all six signals together is what creates
    correlation between them - correlation with a mechanism, not an invented
    covariance number.
    """
    mean = fake[0] + pull * (auth[0] - fake[0])
    k = fake[1] + pull * (auth[1] - fake[1])
    return mean, k


def generate_cases(
    n: int,
    params: Params = TRUE_PARAMS,
    seed: int = 0,
    p_A_false: float | None = None,
) -> pd.DataFrame:
    """
    Generate n influencer cases.

    p_A_false overrides the prior for the sensitivity sweep - the base rate of
    inauthentic audiences is the number nobody can measure, so the experiment
    reports results across a range rather than fixing it.
    """
    rng = np.random.default_rng(seed)
    pa = params.p_A_false if p_A_false is None else p_A_false

    rows = []
    for i in range(n):
        # ---- step 1: sealed true label ----
        A = rng.random() >= pa               # True = authentic
        M = rng.random() >= params.p_M_false  # True = matched
        S = rng.random() >= params.p_S_false  # True = safe

        # is this one actively evading detection? only meaningful if inauthentic
        sophisticated = (not A) and (rng.random() < params.p_sophisticated)
        pull = params.soph_pull if sophisticated else 0.0

        # ---- step 2: observable signals ----
        if A:
            e1 = _beta(rng, params.e1_auth)
        else:
            # bimodal: bought followers push the rate down, bought engagement up
            if rng.random() < params.e1_fake_low_weight:
                e1 = _beta(rng, _blend(params.e1_fake_low, params.e1_auth, pull))
            else:
                e1 = _beta(rng, _blend(params.e1_fake_high, params.e1_auth, pull))

        e2 = _beta(rng, params.e2_auth if A
                   else _blend(params.e2_fake, params.e2_auth, pull))
        lam = params.e3_auth_lambda if A else (
            params.e3_fake_lambda + pull * (params.e3_auth_lambda - params.e3_fake_lambda)
        )
        e3 = int(rng.poisson(lam))
        e4 = _beta(rng, params.e4_match if M else params.e4_mismatch)
        e5 = _beta(rng, params.e5_match if M else params.e5_mismatch)
        e6 = _beta(rng, params.e6_safe if S else params.e6_risk)

        rows.append(
            {
                "case_id": f"INF-{i:03d}",
                # observable
                "e1_engagement_rate": e1,
                "e2_generic_comment_share": e2,
                "e3_growth_spikes": e3,
                "e4_target_market_share": e4,
                "e5_premium_collab_share": e5,
                "e6_disclosure_share": e6,
                # SEALED - not visible to the agent
                "true_A_authentic": A,
                "true_M_matched": M,
                "true_S_safe": S,
                "true_sophisticated": sophisticated,
            }
        )

    return pd.DataFrame(rows)


OBSERVABLE = [
    "e1_engagement_rate",
    "e2_generic_comment_share",
    "e3_growth_spikes",
    "e4_target_market_share",
    "e5_premium_collab_share",
    "e6_disclosure_share",
]

SEALED = ["true_A_authentic", "true_M_matched", "true_S_safe", "true_sophisticated"]


def observable_only(df: pd.DataFrame) -> pd.DataFrame:
    """What the agent is allowed to see."""
    return df[["case_id"] + OBSERVABLE]


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    df = generate_cases(n, seed=seed)
    print(df.head(10).to_string(index=False))
    print()
    print(f"n = {len(df)}")
    print(f"inauthentic : {(~df.true_A_authentic).sum():3d}")
    print(f"mismatched  : {(~df.true_M_matched).sum():3d}")
    print(f"safety risk : {(~df.true_S_safe).sum():3d}")
    print(f"clean (all three fine): {(df.true_A_authentic & df.true_M_matched & df.true_S_safe).sum():3d}")
