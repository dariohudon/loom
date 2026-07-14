#!/usr/bin/env python3
"""A door to Wikipedia — aimed, summary-capped.

Loom names a topic; this returns the lead summary of that one article and
nothing more. It is a DOOR in the loom's own sense (0084/0141): aimable, so
it is gated by Loom's sayable-reason discipline (0087/0111) — open it only
when the hour has a reason it can say out loud, and the reason can't be
scarcity. The cap here is on DEPTH, not aim: you get the lead paragraph, not
the river.

Security posture (matches the pass's closed-web stance): this reaches exactly
ONE endpoint — Wikipedia's REST summary API — over stdlib urllib. No search,
no link-following, no other host. It does not reintroduce the general web that
the heartbeat deliberately closes (--disallowedTools, --strict-mcp-config).

Usage:
    python3 lib/doors/wikipedia.py "Antikythera mechanism"

Exit codes: 0 found · 3 not found (404) · 4 network/other error.
"""
import sys
import json
import urllib.parse
import urllib.request
import urllib.error

API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
# Wikimedia asks for a descriptive User-Agent; a bare urllib default gets 403.
UA = "loom-door/1.0 (https://github.com/dariohudon/loom; hourly weaver, one aimed lookup)"
CAP = 1500  # characters of extract; the depth cap that keeps a door from being a river


def open_door(topic: str) -> int:
    title = urllib.parse.quote(topic.strip().replace(" ", "_"))
    req = urllib.request.Request(API + title, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print(f"No Wikipedia article found for: {topic}")
            return 3
        print(f"Wikipedia returned an error ({err.code}) for: {topic}")
        return 4
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        print(f"Could not reach Wikipedia: {err}")
        return 4

    heading = data.get("title", topic)
    extract = (data.get("extract") or "").strip()
    url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    kind = data.get("type", "")

    if kind == "disambiguation":
        print(f'"{heading}" is a disambiguation page — several articles share the name. '
              f"Aim more precisely to open a single one.")
        if url:
            print(url)
        return 0

    if len(extract) > CAP:
        extract = extract[:CAP].rsplit(" ", 1)[0] + " …"

    print(heading)
    print()
    print(extract if extract else "(no summary text for this article)")
    if url:
        print()
        print(url)
    return 0


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Name a topic to open the door, e.g.:  python3 lib/doors/wikipedia.py "Antikythera mechanism"')
        return 4
    return open_door(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main())
