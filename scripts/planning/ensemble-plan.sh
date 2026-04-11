#!/usr/bin/env bash
# ensemble-plan.sh [--dry-run] [--skip-ensemble] <WRK-NNN>
# Launches 9 planning agents in parallel (3xClaude, 3xCodex, 3xGemini) and
# synthesises their outputs into a single de-biased plan.
#
# Exit codes:
#   0  synthesis complete (plan_ensemble set to true in frontmatter)
#   1  synthesis failed or unresolved SPLIT decisions remain
#   2  bad arguments / WRK not found
#   3  skipped (plan_ensemble already true or --skip-ensemble passed)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"
AGENTS_LIB="${WS_HUB}/scripts/agents/lib"
ENSEMBLE_TIMEOUT="${ENSEMBLE_TIMEOUT:-180}"
# Portable timeout: prefer GNU timeout, fall back to gtimeout (macOS/Homebrew)
if command -v timeout >/dev/null 2>&1; then
    _timeout() { timeout "$@"; }
elif command -v gtimeout >/dev/null 2>&1; then
    _timeout() { gtimeout "$@"; }
else
    echo "WARN: timeout command not found — agent calls will run without time limit" >&2
    _timeout() { shift; "$@"; }  # skip the duration arg
fi

DRY_RUN=false
SKIP=false
WRK_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)       DRY_RUN=true; shift ;;
        --skip-ensemble) SKIP=true;    shift ;;
        WRK-*)           WRK_ID="$1";  shift ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$WRK_ID" ]] && { echo "Usage: ensemble-plan.sh [--dry-run] [--skip-ensemble] <WRK-NNN>" >&2; exit 2; }

resolve_wrk_file() {
    local wrk_id="$1"
    local candidate
    for candidate in \
        "${WS_HUB}/.claude/work-queue/${wrk_id}.md" \
        "${WS_HUB}/.claude/work-queue/pending/${wrk_id}.md" \
        "${WS_HUB}/.claude/work-queue/working/${wrk_id}.md" \
        "${WS_HUB}/.claude/work-queue/done/${wrk_id}.md" \
        "${WS_HUB}/.claude/work-queue/archive/${wrk_id}.md" \
        "${WS_HUB}/.planning/${wrk_id}.md" \
        "${WS_HUB}/.planning/${wrk_id}/plan.md" \
        "${WS_HUB}/docs/plans/${wrk_id}.md"
    do
        [[ -f "$candidate" ]] && { printf '%s\n' "$candidate"; return 0; }
    done

    candidate="$(find "${WS_HUB}/.claude/work-queue" "${WS_HUB}/.planning" "${WS_HUB}/docs/plans" \
        -type f \( -name "${wrk_id}.md" -o -name "${wrk_id}*.md" -o -path "*/${wrk_id}/plan.md" \) 2>/dev/null | head -1 || true)"
    [[ -n "$candidate" ]] && { printf '%s\n' "$candidate"; return 0; }
    return 1
}

wrk_get_frontmatter_value() {
    local file="$1" key="$2"
    uv run --no-project python - "$file" "$key" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = sys.argv[2]
text = path.read_text(encoding='utf-8', errors='replace')
if not text.startswith('---\n'):
    raise SystemExit(0)
parts = text.split('\n---\n', 1)
if len(parts) != 2:
    raise SystemExit(0)
for line in parts[0].splitlines()[1:]:
    if ':' not in line:
        continue
    k, v = line.split(':', 1)
    if k.strip() == key:
        print(v.strip())
        break
PY
}

wrk_set_frontmatter_value() {
    local file="$1" key="$2" value="$3"
    uv run --no-project python - "$file" "$key" "$value" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]
