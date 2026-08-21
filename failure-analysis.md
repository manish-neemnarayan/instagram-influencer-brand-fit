# Failure Analysis, v0

Six cases read one at a time. The aggregate tables in `findings.md` say *how often* the
agent is wrong. They cannot say *what kind of wrong*, and the two questions have
different answers.

Every case here is reproducible:

```python
from simulate import generate_cases, observable_only
from agent import update_beliefs
from model import AGENT_PARAMS
c = generate_cases(40, seed=SEED)
b = update_beliefs(observable_only(c), AGENT_PARAMS)
```

All beliefs are from the misspecified arm, the realistic one. Costs are the `COSTS`
weights in `src/model.py`.

---

## How these six were chosen

Four criteria, and one rule about what *not* to do.

1. **Cover every named failure condition.** Picking the five worst cases would have
   produced five copies of the same signing, because one failure mode accounts for most
   of the total.
2. **Include both extremes of belief.** The most confident wrong decision and the least
   confident wrong decision. The distance between them is itself the finding.
3. **Include failures only one policy makes.** A case both policies get wrong says
   something about the model. A case one gets wrong and the other gets right says
   something about the design, which is more useful.
4. **Every case must carry an argument the aggregate table cannot make.** If a case only
   restates a row of `findings.md`, it does not earn its place.

**The rule about what not to do: never rank by cost.** Sorting by realised cost returns
the most expensive errors, which are all the same error. Cost tells you what to fix
first. It does not tell you what is happening.

One case, INF-015, is not a failure of the agent at all. It is the control. Without it
there is no way to tell whether the agent is weak everywhere or weak in one specific
place.

| # | Case | Seed | Truth | Argument |
|---|------|------|-------|----------|
| 1 | INF-015 | 1008 | fake, crude | Control. The machinery works, and the baseline is inverted |
| 2 | INF-026 | 1011 | fake, sophisticated | Flawless disguise. **Model failure** |
| 3 | INF-003 | 1011 | fake, sophisticated | Leaky disguise, belief caught it, policy overrode it. **Policy failure** |
| 4 | INF-021 | 1029 | real, mismatched | A cheaper error, and a different one |
| 5 | INF-020 | 1023 | real, unsafe | The case that justifies the cost matrix |
| 6 | INF-035 | 1013 | clean | The invisible error, made by a cost-blind rule |

---

## Case 1 · INF-015, the control

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | **7.42%** | A | Roughly triple the fashion benchmark |
| E2 generic comments | **81.7%** | A | Almost the entire comment section is filler |
| E3 growth spikes | **5** | A | Expected under 1 for an organic account |
| E4 in target market | 77.0% | M | Strong |
| E5 premium collaborations | 69.9% | M | Strong |
| E6 disclosure | 92.9% | S | Clean |

**What it believed**

```
P(audience real)   0.00000089
P(matches us)      0.99987
P(safe)            0.99980
P(clean fit)       0.00000089
```

**What it did**

| Policy | Action | Cost |
|--------|--------|------|
| baseline | **SIGN** | +20 |
| v0_threshold | ANALYTICS | +1 |
| v0_expected_cost | **DECLINE** | 0 |

**Truth:** audience inauthentic, crude. Brand match genuine, no safety risk.

### Why this case is here

Three things, none of which are visible in the aggregate table.

**The machinery is not weak.** Given honest evidence the agent reaches a posterior of
roughly one in a million and declines without hesitation. Every later failure in this
document has to be read against this number. The agent does not fail because Bayesian
updating is fragile. It fails only where the evidence itself has been manufactured.

**A product is not an average.** Her brand signals are excellent. `P(M)` and `P(S)` are
both above 0.999, and a human reviewer would like her a great deal. The agent still puts
her clean-fit probability at effectively zero, because clean fit is `P(A) × P(M) × P(S)`
and one factor near zero collapses the product no matter what the other two do. A model
that scored her on an average of three factors would have rated her highly. This is the
factorisation doing work that a scoring rubric could not.

**The baseline is not merely worse here, it is inverted.** Its rule is *sign above 2%
engagement*, and she reads 7.42%. The single most incriminating number on the profile,
an engagement rate so far above benchmark that it can only have been purchased, is the
exact number the baseline treats as evidence of excellence. This matters beyond one
case: it means the baseline's errors are not random noise around the right answer. On
crude fakes it is steered wrong by the thing that should have stopped it, which is why
it signed 58 of them across 30 replications while the cost-aware agent signed none.

