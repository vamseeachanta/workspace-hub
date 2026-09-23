#!/usr/bin/env bash
# sync-machine-branch.sh — publish this machine's generated workspace-hub state
# to branch machine/<host> (e.g. machine/ace-linux-1). NEVER writes to main.
#
# Policy (2026-09-22): after the main-line divergence incident (297 auto-sync
# commits wedged onto a diverged main), machine-generated state is published on
# per-machine branches. A freshness guard aborts the run if the local branch is
# behind origin, so a stale checkout can never grow a new divergence.
#
# Layout: this script runs from inside the machine-branch checkout, a sibling of
# the live workspace-hub checkout:
#   <root>/workspace-hub          live checkout (read-only for this script)
#   <root>/workspace-hub-machine  machine/<host> checkout (written here)
#
# Usage: sync-machine-branch.sh [machine-repo-dir]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${1:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
HOST="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"
BRANCH="machine/${HOST}"
LIVE_HUB="$(cd "${REPO}/../workspace-hub" 2>/dev/null && pwd || true)"
MSG="chore(sync): auto-sync $(date +%F)"

log() { echo "[machine-sync] $*"; }
die() { echo "[machine-sync] ERROR: $*" >&2; exit 1; }

[ -d "${REPO}/.git" ] || die "not a git repo: ${REPO}"
cd "$REPO" || die "cannot cd to ${REPO}"

current="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
[ "$current" = "$BRANCH" ] || die "on branch '${current}', expected '${BRANCH}' — refusing to write (never main)"

# Freshness guard: fetch first; abort if behind origin.
git fetch --prune origin || die "git fetch failed"
behind="$(git rev-list --count "HEAD..@{u}" 2>/dev/null || echo 0)"
if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
  die "local ${BRANCH} is ${behind} behind origin/${BRANCH} — aborting (freshness guard)"
fi
log "fresh: ${BRANCH} at $(git rev-parse --short HEAD)"

# Mirror the live checkout's tracked modifications (read-only there) into this
# machine checkout. Same scope as the old `git add -u` auto-sync: tracked files
# only; untracked files are never picked up.
if [ -n "$LIVE_HUB" ] && [ -d "${LIVE_HUB}/.git" ]; then
  while IFS= read -r -d '' f; do
    if [ -f "${LIVE_HUB}/${f}" ]; then
      mkdir -p "${REPO}/$(dirname "$f")"
      cp -p "${LIVE_HUB}/${f}" "${REPO}/${f}" || log "warn: copy failed for ${f}"
    fi
  done < <(git -C "$LIVE_HUB" diff HEAD --name-only --no-renames --diff-filter=AM -z 2>/dev/null)
  while IFS= read -r -d '' f; do
    if [ -e "${REPO}/${f}" ]; then
      git rm -q -- "$f" || log "warn: git rm failed for ${f}"
    fi
  done < <(git -C "$LIVE_HUB" diff HEAD --name-only --no-renames --diff-filter=D -z 2>/dev/null)
  log "mirrored tracked changes from ${LIVE_HUB}"
else
  log "no live hub checkout found; committing machine-checkout state only"
fi

git add -u
if ! git diff --cached --quiet; then
  git commit -m "$MSG" || die "git commit failed"
  log "committed $(git rev-parse --short HEAD) — ${MSG}"
else
  log "nothing to commit"
fi

git pull --ff-only || die "fast-forward pull failed — aborting before push"
git push origin "$BRANCH" || die "git push failed"
log "pushed ${BRANCH}: $(git rev-parse --short HEAD)"
