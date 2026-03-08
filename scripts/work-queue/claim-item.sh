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
GATE_LOGGER="${WORKSPACE_ROOT}/scripts/work-queue/log-gate-event.sh"
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
EVIDENCE_DIR="${CLAIM_DIR}/evidence"
mkdir -p "$EVIDENCE_DIR"

# --- Stage 5 evidence gate (canonical checker — Phase 1B guard) ---------------
# claim-item.sh is an official Stage 6 downstream validator. Both exit 1 (predicate
# failure) and exit 2 (infrastructure failure) are fail-closed blocking outcomes.
STAGE5_CHECKER="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
if [[ ! -f "$STAGE5_CHECKER" ]]; then
    echo "✖ Stage 5 checker not found: ${STAGE5_CHECKER}" >&2
    echo "Repair the Stage 5 gate infrastructure before claiming." >&2
    exit 2
fi
stage5_exit=0
stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
    --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
if [[ "$stage5_exit" -eq 1 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Complete Stage 5 interactive review and evidence before claiming." >&2
    exit 1
elif [[ "$stage5_exit" -eq 2 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Repair the Stage 5 gate infrastructure before claiming." >&2
    exit 2
fi

# --- Stage 7 evidence gate (plan-final review required before claiming) -------
# claim-item.sh advances work past Stage 6 cross-review. The user must have
# confirmed plan-final-review.yaml before AI agents can proceed to execution.
# Both exit 1 (predicate failure) and exit 2 (infrastructure failure) are fail-closed.
stage7_exit=0
stage7_output="$(uv run --no-project python "$STAGE5_CHECKER" \
    --stage7-check "$WRK_ID" 2>&1)" || stage7_exit=$?
if [[ "$stage7_exit" -eq 1 ]]; then
    echo "✖ Stage 7 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage7_output" >&2
    echo "Complete Stage 7 plan-final review (evidence/plan-final-review.yaml) before claiming." >&2
    exit 1
elif [[ "$stage7_exit" -eq 2 ]]; then
    echo "✖ Stage 7 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
    echo "$stage7_output" >&2
    echo "Repair the Stage 7 gate infrastructure before claiming." >&2
    exit 2
fi

echo "Checking quota..."
QUOTA_STATUS="missing"
if [[ -f "$QUOTA_FILE" ]]; then
  QUOTA_STATUS="available"
else
  echo "⚠ Quota file missing: $QUOTA_FILE"
fi

uv run --no-project python - "$FILE_PATH" "$CLAIM_FILE" "$QUOTA_FILE" "$QUOTA_STATUS" "$WORKSPACE_ROOT" <<'PY'
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

# session_owner — from frontmatter provider
session_owner = provider or "unknown"

# agent_fit — derived from route + workstations + provider
exec_ws = execution_workstations or "unknown"
capability_match = "matched" if session_owner != "unknown" else "undocumented"
agent_fit_rationale = (
    f"Route {route or '?'} / execution_workstations={exec_ws} / provider={session_owner}"
)

# blocking_state — from frontmatter blocked_by (handle inline [] and YAML block format)
blocked_by_raw = get_value("blocked_by")  # captures inline `blocked_by: [WRK-XXX]`
if not blocked_by_raw or not blocked_by_raw.strip("[]").strip():
    # YAML block format:  blocked_by:\n  - WRK-NNN
    block_match = re.search(
        r"^blocked_by:\s*\n((?:[ \t]+-[^\n]*\n?)*)", frontmatter, re.MULTILINE
    )
    if block_match:
        blocked_by_list = [
            item.strip().lstrip("-").strip()
            for item in block_match.group(1).splitlines()
            if item.strip().lstrip("-").strip()
        ]
    else:
        blocked_by_list = []
else:
    blocked_by_list = [
        x.strip().strip("-").strip()
        for x in blocked_by_raw.strip("[]").split(",")
        if x.strip().strip("-").strip()
    ]
is_blocked = len(blocked_by_list) > 0

# quota_snapshot — ISO8601 timestamp; pct_remaining from agent-quota-latest.json
import json
now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
quota_pct = None
quota_status_val = "unknown"
quota_source = quota_file
if Path(quota_file).exists():
    quota_source = str(Path(quota_file).relative_to(workspace_root))
    try:
        qdata = json.loads(Path(quota_file).read_text(encoding="utf-8"))
        for agent in qdata.get("agents", []):
            if agent.get("provider") == session_owner:
                quota_pct = agent.get("pct_remaining")
                quota_status_val = (
                    "available" if quota_pct is None or quota_pct > 10 else "rate-limited"
                )
                break
        else:
            quota_status_val = "available"  # file present, provider not found → optimistic
    except Exception:
        quota_status_val = "unknown"

pct_str = str(quota_pct) if quota_pct is not None else "null"
blocked_by_yaml = "[" + ", ".join(blocked_by_list) + "]" if blocked_by_list else "[]"

claim_file.write_text(
    "\n".join([
        f"claim_date: \"{now_str}\"",
        f"wrk_id: \"{wrk_id}\"",
        f"route: \"{route}\"",
        f"orchestrator: \"{orchestrator}\"",
        f"best_fit_provider: \"{provider or 'unknown'}\"",
        f"alternate_provider: \"{provider_alt}\"",
        f"metadata_version: \"1\"",
        f"session_owner: \"{session_owner}\"",
        "agent_fit:",
        f"  capability_match: \"{capability_match}\"",
        f"  rationale: \"{agent_fit_rationale}\"",
        "blocking_state:",
        f"  blocked: {'true' if is_blocked else 'false'}",
        f"  blocked_by: {blocked_by_yaml}",
        "  notes: \"\"",
        "quota_snapshot:",
        f"  timestamp: \"{now_str}\"",
        f"  provider: \"{session_owner}\"",
        f"  status: \"{quota_status_val}\"",
        f"  pct_remaining: {pct_str}",
        f"  source: \"{quota_source}\"",
        "",
    ]),
    encoding="utf-8",
)

# Bootstrap per-WRK stage evidence ledger from template for mandatory close validation.
stage_evidence_dir = claim_file.parent / "evidence"
stage_evidence_dir.mkdir(parents=True, exist_ok=True)
stage_evidence_file = stage_evidence_dir / "stage-evidence.yaml"
if not stage_evidence_file.exists():
    template_path = workspace_root / "specs" / "templates" / "stage-evidence-template.yaml"
    if template_path.exists():
        template_text = template_path.read_text(encoding="utf-8")
    else:
        # Minimal fallback keeps claim path unblocked even if template is missing.
        template_text = (
            "wrk_id: WRK-000\n"
            "generated_at: \"2026-03-03T00:00:00Z\"\n"
            "reviewed_by: \"agent\"\n"
            "stages:\n"
            "  - order: 1\n"
            "    stage: Capture\n"
            "    status: done\n"
            "    evidence: .claude/work-queue/working/WRK-000.md\n"
        )
    template_text = template_text.replace("WRK-000", wrk_id)
    template_text = template_text.replace("2026-03-03T00:00:00Z", now_str)
    stage_evidence_file.write_text(template_text, encoding="utf-8")

upsert("status", "working")
upsert("claim_routing_ref", str(claim_file.relative_to(workspace_root)))
upsert("stage_evidence_ref", str(stage_evidence_file.relative_to(workspace_root)))
if quota_status_val == "available":
    upsert("claim_quota_snapshot_ref", quota_source)

path.write_text(f"---\n{frontmatter.rstrip()}\n---\n{body}", encoding="utf-8")
PY

# Explicit activation gate: set active WRK and record activation evidence.
SET_ACTIVE_SCRIPT="${WORKSPACE_ROOT}/scripts/work-queue/set-active-wrk.sh"
if ! bash "$SET_ACTIVE_SCRIPT" "$WRK_ID" >/dev/null; then
  echo "✖ Failed to set active WRK for ${WRK_ID}." >&2
  exit 1
fi

SESSION_STATE="${WORKSPACE_ROOT}/.claude/state/session-state.yaml"
SESSION_ID="$(awk -F': ' '/^session_id:/ {gsub(/"/, "", $2); print $2; exit}' "$SESSION_STATE" 2>/dev/null || true)"
ORCH_AGENT="$(awk -F': ' '/^orchestrator_agent:/ {gsub(/"/, "", $2); print $2; exit}' "$SESSION_STATE" 2>/dev/null || true)"
if [[ -z "$SESSION_ID" ]]; then
  SESSION_ID="unknown"
