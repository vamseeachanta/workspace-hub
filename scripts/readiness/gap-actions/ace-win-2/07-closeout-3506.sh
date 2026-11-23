#!/usr/bin/env bash
# Close #3506 only after publish_health is green in the live equality verdict.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

CLOSE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --close) CLOSE=1; shift ;;
    -h|--help)
      echo "Usage: bash $0 [--close]"
      exit 0
      ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "gh is required." >&2; exit 1; }

json="$(uv run --script scripts/readiness/build-equality-matrix.py --json --machine ace-win-2)"
publish="$(printf '%s\n' "$json" | python -c "import json,sys; print(json.load(sys.stdin)['ace-win-2'].get('publish_health',''))")"

if [[ "$publish" != "PUBLISH-OK" ]]; then
  echo "blocked: ace-win-2 publish_health is $publish, not PUBLISH-OK."
  echo "Run 02, 03, and 04 first; then re-run this closeout script."
  exit 2
fi

body="ace-win-2 publish_health is PUBLISH-OK in the live equality matrix. Closing the equivalence fingerprint gap."
gh issue comment 3506 --body "$body"

if [[ $CLOSE -eq 1 ]]; then
  gh issue close 3506 --comment "$body"
else
  echo "Commented on #3506. Re-run with --close to close the issue."
fi