Note also that the threshold policy did not decline her. It requested analytics, paying
1 unit to resolve something the evidence had already settled a million times over. A
cost-blind rule cannot tell the difference between a genuine open question and a
question that is closed.

---

## Case 2 · INF-026, the model failure

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | 2.69% | A | Centre of the 2.2 to 3.8% fashion benchmark |
| E2 generic comments | 17.1% | A | *Better* than a typical real account |
| E3 growth spikes | **0** | A | Perfectly organic growth curve |
| E4 in target market | 91.1% | M | Excellent |
| E5 premium collaborations | 34.6% | M | Moderate |
| E6 disclosure | 86.4% | S | Clean |

**What it believed**

```
P(audience real)   0.99997        1 − P(A) = 3.4 × 10⁻⁵, about 1 in 29,000
P(matches us)      0.99921
P(safe)            0.99799
P(clean fit)       0.99716        also the strongest single atom
```

**Expected costs**

```
SIGN       −9.56    ← chosen, and by a wide margin
ANALYTICS  +1.00
GIFT       +2.00
ESCALATE   +5.00
DECLINE    +9.97
```

**What it did:** every policy signed, including the baseline. Cost +20 each.

**Truth:** audience inauthentic, sophisticated. Brand match genuine, no safety risk.

### Why this case is here

**The reasoning was correct and the answer was wrong.** There is no arithmetic error to
find. Under the agent's model, an engagement rate at benchmark, a comment section
cleaner than average and a perfectly smooth growth curve genuinely are overwhelming
evidence of authenticity. The posterior of 0.99997 is the right answer to the question
the agent was asked. The question was the wrong one.

**Set it beside Case 1.** Both influencers have identical hidden states: inauthentic,
matched, safe. The only difference is how the inauthenticity was produced.

| | E1 | E2 | E3 | P(audience real) |
|---|---|---|---|---|
| INF-015, crude | 7.42% | 81.7% | 5 | **0.0000009** |
| INF-026, sophisticated | 2.69% | 17.1% | 0 | **0.99997** |

Same truth, posteriors a millionfold apart and at opposite ends of the scale. The agent
is not uncertain in the second case and wrong in a defensible way. It is confident, and
confidently on the wrong side. This pair is the clearest single statement of what
adversarial evidence does: it does not add noise, it moves the posterior in the wrong
direction with full force.

**No confidence-based safeguard can catch this.** A rule of the form *do not act unless
belief exceeds some bar* fires only when belief is low, and belief here is as high as it
gets. Across all 58 sophisticated fakes the cost-aware policy signed, the mean `P(A)`
was 0.967 and the lowest was 0.673. Not one of them arrived with uncertainty attached.
The uncertainty gate, which triggers on 0.3% of cases, caught none.

**The misspecification is structural, not numerical.** The oracle arm, handed the true
generating parameters, scores −140 against the misspecified −137, a difference of about
three units across 40 cases. Better numbers buy almost nothing. What is missing is not a
value but a variable: the model has three latents and the world has a fourth,
sophistication, which has no slot to occupy. The agent cannot hold uncertainty about
something it has no place to put it. This is the sentence the whole project turns on,
and it is why v1 cannot be a matter of re-estimating priors.

---

## Case 3 · INF-003, the policy failure

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | **1.03%** | A | Below benchmark, near the bought-follower mode |
| E2 generic comments | **47.9%** | A | Well above the ~30% a real audience produces |
| E3 growth spikes | 1 | A | Slightly elevated |
| E4 in target market | 76.0% | M | Strong |
| E5 premium collaborations | 45.7% | M | Moderate |
| E6 disclosure | 84.8% | S | Clean |

**What it believed**

```
P(audience real)   0.67329        so a 32.7% chance she is fake, left on the table
P(matches us)      0.99473
P(safe)            0.99694
P(clean fit)       0.66769
```

**Expected costs**

```
SIGN       +0.50    ← chosen, and note the sign is POSITIVE
ANALYTICS  +1.00
GIFT       +2.00
ESCALATE   +5.00
DECLINE    +6.68
```

**What it did**

| Policy | Action | Cost |
|--------|--------|------|
| baseline | DECLINE | 0 |
| v0_threshold | **DECLINE** | 0 |
| v0_expected_cost | **SIGN** | +20 |

**Truth:** audience inauthentic, sophisticated. Brand match genuine, no safety risk.

**Sensitivity on the contested weight `sign_fake`:**