fi
if [[ -z "$ORCH_AGENT" ]]; then
  ORCH_AGENT="${provider:-unknown}"
fi

cat > "${EVIDENCE_DIR}/activation.yaml" <<EOF
wrk_id: "${WRK_ID}"
set_active_wrk: true
active_wrk_ref: ".claude/state/active-wrk"
session_id: "${SESSION_ID}"
orchestrator_agent: "${ORCH_AGENT}"
activated_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "claim" "set_active_wrk" "$ORCH_AGENT" "activation evidence captured"
fi

# Bootstrap close user-review evidence files so all WRKs start with required artifacts.
if [[ ! -f "${EVIDENCE_DIR}/user-review-close.yaml" ]]; then
  cat > "${EVIDENCE_DIR}/user-review-close.yaml" <<EOF
reviewer: ""
reviewed_at: ""
confirmed_at: ""
decision: pending
notes: "Populate at Stage 17 user review before closing."
EOF
fi

if [[ ! -f "${EVIDENCE_DIR}/user-review-browser-open.yaml" ]]; then
  cat > "${EVIDENCE_DIR}/user-review-browser-open.yaml" <<'EOF'
events: []
EOF
fi

VERIFY_SCRIPT="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"
echo "Running gate evidence validator for ${WRK_ID}..."
if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "claim" "verify_gate_evidence_start" "$ORCH_AGENT" "phase=claim"
fi
if ! uv run --no-project python "$VERIFY_SCRIPT" "$WRK_ID" --phase claim; then
  if [[ -x "$GATE_LOGGER" ]]; then
    bash "$GATE_LOGGER" "$WRK_ID" "claim" "verify_gate_evidence_fail" "$ORCH_AGENT" "phase=claim"
  fi
  echo "✖ Gate evidence verification failed for ${WRK_ID}; fix the missing artifacts before claiming." >&2
  exit 1
fi

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$WRK_ID" "claim" "verify_gate_evidence_pass" "$ORCH_AGENT" "phase=claim"
  bash "$GATE_LOGGER" "$WRK_ID" "claim" "claim_evidence" "$ORCH_AGENT" "claim gate verified"
fi

# Best-effort stage progress update for claim/activation stage.
STAGE_UPDATER="${WORKSPACE_ROOT}/scripts/work-queue/update-stage-evidence.py"
if [[ -f "$STAGE_UPDATER" ]]; then
  uv run --no-project python "$STAGE_UPDATER" "$WRK_ID" --order 8 --status done --reviewed-by "$ORCH_AGENT" >/dev/null || \
    echo "⚠ Could not update stage-evidence order 8 for ${WRK_ID}" >&2
fi

mkdir -p "${QUEUE_DIR}/working"
mv "$FILE_PATH" "${QUEUE_DIR}/working/${WRK_ID}.md"

uv run --no-project python "${QUEUE_DIR}/scripts/generate-index.py"

echo "✔ ${WRK_ID} claimed and moved to working/"
