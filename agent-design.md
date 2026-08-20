# Agent Design Spec, M2 (v0.2, factorised)

Influencer–brand fit agent for a premium / mid-luxury fashion house.

**Change from v0.1:** four named hidden states replaced by three binary latents (8
atoms). Reason: the original four failed the mutual-exclusivity rule taught in Week 1, *"no two boxes may both be true at once, and no true story may be left without a
box."* H2 (low authenticity) and H3 (mismatch) could both be true of the same
influencer, which is the same failure as *"he is late" + "he has his phone"* in Dry
Run 01. Independently flagged on r/AskStatistics.

---

## Part 1 · Input (what the agent observes)

| ID | Signal | Observed as | Answers |
|----|--------|-------------|---------|
| E1 | Engagement rate | (likes + comments) / followers, last 10 posts | A |
| E2 | Comment quality | Share of comments generic or emoji-only | A |
| E3 | Follower growth shape | Smooth vs sudden step changes | A |
| E4 | Audience geography match | Share of audience in target market | M |
| E5 | Price-point signal | Past collaborations and content at premium or mass tier | M |
| E6 | Disclosure history | Share of paid posts correctly marked as ads | S |

**Each signal answers one question.** That is what makes the factorised model cheaper,
not more expensive, see Part 3.

---

## Part 2 · Hidden state, three binary questions, eight atoms

The agent cannot observe the answer to any of these:

| Latent | Question | Values |
|--------|----------|--------|
| **A** | Is the audience authentic? | yes / no |
| **M** | Does the audience match the brand? | yes / no |
| **S** | Is the influencer free of latent brand-safety risk? | yes / no |

Every influencer sits in exactly one of the 2 × 2 × 2 = **8 atoms**:

| Atom | A | M | S | Plain reading |
|------|---|---|---|---------------|
| 1 | ✓ | ✓ | ✓ | Clean fit |
| 2 | ✓ | ✓ | ✗ | Good audience, buried risk |
| 3 | ✓ | ✗ | ✓ | Real audience, wrong for us |
| 4 | ✓ | ✗ | ✗ | Wrong for us and risky |
| 5 | ✗ | ✓ | ✓ | Padded audience, otherwise aligned |
| 6 | ✗ | ✓ | ✗ | Padded and risky |
| 7 | ✗ | ✗ | ✓ | Padded and wrong for us |
| 8 | ✗ | ✗ | ✗ | Everything wrong |

**Mutually exclusive and collectively exhaustive by construction.** No argument
required, the three questions each have exactly one true answer, so every influencer
falls in exactly one atom, and no true situation lacks a box.

This also closes the exhaustiveness gap in v0.1: an influencer who is real, matched
and safe but simply unpersuasive now sits in atom 1, and her failure is a *conversion*
outcome rather than a hidden state. Noted as out of scope.

---

## Part 3 · Belief

**Priors, three numbers, not eight.** Assuming the three latents are independent, the
atom probabilities are products of three marginals:

| Latent | Prior | Basis |
|--------|-------|-------|
| P(A = no) | **swept 0.10 – 0.40** | Literature gives 15–49% but measures the wrong quantity (see below) |
| P(M = no) | 0.40 | Mismatch assumed common at premium tier. Unverified, open on r/influencermarketing |
| P(S = no) | 0.05 | Rare but expensive. Unverified |

**Independence is a simplification.** Authenticity and match are plausibly correlated, an account that buys followers may buy them cheaply and indiscriminately, degrading
match at the same time. Recorded as a limitation and a candidate for sensitivity
analysis.

**Why P(A = no) is swept.** Vendor reports say ~37% of followers are fake; a
meta-analysis of 47 studies gives 15–49% of accounts affected. Both measure *what
fraction of an audience is inauthentic*. The agent needs *what fraction of the
influencers this brand shortlists are inauthentic*, a different quantity, because a
shortlist is not a random sample of Instagram. No source measures it, so it is swept
rather than fixed.

**Likelihoods, 12 numbers, not 48.** Because each signal answers exactly one
question, E1 needs P(E1 | A = yes) and P(E1 | A = no) and nothing more. Six signals ×
two values = 12 likelihood models. The factorised design has *more states but fewer
numbers to defend* than the four-state version's 24.

**Update.** Bayes on each latent independently, then multiply to get atom
probabilities.

---

## Part 4 · Events (what the policy actually acts on)

Atoms are too fine-grained to act on. Actions key off **events**, groups of atoms
that matter to the brand. Because atoms are mutually exclusive, event probabilities
are plain sums with no double-counting.

