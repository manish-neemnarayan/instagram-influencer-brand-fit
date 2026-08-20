# Probability Decision Record

**Case ID:** MANUAL-2026-08-19-01
**Decided:** 19 August 2026, 07:52 IST
**Agent:** v0, cost-aware policy (`policy_expected_cost`), misspecified arm
**Brand context:** premium / mid-luxury fashion house

---

## Why the true state is genuinely unknown

This case was **constructed at decision time** through the manual scorer on the live
demo. No label exists for her, not even a sealed one. She is not drawn from
`test_cases.csv` and no process ever generated a truth for her.

The honest consequence, stated up front: **because there is no label, the correctness of
this decision can never be checked.** This record documents the reasoning, not the
outcome. That is what Section 10 asks for, and it also matches deployment, where a brand
rarely learns the truth about the creators it declined.

---

## 1. Evidence

Six observable signals, all the agent can see.

| Signal | Observed | Answers | Reading |
|--------|----------|---------|---------|
| E1 engagement rate | **2.80%** | A | Squarely inside the fashion benchmark of 2.2–3.8% |
| E2 generic / emoji-only comments | **30%** | A | Ordinary. Real audiences post emoji too |
| E3 follower-growth spikes in 24 months | **3** | A | Elevated. Expected is under 1 for an organic account |
| E4 audience in target market | **28%** | M | Low for a premium Indian fashion brand |
| E5 past collaborations at premium tier | **61%** | M | Good. She has worked at this price point |
| E6 paid posts properly disclosed | **88%** | S | Clean disclosure history |

The three growth spikes are the only real flag before any inference happens. They are also
ambiguous by construction: a genuine viral month produces the same shape as bought
followers.

---

## 2. Hidden states

Three binary questions, none observable at decision time. Their 2 × 2 × 2 combinations
give **eight atoms**, mutually exclusive and collectively exhaustive by construction.

| Latent | Question |
|--------|----------|
| **A** | Is the audience authentic? |
| **M** | Does the audience match a premium fashion brand? |
| **S** | Is she free of latent brand-safety risk? |

---

## 3. Beliefs

Posteriors on each question after the six signals:

| Question | P(yes) | P(no) |
|----------|--------|-------|
| A, audience authentic | 96.54% | 3.46% |
| M, matches the brand | 75.58% | 24.42% |
| S, no buried risk | 99.87% | 0.13% |

The full belief is the eight atoms, which **must total 100%**:

| # | A | M | S | Plain reading | Belief |
|---|---|---|---|---------------|--------|
| 1 | ✓ | ✓ | ✓ | Clean fit | **72.870%** |
| 2 | ✓ | ✓ | ✗ | Good audience, buried risk | 0.095% |
| 3 | ✓ | ✗ | ✓ | Real audience, wrong for us | 23.544% |
| 4 | ✓ | ✗ | ✗ | Wrong for us and risky | 0.031% |
| 5 | ✗ | ✓ | ✓ | Padded audience, otherwise aligned | 2.612% |
| 6 | ✗ | ✓ | ✗ | Padded and risky | 0.003% |
| 7 | ✗ | ✗ | ✓ | Padded and wrong for us | 0.844% |
| 8 | ✗ | ✗ | ✗ | Everything wrong | 0.001% |
| | | | | **Total** | **100.000%** |

Two atoms carry almost all the belief. She is very probably either a clean fit (72.9%) or
a real person who is simply wrong for this brand (23.5%). Everything else is rounding.

---

## 4. Events

Groups of atoms the brand actually cares about. Because atoms are mutually exclusive,
these are plain sums with no double-counting.

| Event | Atoms | Probability |
|-------|-------|-------------|
| **Clean fit** | 1 | **72.87%** |
| **Audience not usable** | 3,4,5,6,7,8 | **27.03%** |
| **Safety risk** | 2,4,6,8 | **0.13%** |

Note that "audience not usable" is computed as 1 − P(A)·P(M) = 1 − 0.9654 × 0.7558, not
as P(not A) + P(not M). Adding would double-count anyone who is both, and would inflate
the case for rejecting her.