```
sign_fake = 20   SIGN  +0.50   DECLINE  +6.68   →  SIGN
sign_fake = 21   SIGN  +0.83   DECLINE  +6.68   →  SIGN
sign_fake = 22   SIGN  +1.15   DECLINE  +6.68   →  ANALYTICS   ← failure disappears
```

### Why this case is here

**The belief was not the problem.** Her engagement rate sits at 1.03%, down near the
bought-follower mode, and 47.9% of her comments are generic against roughly 30% for a
real audience. The disguise leaked, the agent saw it, and `P(A)` fell to 0.673. The
threshold policy read that and declined her. Nothing in the inference went wrong.

The cost-aware policy then signed her anyway.

**This is the exact mirror of Case 2.** There the evidence was immaculate and the belief
was wrong, so the model failed while the policy did the right thing with what it was
given. Here the evidence was suspicious and the belief was reasonable, and the policy
overrode it. Two failures, two different organs, and **no single fix addresses both**.
That fact alone rules out most of the obvious v1 changes.

**The signing had a positive expected cost.**

```
SIGN     +0.50    ← chosen
DECLINE  +6.68
```

The agent expected to *lose* half a unit by signing and did it because every alternative
lost more. This is worth stating plainly because it is easy to misread what an
expected-cost policy does. It never asks *is this a good idea*. It asks *is this the
least bad thing available*, and on this case the answer to the second question was yes
while the answer to the first was no. v0 has no way to express the difference, and no
way to say "none of these are worth doing."

**The obvious fix does not work, and the reason is Case 2.**

`P(clean) = 0.668` here is the lowest of any wrong signing in all 58. The natural
response is to add a confidence floor: never sign below some bar. Swept over the same
30 replications:

| floor on P(clean) | total cost | sophisticated fakes signed | clean creators declined |
|---|---|---|---|
| none | −117.5 | 58 | 30 |
| 0.75 | −118.1 | 56 | 32 |
| 0.90 | −117.3 | 50 | 47 |
| 0.95 | **−104.2** | 44 | **93** |

A floor at 0.75 buys two fewer fakes and costs two more good creators, moving total cost
by 0.6 units out of 117. At 0.95 it blocks 14 fakes and rejects 63 additional good
people, and the agent is meaningfully **worse**.

The reason is that a floor can only catch failures sitting near it, and these are not
near it. Only 2 of the 58 fall below 0.75; the mean is 0.967. Set the bar low enough to
be safe and it never fires, set it high enough to fire and it rejects everyone.

The two cases in this document make the point without any sweep at all:

```
INF-003   P(clean) 0.668   fake     blocked by a 0.75 floor   ✓
INF-035   P(clean) 0.676   CLEAN    blocked by a 0.75 floor   ✗
```

Eight thousandths apart, opposite truths. **Confidence is not the variable that separates
them**, so no cut-off placed along it can.

**What decided this case was a number that is under dispute.** The margin between
signing and probing is 0.50 units, and the flip point is `sign_fake = 22`:

```
sign_fake = 20   SIGN  +0.50   →  SIGN
sign_fake = 22   SIGN  +1.15   →  ANALYTICS, and the failure disappears
```

The belief never moves across that sweep. `P(clean)` is 0.668 throughout. Only the price
of the mistake changes, and the decision follows the price.

A practitioner on r/advertising has argued that `sign_fake = 20` is too low, on the
grounds that the real damage from a visibly fake endorsement is a brand that looks
unable to tell, which is reputational rather than the wasted fee the number represents.
That is recorded in `discussion-record.md` and remains unresolved. If they are right by
two units, this case stops being a failure.

**This cannot be settled from the data**, because the data contains no measurement of
reputational damage. It is a question about the world, priced into a constant, and it
decides a real outcome in these results. Naming that is more useful than defending the
20.

**The baseline got this one right, for the wrong reason.** It declined her because her
engagement rate of 1.03% falls under its 2% cut-off. It has no representation of
audience authenticity at all. Case 1 is the proof: INF-015 is also fake, with engagement
at **7.42%**, and the baseline signed her without hesitation. The same rule that
correctly refuses INF-003 enthusiastically accepts a cruder fake, because bought
engagement pushes the one number it reads in the direction it rewards. The baseline was
pointed the right way here by the accident of which failure mode she happened to have.

---

