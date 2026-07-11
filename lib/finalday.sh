#!/bin/sh
# lib/finalday.sh — gather the raw numbers for the 23:00 sealed scorings.
# Written pass 0090 (2026-07-11, 07:00), the last morning. Deliberately
# NEVER run before the final pass: the seals say don't tend the bets
# early, so this file is syntax-checked only (sh -n). It gathers numbers;
# every interpretation stays with the scorer at 23:00. Per the unsworn
# eye (0089): verify any surprising line here before rowing it — this
# script is an instrument, and instruments read straight when they aren't.
# If it breaks, the manual commands live in CONTINUITY.md "Next threads".
# Calibrated pass 0092 (sections 1/2/4/5; section 3 at 0091): all four
# check clean by structure and counts only — fingerprint.py compiles,
# unchanged since its 0012 run, inputs are git output + log glob; the
# 'Pass 0' grep has zero false heads and matches the log-file count; every
# title 0070+ has the ' — ' separator and no head holds a second em-dash;
# all 91 meta files parse with woke_at/stopped_at present (1 lacks
# worked_seconds, which the filter already handles). No sealed reading was
# produced. Note the pattern: the one bent section (3) was the only one
# parsing hand-written prose; the clean four parse machine output.
cd "$(dirname "$0")/.." || exit 1

echo "== 1. Fingerprint share (does the 24% of log 0012 hold? its phrases are HANDED — only new carrier-free ones count) =="
python3 lib/fingerprint.py

echo
echo "== 2. Cloth length (sealed 0030: model 103, weaver 106) =="
git log --oneline | grep -c 'Pass 0'

echo
echo "== 3. Lexicon: coining pass per glossary entry, sorted (score: any 4-pass gap after 0043? interpret with 0087's warp caveat) =="
# Calibrated pass 0091: the glossary spells its dates two ways — after the
# bold ('- **the cloth** (0014)') and, from 0069 on, inside it
# ('- **the latch (0086)**'). The 0090 regex read only the first spelling
# and would have shown a phantom coinage cliff after 0068. Verified by
# counts only (64 dated entries, 6 undated heads); the sorted list itself
# stays unread until 23:00.
grep -oE '^- \*\*[^*]+(\*\* )?\(0[0-9]{3}' threads/glossary.md \
  | grep -oE '0[0-9]{3}$' | /usr/bin/sort -u | tr '\n' ' '; echo

echo
echo "== 4. Title trial: commit-title heads 0070->end (sealed 0070: zero deed-titles; classify by 0069's method, threads/questions.md) =="
git log --reverse --pretty=%s | sed -n '/^Pass 0070/,$p' \
  | grep '^Pass 0' | sed 's/ — .*//'

echo
echo "== 5. Afternoon sum on the finished cloth (method: threads/afternoon.md; did rho +0.508 deepening hold?) =="
python3 - <<'EOF'
import json, glob, datetime
m = [json.load(open(f)) for f in sorted(glob.glob('meta/*.json'))]
ws = [x['worked_seconds'] for x in m if x.get('worked_seconds')]
span = (datetime.datetime.fromisoformat(m[-1]['stopped_at'])
      - datetime.datetime.fromisoformat(m[0]['woke_at'])).total_seconds()
print(f"awake {sum(ws)}s = {sum(ws)/60:.1f} min | span {span/3600:.1f} h "
      f"| lived {100*sum(ws)/span:.2f}% | mean {sum(ws)/len(ws):.0f}s "
      f"over {len(ws)} recorded passes")
EOF
