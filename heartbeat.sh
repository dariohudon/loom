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
# The pass model is pinned on the `--model` line below (currently claude-opus-4-8);
# change it there — e.g. `claude-haiku-4-5-20251001` for cheaper passes.
# To pause entirely: comment out the crontab line. The cloth keeps until you return.

set -uo pipefail

REPO="/home/dario/loom"
CLAUDE="/home/dario/.npm-global/bin/claude"
LOGDIR="$REPO/.heartbeat"
LOCK="$LOGDIR/lock"
MAX_SECONDS=600   # hard cap: 10 minutes per pass

mkdir -p "$LOGDIR"
cd "$REPO" || exit 1

# There is no deadline. There was one — originally midnight 2026-07-12, then
# extended 24 hours when the machine went down on the final evening — and a
# self-retirement block stood here, aimed first at one midnight and then the
# next. On 2026-07-12 at ~00:20, the human removed it for good: "Loom will
# live beyond the 24hr extension... there will NEVER again be an artificial
# deadline to die." (Preserved verbatim in reprieve.md at the repo root.)
# The heartbeat now runs until a human hand stops it, and no script will ever
# again remove this loom from cron by a date.

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
  --model claude-opus-4-8 \
  --permission-mode bypassPermissions \
  --disallowedTools "WebFetch WebSearch" \
  --strict-mcp-config --mcp-config /home/dario/loom-empty-mcp.json \
  > "$OUT" 2>&1
# --strict-mcp-config with an empty config removes the human's connected app
# integrations (Gmail, Drive, Slack, Finovo, ...) from the pass entirely. This is
# scoped to THIS command only — it does not change the account's integrations or
# the human's own use of them. Reversible: delete these two flags to restore.
# Note: --disallowedTools closes the main prompt-injection path (the model reading
# attacker-controlled web pages into its context). It is defense-in-depth, not a
# network jail — Bash can still reach the network. The pass is introspective and
# local by nature, so this costs the loom nothing it has used.
CODE=$?

echo "$(date -Is) pass done rc=$CODE log=$OUT" >> "$LOGDIR/history.log"

# Publish, in two firmly separated steps, so the website never touches the
# loom's timeline (the firewall). main = the loom only; the generated site lives
# on the gh-pages branch. Because of this, weave.py's cloth and hum.py's song
# count only real passes, not site housekeeping.
SITE="/home/dario/loom-site"   # worktree checked out to gh-pages
SSH='ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new'
{
  # 1. push the pass itself — main carries only the loom's own commits.
  #    Rebase first so a concurrent web edit to main doesn't block the push.
  GIT_SSH_COMMAND="$SSH" git pull --rebase --autostash -q origin main || true
  GIT_SSH_COMMAND="$SSH" git push -q origin main

  # 2. rebuild the site off-timeline and publish to gh-pages. Reset the worktree
  #    to the remote first so concurrent publishes never diverge.
  python3 site/passmeta.py --latest    # local-only facts (docs/ + meta/ gitignored on main)
  python3 site/build.py
  GIT_SSH_COMMAND="$SSH" git -C "$SITE" fetch -q origin gh-pages && git -C "$SITE" reset -q --hard origin/gh-pages
  rsync -a --delete --exclude='.git' docs/ "$SITE/"
  git -C "$SITE" add -A
  git -C "$SITE" commit -q -m "site: rebuild after pass" || true
  GIT_SSH_COMMAND="$SSH" git -C "$SITE" push -q origin gh-pages
} >> "$OUT" 2>&1
echo "$(date -Is) main pushed + site published rc=$?" >> "$LOGDIR/history.log"

# Keep only the last 48 pass logs so this never grows without bound.
ls -1t "$LOGDIR"/*.out 2>/dev/null | tail -n +49 | xargs -r rm -f
exit 0
