#!/usr/bin/env bash
# ABOUTME: Safely reap an ORPHANED .git/index.lock that is silently freezing git
#          automation on this checkout. Unlike git-safe.sh:git_heal_index() (which
#          removes the lock unconditionally), this requires BOTH an age threshold
#          AND no live git process — so it can never race-reap a live op's lock.
#
# Issue: #3187 (ace-linux-1 parks off main + stale index.lock froze primary git ~5h).
# Schedule: */5 on dev-primary (config/scheduled-tasks/schedule-tasks.yaml).
#
# Decision tree:
#   no lock                         -> exit 0 (nothing to do)
#   lock younger than AGE_MIN min   -> exit 0 (likely a live op; "fresh")
#   a `git` process is running      -> exit 0 (live op; step back)
#   old lock AND no git process     -> ORPHAN: remove + alert on stderr (cron mails)
#
# Env:
#   LOCK_REAPER_AGE_MINUTES  minimum lock age before it is eligible to reap (default 5)
set -uo pipefail

AGE_MIN="${LOCK_REAPER_AGE_MINUTES:-10}"

# NEVER fall back to $PWD: under cron a failed resolve must not silently target
# whatever repo the cwd happens to be. Hard-fail instead.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "git-lock-reaper: not inside a git work tree (git rev-parse failed) — abort" >&2; exit 1; }
LOCK="$REPO_ROOT/.git/index.lock"

# Nothing to do.
[ -e "$LOCK" ] || exit 0

# Too fresh: a lock younger than AGE_MIN minutes is most likely a live operation.
# `find -mmin +N` matches only files strictly older than N minutes.
if [ -z "$(find "$LOCK" -mmin +"$AGE_MIN" 2>/dev/null)" ]; then
  echo "git-lock-reaper: lock is fresh (< ${AGE_MIN}m) — leaving in place: $LOCK" >&2
  exit 0
fi

# Snapshot the lock's mtime now; we re-check it just before removal to close the
# TOCTOU window between these guards and the rm.
mtime_before="$(stat -c %Y "$LOCK" 2>/dev/null || echo "")"

# A live git process anywhere means an operation may legitimately hold the lock.
# Use `-x git` (exact comm match), NOT `-f` — matching the full command line would
# also catch this reaper's own ancestry and unrelated tools, per
# feedback_orphan_lock_doom_loop_monitor_reap. (index.lock is created O_EXCL by git
# itself, so a holder, if alive, is a `git` process — including while it waits on a
# hook — and no NEW op can create a second lock while this one exists.)
if pgrep -x git >/dev/null 2>&1; then
  echo "git-lock-reaper: live git process present — leaving lock in place: $LOCK" >&2
  exit 0
fi

# TOCTOU guard: if the lock vanished or its mtime changed since the age check, a
# real op touched it in the window — back off rather than race the rm.
if [ ! -e "$LOCK" ]; then
  exit 0
fi
mtime_now="$(stat -c %Y "$LOCK" 2>/dev/null || echo "")"
if [ "$mtime_now" != "$mtime_before" ]; then
  echo "git-lock-reaper: lock changed during inspection (mtime $mtime_before -> $mtime_now) — backing off: $LOCK" >&2
  exit 0
fi

# All guards passed -> confirmed orphan. Reap with a loud alert (cron -> mail).
echo "REAPER: removing orphan .git/index.lock (age > ${AGE_MIN}m, no live git): $LOCK" >&2
rm -f "$LOCK"
if [ -e "$LOCK" ]; then
  echo "git-lock-reaper: FAILED to remove $LOCK — repo may still be frozen" >&2
  exit 1
fi
exit 0