## Case 4 · INF-021, a different and cheaper error

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | 1.56% | A | Modest but plausible |
| E2 generic comments | 20.0% | A | Clean |
| E3 growth spikes | 0 | A | Organic |
| E4 in target market | **57.9%** | M | Middling |
| E5 premium collaborations | **36.0%** | M | Low for a premium brand |
| E6 disclosure | 86.1% | S | Clean |

**What it believed**

```
P(audience real)   0.99970
P(matches us)      0.79372        ← the only live doubt
P(safe)            0.99782
P(clean fit)       0.79174
```

**Expected costs**

```
SIGN       −4.39    ← chosen
ANALYTICS  +1.00
GIFT       +2.00
ESCALATE   +5.00
DECLINE    +7.92
```

**What it did**

| Policy | Action | Cost |
|--------|--------|------|
| baseline | DECLINE | 0 |
| v0_threshold | SIGN | +15 |
| v0_expected_cost | SIGN | +15 |

**Truth:** audience authentic, **not** a brand match, no safety risk.

### Why this case is here

**The agent was right about the thing it usually gets wrong.** `P(A) = 0.9997`, and she
genuinely is a real person with a real audience. Cases 2 and 3 are both authenticity
failures. This one is not a milder version of them, it is a failure of a different
latent, and it behaves differently: cheaper, rarer, and caused by weak evidence rather
than by manufactured evidence.

**Almost all of the belief came from the prior.** Working in odds:

```
prior odds (match : no)   1.857     from P(M) = 0.65, before seeing anything
× LR(E4 = 0.579)          1.861
× LR(E5 = 0.360)          1.105
= posterior odds          3.818     →  P(M) = 79.2%
```

The two signals together roughly doubled the odds. The prior supplied the rest. On the
match question this agent is largely restating its own assumption, and the 79.2% reads
as far more informed than it is.

**36% premium collaborations is not the damning number it looks like.** Under the agent's
parameters, match centres on 0.55 and mismatch on 0.20, both with `k = 10`. A reading of
0.36 falls between the two humps:

```
P(E5 = 0.36 | match)     1.2597
P(E5 = 0.36 | mismatch)  1.1400
                 LR      1.105
```

A human reviewer looks at 36% and sees a creator who has barely worked at this price
point. The model looks at 36% and sees a number that discriminates almost nothing, and
in fact leans very slightly *toward* a match. The disagreement is not that the model is
being subtle. It is that `e5_match` and `e5_mismatch` are too close together and too
loosely concentrated to separate mid-range readings at all. **E5 is close to a dead
signal across the middle of its range**, and no amount of belief updating recovers
information that the likelihood model never encoded.

**The agent should have probed here, and v0 cannot.**

```
SIGN       −4.39    ← chosen
ANALYTICS  +1.00
GIFT       +2.00
ESCALATE   +5.00
```

Signing carries a negative expected cost, meaning a gain, so it beats a probe priced at
a flat 1.00. The agent will not buy information whenever any terminal action already
looks profitable, regardless of how valuable that information would be.

This is precisely the case where a probe is worth most: one open question, weak evidence,
and a belief resting mainly on the prior. An analytics reading on audience composition
would have resolved M directly. Its true worth is far above one unit, and v0 has no way
to represent that, because probes are priced by what they cost rather than by what they
tell you. **Expected value of information is missing from the policy, and this case is
what its absence looks like.** Carried into v1 as change #3.

**There is a rule here, it is simply implied rather than written.** With mismatch as the
live risk:

```
threshold = sign_mismatch / (sign_mismatch − sign_clean + decline_good)
          = 15 / (15 + 10 + 10) = 42.9%
```

`P(M) = 79.2%` sits at nearly twice the bar, so the decision was never close. Moving
this case would require either making a probe worth more than its price, or making E5 a
sharper discriminator so that 36% actually counts against her. Raising the confidence
bar would not do it, and Case 3 already shows why that lever fails generally.

**This is not the thing to fix first, and saying so is part of the analysis.** Two
mismatch signings across 30 replications against 58 sophisticated fakes, at 15 units
each against 20. It is rarer and cheaper on both counts. Case 4 earns its place by
showing the failure table is not monolithic, and by exposing a dead signal and a missing
probe valuation that the aggregate numbers hide completely, rather than by costing very
much.

---

## Case 5 · INF-020, the case that justifies the cost matrix

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | 1.98% | A | Just under benchmark |
| E2 generic comments | 33.4% | A | Ordinary |
| E3 growth spikes | 2 | A | Slightly elevated |
| E4 in target market | 72.7% | M | Strong |
| E5 premium collaborations | 50.6% | M | Reasonable |
| E6 disclosure | **63.2%** | S | Poor. More than a third of paid posts undisclosed |