text = path.read_text(encoding='utf-8', errors='replace')
if text.startswith('---\n') and '\n---\n' in text:
    frontmatter, body = text.split('\n---\n', 1)
    lines = frontmatter.splitlines()
    replaced = False
    for idx in range(1, len(lines)):
        if ':' not in lines[idx]:
            continue
        k, _ = lines[idx].split(':', 1)
        if k.strip() == key:
            lines[idx] = f"{key}: {value}"
            replaced = True
            break
    if not replaced:
        lines.append(f"{key}: {value}")
    new_text = '\n'.join(lines) + '\n---\n' + body
else:
    new_text = f"---\n{key}: {value}\n---\n" + text
path.write_text(new_text, encoding='utf-8')
PY
}

if [[ "$SKIP" == "true" ]]; then
    echo "Ensemble gate skipped for $WRK_ID (plan_ensemble=unset, --skip-ensemble=${SKIP})"
    exit 3
fi

RESULTS_DIR="${SCRIPT_DIR}/results/${WRK_ID}-ensemble"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "--- Ensemble Planning Manifest for ${WRK_ID} (DRY RUN) ---"
    echo "  Providers: claude (conservative, creative, adversarial)"
    echo "             codex  (feasibility, architecture, testing)"
    echo "             gemini (risks, simple, extensibility)"
    echo "  Results  : ${RESULTS_DIR}"
    echo "  Timeout  : ${ENSEMBLE_TIMEOUT}s per agent"
    exit 0
fi

WRK_FILE="$(resolve_wrk_file "$WRK_ID")" || { echo "ERROR: $WRK_ID not found in queue" >&2; exit 2; }

# Skip if already done
current="$(wrk_get_frontmatter_value "$WRK_FILE" "plan_ensemble" 2>/dev/null || echo "")"
if [[ "$current" == "true" ]] || [[ "$current" == "skip" ]]; then
    echo "Ensemble gate skipped for $WRK_ID (plan_ensemble=${current:-unset}, --skip-ensemble=${SKIP})"
    exit 3
fi

# Provider availability checks (warn only - missing provider degrades, not fatal)
for provider in claude codex gemini; do
    if ! command -v "$provider" >/dev/null 2>&1; then
        echo "WARN: $provider CLI not found - its 3 agent slots will emit NO_OUTPUT" >&2
    fi
done

mkdir -p "$RESULTS_DIR"

# Extract shared context from WRK file
_section() {
    local hdr="$1" file="$2"
    awk "/^## ${hdr}/{f=1;next} f && /^## /{f=0} f" "$file"
}

TITLE="$(wrk_get_frontmatter_value "$WRK_FILE" "title")"
WHAT="$(_section "What" "$WRK_FILE")"
WHY="$(_section "Why" "$WRK_FILE")"
AC="$(_section "Acceptance Criteria" "$WRK_FILE")"

SHARED_CONTEXT="Work Item: ${WRK_ID}
Title: ${TITLE}

## What
${WHAT}

## Why
${WHY}

## Acceptance Criteria
${AC}"

# --- Agent dispatch ----------------------------------------------------------

_run_claude() {
    local stance="$1"
    local out="${RESULTS_DIR}/claude-${stance}.md"
    local prompt_file="${PROMPTS_DIR}/claude-${stance}.md"
    [[ -f "$prompt_file" ]] || { echo "ERROR: missing prompt ${prompt_file}" > "$out"; return 0; }
    command -v claude >/dev/null 2>&1 || { echo "NO_OUTPUT: claude CLI unavailable" > "$out"; return 0; }
    # claude -p "<instruction>" with context on stdin (independent stateless API call)
    echo "$SHARED_CONTEXT" \
        | _timeout "$ENSEMBLE_TIMEOUT" claude -p "$(cat "$prompt_file")" \
        > "$out" 2>&1 \
        || echo "ERROR: claude ${stance} exited $?" >> "$out"
}

