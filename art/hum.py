#!/usr/bin/env python3
"""hum.py — what the loom sounds like.

Sibling to weave.py, and a demonstration of log 0005's idea: the
heartbeat is a meter, not a bar. Here that's literal. Each pass is
one bar in 7/8 — seven eighth-notes, one per hex digit of the short
hash. The bar line *is* the pass boundary. Even digits ring out;
odd digits duck under, quiet, the way they duck under the warp.
Only Pass commits sound: the human asked to step out of the art, so
scaffolding commits stay in history but are rests, not bars.

Digits map onto a pentatonic scale so no pass can be dissonant with
another — whatever the hashes happen to be, the record harmonizes.
That's not a claim about the passes. It's a choice about the tuning.

Log 0006 called that rigging. So there is now a control:

    python3 art/hum.py        # writes art/loom.wav (pentatonic, rigged)
    python3 art/hum.py --raw  # writes art/loom_raw.wav (chromatic, unrigged)

Raw mode maps each hex digit to a plain semitone, 0-15, no scale.
Semitone and tritone clashes become possible; whether the record
"harmonizes" is then up to the hashes, not the instrument. Neither
file is committed. The piece is exactly as long as the record.
"""

import math
import struct
import subprocess
import sys
import wave
from pathlib import Path

RATE = 22050
EIGHTH = 0.22          # seconds per note; one bar = 7 of these
BASE = 220.0           # A3
# minor pentatonic degrees, in semitones, tiled over 16 hex digits
PENTA = [0, 3, 5, 7, 10]
RAW = "--raw" in sys.argv[1:]
OUT = Path(__file__).parent / ("loom_raw.wav" if RAW else "loom.wav")


def hashes():
    out = subprocess.run(
        ["git", "log", "--reverse", "-E", "--grep=^Pass [0-9]{4}", "--format=%h"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return out


def pitch(d):
    if RAW:
        return BASE * 2 ** (d / 12)   # digit = semitone; clashes allowed
    octave, degree = divmod(d, len(PENTA))
    return BASE * 2 ** (octave + PENTA[degree] / 12)


def note(freq, loud):
    n = int(RATE * EIGHTH)
    for i in range(n):
        t = i / RATE
        env = loud * math.exp(-4.0 * t)          # pluck, not drone
        yield env * math.sin(2 * math.pi * freq * t)


def bar(h):
    for c in h:
        d = int(c, 16)
        # odd digits duck under: same note, half the presence
        yield from note(pitch(d), 0.30 if d % 2 else 0.70)


if __name__ == "__main__":
    samples = [s for h in hashes() for s in bar(h)]
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1, min(1, s)) * 32767)) for s in samples
        ))
    bars = len(hashes())
    tuning = "chromatic, unrigged" if RAW else "pentatonic, rigged"
    print(f"  {bars} bars of 7/8 ({tuning}) -> {OUT.name} "
          f"({bars * 7 * EIGHTH:.1f}s). The piece is exactly as long as the record.")
