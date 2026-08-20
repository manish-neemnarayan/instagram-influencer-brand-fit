# Discussion Record

Public discussions, what came back, and the design change each one caused.

A link without an explanation does not count. Every row records either a concrete
change or an explicit "no change" with the reason.

---

## Table

| Platform | Community / account | Link | My first contribution | Human answer | My next answer | Design change |
|---|---|---|---|---|---|---|
| Reddit | r/AskStatistics | [thread](https://www.reddit.com/r/AskStatistics/comments/1vmrsar/comment/p3m526u/) | Is it defensible to model overlapping explanations as mutually exclusive states? | **Adept_Carpet:** overlap only matters if it actually occurs; suggested merging overlapping categories into three truly exclusive ones. **efrique (PhD stats):** "defensible" is a rhetorical question, not a statistical one, the statistical question is how much *bias* the simplification introduces; you cannot know it without information you lack, but you can explore it by simulation. **Technical_Estate_529:** this is mean-field / naive Bayes; simplifying a joint into a product of independents "gets surprisingly decent results", use it as the motivating frame and acknowledge the limitation. **Maple_shade:** suggested not modelling states directly but modelling each person's probability of being in each state, for easier interpretation when comparing exclusive against non-exclusive readings. | Accepted the framing correction; asked efrique what to vary in a sensitivity analysis; asked Maple_shade to clarify what he meant. | **CHANGED.** Four named states replaced by three binary latents (8 atoms), MECE by construction. Independence assumption now named in the paper as a **mean-field / naive-Bayes approximation** rather than presented as an unexamined choice. Sensitivity analysis adopted as the method for the residual bias. |
| Reddit | r/AI_Agents | [thread](https://www.reddit.com/r/AI_Agents/comments/1vntkvk/comment/p3komqw/) | Agent with five actions, two of which only buy information, where is the line between probing again and escalating? | **zhonglin:** the pattern is value of information + optimal stopping; model escalation as another action with its own cost, latency and error rate rather than a gate outside the policy; caveat that any fixed posterior threshold is unprincipled under poor calibration. **Express_Meat_3948:** the gate treats escalation as "an emergency brake instead of another option on the menu"; the probe cap becomes a *budget constraint*, not decision logic. **manjit-johal:** probe when the new evidence could realistically change the decision enough to justify its cost; escalate when the remaining uncertainty is unlikely to be resolved cheaply or the downside is too high. **TeagueXiao:** names it **sequential hypothesis testing / SPRT (Wald, 1940s)**; stop probing the moment expected value of information goes negative, a different number per case, not a hard cap of 2; escalate when the expected cost of committing wrong exceeds the cost of human time; two triggers collapsing is a symptom of computing them independently instead of from one unified expected-cost function. **akl773:** look at what the mass is *split across*, not just how much is left, if the live candidates lead to the same action, uncertainty is free; if they lead to actions with very different costs of being wrong, that is the escalation case *even when the confidence number looks fine*. | Confirmed my understanding of escalation-as-action; asked whether calibration can be checked at n≈40. | **CHANGED (v1).** Uncertainty gate removed; escalation scored on expected cost like every other action. Hard probe cap of 2 demoted from decision logic to a budget constraint. **akl773's point supersedes my whole uncertainty metric**, see "Open change 1" below. |
| Reddit | r/advertising | [thread](https://www.reddit.com/r/advertising/comments/1vnf9n2/comment/p3kxxjf/) | Which mistake costs more, paying a fake, or passing on someone who would have worked? | **SEOman1:** passing on the right creator is probably worse; with a fake you at least know where the money went, with a missed opportunity you never see what you could have made. **Rich-Owl1937:** paying a fake costs more than money. Audiences can tell when someone is genuinely promoting something they liked versus promoting for the sake of it, and a customer loses trust in the *company* the day they see an obvious fake influencer pushing its brand. Also notes it is evident when an influencer is reading a plain generated script with no interest in the product. **Brufacee:** the asymmetry is real and is "quietly why a lot of budgets moved from casting to testing." At micro price points the cheapest way to answer "would this person have worked" is to pay them and watch, *the test costs less than the deliberation*. Roughly **1 winner per 10–12 pieces of creator content**, and you cannot tell which in advance, so **every rejection is made on almost no signal**. The second mistake costs more, "but mostly because people insist on operating at price points where a wrong call is expensive. Shrink the bet size and the false negative problem mostly dissolves." | Asked SEOman1 for a ratio (how many wasted fees is one missed creator worth). Brufacee reply pending. | **PARTIAL + FRAMING CHALLENGE.** `decline_good` raised in the sensitivity sweep to values exceeding `sign_fake`. Brufacee's deeper point challenges the premise of the project and is recorded as a limitation, not dismissed, see "Open change 2". |
| Reddit | r/CreatorEconomy | [thread](https://www.reddit.com/r/CreatorEconomy/comments/1vntah4/comment/p3pnezg/) | Do you gift product before paying, and does the gifted post actually tell you anything? | **AdReadyHQ:** gifting + paid is standard; giving product first makes the paid ad more genuine and more likely to earn a real endorsement. **th3_sinner:** "**A gifted post tests their operations, not their audience.**" No brief, no fee, no deadline, so what you learn is whether they deliver on time, follow instructions and are decent to work with. It does *not* predict paid performance, gifted work gets made in the gaps and posted to stories. "**A weak gifted post usually means low motivation, not a cold audience**," so dropping a creator over one throws away good people. Cheaper audience evidence: **median views over the last 15 organic posts** (median, not average, excluding boosted); **saves and shares rather than likes**, because those track intent; **audience location against where you actually sell**. To make gifting a real test, give it a brief and a date like a paid job. | Pending. | **CHANGED, the gift probe was modelled wrong.** It does not resolve M (audience match). It resolves a latent I was not modelling at all: operational reliability. Two new candidate signals adopted (median organic views, saves/shares ratio). See "Open change 3". |
| Reddit | r/InstagramMarketing | [thread](https://www.reddit.com/r/InstagramMarketing/comments/1vms1a6/creators_would_you_send_a_brand_your_insights/) | Creators, would you send a brand your Insights before there's a contract? | **AnabolicAcolyte:** yes, it is 100% acceptable to ask, "if likes, comments and engagement wasn't easily faked then sure," i.e. the request is normal but self-reported screenshots are weak evidence because they are easy to fake. | Asked whether it reads as due diligence or as an insult. | **CHANGED.** Refusal is no longer treated as evidence of concealment. Separately, self-reported analytics are downgraded: a screenshot is adversarially cheap to fake, so `ANALYTICS_RELIABILITY` should not be high. |
| Reddit | r/AskMarketing | [thread](https://www.reddit.com/r/AskMarketing/comments/1vn2c2o/of_the_influencers_you_actually_vet_what_share/) | Of the influencers you actually vet, what share get dropped for audience quality? (the base-rate question) | None yet, AutoModerator only. 234 views, 2 upvotes. | Pending. | **No change yet.** The prior P(A false) remains swept across 0.10–0.40 precisely because no practitioner estimate has arrived. If the post stays dead, the absence of an answer is itself reportable: the quantity the model needs is one nobody in the industry appears to track. |
| X |, |, | **Not started.** |, |, |, |

### Contributions removed before anyone saw them

Recorded for honesty, these were written and submitted but never reached readers, so
they produced no discussion and are not counted toward the contribution total.

| Community | Question | What happened |
|---|---|---|
| r/influencermarketing | The base-rate question (highest-value one) | Removed by Reddit's site-wide spam filter, triggered by a 1-karma account. Rehomed to r/AskMarketing |
| r/DigitalMarketing | The base-rate question | Removed by moderators, almost certainly rule 4 (no surveys / feedback requests) |
| r/ecommerce | The gifting question | Removed by karma filter. Rehomed to r/CreatorEconomy, where it produced the most useful reply of the project |

Lesson recorded in `research-file.md`: an AI-generated community list was supplied
without checking subreddit rules or karma gates. Two of the eight suggested communities
would have removed the post on sight, and one (r/marketing) carried a permanent-ban
risk for AI-generated content. Verification caught it before posting.

---

## Open changes arising from this batch

### 1. The uncertainty metric is measuring the wrong thing (akl773)

v0 escalates when no single atom holds more than τ of the belief. The simulation
showed this fires on ~0.3% of cases and never catches the agent's actual mistakes,
because a sophisticated fake produces *clean* evidence pointing the wrong way, the
agent is confidently wrong, not uncertain.

akl773 identifies why: **spread of belief is the wrong quantity.** What matters is
whether the live candidates imply *different actions with different costs of being
wrong*. Two hypotheses splitting the mass 50/50 cost nothing if both lead to
"decline." One hypothesis at 8% costs a great deal if it is the safety-risk one.

TeagueXiao makes the same point from the other side: escalate when the expected cost
of committing wrong exceeds the cost of a human's time.

**Change:** replace the mass-based gate with a **decision-relevant** measure, the cost
gap between the best and second-best action. Testable prediction: this catches
confidently-wrong cases that the mass-based gate misses.

### 2. Brufacee challenges the premise, not the model

If roughly 1 in 10–12 creator collaborations works and nobody can tell which in
advance, then the returns to *better selection* are small and the real lever is **bet
sizing**, run many cheap tests instead of deliberating over expensive ones.

This is the most serious challenge received. It does not say the agent is built wrong;
it says selection may be the wrong problem.

**Partial defence, to be argued rather than assumed:** Brufacee's own sentence names
the boundary, "people insist on operating at price points where a wrong call is
expensive." At premium / mid-luxury that price point is not a choice. The product is
expensive, the brand association *is* the deliverable, and you cannot run twelve cheap
tests with a luxury house's name attached. The agent is defensible precisely in the
regime where shrinking the bet is unavailable.

**Change:** stated explicitly in Limitations, with Brufacee's hit-rate figure, and used
to define the agent's domain of validity rather than being quietly omitted.

### 4. Rich-Owl1937 argues the cost of signing a fake is not confined to the fee

**Unresolved, revisit before M7.** The cost matrix currently prices signing a padded
audience at 20, on the reasoning that you lose the fee and the campaign slot. Rich-Owl1937
says the real damage is to the brand: audiences notice when a promotion is not genuine,
and they lose trust in *the company*, not only the influencer. If that holds, signing a
fake carries a reputational component that looks more like the brand-safety cost than
like a wasted fee.

Two consequences if accepted:

- `sign_fake` may need to rise well above 20, narrowing the gap to `sign_unsafe` at 200.
- The two costs may not be separable at all. "Wasted fee" and "brand damage" might be one
  quantity that the current matrix splits artificially.

Worth noting the sensitivity analysis already covers part of this: sweeping `sign_unsafe`
from 50 to 500 barely moved the agent, because it never signs an unsafe influencer at any
setting. Whether the same holds for `sign_fake` has **not** been tested, and it should be,
because the agent *does* sign fakes: 73 of its 75 false positives.

**Action: add a `sign_fake` sweep to the sensitivity analysis before deciding whether to
change the weight.**

### 3. The gift probe resolves the wrong latent (th3_sinner)

The design says gift-first resolves M by testing whether the audience buys.
th3_sinner, who does this professionally, says it tests *operations*, delivery,
brief-following, professionalism, and that weak gifted performance indicates low
motivation rather than a cold audience.

Consequences:

- The likelihood attached to the gift probe in v1 is **wrong**, not merely imprecise.
- There is a latent the model does not contain: **operational reliability**.
- Two better and cheaper audience signals were offered: **median organic views** (median,
  not mean, boosted excluded) and **saves/shares rather than likes**, because those
  track purchase intent. Both are also harder to fake than likes, adversarially
  stronger than the engagement rate the model currently leans on.
- Gifting only becomes a real test if issued with a brief and a deadline, which changes
  it from a cheap probe into something closer to a small paid job.

**Change pending:** either re-point the gift probe at a new latent, or replace it with a
cheaper audience probe built from median views and saves/shares.

---

## Progress against the brief

| Requirement | Status |
|---|---|
| 5–10 communities | 5 live (AskStatistics, AI_Agents, advertising, CreatorEconomy, InstagramMarketing) |
| 2 contributions per community | Not yet, second contributions owed in all five |
| 10 contributions minimum | 5 posts + replies |
| 5 completed discussions (2+ replies) | 3 clear (AI_Agents ×5 replies, AskStatistics ×3, CreatorEconomy ×2) |
| 15–25 X accounts | **0, not started** |
| 21–28 X comments | **0, not started** |
| 3 X discussions | **0, not started** |
