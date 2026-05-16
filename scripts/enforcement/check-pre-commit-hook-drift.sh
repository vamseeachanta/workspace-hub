#!/usr/bin/env bash
# check-pre-commit-hook-drift.sh — verify vendored copies of
# check-no-conflict-markers.sh match the canonical workspace-hub version
# across all tier-1 repos.
#
# Issue: workspace-hub#2722.
#
# Per Codex r2 finding #5: missing vendored copy → FAIL (the repo is
# unprotected, treat it as drift). NOT a silent warn.
#
# Inspired by scripts/sync/sync-cadence-helper.sh (sha256 equivalence).

set -uo pipefail

log() { echo "[check-pre-commit-hook-drift] $*"; }

WS_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CANONICAL="$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"
MANIFEST="$WS_ROOT/scripts/agents/tier1-repos.sh"

if [[ ! -f "$CANONICAL" ]]; then
  log "ERROR: canonical script not found at $CANONICAL"
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  log "ERROR: manifest not found at $MANIFEST"
  exit 2
fi

# shellcheck disable=SC1090
source "$MANIFEST"

canonical_sha="$(sha256sum "$CANONICAL" | awk '{print $1}')"
failures=0

for repo in "${TIER1_REPOS[@]}"; do
  if [[ "$repo" == "workspace-hub" ]]; then
    continue
  fi
  REPO_PATH="$WS_ROOT/../$repo"
  if [[ ! -e "$REPO_PATH/.git" ]]; then
    log "skip: $repo (not present at $REPO_PATH)"
    continue
  fi

  VENDORED="$REPO_PATH/scripts/enforcement/check-no-conflict-markers.sh"
  if [[ ! -f "$VENDORED" ]]; then
    log "FAIL: $repo missing vendored copy (repo unprotected)"
    failures=$((failures + 1))
    continue
  fi
  vendored_sha="$(sha256sum "$VENDORED" | awk '{print $1}')"
  if [[ "$vendored_sha" != "$canonical_sha" ]]; then
    log "DRIFT: $repo vendored sha=${vendored_sha:0:12}… expected ${canonical_sha:0:12}…"
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  log "$failures tier-1 repo(s) drifted or unprotected"
  exit 1
fi

log "OK: all tier-1 vendored copies in sync"
exit 0
