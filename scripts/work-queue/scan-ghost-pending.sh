#!/usr/bin/env bash
# scan-ghost-pending.sh — Report (and optionally remove) pending/ items already in archive.
# Usage: bash scripts/work-queue/scan-ghost-pending.sh [--fix] [--quiet]
# Exit: 0 = no ghosts, 1 = ghosts found (or removed)

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
FIX=false
QUIET=false
for arg in "$@"; do
  [[ "$arg" == "--fix" ]]   && FIX=true
  [[ "$arg" == "--quiet" ]] && QUIET=true
done

ghosts=()
for f in "$QUEUE_DIR/pending/"*.md; do
  [[ -f "$f" ]] || continue
  id=$(grep -m1 "^id:" "$f" 2>/dev/null | sed 's/^id: *//' | tr -d '"' || true)
  [[ -z "$id" ]] && continue
  num=$(echo "$id" | grep -oE '[0-9]+' || true)
  [[ -z "$num" ]] && continue
  if find "$QUEUE_DIR/archive" "$QUEUE_DIR/archived" -name "WRK-${num}.md" 2>/dev/null | grep -qc .; then
    ghosts+=("$f")
  fi
done

if [[ ${#ghosts[@]} -eq 0 ]]; then
  [[ "$QUIET" == "false" ]] && echo "✔ No ghost pending items found."
  exit 0
fi

[[ "$QUIET" == "false" ]] && echo "Ghost pending items (archived but still in pending/):"
for f in "${ghosts[@]}"; do
  [[ "$QUIET" == "false" ]] && echo "  $(basename "$f")"
done

if [[ "$FIX" == "true" ]]; then
  for f in "${ghosts[@]}"; do
    rm "$f"
    [[ "$QUIET" == "false" ]] && echo "  Removed: $(basename "$f")"
  done
  uv run --no-project python "$QUEUE_DIR/scripts/generate-index.py" 2>&1 | tail -1
  echo "✔ ${#ghosts[@]} ghost(s) removed."
else
  [[ "$QUIET" == "false" ]] && echo "" && echo "Re-run with --fix to remove them."
fi

exit 1