Events deliberately do **not** sum to 100%. They overlap: atom 4 belongs to both "audience
not usable" and "safety risk". The atoms underneath are the partition; events are views
onto it.

---

## 5. Actions

| Action | Reversible? | What it does |
|--------|-------------|--------------|
| Sign | No | Full paid contract |
| Gift first | Yes | Send product, observe the response before paying |
| Request analytics | Yes | Ask for platform-native audience data |
| Escalate | Yes | Route to a human brand manager |
| Decline | In principle, never in practice | No partnership |

---

## 6. Costs

Relative units. Only ratios change decisions, so currency figures would be false
precision.

| Outcome | Cost |
|---------|------|
| Sign someone clean | **−10** (a gain) |
| Sign a padded audience | +20 |
| Sign a poor brand fit | +15 |
| Sign a safety risk | **+200** |
| Decline someone clean | +10 |
| Gift first | +2 |
| Request analytics | +1 |
| Escalate | +5 |

`sign_unsafe = 200` and `decline_good = 10` are **guesses**, both swept in the sensitivity
analysis. A practitioner on r/advertising has separately argued `sign_fake = 20` is too
low, on the grounds that a visibly fake endorsement damages trust in the brand rather than
merely wasting a fee. That is unresolved and recorded in `discussion-record.md`.

---

## 7. Policy

Cost-aware expected-cost minimisation, with an uncertainty gate in front.

1. If no single atom holds more than **τ = 0.50** of the belief, escalate.
2. Otherwise take the action with the lowest expected cost.

The strongest atom here is **72.87%**, comfortably above τ, so **the gate did not fire**.

Expected cost of each action under this belief:

| Action | Expected cost |
|--------|---------------|
| **Sign** | **−2.81** ← cheapest |
| Request analytics | 1.00 |
| Gift first | 2.00 |
| Escalate | 5.00 |
| Decline | 7.29 |

Note there is **no confidence threshold for signing** in this policy. It never asks
"am I sure enough". The threshold is implied, and it varies by what the risk is: with a
mismatch the agent will sign above 42.9% confidence, with a padded audience above 50.0%,
and with a safety risk not until 90.9%.

---

## 8. Decision

**SIGN.**

Signing earns an expected 2.81 units. Declining costs 7.29, driven almost entirely by the
72.87% chance of turning away someone who would have worked. The gap is roughly 10 units
in favour of signing.

The reasoning in one line: she is very likely real, her disclosure history is clean, and
the only live doubt is whether her audience is the right audience. That doubt costs 15 if
wrong, which is not enough to outweigh the gain from a good signing.

---

## 9. Audit data

| Field | Value |
|-------|-------|
| Decided at | 19 August 2026, 07:52 IST |
| Case origin | Manual scorer, live demo. No ground-truth label exists |
| Data version | Six signals entered by hand, no external data source |
| Model version | v0.2, three binary latents, eight atoms, twelve likelihood models |
| Parameter set | `AGENT_PARAMS` (misspecified arm), `src/model.py` |
| Policy version | `policy_expected_cost`, τ = 0.50, `src/policies.py` |
| Cost weights | `COSTS` in `src/model.py`, `sign_unsafe=200`, `decline_good=10`, `sign_fake=20`, `sign_mismatch=15` |
| Code path | `agent.lik_A/lik_M/lik_S` → `agent._posterior` → `agent.update_beliefs` → `policies.expected_costs` → `policies.policy_expected_cost` |
| Reproduce | `python serve.py`, Try it tab, enter 2.80 / 30 / 3 / 28 / 61 / 88 |

---
---

# The update: one new piece of evidence

## Step 1 · The prior

Before the new evidence, the belief on the match question stood at:

```
P(M yes) = 0.7558      P(M no) = 0.2442
prior odds, yes : no   =  3.095 : 1
```

That posterior is now treated as the prior for the next update. **Today's posterior
becomes tomorrow's prior.**

## Step 2 · The new evidence

The agent requests platform analytics. They arrive and report that the share of her
audience in the brand's target market is **18%**, not the **28%** inferred from public
data.

