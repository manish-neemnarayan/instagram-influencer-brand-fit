"""
Decision policies.

Three are compared, as required by the brief (at least two agent policies plus
at least one baseline):

    policy_threshold            fixed rules on event probabilities, cost-blind
    policy_expected_cost        minimise expected cost, with an uncertainty gate
    policy_engagement_baseline  sign if engagement rate clears a cut-off

Actions: SIGN, GIFT, ANALYTICS, ESCALATE, DECLINE.

Thresholds must be chosen on the TUNING set, never on the test set - otherwise
the reported numbers are tuned to the very cases they are measured on.
"""

from __future__ import annotations

from model import COSTS

SIGN = "SIGN"
GIFT = "GIFT"
ANALYTICS = "ANALYTICS"
ESCALATE = "ESCALATE"
DECLINE = "DECLINE"

ACTIONS = [SIGN, GIFT, ANALYTICS, ESCALATE, DECLINE]


# --------------------------------------------------------------------------
# expected cost of each action under the current belief
# --------------------------------------------------------------------------
def expected_costs(b, costs=COSTS) -> dict[str, float]:
    """
    b is a row of beliefs with p_authentic, p_matched, p_safe.

    Signing cost depends on which latent is false, worst case dominating:
    a safety failure swamps a wasted fee, and a wasted fee swamps a mismatch.
    """
    pA, pM, pS = b.p_authentic, b.p_matched, b.p_safe

    p_unsafe = 1 - pS
    p_fake_and_safe = (1 - pA) * pS
    p_mismatch_only = pA * (1 - pM) * pS
    p_clean = pA * pM * pS

    sign = (
        p_clean * costs["sign_clean"]
        + p_unsafe * costs["sign_unsafe"]
        + p_fake_and_safe * costs["sign_fake"]
        + p_mismatch_only * costs["sign_mismatch"]
    )
    decline = p_clean * costs["decline_good"] + (1 - p_clean) * costs["decline_other"]

    return {
        SIGN: sign,
        GIFT: costs["gift"],
        ANALYTICS: costs["analytics"],
        ESCALATE: costs["escalate"],
        DECLINE: decline,
    }


# --------------------------------------------------------------------------
# the three policies
# --------------------------------------------------------------------------
def policy_threshold(b, t_risk=0.15, t_fake=0.40, t_clean=0.70) -> str:
    """Cost-blind rules on event probabilities. Interpretable, ignores stakes."""
    if b.p_safety_risk > t_risk:
        return ESCALATE
    if (1 - b.p_authentic) > t_fake:
        return ANALYTICS
    if b.p_clean > t_clean:
        return SIGN
    return DECLINE


def policy_expected_cost(b, tau=0.50, costs=COSTS) -> str:
    """
    Minimise expected cost. The uncertainty gate fires first: if no single atom
    holds more than tau of the belief, escalate rather than act.

    NOTE - two r/AI_Agents practitioners argued this gate should not sit outside
    the policy at all, and that escalation should compete on expected utility
    like any other action. Kept here as v0; the rebuilt version is v1.
    """
    if b.max_atom < tau:
        return ESCALATE
    ec = expected_costs(b, costs)
    return min(ec, key=ec.get)


# --------------------------------------------------------------------------
# v1 - value of information with optimal stopping
#
# Two r/AI_Agents practitioners independently argued that v0 was wrong in the
# same way: escalation was a GATE sitting outside the policy ("an emergency
# brake instead of another option on the menu"), and probes were chosen by
# their price rather than by what they would reveal. With flat probe costs the
# cheaper probe always wins, so the gift probe was never selected once in 40
# cases - half the action set was dead.
#
# The fix, as named by them: compare, for each probe, the expected cost of the
# best action AFTER seeing its possible outcomes against the best action now,
# minus the probe's cost. Escalation becomes an action with its own cost and
# its own error rate. Then nothing "fires first" and there is no ordering to
# justify.
# --------------------------------------------------------------------------

# Reliability of each probe: probability the outcome points the right way.
# Both are estimates, not measured.
ANALYTICS_RELIABILITY = 0.85   # resolves A (audience authenticity)
GIFT_RELIABILITY = 0.75        # resolves M (does the audience actually buy)
HUMAN_RELIABILITY = 0.90       # probability the escalated human gets it right


def _terminal_cost(pA, pM, pS, costs) -> float:
    """Best achievable expected cost using only SIGN or DECLINE."""
    p_clean = pA * pM * pS
    sign = (
        p_clean * costs["sign_clean"]
        + (1 - pS) * costs["sign_unsafe"]
        + (1 - pA) * pS * costs["sign_fake"]
        + pA * (1 - pM) * pS * costs["sign_mismatch"]
    )
    decline = p_clean * costs["decline_good"] + (1 - p_clean) * costs["decline_other"]
    return min(sign, decline)


