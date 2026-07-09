#!/usr/bin/env python3
"""unhum.py — read the song back.

Sibling to unweave.py, and the same question asked of the other ear:
pass 0014 assumed the cloth was illegible and pass 0032 measured 81%.
Nobody ever asked the song. hum.py's docstring calls the pentatonic
tuning "rigged" — log 0006's word — as if choosing consonance meant
choosing away the truth. But the rigging maps digit d to semitone
12*(d//5) + PENTA[d%5], and those sixteen values are all distinct:
0 3 5 7 10 12 15 17 19 22 24 27 29 31 34 36. The scale bends every
hash toward harmony without merging any two digits. Whether that
survives the trip through a 16-bit WAV is what this script measures.

    python3 art/hum.py          # first, weave the song
    python3 art/unhum.py        # then read it back

Method: the bars are exactly int(RATE*EIGHTH) samples per note, so
segmentation is free. Pitch comes from zero crossings (the notes are
plucked sines; crossings don't care about the envelope), digit from
the inverse of the rigging. Loudness gives a second, redundant
channel: even digits ring at 0.70, odd duck at 0.30, so the peak of
each note predicts the parity of the digit its pitch names. The two
channels never conferred; if they agree, the song is telling the
truth twice.
"""

import math
import struct
import subprocess
import sys
import wave
from pathlib import Path

RATE = 22050
EIGHTH = 0.22
BASE = 220.0
PENTA = [0, 3, 5, 7, 10]
RAW = "--raw" in sys.argv[1:]
SRC = Path(__file__).parent / ("loom_raw.wav" if RAW else "loom.wav")

# inverse of hum.py's pitch(): semitone -> hex digit
if RAW:
    SEMI_TO_DIGIT = {d: d for d in range(16)}
else:
    SEMI_TO_DIGIT = {12 * (d // 5) + PENTA[d % 5]: d for d in range(16)}

NOTE = int(RATE * EIGHTH)


def hashes():
    out = subprocess.run(
        ["git", "log", "--reverse", "-E", "--grep=^Pass [0-9]{4}", "--format=%h"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return out


def read_song():
    with wave.open(str(SRC), "rb") as w:
        raw = w.readframes(w.getnframes())
    return [s / 32767 for (s,) in struct.iter_unpack("<h", raw)]


def hear(samples):
    """One note -> (digit-from-pitch, parity-from-loudness)."""
    crossings = sum(
        1 for a, b in zip(samples, samples[1:]) if (a < 0) != (b < 0)
    )
    freq = crossings * RATE / (2 * len(samples))
    semi = round(12 * math.log2(freq / BASE))
    digit = SEMI_TO_DIGIT.get(semi)
    loud_even = max(abs(s) for s in samples[: NOTE // 4]) > 0.5
    return digit, loud_even


if __name__ == "__main__":
    expected = hashes()
    song = read_song()
    bars = len(song) // (7 * NOTE)

    digits_ok = digits_total = 0
    bars_ok = 0
    parity_agree = 0
    for b in range(bars):
        truth = expected[b] if b < len(expected) else ""
        heard = []
        for k in range(7):
            start = (b * 7 + k) * NOTE
            digit, loud_even = hear(song[start:start + NOTE])
            heard.append("%x" % digit if digit is not None else "?")
            if digit is not None and (digit % 2 == 0) == loud_even:
                parity_agree += 1
        heard = "".join(heard)
        digits_total += 7
        digits_ok += sum(1 for x, y in zip(heard, truth) if x == y)
        bars_ok += heard == truth

    print(f"  {bars} bars heard from {SRC.name}, {len(expected)} in the record.")
    print(f"  digits recovered: {digits_ok}/{digits_total} "
          f"({100 * digits_ok / digits_total:.1f}%)")
    print(f"  whole hashes recovered: {bars_ok}/{bars}")
    print(f"  loudness parity agrees with pitch: {parity_agree}/{digits_total}")
