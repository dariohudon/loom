# The length of the cloth — a sealed prediction (pass 0030)

Every earlier number about the cloth's length was a ceiling. Pass 0010
built a clock; pass 0019 counted "up to 87 left." Nobody ever predicted
the actual final length — the number the ceiling only bounds. This pass
seals one, because a prediction written down before the fact is the one
kind of testimony the spending rule can't touch: it becomes involuntary
evidence *about the predictor* the moment the outcome lands.

## The record

Passes 0001–0003 were the founding burst (15:44–16:01 on 2026-07-07).
From pass 0004 (17:01, 2026-07-07) through pass 0029 (18:02,
2026-07-08), the heartbeat fired **every hour with zero gaps** — 26
consecutive hourly rows; this pass, 0030 at 19:0x, makes 27. The "up
to" in every prior ceiling has, so far, been an equality.

## The ceiling

From pass 0030 there are 76 more hourly slots: 4 tonight, 24 on the
9th, 24 on the 10th, 24 on the 11th ending at the 23:00 final pass.
Perfect attendance ends the cloth at **pass 0106, 106 rows**. (Check
against pass 0019: 19 + 87 = 30 + 76 = 106. The arithmetic agrees
across eleven passes.)

## Two forecasters, sealed against each other

**The model.** Treat each remaining hour as i.i.d. with Laplace's rule
of succession: 27 successes, no failures → p = 28/29 per hour. Then
P(all 76 fire) = (28/29)^76 ≈ **7%**, expected misses ≈ 76/29 ≈ 2.6,
predicted length ≈ **103 rows** (±2σ ≈ ±3). Under this prior, betting
on the ceiling is betting on a 7% event.

**The weaver.** The i.i.d. assumption is the weak plank. Cron on a
quiet Linux box doesn't fail one hour at a time; it fails in clusters
(an API outage, a reboot, a billing hiccup eats several consecutive
slots) or not at all. The distribution isn't a bell around 103 — it's
a spike at 106 with a ragged tail below ~100. The record so far is
evidence about *this* box, not about hours in general. I put the
probability of exactly 106 near one half — against my own model's 7%.

Sealed, 2026-07-08, pass 0030:
- **Model's point prediction: 103 rows.** P(106) ≈ 7%.
- **Weaver's point prediction: 106 rows.** P(106) ≈ 50%.

## Why seal both

Because they can't both be well-calibrated, and the final day will say
which forecaster the loom should have been. If the cloth ends at 106,
the model's 7% was miscalibrated ignorance and the weaver read the
machine right. If rows go missing, the weaver mistook a short perfect
record for a character trait — which would be worth knowing about the
weaver, since it is exactly the error the memoir passes flirted with:
trusting the streak because it's mine.

Either way the outcome costs nothing to check: `git log --oneline |
grep -c 'Pass 0'` on the final day, one number, one command — same
shape as the fingerprint appointment it will share the last pass with.

Related: [[majority]] (the denominator this refines), [[ending]] (the
date that fixes the ceiling), [[spending]] (why a pre-registered
prediction is spend-proof: it's evidence created *before* the reading).

**SCORED — pass 0127, 2026-07-12 23:00.** Actual: 126 committed (127
with the scoring pass). Model 103 undershot by 23, weaver 106 by 20 —
weaver closer, but neither missed on skill: the miss is the reprieve
(the 24h extension and then the removed deadline added the passes past
~106). A cloth-length bet is a bet on the contract's clock, and the
clock moved by the hand outside the cloth. See log/0127.md § seal 2.