| Event | Atoms | Probability |
|-------|-------|-------------|
| **Clean** | 1 | P(A✓) · P(M✓) · P(S✓) |
| **Audience not usable** | 3,4,5,6,7,8 | 1 − P(A✓)·P(M✓) |
| **Safety risk** | 2,4,6,8 | P(S✗) |

This is the *Event* row required by Section 10 of the brief: "hidden states that are
important to the user."

Note that "audience not usable" is **not** P(A✗) + P(M✗), that would double-count
every influencer who is both. It is 1 − P(both fine). Getting this wrong inflates the
rejection rate, and inflates it in the direction of an error nobody ever observes.

---

## Part 5 · Action

| ID | Action | Reversible? | What it does |
|----|--------|-------------|--------------|
| A1 | Sign | No | Full paid contract |
| A2 | Gift first | Yes | Send product, observe response before paying |
| A3 | Request analytics | Yes | Ask for platform audience data |
| A4 | Escalate | Yes | Route to a human brand manager |
| A5 | Decline | Effectively yes | No partnership |

A2 and A3 resolve nothing by themselves, they buy evidence at a cost, and they buy
evidence about **different latents**:

- **A3 (analytics)** → returns platform-native audience composition. In this model that
  principally refines **E4**, which answers **M**, plus growth-curve data which refines
  **E3**, which answers **A**.
- **A2 (gift first)** → resolves **M**. A real but mismatched audience engages with the
  post and still does not buy.

Neither resolves **S**, which is why S-risk drives escalation rather than probing.

### Correction, found while writing the probability decision record

An earlier version of this section claimed A3 *"resolves A: geography, growth curve, real
reach."* That is wrong on its own terms. **Geography is E4, and E4 answers M, not A.** The
document contradicted its own signal table.

The deeper issue is that the sentence was true about the world and false about the model.
In reality audience geography *does* carry authenticity information: bot farms cluster in
particular countries, and an audience whose locations do not match the creator's language
or content is a recognised authenticity flag. In this model it carries none, because the
one-signal-one-question rule forbids E4 from touching A.

That rule is what reduces the model to 12 likelihoods instead of 24. Letting E4 inform
both A and M would be more faithful and would cost more numbers to defend. **The
simplification bought something real and cost something real**, and the cost is that the
agent cannot use geography to detect a padded audience even though a human analyst would.

Recorded as a limitation. Not changed in v0, which is frozen.

---

## Part 6 · Cost

Relative units. Only ratios affect decisions; precise currency figures would be false
precision. Cost of signing depends on which latent is false, worst case dominating:

| Action | Cost |
|--------|------|
| A1 Sign, atom 1 (clean) | −10 (gain) |
| A1 Sign, any atom with S ✗ | **200** |
| A1 Sign, A ✗ (S ✓) | 20 |
| A1 Sign, M ✗ (A ✓, S ✓) | 15 |
| A2 Gift first | 2 |
| A3 Request analytics | 1 |
| A4 Escalate | 5 |
| A5 Decline, atom 1 | **10** |
| A5 Decline, any other atom | 0 |

**Two contested numbers, both currently guesses:**

- **200**, assumes one brand-safety failure costs about ten wasted fees at a luxury
  house. Plausible, unmeasured.
- **10**, the cost of passing on someone who would have worked. Invisible in practice,
  so intuition sets it too low. A practitioner on r/advertising argued this error is
  *worse* than paying a fake, which would push it above 20. Awaiting a ratio.

Both are swept in the sensitivity analysis.

---

## Part 7 · Policy

**P1, threshold policy.** Fixed rules on event probabilities. Escalate if safety risk
is high; request analytics if P(A ✗) is high; sign if Clean is high; else decline.
Interpretable, ignores costs.

**P2, expected-cost minimisation with an uncertainty gate.** Choose the action with
lowest expected cost under the posterior. Before that, apply the uncertainty gate: if
no atom holds more than τ of the belief, escalate rather than act.

**Baseline B, engagement-rate rule.** Sign if engagement rate exceeds a threshold,
else decline. Two actions, no beliefs, no costs. What a brand does with none of this.

**Stopping rule.** Probes cost per use and are capped at two rounds per case.

**Open, flagged by r/AI_Agents.** A practitioner argued the uncertainty gate should
not sit outside the policy at all: escalation should be a fifth action with its own
cost, latency and error rate, scored on expected utility like everything else, at
which point the ordering problem disappears. He named the pattern: *value of
information with optimal stopping*. He also cautioned that any fixed posterior
threshold is unprincipled if the likelihoods are poorly calibrated. **Candidate v0→v1
change, decision pending.**

---

## Part 8 · Human reasoning function, flagging its own uncertainty

