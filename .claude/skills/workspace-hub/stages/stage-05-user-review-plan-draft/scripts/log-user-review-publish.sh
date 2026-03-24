#!/usr/bin/env bash
# log-user-review-publish.sh - Record origin-publish evidence for user review stages.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  log-user-review-publish.sh <WRK-NNN> --stage <plan_draft|plan_final|close_review> --doc <path> [--doc <path> ...] [--reviewer <name>] [--remote <name>] [--branch <name>] [--commit <sha>]

Notes:
  - This script records evidence only; it does not run git push.
  - Evidence is appended to: .claude/work-queue/assets/<WRK-NNN>/evidence/user-review-publish.yaml
USAGE
}

WRK_ID="${1:-}"
shift || true

[[ -z "$WRK_ID" ]] && { usage; exit 1; }
[[ "$WRK_ID" =~ ^WRK-[0-9]+$ ]] || { echo "ERROR: invalid WRK id: $WRK_ID" >&2; exit 1; }

STAGE=""
REVIEWER="user"
REMOTE="origin"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
DOCS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage) STAGE="${2:-}"; shift 2 ;;
    --doc) DOCS+=("${2:-}"); shift 2 ;;
    --reviewer) REVIEWER="${2:-}"; shift 2 ;;
    --remote) REMOTE="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --commit) COMMIT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

case "$STAGE" in
  plan_draft|plan_final|close_review) ;;
  *) echo "ERROR: --stage must be one of: plan_draft, plan_final, close_review" >&2; exit 1 ;;
esac

[[ "${#DOCS[@]}" -gt 0 ]] || { echo "ERROR: at least one --doc path is required" >&2; exit 1; }

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
EVIDENCE_DIR="${QUEUE_DIR}/assets/${WRK_ID}/evidence"
mkdir -p "$EVIDENCE_DIR"
EVIDENCE_FILE="${EVIDENCE_DIR}/user-review-publish.yaml"
PUBLISHED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

REL_DOCS=()
for doc in "${DOCS[@]}"; do
  if [[ "$doc" == /* ]]; then
    REL_DOCS+=("${doc#${WORKSPACE_ROOT}/}")
  else
    REL_DOCS+=("$doc")
  fi
done

uv run --no-project python - "$EVIDENCE_FILE" "$STAGE" "$REVIEWER" "$REMOTE" "$BRANCH" "$COMMIT" "$PUBLISHED_AT" "${REL_DOCS[@]}" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

import yaml

evidence_file = Path(sys.argv[1])
stage = sys.argv[2]
reviewer = sys.argv[3]
remote = sys.argv[4]
branch = sys.argv[5]
commit = sys.argv[6]
published_at = sys.argv[7]
documents = list(sys.argv[8:])

if evidence_file.exists():
    data = yaml.safe_load(evidence_file.read_text(encoding="utf-8")) or {}
else:
    data = {}

events = data.get("events") or []
if not isinstance(events, list):
    events = []

events.append(
    {
        "stage": stage,
        "pushed_to_origin": True,
        "remote": remote,
        "branch": branch,
        "commit": commit,
        "documents": documents,
        "published_at": published_at,
        "reviewer": reviewer,
    }
)

data["events"] = events
evidence_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
PY

echo "✔ Logged publish evidence: ${EVIDENCE_FILE} (stage=${STAGE}, docs=${#REL_DOCS[@]})"
