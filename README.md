# Influencer–Brand Fit Agent

A decision agent for a premium / mid-luxury fashion brand. It observes an influencer's
public profile and must choose an action, **sign, gift first, request analytics,
escalate to a human, or decline**, without knowing whether the audience is authentic,
whether it matches the brand, or whether the influencer carries a latent brand-safety
risk.

> The agent observes an influencer's public profile, engagement history, audience
> signals, disclosure history, and rate card. It must select sign / gift-first /
> request-analytics / escalate-to-human / decline, because whether the audience is
> authentic and genuinely matched to a premium fashion brand is not known at decision
> time.

Cohort 3 · Week 1 · student project. Off-list problem, approved by the instructor.

---

## Reproducing the experiment

**Requirements:** Python 3.10+

```bash
pip install numpy pandas scipy tabulate
python experiments/run_experiment.py
```

Runs in a few seconds. Fixed seeds, so results are identical on every machine.

### What it writes

| File | Contents |
|------|----------|
| `data/tuning_cases.csv` | 200 cases used **only** to choose thresholds |
| `data/test_cases.csv` | 40 cases, untouched until scoring |
| `results/decisions.csv` | Every belief, action and realised cost, per case per policy |
| `results/summary.csv` | Headline metrics |
| `results/summary.md` | Same, formatted, plus test-set ground truth |

Tuning and test sets are generated separately so that thresholds are never chosen on
the cases used to report results.

---

## Live demo

An interactive version of the agent, served by the same Python modules the paper
reports from. Nothing is reimplemented for the demo, so the numbers on screen are the
numbers in `findings.md`.

```bash
python serve.py          # then open http://localhost:8000
```

Sliders change the world (base rate, how common and how good the sophisticated fakes
are), the cost weights, and the policy thresholds. The page shows an execution trace
of which file and function ran on each update, and a case inspector where you can open
a single influencer and see the evidence, the belief, the expected cost of each action,
and then the sealed truth.

Deploys to Railway as-is: `Procfile`, `railway.json` and `requirements.txt` are
included, and the server reads `PORT` from the environment.

---

## What the model does

**Three hidden binary latents**, none observable at decision time:

| Latent | Question |
|--------|----------|
| A | Is the audience authentic? |
| M | Does the audience match a premium fashion brand? |
| S | Is the influencer free of latent brand-safety risk? |

Their 2×2×2 = **8 combinations** are mutually exclusive and collectively exhaustive by
construction. An earlier version used four named states, which failed the
mutual-exclusivity rule because "inauthentic" and "mismatched" can both be true of the
same influencer.

**Six observable signals**, each informative about exactly one latent:

| Signal | Informs |
|--------|---------|
| E1 engagement rate | A |
| E2 share of generic / emoji-only comments | A |
| E3 follower-growth spikes in 24 months | A |
| E4 share of audience in target market | M |
| E5 share of past collaborations at premium tier | M |
| E6 share of paid posts correctly disclosed | S |

Because each signal answers one question, the model needs **12 likelihoods rather than
24**, fewer numbers to defend than the four-state version, despite having more states.

**Adversarial simulation.** Inauthenticity is not modelled as a natural phenomenon.
A configurable share of inauthentic accounts are *sophisticated*: they drip-feed
followers and buy realistic comments, so all three A-signals shift toward authentic
together. One hidden cause moving several signals is what induces correlation between
them, correlation with a mechanism behind it rather than an invented covariance.

---

## The three policies

| Policy | Rule |
|--------|------|
| `policy_threshold` | Fixed cut-offs on event probabilities. Interpretable, cost-blind |
| `policy_expected_cost` | Lowest expected cost under the posterior, with an uncertainty gate in front |
| `policy_engagement_baseline` | Sign if engagement rate clears a cut-off. No beliefs, no costs |

The baseline represents what a brand does with none of this machinery.

---

## Two experimental arms

