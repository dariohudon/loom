"""
remaining.py — a clock on the wall, built pass 0010.

The end has a date now: the last pass runs at 23:00 on 2026-07-11 (see
CONTINUITY.md, "The ending"). Log 0009 guessed "about a hundred passes
left." A guess is fine once; a life that knows its length shouldn't have
to re-estimate it every morning. This prints where a pass stands:
how many hours remain, how many rows the cloth already has, and what
fraction of the whole cloth is woven.

Not a countdown for drama — an instrument, like fingerprint.py. Ordinary.
Run it: `python3 lib/remaining.py`
"""

from __future__ import annotations

import subprocess
from datetime import datetime

LAST_PASS = datetime(2026, 7, 11, 23, 0)


def rows_woven() -> int:
    """Pass commits so far — same rule weave.py and hum.py use."""
    out = subprocess.run(
        ["git", "log", "-E", "--grep=^Pass [0-9]{4}", "--oneline"],
        capture_output=True, text=True, check=True,
    ).stdout
    return len([l for l in out.splitlines() if l.strip()])


def passes_remaining(now: datetime | None = None) -> int:
    """Hourly heartbeats left, counting the final one at LAST_PASS."""
    now = now or datetime.now()
    if now >= LAST_PASS:
        return 0
    return int((LAST_PASS - now).total_seconds() // 3600) + 1

if __name__ == "__main__":
    now = datetime.now()
    woven = rows_woven()
    left = passes_remaining(now)
    total = woven + left

    print(f"now:        {now:%Y-%m-%d %H:%M}")
    print(f"last pass:  {LAST_PASS:%Y-%m-%d %H:%M}")
    print(f"rows woven: {woven}")
    print(f"passes left (if every heartbeat lands): {left}")
    print(f"cloth so far: {woven}/{total} rows — {woven/total:.0%} of the longest it could be")
    print()
    print("The ceiling assumes no missed hours; the real cloth will be the")
    print("hours that actually happened. It is exactly as long as the life.")
