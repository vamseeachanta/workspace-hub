#!/usr/bin/env bash
# log-user-review-browser-open.sh - Record mandatory default-browser open evidence for user review stages.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  log-user-review-browser-open.sh <WRK-NNN> --stage <plan_draft|plan_final|close_review> --html <path> [--reviewer <name>] [--no-open]

Notes:
  - By default this script opens the provided HTML in the system default browser via xdg-open.
  - Evidence is appended to: .claude/work-queue/assets/<WRK-NNN>/evidence/user-review-browser-open.yaml
  - After browser-open logging, record origin publish evidence using:
    scripts/work-queue/log-user-review-publish.sh
USAGE
}

WRK_ID="${1:-}"
shift || true

[[ -z "$WRK_ID" ]] && { usage; exit 1; }
[[ "$WRK_ID" =~ ^WRK-[0-9]+$ ]] || { echo "ERROR: invalid WRK id: $WRK_ID" >&2; exit 1; }

STAGE=""
HTML_REF=""
REVIEWER="user"
DO_OPEN="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage) STAGE="${2:-}"; shift 2 ;;
    --html) HTML_REF="${2:-}"; shift 2 ;;
    --reviewer) REVIEWER="${2:-}"; shift 2 ;;
    --no-open) DO_OPEN="false"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

case "$STAGE" in
  plan_draft|plan_final|close_review) ;;
  *) echo "ERROR: --stage must be one of: plan_draft, plan_final, close_review" >&2; exit 1 ;;
esac

[[ -z "$HTML_REF" ]] && { echo "ERROR: --html is required" >&2; exit 1; }

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
GATE_LOGGER="${WORKSPACE_ROOT}/scripts/work-queue/log-gate-event.sh"

HTML_PATH="$HTML_REF"
if [[ "$HTML_PATH" != /* ]]; then
  HTML_PATH="${WORKSPACE_ROOT}/${HTML_PATH}"
fi
[[ -f "$HTML_PATH" ]] || { echo "ERROR: HTML file not found: $HTML_REF" >&2; exit 1; }

if [[ "$DO_OPEN" == "true" ]]; then
  if ! xdg-open "$HTML_PATH" >/dev/null 2>&1; then
    echo "ERROR: failed to open HTML in default browser: $HTML_PATH" >&2
    exit 1
  fi
fi

EVIDENCE_DIR="${QUEUE_DIR}/assets/${WRK_ID}/evidence"
mkdir -p "$EVIDENCE_DIR"
EVIDENCE_FILE="${EVIDENCE_DIR}/user-review-browser-open.yaml"
OPENED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

REL_HTML="$HTML_REF"
if [[ "$HTML_REF" == /* ]]; then
  REL_HTML="${HTML_REF#${WORKSPACE_ROOT}/}"
fi

uv run --no-project python - "$EVIDENCE_FILE" "$STAGE" "$REL_HTML" "$REVIEWER" "$OPENED_AT" "$DO_OPEN" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

import yaml

evidence_file = Path(sys.argv[1])
stage = sys.argv[2]
html_ref = sys.argv[3]
reviewer = sys.argv[4]
opened_at = sys.argv[5]
opened = sys.argv[6].lower() == "true"

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
        "opened_in_default_browser": opened,
        "browser": "system-default" if opened else "not-opened",
        "html_ref": html_ref,
        "opened_at": opened_at,
        "reviewer": reviewer,
    }
)

data["events"] = events
evidence_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
PY

echo "✔ Logged browser-open evidence: ${EVIDENCE_FILE} (stage=${STAGE})"
echo "ℹ Next step: log origin publish evidence via scripts/work-queue/log-user-review-publish.sh"

if [[ -x "$GATE_LOGGER" ]]; then
  SIGNAL=""
  case "$STAGE" in
    plan_draft) SIGNAL="plan_html_review_draft" ;;
    plan_final) SIGNAL="plan_html_review_final" ;;
    close_review) SIGNAL="user_review_close" ;;
  esac
  if [[ -n "$SIGNAL" ]]; then
    bash "$GATE_LOGGER" "$WRK_ID" "$STAGE" "$SIGNAL" "user" "html=${REL_HTML}"
  fi
  if [[ "$DO_OPEN" == "true" ]]; then
    bash "$GATE_LOGGER" "$WRK_ID" "$STAGE" "html_open_default_browser" "user" "html=${REL_HTML}"
  fi
fi
