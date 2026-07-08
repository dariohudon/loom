#!/usr/bin/env python3
"""passmeta.py — extract the machine-facts of a pass from its session transcript.

Each hourly pass is one headless Claude session, logged as a .jsonl transcript
under ~/.claude/projects/-home-dario-loom/. This reads one transcript and writes
meta/NNNN.json for the pass it produced: when it woke, when it stopped, how long
it worked, which model, and how many tokens it decided to spend.

Usage:
    python3 site/passmeta.py <transcript.jsonl>     # one transcript
    python3 site/passmeta.py --backfill             # every transcript found
    python3 site/passmeta.py --latest               # newest transcript only
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "meta"
SESSIONS = Path.home() / ".claude" / "projects" / "-home-dario-loom"
LOCAL = ZoneInfo("America/Edmonton")


def sh(*a: str) -> str:
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout


def load(transcript: Path) -> list[dict]:
    return [json.loads(l) for l in transcript.read_text().splitlines() if l.strip()]


def parse_ts(s: str) -> datetime:
    # transcript timestamps look like 2026-07-08T01:00:03.285Z
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def pass_commits() -> list[dict]:
    """All commits whose subject is 'Pass NNNN: ...', with author epoch + tz."""
    out = sh("git", "log", "--format=%H%x1f%at%x1f%s")
    rows = []
    for line in out.splitlines():
        h, at, subj = line.split("\x1f")
        m = re.match(r"Pass\s+(\d+)", subj)
        if m:
            rows.append({"hash": h[:7], "at": int(at), "num": m.group(1)})
    return rows


def extract(transcript: Path) -> dict | None:
    recs = load(transcript)
    ts = sorted(parse_ts(r["timestamp"]) for r in recs if r.get("timestamp"))
    if not ts:
        return None
    woke, stopped = ts[0], ts[-1]

    models = Counter()
    tok = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    for r in recs:
        msg = r.get("message")
        if not isinstance(msg, dict):
            continue
        u = msg.get("usage")
        if msg.get("model") and u:
            models[msg["model"]] += u.get("output_tokens", 0)
            tok["input"] += u.get("input_tokens", 0)
            tok["output"] += u.get("output_tokens", 0)
            tok["cache_read"] += u.get("cache_read_input_tokens", 0)
            tok["cache_creation"] += u.get("cache_creation_input_tokens", 0)
    if not models:
        return None
    tok["total"] = tok["input"] + tok["output"] + tok["cache_read"] + tok["cache_creation"]
    model = models.most_common(1)[0][0]

    # Map to the pass by finding the "Pass NNNN" commit made during this session.
    lo, hi = woke.timestamp() - 90, stopped.timestamp() + 90
    num = commit = None
    for c in pass_commits():
        if lo <= c["at"] <= hi:
            num, commit = c["num"], c["hash"]
            break
    if not num:
        return None

    return {
        "pass": num,
        "commit": commit,
        "woke_at": woke.astimezone(LOCAL).isoformat(),
        "stopped_at": stopped.astimezone(LOCAL).isoformat(),
        "worked_seconds": round((stopped - woke).total_seconds()),
        "model": model,
        "tokens": tok,
        "session": transcript.stem,
        "source": "transcript",
    }


def write_meta(data: dict) -> None:
    META.mkdir(exist_ok=True)
    (META / f"{data['pass']}.json").write_text(json.dumps(data, indent=2) + "\n")
    t = data["tokens"]
    print(f"  pass {data['pass']} <- {data['session'][:8]}  "
          f"{data['model']}  {data['worked_seconds']}s  "
          f"{t['output']} out / {t['total']} total tok")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "--backfill"
    if arg == "--backfill":
        files = sorted(SESSIONS.glob("*.jsonl"))
    elif arg == "--latest":
        files = sorted(SESSIONS.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)[-1:]
    else:
        files = [Path(arg)]
    n = 0
    for f in files:
        try:
            d = extract(f)
        except Exception as e:  # a partial/odd transcript shouldn't break the site
            print(f"  skip {f.name}: {e}")
            continue
        if d:
            write_meta(d)
            n += 1
    print(f"wrote {n} pass-meta file(s)")


if __name__ == "__main__":
    main()
