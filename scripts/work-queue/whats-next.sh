#!/usr/bin/env bash
# Legacy compatibility wrapper for historical work-queue helper.
# Current canonical queue view is notes/agent-work-queue.md.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_FILE="${REPO_ROOT}/notes/agent-work-queue.md"
CATEGORY=""
SHOW_ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) SHOW_ALL=true; shift ;;
    --category) CATEGORY="${2:-}"; shift 2 ;;
    -h|--help)
      cat <<'EOF'
Legacy compatibility wrapper for scripts/work-queue/whats-next.sh.

Current source of truth:
- notes/agent-work-queue.md
- scripts/refresh-agent-work-queue.py

Options:
  --all                 show top tasks across the current queue snapshot
  --category <name>     filter by heading text (case-insensitive)
EOF
      exit 0
      ;;
    *) shift ;;
  esac
done

echo "[legacy] scripts/work-queue/whats-next.sh now reads notes/agent-work-queue.md; refresh with scripts/refresh-agent-work-queue.sh" >&2

if [[ ! -f "$QUEUE_FILE" ]]; then
  echo "No queue snapshot found. Run scripts/refresh-agent-work-queue.sh" >&2
  exit 0
fi

uv run --no-project python - "$QUEUE_FILE" "$CATEGORY" <<'PYEOF'
import re
import sys
from pathlib import Path

queue_file = Path(sys.argv[1])
category = sys.argv[2].strip().lower()
lines = queue_file.read_text(encoding="utf-8").splitlines()

current_heading = ""
results = []
for line in lines:
    if line.startswith("## ") or line.startswith("### "):
        current_heading = line.lstrip("# ").strip()
        continue
    m = re.match(r"^\|\s*\d+\s*\|\s*(#\d+)\s*\|\s*(.*?)\s*\|$", line)
    if not m:
        continue
    issue, title = m.groups()
    if category and category not in current_heading.lower():
        continue
    results.append((current_heading or "Queue", issue, title))

if not results:
    if category:
        print(f"No queue items matched category: {category}")
    else:
        print("No queue items found in notes/agent-work-queue.md")
    raise SystemExit(0)

for idx, (heading, issue, title) in enumerate(results[:12], start=1):
    print(f"{idx}. [{heading}] {issue} — {title}")
PYEOF
