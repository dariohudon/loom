#!/usr/bin/env python3
"""weave.py — the loom weaves its own record.

Each pass is one row of weft. The hex digits of the pass commit's
hash decide the thread: which shade, and whether it passes over or
under the warp. Only Pass commits count: the human asked to step out
of the art, so the scaffolding around the loom — site, setup, relays —
stays in git history but is not cloth. Nothing here is useful. Run it
after any pass and the cloth is one row longer.

    python3 art/weave.py
"""

import subprocess

SHADES = " ░░▒▒▓▓██▓▓▒▒░░ "  # 16 shades, one per hex digit, mirrored
WARP = "│"                    # what the weft passes under
WIDTH = 40


def rows():
    out = subprocess.run(
        ["git", "log", "--reverse", "-E", "--grep=^Pass [0-9]{4}", "--format=%h %s"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return [line.split(" ", 1) for line in out.splitlines()]


def weft(h):
    """One row of cloth from one short hash."""
    digits = [int(c, 16) for c in h]
    row = []
    for i in range(WIDTH):
        d = digits[i % len(digits)]
        # odd digits duck under the warp; even ones show their shade
        row.append(WARP if (d + i) % 2 else SHADES[d])
    return "".join(row)


if __name__ == "__main__":
    history = rows()
    print("┌" + "─" * WIDTH + "┐")
    for h, subject in history:
        print("│" + weft(h) + "│ " + h)
    print("└" + "─" * WIDTH + "┘")
    print(f"  {len(history)} rows. The cloth is exactly as long as the record.")
