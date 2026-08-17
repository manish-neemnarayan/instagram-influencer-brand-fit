# Findings, v0

Running log of results. Every number here has a file behind it in `results/`.
This is the backbone of the preprint; nothing goes in the paper that is not here
first.

**Status: v0 frozen.** All changes arising from public discussion are collected for a
single v1 rebuild in M7 rather than patched in piecemeal.

---

## 1. Headline, the agent beats the baseline by a wide margin

Designated test set, 40 cases, agent using misspecified (realistic) parameters:

| policy | total cost | signed | signed unsafe | signed fake | declined clean | escalated |
|---|---|---|---|---|---|---|
| v0_threshold | −119 | 17 | 0 | 1 | 0 | 7.5% |
| v0_expected_cost | **−137** | 17 | 0 | 1 | 0 | 0% |
| engagement_baseline | **+375** | 28 | 1 | 7 | 4 | 0% |

Negative cost is net gain. The baseline's damage is dominated by a **single decision**, one safety-risk signing at cost 200, more than half its total. Twenty-eight signings,
and one of them wiped out what the other twenty-seven earned.

Pooled over 40 replications (1,600 cases):

| policy | precision | recall | FP | FN | FP that were safety risks | FP that were sophisticated fakes | review rate |
|---|---|---|---|---|---|---|---|
| v0_threshold | 0.886 | 0.964 | 85 | 25 | **5** | 79 | 6.0% |
| v0_expected_cost | 0.894 | 0.924 | 75 | 52 | **0** | 73 | 0.3% |
| engagement_baseline | 0.466 | 0.778 | 610 | 152 | **56** | 111 | 0% |

The two agent policies have near-identical precision, but differ in what they get wrong.
The cost-blind threshold policy has better recall (0.964 vs 0.924) and signs five safety
risks. The cost-aware policy is more conservative, misses more good creators, and signs
**zero** safety risks. That is the cost matrix doing its job: it trades recall for
avoidance of the one error that cannot be undone.

---

## 2. One failure mode accounts for almost everything

Of the cost-aware policy's 75 false positives, **73 were sophisticated fakes**. The
named failure conditions, pooled:

| failure | n |
|---|---|
| `signed_sophisticated_fake` | 58 |
| `signed_mismatch` | 2 |
| `signed_crude_fake` | 0 |
| `signed_safety_risk` | 0 |
| `declined_clean` | 0 |

Crude fakes are caught every time. Sophisticated ones are caught almost never.

**And the agent is not uncertain while making these mistakes.** When it signs a
sophisticated fake, its mean belief that the audience is authentic is **0.967**; the
lowest across all 58 failures is 0.673. It is not confused. It is reading exactly the
evidence it was shown, and the evidence was constructed to mislead it.

---

## 3. The uncertainty gate does not work, and now there are two reasons

The gate escalates when no single atom holds more than τ of the belief. It fires on
**0.3% of cases** and catches none of the failures above.

- **Empirical reason:** errors do not arrive with uncertainty attached. Adversarial
  evidence is *clean* evidence pointing the wrong way.
- **Structural reason (akl773, r/AI_Agents):** spread of belief is the wrong quantity.
  What matters is whether the live candidates imply *different actions with different
  costs of being wrong*. Two hypotheses splitting the mass evenly cost nothing if both
  lead to "decline"; one hypothesis at 8% costs a great deal if it is the safety risk.

Two independent lines of attack, arrived at separately, agreeing. The v1 replacement is
a decision-relevance measure, the cost gap between best and second-best action.

---

## 4. Sensitivity: none of the three guessed numbers change the conclusion

Method suggested by efrique (PhD statistics, r/AskStatistics): the bias cannot be known
without information not available, but sensitivity to a range of circumstances can be
explored by simulation.

**Base rate of inauthentic audiences**, swept across the entire range the literature
supports:

| p_A_false | 0.10 | 0.20 | 0.25 | 0.30 | 0.40 |
|---|---|---|---|---|---|
| v0_expected_cost | −171 | −124 | −103 | −87 | −45 |
| baseline | +426 | +413 | +447 | +441 | +429 |

The agent degrades as fakes get more common but remains profitable throughout, and the
policy ordering never flips. **The number nobody can measure turns out not to matter.**

**Cost of signing a safety risk**, the invented 200:

