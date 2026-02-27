#!/usr/bin/env bash
# close-item.sh - Atomic closure of a work-queue item
set -euo pipefail

WRK_ID="${1:-}"
COMMIT_HASH="${2:-}"

if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 <WRK-NNN> [commit-hash] [--commit]"
  exit 1
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

# Find the file
FILE_PATH=""
SOURCE_DIR=""
for dir in "working" "pending" "blocked"; do
  if [[ -f "${QUEUE_DIR}/${dir}/${WRK_ID}.md" ]]; then
    FILE_PATH="${QUEUE_DIR}/${dir}/${WRK_ID}.md"
    SOURCE_DIR="$dir"
    break
  fi
done

if [[ -z "$FILE_PATH" ]]; then
  if [[ -f "${QUEUE_DIR}/done/${WRK_ID}.md" ]]; then
    echo "✔ Item $WRK_ID is already in done/"
    FILE_PATH="${QUEUE_DIR}/done/${WRK_ID}.md"
    SOURCE_DIR="done"
  else
    echo "✖ Error: Could not find ${WRK_ID}.md in pending/, working/, or blocked/"
    exit 1
  fi
fi

COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Closing $WRK_ID..."

# Update frontmatter using python for safety
python3 <<EOF
import re
import os

path = "$FILE_PATH"
with open(path, 'r') as f:
    content = f.read()

match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
if not match:
    print("Error: No frontmatter found")
    exit(1)

fm = match.group(1)
end_pos = match.end()

# Update fields
fm = re.sub(r"^status:.*$", "status: done", fm, flags=re.MULTILINE)
fm = re.sub(r"^percent_complete:.*$", "percent_complete: 100", fm, flags=re.MULTILINE)

if "$COMMIT_HASH":
    if re.search(r"^commit:", fm, re.MULTILINE):
        fm = re.sub(r"^commit:.*$", f"commit: $COMMIT_HASH", fm, flags=re.MULTILINE)
    else:
        fm += f"\ncommit: $COMMIT_HASH"

if re.search(r"^completed_at:", fm, re.MULTILINE):
    fm = re.sub(r"^completed_at:.*$", f"completed_at: $COMPLETED_AT", fm, flags=re.MULTILINE)
else:
    fm += f"\ncompleted_at: $COMPLETED_AT"

new_content = "---\n" + fm + "\n---\n" + content[end_pos:]
with open(path, 'w') as f:
    f.write(new_content)
EOF

# Move to done/ if not already there
if [[ "$SOURCE_DIR" != "done" ]]; then
  mkdir -p "${QUEUE_DIR}/done"
  mv "$FILE_PATH" "${QUEUE_DIR}/done/${WRK_ID}.md"
  echo "✔ Moved to done/"
fi

# Regenerate index
python3 "${QUEUE_DIR}/scripts/generate-index.py"

# Commit if requested
if [[ "${3:-}" == "--commit" ]]; then
  git add "${QUEUE_DIR}/done/${WRK_ID}.md" "${QUEUE_DIR}/INDEX.md"
  git commit -m "chore(work-queue): close $WRK_ID"
  echo "✔ Changes committed."
else
  echo "Proposing commit: git add . && git commit -m 'chore(work-queue): close $WRK_ID'"
fi

echo "✔ $WRK_ID closed successfully."
