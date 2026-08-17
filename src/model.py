"""
Model parameters for the influencer-brand fit agent.

Three binary latents:
    A  audience authentic?      (True = authentic)
    M  audience matched?        (True = matched to a premium fashion brand)
    S  free of safety risk?     (True = no latent brand-safety problem)

Six observable signals, each informative about exactly one latent:
    E1 engagement rate                  -> A
    E2 share of generic/emoji comments  -> A
    E3 follower-growth spikes in 24m    -> A
    E4 share of audience in target mkt  -> M
    E5 share of past collabs at premium -> M
    E6 share of paid posts disclosed    -> S

PROVENANCE OF NUMBERS
    E1 is anchored on published benchmarks: fashion/beauty Instagram engagement
    runs 2.2-3.8%, >1% acceptable, >3% strong, and falls as follower count rises.
    E2-E6 are reasoned estimates, NOT measured. They are treated as assumptions
    and their influence is tested by running the agent with deliberately
    misspecified parameters (see AGENT_PARAMS).
"""

from dataclasses import dataclass


# --------------------------------------------------------------------------
# Beta helper: it is far easier to reason about "mean 2.8%, fairly tight"
# than about alpha=9.4, beta=326. concentration k controls the spread:
# larger k = narrower.
# --------------------------------------------------------------------------
def beta_ab(mean: float, k: float) -> tuple[float, float]:
    return mean * k, (1.0 - mean) * k


@dataclass(frozen=True)
class Params:
    """Everything needed to simulate a case or to score one."""

    # ---- priors: marginal probability that each latent is FALSE ----
    p_A_false: float      # audience not authentic
    p_M_false: float      # audience not matched
    p_S_false: float      # latent safety risk

    # ---- adversarial sophistication ----
    # Inauthenticity is not a natural phenomenon, it is adversarial: someone
    # buying followers is actively trying not to be caught. Crude operators buy
    # in bulk and leave obvious traces. Sophisticated ones drip-feed followers
    # and buy realistic comments, so ALL their signals shift toward authentic
    # together. That shared cause is what induces correlation between signals -
    # correlation with a mechanism behind it, rather than an invented number.
    p_sophisticated: float              # P(sophisticated | inauthentic)
    soph_pull: float                    # 0 = indistinguishable from crude,
                                        # 1 = indistinguishable from authentic

    # ---- E1 engagement rate ----
    e1_auth: tuple[float, float]        # (mean, k) when A is True
    # when A is False the rate is BIMODAL:
    #   bought followers  -> denominator inflated -> rate collapses
    #   bought engagement -> numerator inflated   -> rate suspiciously high
    e1_fake_low: tuple[float, float]
    e1_fake_high: tuple[float, float]
    e1_fake_low_weight: float           # share of inauthentic accounts in the low mode

    # ---- E2 share of generic / emoji-only comments ----
    e2_auth: tuple[float, float]
    e2_fake: tuple[float, float]

    # ---- E3 growth spikes in the last 24 months (Poisson rate) ----
    e3_auth_lambda: float
    e3_fake_lambda: float

    # ---- E4 share of audience inside the brand's target market ----
    e4_match: tuple[float, float]
    e4_mismatch: tuple[float, float]

    # ---- E5 share of past collaborations at premium tier ----
    e5_match: tuple[float, float]
    e5_mismatch: tuple[float, float]

    # ---- E6 share of paid posts correctly disclosed ----
    e6_safe: tuple[float, float]
    e6_risk: tuple[float, float]


# --------------------------------------------------------------------------
# TRUE parameters - used by the simulator to generate cases.
# --------------------------------------------------------------------------
TRUE_PARAMS = Params(
    p_A_false=0.25,          # swept 0.10-0.40 in the sensitivity analysis
    p_M_false=0.40,          # mismatch assumed common at premium tier (unverified)
    p_S_false=0.05,          # rare but expensive (unverified)

    p_sophisticated=0.40,    # 40% of inauthentic accounts actively evade detection
    soph_pull=0.80,          # and they get 80% of the way to looking authentic

    e1_auth=(0.028, 335),           # ~2.8%, sd ~0.9pp  -> matches fashion benchmark
    e1_fake_low=(0.010, 618),       # ~1.0%, bots dilute the rate
    e1_fake_high=(0.070, 288),      # ~7.0%, pods inflate it
    e1_fake_low_weight=0.70,        # most inauthentic accounts are the low kind

    e2_auth=(0.30, 20),      # real audiences post plenty of emoji too
    e2_fake=(0.75, 20),

    e3_auth_lambda=0.3,      # a genuine viral month happens sometimes - innocent
    e3_fake_lambda=2.5,

    e4_match=(0.70, 20),
    e4_mismatch=(0.35, 20),

    e5_match=(0.60, 15),
    e5_mismatch=(0.15, 15),

    e6_safe=(0.85, 15),
    e6_risk=(0.40, 15),
)


# --------------------------------------------------------------------------
# AGENT parameters - deliberately misspecified.
#
# Nobody deploying this would know the true generating parameters. Running the
# agent on TRUE_PARAMS answers "how good is Bayes when you already know
# everything", which is not the question. Running it on these answers "how good
# is it when the assumptions are a bit wrong", and the gap between the two is
# what gets reported.
#
# Every mean is shifted toward the middle (less separation than reality) and
# every k is loosened (the agent thinks the world is noisier than it is). Both
# are the realistic direction of error for a human guessing.
# --------------------------------------------------------------------------
AGENT_PARAMS = Params(
    p_A_false=0.30,          # agent over-estimates the base rate, as vendor stats encourage
    p_M_false=0.35,
    p_S_false=0.08,

    p_sophisticated=0.25,    # agent UNDER-estimates how many fakes evade detection
    soph_pull=0.65,          # and under-estimates how well they do it

    e1_auth=(0.026, 200),
    e1_fake_low=(0.015, 300),       # agent thinks fake accounts sit higher than they do
    e1_fake_high=(0.062, 180),
    e1_fake_low_weight=0.60,

    e2_auth=(0.35, 12),
    e2_fake=(0.68, 12),

    e3_auth_lambda=0.5,
    e3_fake_lambda=2.0,

    e4_match=(0.65, 12),
    e4_mismatch=(0.40, 12),

    e5_match=(0.55, 10),
    e5_mismatch=(0.20, 10),

    e6_safe=(0.80, 10),
    e6_risk=(0.48, 10),
)


# --------------------------------------------------------------------------
# Costs. Relative units - only ratios change decisions, so inventing rupee
# figures would be false precision.
#
# The two contested numbers are flagged; both are swept in the sensitivity
# analysis.
# --------------------------------------------------------------------------
COSTS = {
    "sign_clean": -10.0,      # gain
    "sign_unsafe": 200.0,     # CONTESTED: assumes 1 safety failure ~ 10 wasted fees
    "sign_fake": 20.0,
    "sign_mismatch": 15.0,
    "gift": 2.0,
    "analytics": 1.0,
    "escalate": 5.0,
    "decline_good": 10.0,     # CONTESTED: invisible in practice, so intuition sets it low
    "decline_other": 0.0,
}