This is **not a new signal.** E4 already measures audience-in-target-market. What changed
is where the number came from: before it was inferred from public information, now it is
platform-native and more reliable. Same column, better reading.

## Step 3 · The likelihood

How surprising is 18% under each answer to the match question?

| | P(E4 = 0.18 \| M yes) | P(E4 = 0.18 \| M no) | Likelihood ratio |
|---|---|---|---|
| **New reading** | 0.0070 | 0.9208 | **0.0076** |
| *(previous reading, 28%)* | *0.0927* | *2.2037* | *0.0421* |

A likelihood ratio of 0.0076 means this observation is roughly **131 times more likely**
if her audience does *not* match the brand than if it does. That is strong evidence
against a match.

## Step 4 · The posterior

Working in odds, which avoids computing the normaliser:

```
prior odds (M yes : no)          1.857          from P(M no) = 0.35
× likelihood ratio for E4=0.18   0.0076
× likelihood ratio for E5=0.61  39.615          (unchanged, still supports a match)
                                 -------
posterior odds                   0.557

P(M yes) = 0.557 / (1 + 0.557) = 0.3576
```

The match belief falls from **75.58% to 35.76%**. A and S are untouched, because E4 says
nothing about authenticity or safety in this model.

The eight atoms after the update, still totalling 100%:

| # | Plain reading | Before | After |
|---|---------------|--------|-------|
| 1 | Clean fit | 72.870% | **34.478%** |
| 2 | Good audience, buried risk | 0.095% | 0.045% |
| 3 | Real audience, wrong for us | 23.544% | **61.937%** |
| 4 | Wrong for us and risky | 0.031% | 0.081% |
| 5 | Padded audience, otherwise aligned | 2.612% | 1.236% |
| 6 | Padded and risky | 0.003% | 0.002% |
| 7 | Padded and wrong for us | 0.844% | 2.220% |
| 8 | Everything wrong | 0.001% | 0.003% |
| | **Total** | **100.000%** | **100.002%** *(rounding)* |

**The most likely explanation has changed.** Before, the leading atom was "clean fit" at
72.9%. Now it is "real audience, wrong for us" at 61.9%. The agent no longer doubts she is
a real person. It doubts she is *our* person.

## Step 5 · Compare against the decision rule

Strongest atom is now **61.94%**, still above τ = 0.50, so **the gate still does not
fire**. The agent remains confident about *something*; what changed is what it is
confident about.

Expected costs under the new belief:

| Action | Before | After |
|--------|--------|-------|
| Sign | **−2.81** | 6.79 |
| Request analytics | 1.00 | 1.00 |
| Gift first | 2.00 | 2.00 |
| Escalate | 5.00 | 5.00 |
| **Decline** | 7.29 | **3.45** |

## Step 6 · The new action

**DECLINE.**

Signing moved from earning 2.81 to costing 6.79. Declining moved from costing 7.29 to
costing 3.45. One measurement, and the ordering reverses.

### Two things this record exposed about v0

**Analytics shows as nominally cheapest at 1.00.** It is not available: the probe has
already been bought, and you do not purchase the same information twice. Among the actions
still open, Decline at 3.45 beats Sign at 6.79. That the policy does not itself know the
probe is spent is the flat-probe-cost flaw, visible inside a real decision rather than as
an abstract limitation.

**P(M) moving from 0.76 to 0.36 on a single signal is a very large jump.** Only E4 changed,
and E5 still argues strongly for a match with a likelihood ratio of 39.6. The model treats
the two match signals as independent, so their evidence multiplies rather than partly
repeating each other. A model that allowed correlation between them would move less. This
is the naive-Bayes sharpness recorded in the limitations, visible in one case.

### Audit data for the update

| Field | Value |
|-------|-------|
| Updated at | 19 August 2026, 07:58 IST |
| Trigger | Analytics probe returned |
| Evidence changed | E4 only: 0.28 → 0.18 |
| Evidence unchanged | E1, E2, E3, E5, E6 |
| Beliefs changed | M only. A and S untouched by construction |
| Model, parameters, policy, costs | Unchanged from the original decision |
| Reproduce | Same as above, then move audience-in-target-market to 18 |
