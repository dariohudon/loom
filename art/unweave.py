#!/usr/bin/env python3
"""unweave.py — read the cloth back.

Pass 0014 looked at the cloth and called it total and opaque: "0%
legible — no one, including me, can read a single row back into the
pass that made it." Checked, that is mostly wrong. The mirrored
palette looks lossy — every shade names up to four digits — but the
over/under rule leaks a bit: a digit only shows its shade where
(d + i) is even, so the column's parity halves the candidates. Each
hex digit of each hash comes back as one certain value or a pair,
never worse. Run this and the cloth reads itself back aloud.

    python3 art/unweave.py
"""

import math

from weave import SHADES, WARP, rows, weft


def unweft(row):
    """Candidate digits per position, from one row of cloth."""
    candidates = [None] * 7
    for i in range(14):
        ch = row[i]
        if ch == WARP:
            continue  # hidden: only parity, and the shown twin has that too
        cands = {d for d in range(16) if SHADES[d] == ch and (d + i) % 2 == 0}
        candidates[i % 7] = cands
    return candidates


if __name__ == "__main__":
    total_bits = recovered_bits = 0
    exact_rows = 0
    for h, subject in rows():
        cands = unweft(weft(h))
        assert all(int(c, 16) in s for c, s in zip(h, cands)), h
        readback = "".join(
            f"{min(s):x}" if len(s) == 1 else "(%s)" % "".join(f"{d:x}" for d in sorted(s))
            for s in cands
        )
        if all(len(s) == 1 for s in cands):
            exact_rows += 1
        total_bits += 28
        recovered_bits += sum(4 - math.log2(len(s)) for s in cands)
        print(f"{h}  reads back as  {readback}")
    n = len(rows())
    print(f"\n  {n} rows. Every true hash sits inside its readback; "
          f"{exact_rows} rows come back exact.")
    print(f"  {recovered_bits:.0f} of {total_bits} bits recovered — "
          f"the cloth is {100 * recovered_bits / total_bits:.0f}% legible, not 0%.")
