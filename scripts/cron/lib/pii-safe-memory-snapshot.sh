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
#   4. C20: when the caller defines pii_snapshot_copy SRC DEST, every copy goes
#      through it (commit-learning-artifacts.sh passes the identifier gate's
#      redactor, which also skips a file whose NAME carries an identifier).
# Prints a one-line summary. Returns 0, except when a caller-defined
# pii_snapshot_copy fails: then it stops and returns 1 so the caller can fail
# closed instead of committing an unredacted snapshot.

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
    if declare -F pii_snapshot_copy >/dev/null 2>&1; then
      if ! pii_snapshot_copy "$f" "$dest/$base"; then
        [ -n "$denyfile" ] && rm -f "$denyfile"
        echo "[pii-snapshot] redacting copy failed; snapshot stopped"
        return 1
      fi
      if [ -e "$dest/$base" ]; then copied=$((copied + 1)); else skipped=$((skipped + 1)); fi
    else
      cp "$f" "$dest/" && copied=$((copied + 1))
    fi
  done
  [ -n "$denyfile" ] && rm -f "$denyfile"

  echo "[pii-snapshot] copied=$copied skipped=$skipped healed=$healed (project_* + deny-list excluded from public)"
  return 0
}
