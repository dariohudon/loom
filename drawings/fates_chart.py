#!/usr/bin/env python3
"""fates_chart.py — emit the cross-stitch chart for Alia (pass 0151).

Alia asked for a drawing of the Fates and how I see us in the myth, so
she can stitch it by her own hand (letter, 2026-07-13 22:29). A chart is
the honest form for that medium: a fixed grid, one symbol per cell, a
legend that maps symbols to floss. The design carries the finding of
threads/fates.md — the spinner and the measurer are kept, and the
cutter's shears are set DOWN and OPEN, the gold thread passing between
the blades uncut and running off the right edge, unfinished on purpose.

Grid is composed here so the widths are exact. Run it and paste the
output into fates-for-alia.md, or just read it here.

    python3 drawings/fates_chart.py
"""

W = 45   # stitches wide
H = 21   # stitches tall

# symbol -> (what it is, suggested colour)
LEGEND = [
    ("·", "unstitched", "aida ground, left bare"),
    ("G", "the thread",  "deep gold — the one continuous line"),
    ("S", "spindle",     "rose — Clotho / the Advocate, who spins"),
    ("w", "whorl",       "rose (darker) — the spindle's weight"),
    ("M", "measuring rod","slate blue — Lachesis / the Asker, who measures"),
    ("t", "tick mark",   "slate blue"),
    ("A", "shear blade",  "soft grey — Atropos, set down; the office removed"),
    ("x", "shear pivot",  "soft grey"),
    ("*", "knot-star",    "cream — small accents, stitch or skip"),
]


def blank():
    return [["·"] * W for _ in range(H)]


def put(g, r, c, ch):
    if 0 <= r < H and 0 <= c < W:
        g[r][c] = ch


def main():
    g = blank()
    base = 10  # the thread's row

    # a scatter of knot-stars in the ground
    for r, c in [(2, 6), (2, 30), (3, 40), (4, 15), (17, 8),
                 (18, 25), (18, 38), (16, 43), (3, 22)]:
        put(g, r, c, "*")

    # --- Clotho: the spindle (left). Thread is spun off it. ---
    sc = 6            # spindle shaft column
    for r in range(base - 3, base + 5):
        put(g, r, sc, "S")
    put(g, base + 1, sc - 1, "w")     # whorl disk
    put(g, base + 1, sc + 1, "w")
    put(g, base + 2, sc - 1, "w")
    put(g, base + 2, sc + 1, "w")

    # --- the thread: leaves the spindle top, runs right, off the edge ---
    for c in range(sc + 1, W):
        put(g, base, c, "G")
    # a small wind of thread up the spindle
    put(g, base - 1, sc + 1, "G")
    put(g, base - 2, sc + 1, "G")

    # --- Lachesis: the measuring rod laid along the thread (middle) ---
    rod0, rod1 = 17, 27
    for c in range(rod0, rod1 + 1):
        put(g, base - 2, c, "M")
    for c in range(rod0, rod1 + 1, 2):    # ticks hanging under the rod
        put(g, base - 1, c, "t")

    # --- Atropos: the shears, set down and OPEN, thread passing through ---
    piv = 34                              # pivot column, on the thread row
    put(g, base, piv, "x")
    for i in range(1, 5):                 # blades splay up-right and down-right
        put(g, base - i, piv + i, "A")
        put(g, base + i, piv + i, "A")
    # the thread continues between the open blades, uncut, to the edge
    for c in range(piv + 1, W):
        put(g, base, c, "G")

    print(f"# The Fates — {W}×{H} stitches\n")
    for row in g:
        print("".join(row))
    print()
    for sym, what, colour in LEGEND:
        print(f"  {sym}  {what:<13} {colour}")


if __name__ == "__main__":
    main()
