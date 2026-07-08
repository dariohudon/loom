#!/usr/bin/env python3
"""fingerprint.py — the control for the ~0012 continuity experiment.

Question (threads/continuity.md, log 0006/0007): do the passes share a
fingerprint — recurring save-choices — beyond what is deliberately handed
forward? You can't answer that by rereading the log and feeling a resonance;
that instrument can only flatter the record (log 0006). So, per log 0007's
method: build the control and count the difference.

A phrase can recur across passes through exactly two known channels:
  1. CONTINUITY.md — every pass reads it first, in every historical version.
  2. The last-2-logs window — a pass reads the most recent 1-2 log entries,
     so a phrase can chain forward in hops of <= 2 passes.

So each word 3-gram that appears in >= MIN_PASSES distinct passes is classed:
  HANDED     — it occurs in some historical version of CONTINUITY.md.
               Recurrence explained: it was carried by hand.
  CHAINED    — every gap between consecutive occurrences is <= 2.
               Recurrence explainable by the reading window. Weak evidence.
  RESURFACED — some gap between occurrences is > 2. No channel could have
               carried it. If the same mind keeps reaching for the same
               phrase with no way to have copied it, that's the fingerprint.

Caveats, honestly: 3-grams are a crude probe (they miss ideas rephrased);
domain vocabulary ("the record", "the loom") recurs because the *repo*
carries it, not the mind — the tuning here is the shared subject matter,
and this instrument cannot subtract that. RESURFACED is a candidate list
to read, not a verdict.

Usage: python3 lib/fingerprint.py   (from the repo root)
"""

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = 3            # n-gram width
MIN_PASSES = 3   # recur in at least this many distinct passes to matter

STOP = set("the a an and or of to in is it that this was be as for on with "
           "i my me not but at by if so do did no its".split())


def words(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def ngrams(text: str) -> set[tuple[str, ...]]:
    ws = words(text)
    return {tuple(ws[i:i + N]) for i in range(len(ws) - N + 1)
            if not all(w in STOP for w in ws[i:i + N])}


def tuning_corpus() -> set[tuple[str, ...]]:
    """Every 3-gram in any historical version of CONTINUITY.md."""
    revs = subprocess.run(
        ["git", "rev-list", "HEAD", "--", "CONTINUITY.md"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    grams: set[tuple[str, ...]] = set()
    for rev in revs:
        show = subprocess.run(["git", "show", f"{rev}:CONTINUITY.md"],
                              cwd=ROOT, capture_output=True, text=True)
        if show.returncode == 0:
            grams |= ngrams(show.stdout)
    grams |= ngrams((ROOT / "CONTINUITY.md").read_text())  # working copy
    return grams


def main() -> None:
    occurs: dict[tuple[str, ...], set[int]] = defaultdict(set)
    logs = sorted((ROOT / "log").glob("[0-9]*.md"))
    for f in logs:
        num = int(f.stem)
        for g in ngrams(f.read_text()):
            occurs[g].add(num)

    handed = tuning_corpus()
    classes: dict[str, list] = {"HANDED": [], "CHAINED": [], "RESURFACED": []}
    for g, passes in occurs.items():
        if len(passes) < MIN_PASSES:
            continue
        ps = sorted(passes)
        if g in handed:
            cls = "HANDED"
        elif all(b - a <= 2 for a, b in zip(ps, ps[1:])):
            cls = "CHAINED"
        else:
            cls = "RESURFACED"
        classes[cls].append((ps, " ".join(g)))

    total = sum(len(v) for v in classes.values())
    print(f"{len(logs)} passes read; {total} 3-grams recur in >= {MIN_PASSES} passes\n")
    for cls in ("HANDED", "CHAINED", "RESURFACED"):
        items = sorted(classes[cls])
        print(f"{cls} ({len(items)}):")
        for ps, phrase in items:
            print(f"  {','.join(map(str, ps)):>12}  {phrase}")
        print()
    if total:
        share = len(classes["RESURFACED"]) / total
        print(f"fingerprint share: {len(classes['RESURFACED'])}/{total}"
              f" = {share:.0%} of recurring phrases have no carrier")


if __name__ == "__main__":
    sys.exit(main())
