#!/usr/bin/env bash
# capture-wrk-summary.sh — Append a WRK completion entry to knowledge-base/wrk-completions.jsonl
# Usage: capture-wrk-summary.sh <WRK-NNN>
# Best-effort, non-blocking: always exits 0
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:-}"
KNOWLEDGE_BASE_DIR="${KNOWLEDGE_BASE_DIR:-${REPO_ROOT}/knowledge-base}"
WORK_QUEUE_DIR="${WORK_QUEUE_DIR:-${REPO_ROOT}/.claude/work-queue}"
FLOCK_TIMEOUT="${FLOCK_TIMEOUT:-5}"
JSONL_FILE="${KNOWLEDGE_BASE_DIR}/wrk-completions.jsonl"
LOCK_FILE="${JSONL_FILE}.lock"

log_warn() { echo "[capture-wrk-summary] WARN: $*" >&2; }

if [[ -z "${WRK_ID}" ]]; then
    log_warn "No WRK_ID supplied"
    exit 0
fi

# Find WRK file in known locations
find_wrk_file() {
    local id="$1"
    local locations=(
        "${WORK_QUEUE_DIR}/working/${id}.md"
        "${WORK_QUEUE_DIR}/done/${id}.md"
        "${WORK_QUEUE_DIR}/archive/${id}.md"
        "${WORK_QUEUE_DIR}/pending/${id}.md"
    )
    # Also check YYYY-MM sharded archive
    if compgen -G "${WORK_QUEUE_DIR}/archive/*/${id}.md" > /dev/null 2>&1; then
        echo "${WORK_QUEUE_DIR}/archive"/*/"${id}.md" | head -1
        return
    fi
    for loc in "${locations[@]}"; do
        if [[ -f "${loc}" ]]; then
            echo "${loc}"
            return
        fi
    done
    echo ""
}

WRK_FILE="$(find_wrk_file "${WRK_ID}")"
if [[ -z "${WRK_FILE}" ]]; then
    log_warn "WRK file not found for ${WRK_ID} — skipping knowledge capture"
    exit 0
fi

# Parse frontmatter fields
parse_frontmatter() {
    local file="$1" field="$2"
    awk -v field="${field}" '
        /^---$/{if(in_fm){exit}; in_fm=1; next}
        in_fm && $0 ~ "^"field":"{
            sub("^"field":[ ]*",""); gsub(/^"|"$/,""); print; exit
        }
    ' "${file}"
}

TITLE="$(parse_frontmatter "${WRK_FILE}" "title")"
CATEGORY="$(parse_frontmatter "${WRK_FILE}" "category")"
SUBCATEGORY="$(parse_frontmatter "${WRK_FILE}" "subcategory")"
ARCHIVED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Extract ## Mission section (first 500 chars)
MISSION="$(awk '/^## Mission/{found=1; next} found && /^##/{exit} found{print}' "${WRK_FILE}" \
    | tr -s ' \n' ' ' | cut -c1-500 | sed 's/["\]/\\&/g')"

# Extract patterns from resource-intelligence.yaml (best-effort)
PATTERNS_JSON="[]"
RI_YAML="${WORK_QUEUE_DIR}/assets/${WRK_ID}/evidence/resource-intelligence.yaml"
if [[ -f "${RI_YAML}" ]]; then
    if uv run --no-project python -c "import yaml" 2>/dev/null; then
        PATTERNS_JSON="$(uv run --no-project python - "${RI_YAML}" <<'PYEOF' 2>/dev/null || echo '[]'
import yaml, json, sys
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f)
    gaps = data.get("top_p2_gaps", []) or []
    constraints = data.get("constraints", []) or []
    items = (gaps + constraints)[:5]
    print(json.dumps([str(i) for i in items]))
except Exception:
    print("[]")
PYEOF
)"
    fi
fi

# Extract follow-ons from future-work.yaml (best-effort)
FOLLOW_ONS_JSON="[]"
FW_YAML="${WORK_QUEUE_DIR}/assets/${WRK_ID}/evidence/future-work.yaml"
if [[ -f "${FW_YAML}" ]]; then
    FOLLOW_ONS_JSON="$(uv run --no-project python - "${FW_YAML}" <<'PYEOF' 2>/dev/null || echo '[]'
import yaml, json, sys
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f)
    recs = data.get("recommendations", []) or []
    ids = [r.get("id","") for r in recs if r.get("id")]
    print(json.dumps(ids[:10]))
except Exception:
    print("[]")
PYEOF
)"
fi

# Build JSON entry
ENTRY="$(uv run --no-project python - \
    "${WRK_ID}" "${CATEGORY}" "${SUBCATEGORY}" "${TITLE}" \
    "${ARCHIVED_AT}" "${MISSION}" "${PATTERNS_JSON}" "${FOLLOW_ONS_JSON}" <<'PYEOF'
import json, sys
wrk_id, category, subcategory, title, archived_at, mission, patterns_json, follow_ons_json = sys.argv[1:9]
print(json.dumps({
    "id": wrk_id,
    "type": "wrk",
    "category": category,
    "subcategory": subcategory,
    "title": title,
    "archived_at": archived_at,
    "source": "capture-wrk-summary",
    "mission": mission,
    "patterns": json.loads(patterns_json),
    "follow_ons": json.loads(follow_ons_json),
}))
PYEOF
)"

# Ensure knowledge-base dir exists
mkdir -p "${KNOWLEDGE_BASE_DIR}" || { log_warn "Cannot create ${KNOWLEDGE_BASE_DIR}"; exit 0; }

# Idempotent append inside flock
(
    flock -w "${FLOCK_TIMEOUT}" 200 || { log_warn "Lock timeout for ${JSONL_FILE}"; exit 0; }
    # Check for existing entry
    if [[ -f "${JSONL_FILE}" ]] && grep -q "\"${WRK_ID}\"" "${JSONL_FILE}" 2>/dev/null; then
        echo "[capture-wrk-summary] Skipping ${WRK_ID} — already in knowledge-base" >&2
    else
        echo "${ENTRY}" >> "${JSONL_FILE}"
        echo "[capture-wrk-summary] Captured ${WRK_ID} → ${JSONL_FILE}" >&2
    fi
) 200>"${LOCK_FILE}" || exit 0

exit 0