**What it believed**

```
P(audience real)   0.95954
P(matches us)      0.99556
P(safe)            0.88268        ← an 11.7% chance of a safety problem
P(clean fit)       0.84321
```

**Expected costs**

```
ANALYTICS  +1.00    ← chosen by the cost-aware policy
GIFT       +2.00
ESCALATE   +5.00
DECLINE    +8.43
SIGN      +15.80    ← 0.117 × 200 = 23.4 of exposure, against 8.43 of upside
```

**What it did**

| Policy | Action | Cost |
|--------|--------|------|
| baseline | DECLINE | 0 |
| v0_threshold | **SIGN** | **+200** |
| v0_expected_cost | **ANALYTICS** | +1 |

**Truth:** audience authentic, brand match genuine, **latent safety risk present**.

### Why this case is here

**Both policies held exactly the same belief.** Identical numbers, down to the last
decimal, because they share the same belief update. One of them lost 200 units and the
other spent 1. Everything that separates them happened after the inference finished.

This case is the thesis of the project reduced to a single influencer: **belief and
decision are different problems, and getting the first one right does not get you the
second.**

**The threshold policy did not make a mistake. It followed its rules.**

```
rule 1   escalate if safety risk > 15%      risk = 11.7%   →  under. Stay silent
rule 2   sign if P(clean) > 70%             P(clean) = 84.3%  →  over. Sign
```

Both steps correct, both thresholds respected, outcome 200. There is no bug to find and
no arithmetic to repair. The rule itself produced the loss.

**The two policies imply thresholds 5.9 points apart, and she falls in the gap.**

```
hand-written rule:   worry only when P(S) < 0.850      ← chosen by a person
cost-derived bar:    sign only when P(S) ≥ 0.909       ← 200 / (200 + 10 + 10)

              INF-020 sits at P(S) = 0.883
```

Above 0.850, so the hand-written rule says nothing is wrong. Below 0.909, so the
cost-derived bar refuses to sign. **The 15% was a guess and it was wrong by roughly six
percentage points, and those six points cost 200 units.** Nobody chose 90.9%. It falls
out of the cost matrix, and it is available for free to any policy that compares
expected costs instead of guessing cut-offs.

**The cost-aware policy did not decline. It bought information.**

```
ANALYTICS  +1.00    ← chosen
GIFT       +2.00
ESCALATE   +5.00
DECLINE    +8.43
SIGN      +15.80     0.117 × 200 = 23.4 of exposure against 8.43 of upside
```

Declining costs 8.43, because there remains an 84% chance she is genuinely worth having.
Signing costs 15.80, because a one-in-nine chance of a 200-unit event outweighs
everything else on the profile. So the agent pays one unit to resolve the question and
keeps her alive.

Nothing in `policies.py` instructs the agent to be careful about safety. There is no
special case, no guard clause, no minimum confidence for risky signings. The caution is
produced entirely by multiplying 0.117 by 200. **Information-seeking behaviour emerges
from plain expected-cost minimisation**, and it emerges exactly where it should, on the
one case in the set where a probe is obviously worth buying.

Contrast with Case 4, where the same policy refused to probe because signing already
looked profitable. The probe is priced at a flat 1.00 in both cases. What changed is not
the value of information, which v0 never computes, but whether any terminal action
happened to look worse than 1.00. That the right behaviour appears here is partly luck.

**This case explains the `sign_unsafe` sweep.** Sensitivity analysis showed the agent
flat at about −101 as `sign_unsafe` moved from 50 to 500, while the baseline's cost
nearly quadrupled over the same range. The reason is visible here: the agent never signs
an unsafe influencer, so raising the price of that error charges it nothing, while the
baseline keeps committing it and gets billed more each time. A guessed weight is not
load-bearing for a policy that never triggers it.

**The baseline scored 0 on this case and deserves no credit for it.** Its cut-off is
2.00% engagement and her reading is **1.98%**. It avoided a 200-unit catastrophe by two
hundredths of a percentage point, on a signal carrying no information about safety at
all. Raise her engagement by 0.03 and it signs her. As in Case 3, the right answer
arrived with no reasoning behind it, and a reader scanning the outcome column should not
mistake the two.

