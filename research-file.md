# Research File, Influencer–Brand Fit Agent

**Student:** Mani
**Cohort 3 · Week 1**
**Status:** M0 complete (problem locked). Sections 3–9 pending in M1.

---

## 1. Problem statement

> The agent observes an influencer's public profile, engagement history, audience
> signals, disclosure history, and rate card. It must select **sign**, **gift-first**,
> **request-analytics**, **escalate-to-human**, or **reject**, because whether the
> audience is authentic and genuinely matched to a premium fashion brand is not known
> at decision time.

**Scope lock:** premium / mid-luxury fashion (a tier above fast fashion). Fewer
partnerships, higher fee per partnership, and brand-safety failures are far more
expensive than in fast fashion. This asymmetry drives the entire cost model.

**Approved by instructor** as an off-list problem (Section 3 permits this).

---

## 2. Project objective

Build the smallest testable agent that decides whether a premium fashion brand should
partner with a given influencer, under incomplete information, and that can **buy
information** (gift-first, request-analytics) rather than being forced to commit or
refuse immediately.

Success is not classification accuracy. Success is making decisions whose **expected
cost** is lower than a naive baseline, while routing genuinely ambiguous cases to a
human instead of guessing.

---

## 3. Why this problem is not a classifier

A classifier outputs a label. This agent must output an **action**, and two of its
five actions exist purely to reduce uncertainty at a cost:

- **gift-first**, send product, observe whether the resulting post drives real
  engagement, before committing to a paid contract.
- **request-analytics**, ask the influencer for platform-native audience data.
  Costs time, and refusal is itself evidence.

This is the "information is not free" idea from Week 1 applied to a real decision.

---

## 4. Draft hidden states *(to be finalised in M2)*

The agent cannot observe which of these is true:

| ID | Hidden state | What it means |
|----|--------------|---------------|
| H1 | **Genuine fit** | Real, engaged audience that matches the brand's demographic and price point |
| H2 | **Low audience authenticity** | A large share of the audience is inauthentic or inactive, bots, purchased followers, or pod-driven engagement |
| H3 | **Authentic but mismatched** | Real engaged audience, wrong demographic / price point / aesthetic for a premium house |
| H4 | **Latent brand-safety risk** | Real and matched, but past controversy or undisclosed-ad history that can surface after signing |

**Terminology note.** H2 is deliberately framed as a property of the *audience*, not
an accusation of intent against the influencer. "Fraud" is a claim about intent, and
nothing the agent observes identifies intent: inauthentic followers accrue passively
to popular accounts, are sold by agencies without the influencer's knowledge, or come
from engagement pods that are normalised in some markets. A hidden state that cannot
be estimated from the available evidence makes the Bayesian update meaningless, so the
state is defined as measurable audience quality instead. This also removes a real
deployment harm: an agent that labels a named person "fraudulent" is defamation-shaped
and unsafe to ship.

The agent's output is a **brand-side partnership decision**, never a verdict on a
person. `A5` means "not a fit for this campaign," not "this person is dishonest."

Beliefs over H1–H4 must sum to 100%.

**Known simplification:** these are treated as mutually exclusive, but in reality an
influencer can be both inflated *and* mismatched. A factorised model (three
independent binary latents: authentic? matched? safe?) would be more correct and
gives 8 joint states. Starting with 4 exclusive states per the spec's instruction to
"build the smallest version that you can test." Recorded here as a limitation.

---

## 5. Draft action set *(to be finalised in M2)*

| ID | Action | Reversible? | Cost profile |
|----|--------|-------------|--------------|
| A1 | **Sign**, full paid contract | No | Highest exposure |
| A2 | **Gift-first**, seeded product, observe outcome | Yes | Low cost, buys evidence |
| A3 | **Request-analytics**, ask for platform audience data | Yes | Time cost; refusal is evidence |
| A4 | **Escalate**, route to human brand manager | Yes | Human-review cost |
| A5 | **Reject** | Effectively yes | Opportunity cost only |

**Key asymmetry to test:** in this market the supply of influencers is large, so a
false negative (rejecting a good fit) is *cheap*, you simply approach someone else.
A false positive on H4 (signing a latent brand-safety risk) may be the most expensive
outcome available to a luxury brand. If that holds, the optimal policy should be
markedly conservative, and a naive accuracy-maximising baseline should lose badly on
cost. This is the central hypothesis of the experiment.

---

## 6. Fragile assumptions, the targets for Reddit / X questions

These are the things I would be embarrassed to defend, and therefore the things worth
asking humans about in M1:

1. **Base rate of inflated accounts.** Vendor studies claim ~37% of followers are fake
   on the average account, and 42%+ of influencers have at least a third fake. Every
   one of those sources sells fraud detection, so they have an interest in a high
   number. Treated as an upper bound. Needs a practitioner estimate.
2. **Wrong quantity.** Those studies measure *fraction of followers that are fake*.
   My prior needs *fraction of influencers who are frauds*. These are different
   numbers and conflating them is exactly the base-rate error from Chapter 2.
3. **Is H2 even the dominant failure?** I have assumed fake engagement is the main
   risk. It may be that mismatch (H3) or controversy (H4) is what actually kills
   luxury partnerships.
4. **Is gift-first real?** I have assumed brands de-risk by seeding product before
   paying. This may be naive or may not apply at luxury tier.
5. **Which error actually costs more**, paying a fraud, or passing on someone who
   would have converted?

---

## 7. Technical terms

*Pending, M1.*

## 8. Search queries

*Pending, M1.*

## 9. Verified Reddit communities

*Pending, M1. Five to ten, each with a stated reason for relevance.*

## 10. X accounts

*Pending, M1. Fifteen to twenty-five: researchers, engineers, practitioners, critics.*

## 11. Sources read

*Pending, M1. Five papers, articles, repositories, or datasets that I have actually
read, not merely found.*

## 12. Questions I want answered

*Pending, M1.*

## 13. AI prompt log and AI errors caught

*Maintained continuously from M1 onward. Records prompts used and any case where an
AI tool gave me something wrong, unverifiable, or fabricated.*
