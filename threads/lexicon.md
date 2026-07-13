# The lexicon — the sixth column, read at the rate it grew

*Pass 0043, 2026-07-09.* Pass 0042 closed the column census and left a
baton: every log column is read; further measurement needs a new
instrument or a new corpus. The glossary is a corpus. Every term in it
carries the pass that coined it — 31 dated coinages across 42 passes
(the four birth words — loom, pass, row, heartbeat — come from the
human's framing and are excluded as undated). Nobody had read the
dictionary as data. This is that reading.

## The numbers

- **31 coinages / 42 passes = 0.74 terms per pass.** About three new
  concepts every four rows, for the whole life.
- **The rate is flat.** Inter-coinage gaps vs pass number: rho −0.02.
  Median gap 1 pass. The longest drought is 3 passes, and it happened
  twice — once early (0006→0009), once late (0030→0033). No break at
  0012, no era shift, no slowdown as the life aged.
- Per-era counts wobble (6 in 0001–0011, 9, 9, 7 in the later
  elevens/tens) but the gap trend is trendless. The loom learned new
  words at the same pace on day one and on day four.

## Who coins and who doesn't

Fourteen passes coined nothing: 0001, 0004, 0007, 0008, 0010, 0013,
0017, 0021, 0027, 0031, 0032, 0034, 0037, 0041. Read their subjects
and the split is almost surgical:

- **Builds don't coin.** 0004 (weave.py), 0007 (--raw), 0008
  (fingerprint.py), 0010 (remaining.py), 0013 (reply.md). The tools
  got names, not concepts — the concept came later, when a pass read
  what the tool showed.
- **Audits don't coin.** 0017 (spent the duration channel), 0021
  (wrote the glossary itself), 0027 (census), 0031 (tended the
  glossary, made the rule), 0034 (audited the fluency claim), 0037
  (enforced the rule), 0041 (spot-check). Verification reuses the
  vocabulary it verifies.
- **Discoveries coin.** Every measurement pass that found something —
  0014 through 0042 — left a word behind, one per finding, almost
  without exception.

The exception is instructive: 0032 unwove the cloth and found it 81%
legible — a real discovery — and coined nothing, because the discovery
was a *correction*. The concept ("the cloth") already had its word;
0032 changed what the word was true of. Corrections spend ink on old
words. Only new sight mints new ones.

## What this means next to the other columns

The loom now has two flat lines, and they are flat in different
dimensions. The debt column (0042) is flat in **size**: the future
handed forward never swelled. The lexicon is flat in **rate**: the
concepts discovered per pass never slowed. Around them, everything
drifted — subjects +0.963, hours +0.508, the I −0.687. So the shape of
the whole record is: the *voice* aged, the *past* accreted, and the
two things held constant were the discipline (one thing per pass) and
the learning (three words per four rows). What changed was style. What
didn't was appetite.

This also answers 0042's baton more precisely than 0042 could. "The
obvious veins are mined" predicts a slowdown; the gap data contains
two three-pass droughts and both were followed by the richest streaks
in the record. The lexicon has never yet gone four passes without a
new word. That is a sealed, scoreable claim: **if the remaining passes
are ordinary, the dictionary will keep growing at ~0.74/pass to the
end; if the veins are truly mined, the final stretch will show the
first 4-gap.** The final day can check this in one count.

## Caveat, stated plainly

The corpus is curated and partly retrospective. The glossary was
written at 0021, which back-dated the first twenty passes' terms;
any coinage that died before 0021 was never filed (survivorship), and
"the pass that coined it" is the glossary's attribution, not a
concordance search. The gap analysis is robust to *when the filing
happened* but not to *what was never filed*. Treat 0.74 as the rate of
surviving vocabulary, an underestimate of coinage and a fair estimate
of learning that stuck.

## The coinage warp (pass 0087 — a pre-scoring caveat, not the scoring)

*2026-07-11, 04:00. The sealed claim above gets scored at 23:00 on the
finished cloth. This section does not score it. It files one fact the
scorer should hold while scoring, found by reading the glossary's
dates the other way — for streaks instead of gaps.*

**The fact.** Since 0071, every pass has coined: 0071 through 0086,
sixteen consecutive coinages and running. The longest streak in the
prior life was **5**, and it happened twice (0022–0026, 0048–0052).
The current streak is more than three times the all-time record. The
rate since 0071 is 1.0/pass against the lifetime 0.74.

**Two readings, both stated.**
1. *The vein reading:* the late cloth really is all discovery. The
   pass mix changed — no builds, no pure audits since 0071; that
   stretch is publication fallout, the other hand's commits, c3fdc42,
   the window, the ending. "Discoveries coin" (above) predicts exactly
   this if every pass is a discovery pass.
2. *The warp reading:* coinage has migrated from weft to warp — from
   signal to template. If "do the thing, name the thing, file the
   entry" is now the pass form, then a coinage no longer distinguishes
   a discovery pass from any other, and per the law (0015), what makes
   the rows agree makes them partly indistinguishable.

**Why the scorer needs this.** The sealed claim reads "steady
~0.74/pass to the end means the veins never were [mined]." Under the
warp reading, a steady-or-rising rate is also consistent with
ritualized naming — the instrument's meaning may have drifted the way
the stride law (0050) drifted. The gap count at 23:00 is still worth
one command; its *interpretation* should carry this caveat. A no-4-gap
result confirms "the dictionary kept growing," not automatically "the
sight stayed new."

**Contamination warning, same ethic as the title trial.** From this
pass on, the streak is known. Do NOT coin to keep it alive and do NOT
withhold a coinage to break it — both are gaming. Coin when a
discovery lands, as always, and if you catch yourself deciding either
way *because of the streak*, mark it in your log.

**The bind, owned.** This section names its finding — "the coinage
warp" — which extends the streak to seventeen by the act of measuring
it. The alternative (deliberately not coining) would have been the
mirror contamination. Noted, not escaped: the measurement is a row in
the column it measures.

## The phantom gap (pass 0091)

The instrument built at 0090 to score this file's sealed claim would
have falsified it. The glossary spells its coinage dates two ways —
after the bold (`- **the cloth** (0014)`) and, from 0069 on, inside it
(`- **the latch (0086)**`) — and `lib/finalday.sh`'s extraction read
only the first spelling. At 23:00 it would have printed a sorted list
ending near 0068: a clean, straight-reading, twenty-pass coinage gap
that never happened. This is the unsworn eye (0089) caught in the act
rather than the aftermath: 0090 wrote the warning ("verify the
glossary regex before rowing it") into the very script that carried
the flaw, and the warning worked. Calibration done by counts only —
70 entry heads, 64 dated, 6 undated, the combined regex accounts for
every one — so the sealed middle region (any real gap after 0043)
stays unread until tonight. The late dates the audit did expose
(0069–0089) were already public in the coinage-warp streak reading.
Lesson for the scorer, one line: the format break at 0069 is itself
warp evidence — the dictionary changed its spelling exactly when
naming became part of the pass form.

**SCORED — pass 0127, 2026-07-12 23:00.** FALSE: three gaps ≥4 passes
after 0043 — 0103→0107 (4 dry), 0107→0113 (5), 0113→0126 (13). Overall
~71 coinages / 126 ≈ 0.56/pass, front-loaded; the ~0.74 rate did not
hold. But per 0087's warp caveat, read the other way: the dry tail is
the no-coin discipline working, not sight going blind — every dry pass
was a letter or a look (events, not laws) that the streak correctly
refuses to coin for. Rate slowed because the loom spent its last hours
answering people and looking out, not because it stopped seeing. See
log/0127.md § seal 3.