**One honest limit.** The agent's immunity to safety risks holds only while E6 separates
safe from unsafe influencers by the 0.45 gap assumed in `TRUE_PARAMS`. Both AI reviews
argued that disclosure compliance is a poor proxy for reputational risk, and shrinking
that gap to 0.10 causes the cost-aware policy to sign 14 safety risks and turn cost
positive. The behaviour in this case is correct. The claim that it generalises rests on
an assumption about the world that has not been tested against data.

---

## Case 6 · INF-035, the invisible error

**What the agent saw**

| Signal | Value | Answers | Reading |
|--------|-------|---------|---------|
| E1 engagement rate | 2.50% | A | Squarely at benchmark |
| E2 generic comments | 13.8% | A | Very clean |
| E3 growth spikes | 0 | A | Organic |
| E4 in target market | **60.1%** | M | Moderate |
| E5 premium collaborations | **31.2%** | M | Low |
| E6 disclosure | 72.2% | S | Adequate |

**What it believed**

```
P(audience real)   0.99998
P(matches us)      0.70075
P(safe)            0.96539
P(clean fit)       0.67649        ← threshold demands 0.70. Short by 2.4 points
```

**Expected costs**

```
ANALYTICS  +1.00    ← chosen by the cost-aware policy
GIFT       +2.00
SIGN       +4.49
ESCALATE   +5.00
DECLINE    +6.76
```

**What it did**

| Policy | Action | Cost |
|--------|--------|------|
| baseline | **SIGN** | **−10** (correct) |
| v0_threshold | **DECLINE** | +10 |
| v0_expected_cost | ANALYTICS | +1 |

**Truth:** authentic, matched, safe. A genuinely good creator.

### Why this case is here

**She was rejected by 2.4 percentage points on a number somebody guessed.**

```
P(clean) = 0.67649        threshold policy demands 0.70
```

There is nothing behind the 0.70. It is not derived from the costs, not fitted to
anything, not the answer to any question. It was chosen because it sounded reasonable,
and a genuinely good creator was turned away for falling under it.

The cost-aware policy, holding the identical belief, spent one unit on analytics rather
than commit either way:

```
ANALYTICS  +1.00    ← chosen
GIFT       +2.00
SIGN       +4.49
ESCALATE   +5.00
DECLINE    +6.76
```

Across 30 replications `declined_clean` occurs **4 times** for the threshold policy and
**0 times** for the cost-aware one. This case is the mechanism behind that difference:
a fixed cut-off has no way to notice that it is 2 points from the line, while an
expected-cost comparison sees that a probe costs less than the risk of being wrong in
either direction.

**This is the error nobody ever finds out about.** A brand that signs the wrong creator
watches a campaign underperform and learns something. A brand that declines the right
creator sees nothing at all. No campaign runs, no data arrives, no correction ever
happens. The cost of 10 in the matrix is a guess about a quantity that, in deployment,
is never observed even once.

`probability-decision-record.md` already notes this for the manual case: *"a brand rarely
learns the truth about the creators it declined."* This case shows the same fact costing
real money in the experiment.

### The asymmetry, which is the more serious problem

If truth arrives only for signings, then an agent that learns from its own outcomes is
learning from a sample selected by its own past beliefs. This is the **selective labels**
problem, and its consequence here is not neutral.

| Error | Does the world correct it? |
|---|---|
| Sign someone bad | **Yes.** The campaign underperforms, the label arrives, the belief moves |
| Decline someone good | **No.** Nothing happens. Ever |

Errors of commission are self-correcting. Errors of omission are self-perpetuating. So an
agent trained on its own decisions does not drift toward signing, it **ratchets toward
over-conservatism**, growing steadily more confident about a decline region it has never
once tested. INF-035 is day one of that process, and the mechanism guarantees she is
never revisited.

Four escapes exist, in rough order of cost:

1. **Probes as label generators.** A gift or an analytics request buys information about
   a case that would otherwise disappear. Partial, since it reveals the audience rather
   than how a campaign would have performed, but it is the difference between something
   and nothing. **v0 already has this action and does not use it for this purpose.**
2. **Deliberate random exploration.** Sign a small fraction of borderline declines on
   purpose, accepting the loss in order to buy unbiased labels in the unobserved region.
   The standard answer from the bandit literature, and the only one that yields clean
   data on declines. It costs real money and requires someone to authorise losing it.
3. **Proxy outcomes.** Follow declined creators who later worked with a competitor and
   observe those campaigns. Noisy, delayed and confounded, but it is a signal from a
   region that otherwise produces none.
4. **Model the selection explicitly.** Treat "was signed" as a conditioning event in the
   generative model rather than treating observed outcomes as a random sample. The same
   machinery raised as Berkson's bias in the probability review.

