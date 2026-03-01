#!/usr/bin/env bash
# claim-item.sh - Handle claim gate for a work item with structured evidence
set -euo pipefail

WRK_ID="${1:-}"

if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>" >&2
  exit 1
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
QUOTA_FILE="${WORKSPACE_ROOT}/config/ai-tools/agent-quota-latest.json"

FILE_PATH=""
if [[ -f "${QUEUE_DIR}/pending/${WRK_ID}.md" ]]; then
  FILE_PATH="${QUEUE_DIR}/pending/${WRK_ID}.md"
elif [[ -f "${QUEUE_DIR}/blocked/${WRK_ID}.md" ]]; then
  echo "✖ Error: ${WRK_ID} is blocked. Resolve blockers first." >&2
  exit 1
fi

if [[ -z "$FILE_PATH" ]]; then
  echo "✖ Error: Could not find ${WRK_ID}.md in pending/" >&2
  exit 1
fi

provider="$(awk -F': ' '/^provider:/ { gsub(/"/, "", $2); print $2; exit }' "$FILE_PATH")"

CLAIM_DIR="${WORKSPACE_ROOT}/.claude/work-queue/assets/${WRK_ID}"
mkdir -p "$CLAIM_DIR"
CLAIM_FILE="${CLAIM_DIR}/claim-evidence.yaml"

echo "Checking quota..."
QUOTA_STATUS="missing"
if [[ -f "$QUOTA_FILE" ]]; then
  QUOTA_STATUS="available"
else
  echo "⚠ Quota file missing: $QUOTA_FILE"
fi

python3 - "$FILE_PATH" "$CLAIM_FILE" "$QUOTA_FILE" "$QUOTA_STATUS" "$WORKSPACE_ROOT" <<'PY'
from datetime import datetime, timezone
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
claim_file = Path(sys.argv[2])
quota_file = sys.argv[3]
quota_status = sys.argv[4]
workspace_root = Path(sys.argv[5])

text = path.read_text(encoding="utf-8")
match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
if not match:
    print("Error: Invalid frontmatter layout", file=sys.stderr)
    sys.exit(1)

frontmatter = match.group(1)
body = text[match.end():]

def get_value(field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else ""

def upsert(field: str, value: str) -> None:
    global frontmatter
    line = f"{field}: {value}"
    if re.search(rf"^{re.escape(field)}:", frontmatter, re.MULTILINE):
        frontmatter = re.sub(rf"^{re.escape(field)}:.*$", line, frontmatter, flags=re.MULTILINE)
    else:
        frontmatter = frontmatter.rstrip() + "\n" + line

wrk_id = get_value("id") or path.stem
route = get_value("route")
orchestrator = get_value("orchestrator")
provider = get_value("provider")
provider_alt = get_value("provider_alt")
plan_workstations = get_value("plan_workstations")
execution_workstations = get_value("execution_workstations")

quota_snapshot = {
    "source": str(Path(quota_file).relative_to(workspace_root)) if Path(quota_file).exists() else quota_file,
    "status": quota_status,
}
if Path(quota_file).exists():
    try:
        quota_snapshot["captured_at"] = Path(quota_file).stat().st_mtime
    except OSError:
        pass

claim_doc = {
    "claim_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "wrk_id": wrk_id,
    "route": route,
    "orchestrator": orchestrator,
    "best_fit_provider": provider,
    "alternate_provider": provider_alt,
    "plan_workstations": plan_workstations,
    "execution_workstations": execution_workstations,
    "quota_snapshot": quota_snapshot,
    "agent_capability": {
        "best_fit": "matched" if provider else "undocumented",
        "rationale": "Claim created from WRK frontmatter. Review before execution if task shape changed.",
    },
    "user_html_blocker": {
        "status": "planning_gates_must_pass_before_execution",
    },
}

claim_file.write_text(
    "\n".join(
        [
            f"claim_date: {claim_doc['claim_date']}",
            f"wrk_id: {claim_doc['wrk_id']}",
            f"route: {claim_doc['route']}",
            f"orchestrator: {claim_doc['orchestrator']}",
            f"best_fit_provider: {claim_doc['best_fit_provider']}",
            f"alternate_provider: {claim_doc['alternate_provider']}",
            f"plan_workstations: {claim_doc['plan_workstations']}",
            f"execution_workstations: {claim_doc['execution_workstations']}",
            "quota_snapshot:",
            f"  source: {claim_doc['quota_snapshot']['source']}",
            f"  status: {claim_doc['quota_snapshot']['status']}",
            "agent_capability:",
            f"  best_fit: {claim_doc['agent_capability']['best_fit']}",
            f"  rationale: {claim_doc['agent_capability']['rationale']}",
            "user_html_blocker:",
            f"  status: {claim_doc['user_html_blocker']['status']}",
            "",
        ]
    ),
    encoding="utf-8",
)

upsert("status", "working")
upsert("claim_routing_ref", str(claim_file.relative_to(workspace_root)))
if quota_status == "available":
    upsert("claim_quota_snapshot_ref", quota_snapshot["source"])

path.write_text(f"---\n{frontmatter.rstrip()}\n---\n{body}", encoding="utf-8")
PY

VERIFY_SCRIPT="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
echo "Running gate evidence validator for ${WRK_ID}..."
if ! python3 "$VERIFY_SCRIPT" "$WRK_ID"; then
  echo "✖ Gate evidence verification failed for ${WRK_ID}; fix the missing artifacts before claiming." >&2
  exit 1
fi

mkdir -p "${QUEUE_DIR}/working"
mv "$FILE_PATH" "${QUEUE_DIR}/working/${WRK_ID}.md"

python3 "${QUEUE_DIR}/scripts/generate-index.py"

echo "✔ ${WRK_ID} claimed and moved to working/"