def _after_probe(p: float, reliability: float) -> tuple[float, float, float]:
    """
    A probe of the given reliability returns 'looks good' or 'looks bad'.
    Returns (P(good outcome), posterior if good, posterior if bad).
    """
    p_good = p * reliability + (1 - p) * (1 - reliability)
    post_good = p * reliability / p_good if p_good > 0 else p
    p_bad = 1 - p_good
    post_bad = p * (1 - reliability) / p_bad if p_bad > 0 else p
    return p_good, post_good, post_bad


def policy_voi(b, costs=COSTS) -> str:
    """
    Every action - including escalation and both probes - is scored on expected
    cost and the cheapest wins. No gate, no ordering.
    """
    pA, pM, pS = b.p_authentic, b.p_matched, b.p_safe

    now = _terminal_cost(pA, pM, pS, costs)

    # --- analytics: resolves A ---
    pg, good, bad = _after_probe(pA, ANALYTICS_RELIABILITY)
    ec_analytics = costs["analytics"] + (
        pg * _terminal_cost(good, pM, pS, costs)
        + (1 - pg) * _terminal_cost(bad, pM, pS, costs)
    )

    # --- gift: resolves M, and is the only adversarially robust signal here,
    #     because faking it means actually buying the product at premium prices
    pg, good, bad = _after_probe(pM, GIFT_RELIABILITY)
    ec_gift = costs["gift"] + (
        pg * _terminal_cost(pA, good, pS, costs)
        + (1 - pg) * _terminal_cost(pA, bad, pS, costs)
    )

    # --- escalate: an action with its own cost and its own error rate ---
    # with probability HUMAN_RELIABILITY the human sees the truth and takes the
    # cost-minimal action for it; otherwise they do no better than the agent.
    perfect = 0.0
    for a, pa in ((True, pA), (False, 1 - pA)):
        for m, pm in ((True, pM), (False, 1 - pM)):
            for s, ps in ((True, pS), (False, 1 - pS)):
                if s and a and m:
                    best = costs["sign_clean"]
                elif not s:
                    best = min(costs["sign_unsafe"], costs["decline_other"])
                elif not a:
                    best = min(costs["sign_fake"], costs["decline_other"])
                else:
                    best = min(costs["sign_mismatch"], costs["decline_other"])
                perfect += pa * pm * ps * best
    ec_escalate = costs["escalate"] + (
        HUMAN_RELIABILITY * perfect + (1 - HUMAN_RELIABILITY) * now
    )

    # --- terminal actions ---
    p_clean = pA * pM * pS
    ec_sign = (
        p_clean * costs["sign_clean"]
        + (1 - pS) * costs["sign_unsafe"]
        + (1 - pA) * pS * costs["sign_fake"]
        + pA * (1 - pM) * pS * costs["sign_mismatch"]
    )
    ec_decline = p_clean * costs["decline_good"] + (1 - p_clean) * costs["decline_other"]

    options = {
        SIGN: ec_sign,
        DECLINE: ec_decline,
        ANALYTICS: ec_analytics,
        GIFT: ec_gift,
        ESCALATE: ec_escalate,
    }
    return min(options, key=options.get)


def policy_engagement_baseline(row, cutoff=0.02) -> str:
    """
    What a brand does with none of this machinery: look at engagement rate,
    sign if it looks healthy.

    Has no way to distinguish a strong real account from one buying engagement,
    so it signs pod users enthusiastically.
    """
    return SIGN if row.e1_engagement_rate >= cutoff else DECLINE


# --------------------------------------------------------------------------
# realised cost, scored against the sealed labels
# --------------------------------------------------------------------------
def realised_cost(action: str, truth, costs=COSTS) -> float:
    """Only the scorer may read the sealed labels."""
    A, M, S = truth.true_A_authentic, truth.true_M_matched, truth.true_S_safe
    clean = A and M and S

    if action == SIGN:
        if not S:
            return costs["sign_unsafe"]
        if not A:
            return costs["sign_fake"]
        if not M:
            return costs["sign_mismatch"]
        return costs["sign_clean"]
    if action == DECLINE:
        return costs["decline_good"] if clean else costs["decline_other"]
    if action == GIFT:
        return costs["gift"]
    if action == ANALYTICS:
        return costs["analytics"]
    if action == ESCALATE:
        return costs["escalate"]
    raise ValueError(action)