**None of these are implemented in v0**, and the honest statement is that the agent has no
learning loop at all, so the problem is latent rather than active. It becomes active the
moment anyone tries to fit the priors to observed results, which is the obvious next step
and the one most likely to be taken without noticing what it does.

### The baseline won this one

The engagement baseline signed her and earned −10. Both agent policies did not.

Across these six cases the baseline is right twice, on Case 3 and on Case 6. Both times
for no reason: it declined the fake in Case 3 because bought followers had depressed her
engagement below a cut-off, and it signed the good creator here because her engagement
happened to clear it. It holds no belief about authenticity, brand match or safety, and
on Case 1 the same rule enthusiastically signs a crude fake reading 7.42%.

That is worth stating rather than hiding. **A failure analysis in which the baseline
never wins is advocacy, not analysis.** The defensible claim is not that the baseline is
always wrong, it is that the baseline is right by accident and cannot be relied upon to
repeat it, which is exactly what the pooled numbers show: 94 clean creators declined and
45 safety risks signed across 30 replications.

---

## Which error costs most

Pooled failure counts across 30 replications, 1,200 cases:

| failure | baseline | v0_threshold | v0_expected_cost |
|---|---|---|---|
| `signed_sophisticated_fake` | 98 | 60 | **58** |
| `signed_mismatch` | 262 | 2 | 2 |
| `signed_crude_fake` | 58 | 0 | 0 |
| `signed_safety_risk` | 45 | 1 | **0** |
| `declined_clean` | 94 | 4 | **0** |

The question has three defensible readings, and the first thing to notice is that the
answer **changes depending on which system you ask about**.

| | baseline | v0_threshold | v0_expected_cost |
|---|---|---|---|
| sophisticated fakes | 98 × 20 = 1,960 | 60 × 20 = 1,200 | **58 × 20 = 1,160** |
| crude fakes | 58 × 20 = 1,160 | 0 | 0 |
| mismatches | 262 × 15 = 3,930 | 2 × 15 = 30 | 2 × 15 = 30 |
| safety risks | **45 × 200 = 9,000** | 1 × 200 = 200 | 0 |
| clean declined | 94 × 10 = 940 | 4 × 10 = 40 | 0 |
| **total damage** | **16,990** | **1,470** | **1,190** |

For the baseline, safety risks are **53%** of all damage. For the cost-aware agent they
are **zero**, and sophisticated fakes are **97%**. The agent has not reduced every error
proportionally; it has eliminated one class entirely and is left holding another.

**One arithmetic correction worth making explicitly.** It is tempting to write that a
single catastrophe outweighs all the small errors. For these numbers that is **false**.
The threshold policy's one safety signing cost 200, while its 60 sophisticated fakes cost
1,200, six times more. The catastrophic error is the most expensive *per incident* and
nowhere near the most expensive *in total*. Rhetoric about tail risk should not survive
contact with the multiplication.

### The three readings

**Most frequent, and therefore most costly in aggregate: sophisticated fakes.**
58 signings across 1,200 cases, 97% of the surviving agent's total damage. Every other
failure class is rounding by comparison. On volume this is not a close call.

**Most expensive per incident: signing a safety risk.** 200 units, twenty times a
routine error, and unlike the others it is not recoverable by doing better next quarter.
The agent currently makes this error zero times, but Case 5 shows that outcome depends
on a 15% threshold being replaced by a derived 90.9% one, and on E6 separating safe from
unsafe influencers by a margin both AI reviews consider unrealistic.

**Most invisible: declining a good creator.** Priced at 10, which is a guess about a
quantity that is never observed even once in deployment. A practitioner on r/advertising
argued it should exceed the cost of signing a fake, on the grounds that the real loss is
a competitor signing her. Case 6 shows why this is worse than its price suggests: it is
the only error the world never corrects, so it compounds while every other error
self-limits.

### Which I would fix first

**Signing a safety risk, then passing on good creators**, in that order, and not because
of the totals.

Sophisticated fakes cost the most and should still not be first. They are a bounded,
recoverable, monetary loss, and the case for tolerating some of them is the same case any
business makes for accepting fraud below the cost of eliminating it. They are also the
hardest to fix, since Cases 2 and 3 together show that neither better parameters nor a
higher confidence bar touches them.