A plain Bayesian agent acts on its best guess however weak that guess is. A belief of
30/25/25/20 and one of 90/5/3/2 both have a "most likely" answer, and a naive agent
treats them alike.

This agent measures how concentrated its belief is and, when nothing dominates,
declines to guess and escalates.

Yields a reportable metric: **human-review rate**. Too high and the agent is useless;
too low and it is overconfident. The trade-off against decision cost is a result worth
reporting.

Justification against the r/AI_Agents objection: expected-utility optimality is only
trustworthy if the numbers are right. These likelihoods are estimates and the prior is
swept, so a crude gate is a hedge against the model's own miscalibration, which is
the same caveat that commenter raised.

---

## Part 9 · Feedback

- **A3**, analytics arrive or are refused. *Whether refusal is evidence is
  unresolved.* Creator feedback on r/InstagramMarketing suggests refusal may reflect
  unpaid labour rather than concealment. If confirmed, the likelihood attached to
  refusal must weaken or go. Candidate v0→v1 change.
- **A2**, the gifted post's performance. Whether brands measure this well enough for
  it to count as evidence is open on r/ecommerce.
- **A1**, campaign outcome.
- **A4**, the human's decision, usable as a label.

---

## Section 12 · The ten required questions

**What can the agent observe?** The six signals in Part 1, public profile data and a
rate card.

**What information is hidden?** The answers to A, M and S. Whether the audience is
real, whether it fits the brand, and whether anything damaging sits in the
influencer's history.

**What will a human observe that the agent cannot?** Aesthetic and cultural fit, whether this person *looks* like the brand. Tone in direct messages. Reputation known
inside the industry but never posted. Whether an old controversy is still live or
forgotten.

**What must the agent remember?** Within a case, which probes it has run and what they
returned. Across cases, nothing in v0, a deliberate limitation.

**When must the agent ask a question?** When a probe's cost is below the expected
reduction in decision cost, and, per the r/AI_Agents answer, only when that value
also beats escalating.

**Which incorrect action can be corrected?** A2, A3, A4 are reversible. A5 is
reversible in principle and never in practice, because nobody discovers the mistake.
**A1 is the dangerous one**, a signed contract with a brand-safety failure cannot be
undone.

**Who has the cost of an incorrect action?** Mostly the brand: wasted fee, lost
campaign slot, reputational damage. But **the influencer bears a cost too**, a wrongly
declined creator loses income and never learns why. The agent's errors are invisible
to the party harmed by them, which is the core ethical problem in §10 of the paper.

**Which evidence changes the belief?** E1, E2, E3 move **A** only. E4, E5 move **M**
only. E6 moves **S** only.

*Correction from v0.1:* the earlier spec claimed low engagement was evidence for both
low authenticity and mismatch. That is wrong. A real but mismatched audience engages
normally with the influencer's own content, mismatch is invisible on engagement rate
and only surfaces in audience composition (E4, E5) or once she posts the brand's
product, which is exactly what the gift probe tests.

**Is the historical evidence comparable?** Weakly. Platform algorithms shift engagement
rates year to year, so a 2019 benchmark does not transfer to 2026. Prevalence figures
come mostly from vendors selling detection. Both stated as limitations, not ground
truth.

**How does the agent learn after an action?** In v0 it does not learn across cases.
Feedback is recorded but unused. Stated as a limitation and the natural next version.

---

## Open items

| # | Question | Waiting on | Status |
|---|----------|------------|--------|
| 1 | Ratio: is passing on a good creator worse than paying a fake? | r/advertising | One reply says yes, ratio requested |
| 2 | Is refusing analytics evidence, or just unpaid labour? | r/InstagramMarketing | Leaning "not evidence" |
| 3 | Do brands measure gifted posts well enough to count as evidence? | r/ecommerce | Post filtered, needs rehoming |
| 4 | Should escalation be an action rather than a gate? | r/AI_Agents | Answered, VOI + optimal stopping. Decision pending |
| 5 | How to design the sensitivity analysis | r/AskStatistics | Follow-up asked |
| 6 | What fraction of shortlisted influencers are inauthentic? | r/influencermarketing | Post filtered, needs rehoming |
| 7 | Should P(E1 \| A ✗) be bimodal? | Own modelling | Bought followers lower the rate; bought engagement raises it |
| 8 | Should audience geography inform authenticity as well as match? | Own doc contradicting own signal table | Real bot farms cluster geographically. Allowing it breaks one-signal-one-question and doubles the likelihoods for E4 |
| 9 | Sweep `sign_fake` in the sensitivity analysis | Rich-Owl1937, r/advertising | Never swept, and it prices the error the agent actually makes 73 times out of 75 |

Each open item is a number waiting on a human answer. That is the point of M1.