| sign_unsafe | 50 | 100 | 200 | 350 | 500 |
|---|---|---|---|---|---|
| v0_expected_cost | −105 | −106 | −103 | −97 | −95 |
| baseline | +237 | +307 | +447 | +657 | +867 |

The agent barely moves, because it never signs an unsafe influencer at any setting. The
baseline's cost nearly quadruples, because it keeps doing it. The guessed value is not
load-bearing for the agent, and the comparison only improves as it rises.

**Cost of declining a good creator**, swept 5 to 40, covering the practitioner claim
that this error exceeds the cost of signing a fake. Agent cost is flat at about −101
throughout, because with recall of 0.92–0.96 it rarely makes that error at all. The
baseline *is* exposed: its cost rises from 471 to 519 across the same range.

So the practitioners are right in general and right about the baseline, and the weight
still is not load-bearing for this agent.

---

## 5. Calibration: miscalibrated where it matters, and better parameters do not fix it

Pooled over 1,600 cases. Bins on P(clean):

| bin | n | predicted | observed | gap |
|---|---|---|---|---|
| 0.0–0.2 | 790 | 0.014 | 0.003 | +0.011 |
| 0.2–0.4 | 24 | 0.280 | 0.042 | **+0.238** |
| 0.4–0.6 | 15 | 0.500 | 0.200 | **+0.300** |
| 0.6–0.8 | 42 | 0.724 | 0.762 | −0.038 |
| 0.8–1.0 | **729** | 0.972 | 0.888 | **+0.084** |

Expected calibration error **0.051**.

Two things stand out.

**The distribution is U-shaped.** 1,519 of 1,600 cases sit in the two extreme bins.
Only 81 land anywhere in the middle. This is the "confidently right or confidently
wrong" pattern, quantified.

**The top bin is where the damage is.** The agent says 97% and is right 89% of the time,
across 729 cases, and that bin is where it signs. An 8-point overconfidence gap applied
to the bin containing every signing decision is precisely where the sophisticated fakes
hide.

**The oracle arm is no better calibrated (ECE 0.053 vs 0.051).** Handing the agent the
true generating parameters does not improve calibration at all. The miscalibration is
not caused by bad parameter estimates, it is caused by the adversary. This is a result
worth stating plainly: *better priors would not fix this agent.*

---

## 6. The oracle gap is small, the guessed likelihoods are not doing the work

Misspecified −137 against oracle −140 on the test set; −2.92 against −2.79 mean cost
pooled. Deliberately wrong parameters cost the agent almost nothing.

This is the empirical answer to "where did these likelihoods come from?" They are
estimates, and the result does not depend on them being right.

---

## 7. Open, carried into M7

| # | Change | Source |
|---|---|---|
| 1 | Replace the mass-based uncertainty gate with a decision-relevance measure | akl773, r/AI_Agents + own simulation |
| 2 | Escalation becomes an action scored on expected cost, not a gate | zhonglin, Express_Meat_3948, TeagueXiao, r/AI_Agents |
| 3 | Stop probing when expected value of information goes negative, rather than at a fixed cap of 2 | TeagueXiao (SPRT / Wald), r/AI_Agents |
| 4 | Gift probe re-pointed: it tests operations, not audience | th3_sinner, r/CreatorEconomy |
| 5 | Add median organic views and saves/shares as signals, harder to fake than likes | th3_sinner, r/CreatorEconomy |
| 6 | Human reliability split by latent: strong on match and safety, weak on authenticity | own design doc contradicting own code |
| 7 | Downgrade reliability of self-reported analytics, screenshots are cheap to fake | AnabolicAcolyte, r/InstagramMarketing |

---

## Caveats to state, not bury

- Recall of 0.92–0.96 is high partly because the simulator and the agent share a model
  family. Real data would be messier and the invisible-rejection cost would likely
  matter more than it does here.
- The middle calibration bins hold only 15–24 cases each; their gaps are suggestive,
  not reliable.
- All cases are simulated. No real influencer data is used.
- Brufacee (r/advertising) argues the returns to better *selection* are small, roughly
  1 winner per 10–12 collaborations, unpredictable in advance, and that the real lever
  is bet sizing. That challenges the premise rather than the model, and is answered by
  restricting the claim to price points where shrinking the bet is not available.