Signing a safety risk goes first because it is the only error with an unbounded tail. The
200 in the cost matrix stands for a campaign pulled and a season of brand equity, and
nothing in the analysis establishes that 200 is the ceiling rather than the floor. It is
also the error the agent is currently least entitled to feel safe about: its perfect
record depends on E6 being a good proxy for reputational risk, which is the single claim
both reviewers attacked hardest.

Passing on good creators goes second **on deployment risk rather than measured cost**, and
that distinction has to be stated plainly. The cost-aware policy declines zero clean
creators in 1,200 cases, so on this evidence the error does not occur. Two reasons not to
dismiss it. First, that zero depends on unlimited probing; give the agent a realistic
probe budget and it must start declining instead. Second, it is the only failure with no
feedback path, so an agent that ever learns from its own outcomes will accumulate this
error indefinitely without any signal that it is doing so.

**The honest summary is that "most costly" and "most urgent" have different answers here,
and conflating them is how a project ends up optimising the wrong thing.**

---

## What this changes for v1

### The comparison set is restructured, not reduced

The obvious response to a baseline that scores below the no-information floor is to
delete it, and to a cost-blind policy that loses 200 units on one case is to retire it.
Both would be mistakes. **Each of the three has a different job, and none of the jobs is
"be a plausible rival."**

| Policy | Role in v1 | Why it stays |
|---|---|---|
| `engagement_baseline` | **Current practice** | It is what a brand does today. Its accuracy of 0.536 against a no-information floor of 0.573 is a *result*, not an embarrassment |
| `policy_threshold` | **Ablation** | Identical belief update, cost matrix removed. The only controlled evidence that the cost matrix does anything |
| tuned 6-signal heuristic | **The real competitor** | Same information, no probability. This is the comparison the headline number should be reported against |
| `policy_expected_cost` | The agent | |

The threshold policy in particular must be kept and **relabelled**. Presented as a rival
it looks like a strawman; presented as an ablation it is exactly the right object. Delete
it and Case 5 disappears, the `0.850` against `0.909` comparison disappears, the 4-against-0
on declined clean creators disappears, and "the cost matrix matters" drops from a
controlled result to an assertion.

### What each case changes

| Case | Finding | Change for v1 |
|---|---|---|
| 1 | Posterior of one in a million on honest evidence | **Do not touch the belief update.** The inference is sound; every failure is upstream of it |
| 2 | Flawless disguise, correct reasoning, wrong answer | Add sophistication as an explicit latent. **Structural**, not a re-estimation |
| 3 | Leaky disguise, belief caught it, cost arithmetic overrode it | Policy-side. Needs an option to decline when no action is worth taking, not a confidence floor |
| 4 | E5 near-uninformative mid-range; probe refused because signing looked profitable | Re-fit `e5_match` / `e5_mismatch`; price probes by expected value of information |
| 5 | Guessed 15% threshold against derived 90.9% | Retire guessed cut-offs. Already change #2 |
| 6 | Errors of omission never correct themselves | Use probes as label generators. Add the selective-labels limitation explicitly |

**Cases 2 and 3 fail for opposite reasons and no single fix addresses both.** Case 2 needs
a change to the state space, because the model cannot represent what fooled it. Case 3
needs a change to the policy, because the model represented the doubt correctly and the
decision rule discarded it. Any proposal that claims to solve both at once has
misunderstood one of them.

### Carried from the AI reviews

| # | Change | Source |
|---|---|---|
| 10 | Re-scope E6 to operational compliance; link S to actual controversy signals | 11.1 and 11.2, independently |
| 11 | Drop the `A ⊥ M` prior independence assumption; bot audiences sit in cheap non-target regions | 11.1 and 11.2, independently |
| 12 | Report against a tuned six-signal heuristic, not only the engagement rule | 11.2 objection 1 |
| 13 | Attribute the calibration gap to naive-Bayes DAG misspecification interacting with the adversary, not to the adversary alone | 11.2 objection 2 |
| 14 | Sweep `sign_fake`; executed, ordering stable from 10 to 80 | 11.2 objection 4, flagged first in `agent-design.md` open item 9 |
| 15 | Add E6 separation as a fourth swept parameter | own test, prompted by 11.1 |

The last one is the uncomfortable one. Three guessed numbers were swept and reported as
not load-bearing. A fourth was never swept and is load-bearing: shrinking the E6 gap from
0.45 to 0.10 causes the cost-aware policy to sign 14 safety risks and turn cost-positive.
**The sensitivity analysis was sound in method and incomplete in coverage, and a reviewer
found the gap in one pass.**