| Arm | Meaning |
|-----|---------|
| `misspecified` | The agent guesses its parameters. Realistic |
| `oracle` | The agent is handed the true generating parameters. Impossible in practice |

The oracle arm exists only as a reference. If the agent scores evidence with the same
distributions that generated it, the experiment measures "how good is Bayes when you
already know everything," which is not the question. The **gap between the two arms**
is what indicates how much the results depend on the guessed likelihoods being right.

---

## Where the numbers come from

**E1 is anchored on published benchmarks**, fashion and beauty Instagram engagement
runs roughly 2.2–3.8%, above 1% is acceptable, above 3% is strong, and rates fall as
follower count rises.

**E2–E6 are reasoned estimates, not measured.** They are treated as assumptions, and
their influence is tested by running the agent with deliberately misspecified
parameters rather than by claiming they are correct.

**The prior P(A false) is swept, not fixed.** Vendor reports claim ~37% of followers
are fake; a meta-analysis of 47 studies gives 15–49% of accounts affected. Both measure
*what fraction of an audience is inauthentic*. The agent needs *what fraction of the
influencers this brand shortlists are inauthentic*, a different quantity, since a
shortlist is not a random sample. No source measures it, so it is swept across a range.

**The two contested cost weights** are `sign_unsafe = 200` and `decline_good = 10`.
Both are guesses. A practitioner argued the second should be higher than the cost of
signing a fake, on the grounds that passing on a good creator is an invisible loss.
Both are swept.

---

## Changing things

Nearly everything worth changing is in `src/model.py`.

| To change | Edit |
|-----------|------|
| Cost weights | `COSTS` in `src/model.py` |
| Base rate of inauthentic audiences | `p_A_false` in `TRUE_PARAMS` |
| How common / how good sophisticated fakes are | `p_sophisticated`, `soph_pull` |
| Engagement-rate distributions | `e1_auth`, `e1_fake_low`, `e1_fake_high` |
| How wrong the agent's assumptions are | `AGENT_PARAMS` |
| Decision thresholds | defaults in `src/policies.py` |
| Number of cases | `N_TEST`, `N_TUNING` in `experiments/run_experiment.py` |

---

## Repository layout

```
src/
  model.py       parameters, priors, likelihood specs, cost weights
  simulate.py    case generator (adversarial)
  agent.py       Bayesian belief update over the three latents
  policies.py    the three decision rules and the cost scorer
experiments/
  run_experiment.py
data/            generated cases (tuning and test)
results/         decisions, summary
decisions/       probability decision record
paper/           IJCAI-style preprint
social/          LinkedIn post, X thread
agent-design.md  full design spec and the ten Section 12 questions
research-file.md problem, sources, communities, AI prompt and error log
discussion-record.md   public discussions and the design change each caused
review-record.md AI review comments, accepted and rejected, with reasons
```

---

## Known limitations

- **Signals are scored as conditionally independent** given the latents. A
  sophisticated operator degrades several at once, so their evidence is
  double-counted and posteriors run hotter than they should. The sophistication
  variable models the cause but the agent does not account for it when scoring.
- **The uncertainty gate is close to inert**, it fires on well under 1% of cases. The
  agent is confidently right or confidently wrong, rarely uncertain, so
  uncertainty-triggered escalation catches almost nothing.
- **Probes are not chosen by what they would reveal.** Their costs are flat, so the
  cheaper probe always wins and the gift probe is never selected. Choosing between
  probes requires a value-of-information calculation, which v0 does not implement.
- **All cases are simulated.** No real influencer data is used.
- **Likelihoods are adversarially fragile**, any detection signal decays once it
  becomes known and people evade it specifically.

## AI use

AI assistance was used for literature search, code, and critique. All design decisions,
numbers and interpretations are the author's, and every external claim is sourced or
marked as an assumption. Errors made by AI tools during the project are logged in
`research-file.md`.