_run_codex() {
    local stance="$1"
    local out="${RESULTS_DIR}/codex-${stance}.md"
    local prompt_file="${PROMPTS_DIR}/codex-${stance}.md"
    [[ -f "$prompt_file" ]] || { echo "ERROR: missing prompt ${prompt_file}" > "$out"; return 0; }
    command -v codex >/dev/null 2>&1 || { echo "NO_OUTPUT: codex CLI unavailable" > "$out"; return 0; }
    # codex exec - reads full content from stdin
    printf "%s\n\n---\nCONTEXT:\n%s" "$(cat "$prompt_file")" "$SHARED_CONTEXT" \
        | _timeout "$ENSEMBLE_TIMEOUT" codex exec - \
        > "$out" 2>&1 \
        || echo "ERROR: codex ${stance} exited $?" >> "$out"
}

_run_gemini() {
    local stance="$1"
    local out="${RESULTS_DIR}/gemini-${stance}.md"
    local err="${RESULTS_DIR}/gemini-${stance}.err"
    local prompt_file="${PROMPTS_DIR}/gemini-${stance}.md"
    [[ -f "$prompt_file" ]] || { echo "ERROR: missing prompt ${prompt_file}" > "$out"; return 0; }
    command -v gemini >/dev/null 2>&1 || { echo "NO_OUTPUT: gemini CLI unavailable" > "$out"; return 0; }
    # gemini: -p takes instruction; context piped via stdin
    # Separate stderr from stdout to detect exit-0-on-capacity-error (#1326)
    echo "$SHARED_CONTEXT" \
        | _timeout "$ENSEMBLE_TIMEOUT" gemini -p "$(cat "$prompt_file")" -y \
        > "$out" 2>"$err" \
        || echo "ERROR: gemini ${stance} exited $?" >> "$out"
    # Detect empty stdout with capacity errors on stderr (gemini exits 0)
    local out_size; out_size=$(wc -c < "$out" 2>/dev/null || echo 0)
    if [[ $out_size -lt 50 ]] && grep -qE "RESOURCE_EXHAUSTED|MODEL_CAPACITY_EXHAUSTED|429" "$err" 2>/dev/null; then
        echo "NO_OUTPUT: gemini capacity exhausted (exit 0, stderr has 429)" > "$out"
        head -3 "$err" | sed 's/^/# /' >> "$out"
    fi
}

# --- Parallel execution ------------------------------------------------------
echo "--- Ensemble Planning: ${WRK_ID} (timeout ${ENSEMBLE_TIMEOUT}s per agent) ---"

_run_claude conservative &
_run_claude creative     &
_run_claude adversarial  &
_run_codex  feasibility  &
_run_codex  architecture &
_run_codex  testing      &
_run_gemini risks        &
_run_gemini simple       &
_run_gemini extensibility &

wait
echo "--- All 9 agent slots finished ---"

# --- Synthesis ---------------------------------------------------------------
echo "--- Running synthesis ---"
synthesis_exit=0
"${SCRIPT_DIR}/synthesise.sh" "$RESULTS_DIR" "$WRK_FILE" || synthesis_exit=$?

if [[ $synthesis_exit -eq 0 ]]; then
    wrk_set_frontmatter_value "$WRK_FILE" "plan_ensemble" "true"
    score="$(grep "^CONSENSUS_SCORE:" "${RESULTS_DIR}/synthesis.md" 2>/dev/null \
             | grep -o '[0-9]\+' | head -1 || echo "")"
    [[ -n "$score" ]] && wrk_set_frontmatter_value "$WRK_FILE" "ensemble_consensus_score" "$score"
    echo ""
    echo "Ensemble complete. Synthesis: ${RESULTS_DIR}/synthesis.md"
    echo "Next: read synthesis.md, resolve any SPLIT decisions, write ## Plan in ${WRK_FILE}"
    exit 0
else
    echo "ERROR: synthesis failed or SPLIT decisions require resolution (exit ${synthesis_exit})" >&2
    echo "       See: ${RESULTS_DIR}/synthesis.md" >&2
    exit 1
fi
