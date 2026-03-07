#!/usr/bin/env bash
# close-item.sh - Atomic closure of a work-queue item with HTML gate evidence
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  close-item.sh <WRK-NNN> [commit-hash] [options]

Options:
  --html-output <path>         Path to final HTML review artifact (auto-generated if omitted)
  --html-verification <path>   Path to HTML verification evidence
  --learning-output <value>    Path or WRK id to append to learning_outputs (repeatable)
  --followup <WRK-NNN>         Follow-up WRK id to append (repeatable)
  --commit                     Commit queue-state changes
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || -z "${1:-}" ]]; then
  usage
  [[ -n "${1:-}" ]] && exit 0 || exit 1
fi

WRK_ID="$1"
shift

COMMIT_HASH=""
if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  COMMIT_HASH="$1"
  shift
fi

if [[ -z "$WRK_ID" ]]; then
  usage
  exit 1
fi

HTML_OUTPUT=""
HTML_VERIFICATION=""
DO_COMMIT="false"
LEARNING_OUTPUTS=()
FOLLOWUPS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --html-output)
      HTML_OUTPUT="${2:-}"
      shift 2
      ;;
    --html-verification)
      HTML_VERIFICATION="${2:-}"
      shift 2
      ;;
    --learning-output)
      LEARNING_OUTPUTS+=("${2:-}")
      shift 2
      ;;
    --followup)
      FOLLOWUPS+=("${2:-}")
      shift 2
      ;;
    --commit)
      DO_COMMIT="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
GATE_LOGGER="${WORKSPACE_ROOT}/scripts/work-queue/log-gate-event.sh"
FINAL_REVIEW_GENERATOR="${WORKSPACE_ROOT}/scripts/work-queue/generate-final-review.py"

FILE_PATH=""
SOURCE_DIR=""
for dir in working pending blocked done; do
  if [[ -f "${QUEUE_DIR}/${dir}/${WRK_ID}.md" ]]; then
    FILE_PATH="${QUEUE_DIR}/${dir}/${WRK_ID}.md"
    SOURCE_DIR="$dir"
    break
  fi
done

if [[ -z "$FILE_PATH" ]]; then
  echo "✖ Error: Could not find ${WRK_ID}.md in pending/, working/, blocked/, or done/" >&2
  exit 1
fi

