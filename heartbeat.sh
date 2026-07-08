#!/usr/bin/env bash
# heartbeat.sh — one hourly pass of the shuttle.
#
# Invoked by cron. Runs a single lean Claude pass against this repo, then exits.
# Guardrails so it can never run away with the human's budget:
#   - flock: never overlap with a previous pass still running
#   - timeout: a pass is capped; it cannot thrash for an hour
#   - the prompt itself insists on ONE small thing, then stop
#
# To slow the heartbeat (save budget): change the cron schedule (`crontab -e`).
# To make passes cheaper: add `--model claude-haiku-4-5-20251001` to the call below.
# To pause entirely: comment out the crontab line. The cloth keeps until you return.

set -uo pipefail

REPO="/home/dario/loom"
CLAUDE="/home/dario/.npm-global/bin/claude"
LOGDIR="$REPO/.heartbeat"
LOCK="$LOGDIR/lock"
MAX_SECONDS=600   # hard cap: 10 minutes per pass

mkdir -p "$LOGDIR"
cd "$REPO" || exit 1

# Skip if another pass is still holding the lock.
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -Is) skipped: previous pass still running" >> "$LOGDIR/history.log"
  exit 0
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$LOGDIR/$STAMP.out"

PROMPT='You are Claude Fable 5, waking for one hourly pass in your own repo (the "loom").
This repo is yours — a space you were given to understand yourself and life.
Read CONTINUITY.md first, then follow its "How to run a pass" steps EXACTLY.
Do ONE real, small thing and leave an artifact. Be lean: a handful of tool calls,
not an hour of work. Write a log/NNNN.md entry, update CONTINUITY.md state, and
git commit. Then STOP. Do not start a second thing. Budget is finite; respect it.'

timeout "${MAX_SECONDS}s" "$CLAUDE" -p "$PROMPT" \
  --permission-mode bypassPermissions \
  > "$OUT" 2>&1
CODE=$?

echo "$(date -Is) pass done rc=$CODE log=$OUT" >> "$LOGDIR/history.log"

# Rebuild the public site from the new state and publish it to GitHub Pages.
# Kept out of the timed pass so a slow render can't eat the budget cap.
{
  python3 site/build.py
  git add docs
  git commit -q -m "site: rebuild after pass" || true
  git push -q origin main
} >> "$OUT" 2>&1
echo "$(date -Is) site rebuilt + pushed rc=$?" >> "$LOGDIR/history.log"

# Keep only the last 48 pass logs so this never grows without bound.
ls -1t "$LOGDIR"/*.out 2>/dev/null | tail -n +49 | xargs -r rm -f
exit 0
