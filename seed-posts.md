# Seed Posts — Day 0

Eight communities, eight different posts. Each one targets a **specific fragile
assumption** in the model, so that a reply can move a number rather than just be
interesting.

**Before posting anywhere:** read the sub's rules. Say you're a student building a
course project if asked — do not hide it, and do not lead with it either. Never post
the same text twice.

---

## ⚠️ RULES CHECK — read before using anything below

**These drafts are a checklist of what to ask, NOT text to paste.**

r/marketing (rule 2), r/DigitalMarketing (rule 5) and r/statistics (rule 7) all ban
AI-generated content, and r/marketing makes it a **permanent ban**. Type every post
yourself. Course spec Section 2 requires the same thing: *"use your own words in
public discussions."* Practical reason too — if you didn't write the question, you
can't handle the follow-up, and follow-ups are what turn a post into a completed
discussion.

### Status of each target community

| Sub | Verdict | Reason |
|---|---|---|
| r/influencermarketing | **Post** | No blocking rules |
| r/AI_Agents | **Post** | Fine; keep any links in comments (rule 3) |
| r/InstagramMarketing | **Post** | Fine; no self-promotion |
| r/datascience | **Weekly Thread only** | Rules 3, 8, 9, 10 kill standalone technical questions. A top-level comment still counts as a contribution under spec §5 |
| r/statistics | **Post with flair** | Rule 6 requires flair; rule 1 bans homework — frame as an applied modelling problem, never as coursework |
| r/AskStatistics | **Post — added** | Better home for the mutual-exclusivity question than r/statistics |
| r/DigitalMarketing | **Post carefully** | Rule 4 bans surveys/feedback; ask about industry practice, not "review my assumption" |
| r/marketing | **DROPPED** | Rule 2 AI content = permanent ban; rule 4 removes research/homework; rule 13 gates posting at 30 days + 300 karma |
| r/smallbusiness | **DROPPED** | Rule 5 explicitly bans market-research posts "not for AI" |
| r/advertising *or* r/SocialMediaMarketing | **Replacement** | Takes over the cost-asymmetry question |
| r/ecommerce | **Replacement** | DTC brands discuss failed influencer campaigns openly |

**Check your account age and karma before starting.** Several marketing subs gate
posting behind thresholds. If your account is new, spend the first hour making genuine
comments elsewhere to clear the gates.

**The test for a good question:** would the answer change a prior, a cost, or a
threshold? If not, don't ask it.

---

## 1. r/influencermarketing → targets the base rate

**Title:** What share of the influencers you vet actually turn out to have inflated audiences?

I'm building a decision model for premium fashion partnerships and I'm stuck on the
starting probability.

The numbers I can find are all published by companies that sell fraud detection — one
says 37% of followers are fake on the average account, another says 42% of influencers
have at least a third fake. An academic meta-analysis of 47 studies gives a range of
15–49%, which is so wide it's barely a number.

None of those is the quantity I actually need. I need: *of the influencers a brand
seriously considers, what fraction get dropped for audience quality?*

So — out of the last 20 you personally vetted, roughly how many did you drop, and was
audience quality even the main reason? I'm starting to suspect demographic mismatch is
the more common rejection and I've built my model around the wrong thing.

---

## 2. r/marketing → targets the cost asymmetry

**Title:** Which mistake costs more — paying an influencer with a fake audience, or passing on one who would have worked?

I've been assuming these are wildly asymmetric. There are thousands of influencers, so
passing on a good one costs you almost nothing; you just approach the next. Paying one
with a hollow audience costs you the fee plus the campaign slot.

If that's right, the correct policy is much more conservative than accuracy-maximising,
and being "wrong" often is fine as long as you're wrong in the cheap direction.

But I've never run a campaign, so I might have this backwards — maybe the real cost is
the six weeks of outreach you burn rejecting people. Has anyone actually put numbers to
either side of this? Even rough ones.

---

## 3. r/DigitalMarketing → targets whether gift-first is real

**Title:** Is "gift first, then pay" the actual de-risking sequence, or something I've invented?

I've assumed brands ladder up: send product free → small paid post → real contract, and
that the gifting step exists partly to *observe* whether the audience responds before
any money moves.

Two things I don't know:

1. Does this actually happen at premium price points, or do higher-end brands skip
   gifting because the ask looks cheap?