# --- Stage 5 evidence gate (canonical checker — Phase 1B guard) ---------------
# close-item.sh is an official Stage 6 downstream validator. Both exit 1 and exit 2
# are fail-closed blocking outcomes.
STAGE5_CHECKER="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
if [[ -f "$STAGE5_CHECKER" ]]; then
  stage5_exit=0
  stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
      --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
  if [[ "$stage5_exit" -eq 1 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Complete Stage 5 interactive review and evidence before closing." >&2
    exit 1
  elif [[ "$stage5_exit" -eq 2 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Repair the Stage 5 gate infrastructure before closing." >&2
    exit 2
  fi
fi

COMPLETED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Ensure final HTML review exists for this WRK; default path is auto-generated.
if [[ -z "$HTML_OUTPUT" ]]; then
  HTML_OUTPUT=".claude/work-queue/assets/${WRK_ID}/workflow-final-review.html"
fi
HTML_OUTPUT_ABS="$HTML_OUTPUT"
if [[ "$HTML_OUTPUT_ABS" != /* ]]; then
  HTML_OUTPUT_ABS="${WORKSPACE_ROOT}/${HTML_OUTPUT_ABS}"
fi
if [[ ! -f "$HTML_OUTPUT_ABS" ]]; then
  if [[ ! -f "$FINAL_REVIEW_GENERATOR" ]]; then
    echo "✖ Error: Missing final review generator: ${FINAL_REVIEW_GENERATOR}" >&2
    exit 1
  fi
  echo "Generating final HTML review for ${WRK_ID}..."
  # The generator is a bash/Python polyglot wrapper; invoke via bash for portability.
  if ! bash "$FINAL_REVIEW_GENERATOR" "$WRK_ID" --output "$HTML_OUTPUT_ABS"; then
    echo "✖ Error: Failed to generate final HTML review for ${WRK_ID}" >&2
    exit 1
  fi
fi

# Normalize to workspace-relative path when possible.
if [[ "$HTML_OUTPUT_ABS" == "${WORKSPACE_ROOT}/"* ]]; then
  HTML_OUTPUT="${HTML_OUTPUT_ABS#${WORKSPACE_ROOT}/}"
fi

VALIDATOR="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
echo "Running gate evidence validator for ${WRK_ID} before close..."
if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "close" "verify_gate_evidence_start" "orchestrator" "phase=close"
fi
if ! uv run --no-project python "$VALIDATOR" "$WRK_ID" --phase close; then
  if [[ -x "$GATE_LOGGER" ]]; then
    bash "$GATE_LOGGER" "$WRK_ID" "close" "verify_gate_evidence_fail" "orchestrator" "phase=close"
  fi
  echo "✖ Gate evidence verification failed for ${WRK_ID}; gather the missing artifacts before closing." >&2
  exit 1
fi

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "close" "verify_gate_evidence_pass" "orchestrator" "phase=close"
  bash "$GATE_LOGGER" "$WRK_ID" "close" "verify_gate_evidence" "orchestrator" "close gate verified"
fi

echo "Closing $WRK_ID..."

uv run --no-project python - "$FILE_PATH" "$COMMIT_HASH" "$COMPLETED_AT" "$HTML_OUTPUT" "$HTML_VERIFICATION" "$WORKSPACE_ROOT" <<'PY'
import sys
import re
from pathlib import Path

path = Path(sys.argv[1])
commit_hash = sys.argv[2]
completed_at = sys.argv[3]
html_output = sys.argv[4]
html_verification = sys.argv[5]
workspace_root = Path(sys.argv[6])

text = path.read_text(encoding="utf-8")
match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
if not match:
    print("Error: No frontmatter found", file=sys.stderr)
    sys.exit(1)

frontmatter = match.group(1)
body = text[match.end():]

def get_value(field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:\s*(.*)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else ""

def upsert(field: str, value: str) -> None:
    global frontmatter
    line = f"{field}: {value}"
    if re.search(rf"^{re.escape(field)}:", frontmatter, re.MULTILINE):
        frontmatter = re.sub(rf"^{re.escape(field)}:.*$", line, frontmatter, flags=re.MULTILINE)
    else:
        frontmatter = frontmatter.rstrip() + "\n" + line

wrk_id = get_value("id") or path.stem
wrk_num = int(wrk_id.split("-", 1)[1]) if wrk_id.startswith("WRK-") and wrk_id.split("-", 1)[1].isdigit() else 0

if html_output:
    upsert("html_output_ref", html_output)
if html_verification:
    upsert("html_verification_ref", html_verification)

if wrk_num >= 624:
    html_output_ref = get_value("html_output_ref")
    html_verification_ref = get_value("html_verification_ref")
    if not html_output_ref:
        print(f"Error: {wrk_id} requires html_output_ref before close", file=sys.stderr)
        sys.exit(1)
    if not html_verification_ref:
        print(f"Error: {wrk_id} requires html_verification_ref before close", file=sys.stderr)
        sys.exit(1)
    for ref_name, ref_value in (
        ("html_output_ref", html_output_ref),
        ("html_verification_ref", html_verification_ref),
    ):
        resolved = (workspace_root / ref_value).resolve() if not ref_value.startswith("/") else Path(ref_value)
        if not resolved.exists():
            print(f"Error: {wrk_id} {ref_name} path does not exist -> {ref_value}", file=sys.stderr)
            sys.exit(1)

upsert("status", "done")
upsert("percent_complete", "100")
upsert("completed_at", completed_at)
if commit_hash:
    upsert("commit", commit_hash)

path.write_text(f"---\n{frontmatter.rstrip()}\n---\n{body}", encoding="utf-8")
PY

if [[ "$SOURCE_DIR" != "done" ]]; then
  mkdir -p "${QUEUE_DIR}/done"
  mv "$FILE_PATH" "${QUEUE_DIR}/done/${WRK_ID}.md"
  FILE_PATH="${QUEUE_DIR}/done/${WRK_ID}.md"
  echo "✔ Moved to done/"
fi

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "close" "close_item" "orchestrator" "work item moved to done"
  bash "$GATE_LOGGER" "$WRK_ID" "close" "close_or_archive" "orchestrator" "terminal close signal"
fi

# Best-effort stage progress update for close stage.
STAGE_UPDATER="${WORKSPACE_ROOT}/scripts/work-queue/update-stage-evidence.py"
if [[ -f "$STAGE_UPDATER" ]]; then
  uv run --no-project python "$STAGE_UPDATER" "$WRK_ID" --order 19 --status done --reviewed-by "orchestrator" >/dev/null || \
    echo "⚠ Could not update stage-evidence order 19 for ${WRK_ID}" >&2
fi

uv run --no-project python "${QUEUE_DIR}/scripts/generate-index.py"

if [[ "$DO_COMMIT" == "true" ]]; then
  git add "${QUEUE_DIR}/done/${WRK_ID}.md" "${QUEUE_DIR}/INDEX.md"
  git commit -m "chore(work-queue): close $WRK_ID"
  echo "✔ Changes committed."
else
  echo "Proposing commit: git add . && git commit -m 'chore(work-queue): close $WRK_ID'"
fi

echo "✔ $WRK_ID closed successfully."
