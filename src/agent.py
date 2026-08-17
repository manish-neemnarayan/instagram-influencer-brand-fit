"""
Belief update for the influencer-brand fit agent (v0).

Each signal is informative about exactly one latent, so the three latents can be
updated independently and the eight atoms fall out as products. That is why the
factorised model needs 12 likelihoods rather than 24: E1 only ever needs
P(E1 | authentic) and P(E1 | not authentic).

Atoms are mutually exclusive and collectively exhaustive by construction, so
event probabilities are plain sums with no double-counting.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from model import Params, AGENT_PARAMS, beta_ab


# --------------------------------------------------------------------------
# likelihoods: P(signal | latent value)
# --------------------------------------------------------------------------
def _beta_pdf(x: float, spec: tuple[float, float]) -> float:
    a, b = beta_ab(*spec)
    return float(stats.beta.pdf(np.clip(x, 1e-6, 1 - 1e-6), a, b))


def lik_A(row, p: Params) -> tuple[float, float]:
    """Returns (P(evidence | authentic), P(evidence | not authentic))."""
    e1, e2, e3 = row.e1_engagement_rate, row.e2_generic_comment_share, row.e3_growth_spikes

    # E1 is bimodal when the audience is inauthentic
    e1_yes = _beta_pdf(e1, p.e1_auth)
    e1_no = (
        p.e1_fake_low_weight * _beta_pdf(e1, p.e1_fake_low)
        + (1 - p.e1_fake_low_weight) * _beta_pdf(e1, p.e1_fake_high)
    )

    e2_yes, e2_no = _beta_pdf(e2, p.e2_auth), _beta_pdf(e2, p.e2_fake)
    e3_yes = float(stats.poisson.pmf(e3, p.e3_auth_lambda))
    e3_no = float(stats.poisson.pmf(e3, p.e3_fake_lambda))

    return e1_yes * e2_yes * e3_yes, e1_no * e2_no * e3_no


def lik_M(row, p: Params) -> tuple[float, float]:
    e4, e5 = row.e4_target_market_share, row.e5_premium_collab_share
    yes = _beta_pdf(e4, p.e4_match) * _beta_pdf(e5, p.e5_match)
    no = _beta_pdf(e4, p.e4_mismatch) * _beta_pdf(e5, p.e5_mismatch)
    return yes, no


def lik_S(row, p: Params) -> tuple[float, float]:
    e6 = row.e6_disclosure_share
    return _beta_pdf(e6, p.e6_safe), _beta_pdf(e6, p.e6_risk)


def _posterior(prior_false: float, lik_true: float, lik_false: float) -> float:
    """P(latent is True | evidence)."""
    num_t = (1 - prior_false) * lik_true
    num_f = prior_false * lik_false
    total = num_t + num_f
    return 0.5 if total <= 0 else num_t / total


# --------------------------------------------------------------------------
# beliefs
# --------------------------------------------------------------------------
def update_beliefs(df: pd.DataFrame, p: Params = AGENT_PARAMS) -> pd.DataFrame:
    """
    Takes observable columns only. Returns posteriors for each latent, the eight
    atom probabilities, and the three events the policy acts on.
    """
    out = []
    for row in df.itertuples():
        pA = _posterior(p.p_A_false, *lik_A(row, p))
        pM = _posterior(p.p_M_false, *lik_M(row, p))
        pS = _posterior(p.p_S_false, *lik_S(row, p))

        # eight atoms, mutually exclusive and exhaustive by construction
        atoms = {}
        for a in (True, False):
            for m in (True, False):
                for s in (True, False):
                    atoms[(a, m, s)] = (
                        (pA if a else 1 - pA)
                        * (pM if m else 1 - pM)
                        * (pS if s else 1 - pS)
                    )

        # events: plain sums, safe because atoms cannot overlap
        p_clean = atoms[(True, True, True)]
        p_unusable = 1.0 - pA * pM        # NOT (1-pA)+(1-pM) - that double-counts
        p_risk = 1.0 - pS

        out.append(
            {
                "case_id": row.case_id,
                "p_authentic": pA,
                "p_matched": pM,
                "p_safe": pS,
                "p_clean": p_clean,
                "p_audience_unusable": p_unusable,
                "p_safety_risk": p_risk,
                "max_atom": max(atoms.values()),
            }
        )

    return pd.DataFrame(out)


if __name__ == "__main__":
    from simulate import generate_cases, observable_only
    from model import TRUE_PARAMS

    cases = generate_cases(40, seed=0)
    beliefs = update_beliefs(observable_only(cases))

    check = beliefs.merge(cases[["case_id", "true_A_authentic", "true_M_matched", "true_S_safe"]],
                         on="case_id")
    pd.set_option("display.width", 200)
    print(check.head(12).round(3).to_string(index=False))
    print()
    print("mean P(authentic) when truly authentic    :",
          round(check.loc[check.true_A_authentic, "p_authentic"].mean(), 3))
    print("mean P(authentic) when truly inauthentic  :",
          round(check.loc[~check.true_A_authentic, "p_authentic"].mean(), 3))