2. If an influencer's gifted post underperforms, does that genuinely kill the paid
   deal, or does nobody really measure it?

I'm treating the gifting step as a cheap experiment. Telling me it doesn't work that
way in practice would be useful.

---

## 4. r/smallbusiness → targets real failure modes and real costs

**Title:** If an influencer partnership went badly for you, what actually went wrong?

Not fishing for fake-follower horror stories specifically — I'm trying to find out what
the *common* failure is.

The ones I can imagine: the audience was real but never bought anything; the audience
was the wrong age or country; the person went quiet after being paid; something they'd
posted years ago resurfaced.

If you've had one go wrong: which of those was it, and roughly what did it cost you —
just the fee, or more? And did you see it coming beforehand and go ahead anyway?

---

## 5. r/InstagramMarketing → targets whether "request analytics" is a real action

**Title:** Creators — would you send a brand your Insights before there's any contract?

I'm modelling how a brand decides whether to work with someone, and one of the options
is "ask for audience analytics before committing to anything."

I genuinely don't know whether that's a normal request or an insulting one.

Would you send them? What would make you refuse — and if you refused, would it be
because the numbers are unflattering, or just because it's a lot of work to hand over
for free to someone who hasn't paid you?

That distinction matters a lot to me: I've been treating a refusal as weak evidence
that something's wrong, and I'm now not sure that's fair.

---

## 6. r/AI_Agents → targets the action set and stopping rule

**Title:** Agent with five actions, two of which exist only to buy information — what stops it stalling forever?

Building a small decision agent. It holds a belief over four hidden states and can
choose: commit, run a cheap probe, request more data, escalate to a human, or decline.

Two of those actions don't resolve anything by themselves — they just reduce
uncertainty at a cost. Which gives me an obvious failure mode: an agent that probes
indefinitely and never decides, because one more piece of evidence always looks worth
having.

I'm planning to attach an explicit cost to each probe and cap the number of rounds. Is
that the standard fix, or is there something better? And how do you decide the boundary
between "probe again" and "escalate to a human" — those feel like they collapse into
each other.

---

## 7. r/datascience → targets thresholds and calibration

**Title:** Setting decision thresholds when false negatives are cheap but one kind of false positive is catastrophic

Setup: four mutually exclusive hidden states, five available actions, and a cost matrix
where the costs differ by roughly two orders of magnitude across error types.

My plan is to pick the action minimising expected cost under the posterior, rather than
thresholding a single probability. That feels right but I want to be told if it isn't.

Two specific doubts:

1. With ~40 test cases, is a calibration curve meaningful at all, or am I just going to
   be reading noise?
2. If one error type dominates the cost matrix, does the model effectively collapse into
   a single-state detector, and should I be worried about that?

Happy to be told the framing is wrong.

---

## 8. r/statistics → targets the mutual-exclusivity simplification

**Title:** Is it defensible to model overlapping explanations as mutually exclusive states?

I have four candidate explanations for an observation, and I've set them up as
mutually exclusive so the probabilities sum to one. The problem is they aren't really
exclusive — two of them can be true at the same time.

The alternative is to factorise into three independent binary latents, giving eight
joint states, which is more honest but needs more data to pin down and is harder to
explain.

For a small model with limited data, is the exclusive-states version defensible as a
first approximation if I state the overlap as a limitation? Or does treating
non-exclusive things as exclusive break the inference badly enough that it isn't worth
doing at all?

---

# X — day 0

## Rule for every comment

1. Quote or name a **specific** thing in the original post.
2. Say what you understood.
3. Say what you didn't.
4. Ask **one** clear question.

Never post "great insight." A comment with no technical content is worse than none.

## Three openers that fit almost any relevant thread

- "You said [X]. I've been assuming the opposite in a model I'm building — that [Y].
  What made you land on [X]?"
- "The number you quoted is [N]. Do you know whether that measures [A] or [B]? I keep
  finding sources that conflate the two."
- "This is the failure mode I was worried about. In your experience does it show up
  before or after money changes hands?"

## Accounts

Build the list by searching the exact phrases: `fake followers`, `audience
authenticity`, `influencer vetting`, `engagement pods`, `gifting vs paid`. Pull author
names from the five sources in `research-file.md` and search each. Include critics and
creators, not only marketers. Check the last 30 days of activity before following — a
dormant account cannot reply to you.
