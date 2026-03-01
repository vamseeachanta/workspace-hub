#!/usr/bin/env bash
# close-item.sh - Atomic closure of a work-queue item with HTML gate evidence
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  close-item.sh <WRK-NNN> [commit-hash] [options]

Options:
  --html-output <path>         Path to final HTML review artifact
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

COMPLETED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

VALIDATOR="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
echo "Running gate evidence validator for ${WRK_ID} before close..."
if ! python3 "$VALIDATOR" "$WRK_ID"; then
  echo "✖ Gate evidence verification failed for ${WRK_ID}; gather the missing artifacts before closing." >&2
  exit 1
fi

echo "Closing $WRK_ID..."

python3 - "$FILE_PATH" "$COMMIT_HASH" "$COMPLETED_AT" "$HTML_OUTPUT" "$HTML_VERIFICATION" "$WORKSPACE_ROOT" <<'PY'
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

python3 "${QUEUE_DIR}/scripts/generate-index.py"

if [[ "$DO_COMMIT" == "true" ]]; then
  git add "${QUEUE_DIR}/done/${WRK_ID}.md" "${QUEUE_DIR}/INDEX.md"
  git commit -m "chore(work-queue): close $WRK_ID"
  echo "✔ Changes committed."
else
  echo "Proposing commit: git add . && git commit -m 'chore(work-queue): close $WRK_ID'"
fi

echo "✔ $WRK_ID closed successfully."
