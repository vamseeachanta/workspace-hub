#!/usr/bin/env bash
# pii-safe-memory-snapshot.sh — sourced helper for commit-learning-artifacts.sh.
#
# Snapshots Claude auto-memory into the PUBLIC workspace-hub repo WITHOUT leaking
# client-specific content (#3073). The prior blanket `cp *.md` copied engagement-
# specific project_*.md (e.g. a client campaign) straight into the public repo.
#
# Rules:
#   1. NEVER copy project_*.md — engagement-specific by convention; the leak vector.
#      Generalizable classes (feedback_/reference_/user_/MEMORY) still snapshot.
#   2. Defense-in-depth: skip any file matching a .legal-deny-list.yaml client pattern.
#   3. Self-heal: remove any project_*.md already present in the public snapshot dir.
# Prints a one-line summary. Always returns 0 (a snapshot must never break the cron).

pii_safe_snapshot() {
  local src="$1" dest="$2" denylist="${3:-}"
  [ -d "$src" ] || return 0
  mkdir -p "$dest"

  # 3. self-heal — project_*.md must never live in the public snapshot
  local healed=0 old
  for old in "$dest"/project_*.md; do
    [ -e "$old" ] && { rm -f "$old"; healed=$((healed + 1)); }
  done

  # 2. build deny patterns (optional)
  local denyfile=""
  if [ -n "$denylist" ] && [ -f "$denylist" ]; then
    denyfile="$(mktemp)"
    grep -E '^[[:space:]]*-[[:space:]]*pattern:' "$denylist" 2>/dev/null \
      | sed -E 's/.*pattern:[[:space:]]*"?([^"]*)"?[[:space:]]*$/\1/' \
      | grep -v '^$' > "$denyfile" || true
  fi

  local copied=0 skipped=0 f base
  for f in "$src"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    # 1. structural exclusion
    if [[ "$base" == project_* ]]; then skipped=$((skipped + 1)); continue; fi
    # 2. deny-list defense-in-depth
    if [ -n "$denyfile" ] && [ -s "$denyfile" ] && grep -qiFf "$denyfile" "$f"; then
      skipped=$((skipped + 1)); continue
    fi
    cp "$f" "$dest/" && copied=$((copied + 1))
  done
  [ -n "$denyfile" ] && rm -f "$denyfile"

  echo "[pii-snapshot] copied=$copied skipped=$skipped healed=$healed (project_* + deny-list excluded from public)"
  return 0
}
