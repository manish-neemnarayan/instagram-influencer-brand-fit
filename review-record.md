# Review Record

Three AI reviews, per section 11 of the brief. Each comment is logged with a verdict and
a reason. **Rejections matter as much as acceptances.** A record in which every comment
was accepted would mean the reviews were transcribed, not reviewed.

| Review | Type | Reviewer | Status |
|---|---|---|---|
| 11.1 | Practitioner | | pending |
| 11.2 | Probability | | pending |
| 11.3 | Preprint | | after M8 |

The reviewer is deliberately **not** the assistant used to build the project. A reviewer
that helped choose the latents, the likelihood families and the cost weights shares every
blind spot that produced them. This is the same failure documented in Case 2 of
`failure-analysis.md`: a model cannot be uncertain about something it has no slot for.

---

## How to run these

Attach or paste, in this order:

1. `agent-design.md`
2. `findings.md`
3. `README.md` (for the parameter table and known limitations)
4. Repo link: `https://github.com/manish-neemnarayan/instagram-influencer-brand-fit`

For 11.2, also attach `decisions/probability-decision-record.md` and `src/model.py`.

Run each prompt in a **different** model from the one used to build the project. Paste
the raw output into the transcript section below before triaging, unedited, including
anything that turns out to be wrong.

---

## Prompt 11.1, practitioner review

```
You are a brand partnerships lead at a premium / mid-luxury fashion house. Fifteen
years in the role. You have signed influencers who turned out to have bought their
audience, you have passed on people who went on to work well for a competitor, and
you have had one partner say something in public that cost you a season.

Attached is a decision agent someone is proposing to put in front of your shortlist.
Read it as though it will be used on your budget next quarter.

Find the problems. Specifically:

1. ASSUMPTIONS THAT ARE NOT REALISTIC. Which parts of this describe a version of
   influencer marketing that does not exist? Name the assumption and say what
   actually happens instead.
2. MISSING STAKEHOLDERS. Who else in a real brand has a say in this decision, and
   what happens to their input in this design? Consider anyone whose objection could
   kill a partnership after the agent has approved it.
3. DEPLOYMENT RISKS. What breaks in month three that looks fine on day one?
4. ACTIONS THAT CAN CAUSE HARM. Which of the five actions could damage the brand,
   the influencer, or the relationship, in a way the cost matrix does not capture?
5. ACTIONS THAT CAUSE UNNECESSARY WORK. Which parts of this create labour for
   someone without producing a better decision?

Rules for your response:

- Do not summarise the design back to me. I wrote it.
- Do not list strengths. I am not asking what works.
- Open with the single strongest objection you have, the one you would raise first
  in a room, and say why it is the strongest.
- Every criticism must name a specific section, action, signal or cost weight. A
  criticism I cannot act on is not a criticism.
- After each objection, state what evidence would make you withdraw it.
- Find at least five problems worth raising in a real design review, ranked by how
  much money they would cost.
- If a section genuinely has no serious problem, say so plainly rather than inventing
  a small one to appear thorough.
- I am not asking whether this is a good student project. I am asking whether you
  would let it near your budget.
```

---

## Prompt 11.2, probability review

```
You are reviewing the probabilistic modelling in an applied decision agent. Assume
the author is competent and has already considered the obvious. Do not tell them
probabilities must sum to one, or that priors matter, or that correlation is not
causation. Go straight to what is actually wrong.

The model: three binary latent variables (A audience authentic, M audience matches a
premium fashion brand, S no latent brand-safety risk), giving eight mutually
exclusive atoms. Six observed signals, each modelled as informative about exactly one
latent, conditionally independent given the latents. Five Beta-distributed
proportions and one Poisson count. Engagement rate under an inauthentic audience is a
two-component mixture, low for bought followers and high for bought engagement. The
data is simulated, with an adversarial component: a configurable share of inauthentic
accounts are "sophisticated" and have all three authenticity signals blended toward
the authentic distribution.

Check the following, and be specific:

1. HIDDEN STATES. Is the state space right? Is anything conflated, missing, or
   badly binarised? Is the independence assumed between A, M and S in the prior
   defensible?
2. PRIOR PROBABILITIES. The base rate of inauthentic audiences is swept from 0.10 to
   0.40 rather than fixed, because the required quantity (the rate among influencers
   this brand shortlists) is not measured anywhere. Is sweeping an adequate response
   or an evasion?
3. LIKELIHOOD ESTIMATES. E1 is anchored on published fashion engagement benchmarks.
   E2 to E6 are reasoned estimates. Are the distributional families right? Are the
   concentration parameters (Beta k values) doing work the author has not justified?
4. DECISION THRESHOLDS. The cost-aware policy has no confidence threshold; it
   compares expected costs. Implied thresholds vary by which error is live: 42.9% for
   mismatch, 50.0% for a padded audience, 90.9% for a safety risk. Is anything wrong
   with deriving thresholds this way?
5. ERROR COSTS. Two weights are admitted guesses, sign_unsafe = 200 and
   decline_good = 10. Both are swept. A practitioner argues sign_fake = 20 is too
   low. Is the sensitivity analysis adequate to support the claim that the guesses
   are not load-bearing?
6. CALIBRATION. Expected calibration error is 0.051. The distribution is U-shaped,
   1,519 of 1,600 cases in the two extreme bins. The top bin predicts 0.972 and
   observes 0.888 across 729 cases. Crucially the oracle arm, handed the true
   generating parameters, is no better calibrated (0.053). The author concludes the
   miscalibration is caused by the adversary rather than by bad parameter estimates.
   Is that conclusion supported, or is there a simpler explanation?
7. EVIDENCE FOR AN ALTERNATIVE EXPLANATION. This is the one I most want you to
   attack. The headline result is that the agent beats an engagement-rate baseline by
   a wide margin on simulated data. Give me the strongest competing explanation for
   that result that does not involve the agent being good. Consider in particular
   that the same author wrote both the generator and the agent, and that the
   conditional independence assumed by the agent is also true by construction in the
   generator.

Rules for your response:

- Open with the objection you consider most damaging and say why.
- Cite the specific parameter, distribution or number you are objecting to.
- For each objection, state what result would make you withdraw it.
- Rank your objections by how much they threaten the paper's conclusions, not by how
  easy they are to fix.
- Where the author has already anticipated an objection, say so and assess whether
  the response is adequate, rather than raising it as though it were new.
- If you think a section is sound, say so plainly.
```

---

## 11.1 Practitioner review, transcript

> Paste the raw reviewer output here, unedited.

## 11.1 triage

| # | Comment | Verdict | Reason |
|---|---------|---------|--------|
| | | | |

---

## 11.2 Probability review, transcript

> Paste the raw reviewer output here, unedited.

## 11.2 triage

| # | Comment | Verdict | Reason |
|---|---------|---------|--------|
| | | | |

---

## 11.3 Preprint review

Runs in M8, against the finished preprint. Checks problem statement, new information,
methods, test design, baseline quality, reproducibility and limitations.

---

## Changes carried into v1

| # | Change | Source review | Status |
|---|--------|---------------|--------|
| | | | |
