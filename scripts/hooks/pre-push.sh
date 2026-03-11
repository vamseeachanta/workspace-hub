#!/usr/bin/env bash
# pre-push.sh — Pre-push CI gate
# WRK-1070: original stub (secrets + coverage).
# WRK-1064: extended with tier-1 repo quality + test gate.
#
# Usage (as git hook):
#   Called automatically by git push; stdin receives push refspecs.
#
# Environment overrides (for testing):
#   PRE_PUSH_DRY_RUN=1          — skip all real checks (no-op pass)
#   PRE_PUSH_CHECK_ALL_SCRIPT   — override path to check-all.sh
#   PRE_PUSH_RUN_TESTS_SCRIPT   — override path to run-all-tests.sh
#   PRE_PUSH_CHANGED_FILES      — override output of git diff --name-only
#   PRE_PUSH_BYPASS_LOG         — override path to bypass JSONL log
#   GIT_PRE_PUSH_SKIP=1         — soft bypass: log and exit 0 (audited)
set -euo pipefail

# ── Resolve paths ─────────────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CHECK_ALL="${PRE_PUSH_CHECK_ALL_SCRIPT:-${REPO_ROOT}/scripts/quality/check-all.sh}"
RUN_TESTS="${PRE_PUSH_RUN_TESTS_SCRIPT:-${REPO_ROOT}/scripts/testing/run-all-tests.sh}"
BYPASS_LOG="${PRE_PUSH_BYPASS_LOG:-${REPO_ROOT}/logs/hooks/pre-push-bypass.jsonl}"

TIER1_REPOS=(assetutilities digitalmodel worldenergydata assethold OGManufacturing)
ZERO_OID="0000000000000000000000000000000000000000"

# ── Argument parsing ──────────────────────────────────────────────────────────
RUN_ALL=false

for arg in "$@"; do
    case "$arg" in
        --all) RUN_ALL=true ;;
        --help)
            echo "Usage: pre-push.sh [--all] [--help]"
            echo ""
            echo "Pre-push CI gate for workspace-hub tier-1 repos."
            echo ""
            echo "Options:"
            echo "  --all   Run checks for all 5 tier-1 repos (ignore diff)"
            echo "  --help  Show this help and exit"
            echo ""
            echo "Environment:"
            echo "  GIT_PRE_PUSH_SKIP=1   Soft bypass — logs audit record and exits 0"
            exit 0
            ;;
    esac
done

# ── Read and buffer stdin (git passes push info here) ─────────────────────────
declare -a PUSH_LINES=()
while IFS=' ' read -r local_ref local_oid remote_ref remote_oid; do
    [[ -z "$local_ref" ]] && continue
    PUSH_LINES+=("${local_ref} ${local_oid} ${remote_ref} ${remote_oid}")
done

if [[ ${#PUSH_LINES[@]} -eq 0 ]]; then
    exit 0
fi

# Use first line to extract OIDs (multi-ref pushes are uncommon; first is sufficient
# for branch detection heuristics).
read -r FIRST_LOCAL_REF FIRST_LOCAL_OID FIRST_REMOTE_REF FIRST_REMOTE_OID \
    <<< "${PUSH_LINES[0]}"

# ── GIT_PRE_PUSH_SKIP soft bypass (checked before dry-run) ────────────────────
if [[ "${GIT_PRE_PUSH_SKIP:-0}" == "1" ]]; then
    TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    mkdir -p "$(dirname "$BYPASS_LOG")"
    printf '{"timestamp":"%s","local_ref":"%s","local_oid":"%s","remote_ref":"%s","remote_oid":"%s","operator":"GIT_PRE_PUSH_SKIP","exit_code":0}\n' \
        "$TIMESTAMP" \
        "$FIRST_LOCAL_REF" \
        "$FIRST_LOCAL_OID" \
        "$FIRST_REMOTE_REF" \
        "$FIRST_REMOTE_OID" \
        >> "$BYPASS_LOG"
    echo "[pre-push] GIT_PRE_PUSH_SKIP=1 — bypass logged to ${BYPASS_LOG}" >&2
    exit 0
fi

# ── Dry-run mode (used by tests to exercise parsing without real checks) ───────
if [[ "${PRE_PUSH_DRY_RUN:-0}" == "1" ]]; then
    exit 0
fi

# ── Delete-branch guard: local_oid all-zeros means branch deletion → skip ─────
if [[ "$FIRST_LOCAL_OID" == "$ZERO_OID" ]]; then
    echo "[pre-push] Delete-branch push detected — skipping CI gate." >&2
    exit 0
fi

# ── New-branch guard: remote_oid all-zeros → can't diff, run all repos ────────
if [[ "$FIRST_REMOTE_OID" == "$ZERO_OID" ]]; then
    echo "[pre-push] New branch — running all tier-1 repo checks." >&2
    RUN_ALL=true
fi

# ── Detect changed tier-1 repos ──────────────────────────────────────────────
declare -a REPOS_TO_CHECK=()

if [[ "$RUN_ALL" == "true" ]]; then
    REPOS_TO_CHECK=("${TIER1_REPOS[@]}")
else
    # Use override if set (for testing), otherwise run git diff
    if [[ -n "${PRE_PUSH_CHANGED_FILES:-}" ]]; then
        CHANGED_FILES="$PRE_PUSH_CHANGED_FILES"
    else
        CHANGED_FILES="$(git diff --name-only "${FIRST_REMOTE_OID}..${FIRST_LOCAL_OID}" 2>/dev/null || true)"
    fi

    for repo in "${TIER1_REPOS[@]}"; do
        if echo "$CHANGED_FILES" | grep -q "^${repo}/"; then
            REPOS_TO_CHECK+=("$repo")
        fi
    done

    # ── Config drift check on changed harness files (WRK-1094) ───────────────
    # Must run BEFORE the early exit so root-only harness pushes are checked.
    CONFIG_DRIFT_SCRIPT="${REPO_ROOT}/scripts/quality/check_config_drift.py"
    HARNESS_FILES=(CLAUDE.md AGENTS.md CODEX.md GEMINI.md)
    _harness_changed=false
    for hf in "${HARNESS_FILES[@]}"; do
        if echo "${CHANGED_FILES:-}" | grep -q "$hf"; then
            _harness_changed=true
            break
        fi
    done
    if [[ "$_harness_changed" == "true" && -f "$CONFIG_DRIFT_SCRIPT" ]]; then
        echo "[pre-push] Harness file changed — running config drift check..." >&2
        _HARNESS_EXIT=0
        uv run --no-project python "$CONFIG_DRIFT_SCRIPT" 2>&1 || _HARNESS_EXIT=$?
        # Config drift failures will propagate into OVERALL_EXIT after the early-exit
        # guard below — store result for use after repos loop.
        _HARNESS_DRIFT_EXIT=$_HARNESS_EXIT
    fi

    if [[ ${#REPOS_TO_CHECK[@]} -eq 0 ]]; then
        echo "[pre-push] No tier-1 repo changes detected — skipping repo CI gate." >&2
        exit "${_HARNESS_DRIFT_EXIT:-0}"
    fi
fi

# ── Run checks and tests for each affected repo ───────────────────────────────
OVERALL_EXIT=0

for repo in "${REPOS_TO_CHECK[@]}"; do
    echo "[pre-push] Checking repo: ${repo}" >&2

    if [[ -x "$CHECK_ALL" ]]; then
        if ! bash "$CHECK_ALL" --repo "$repo"; then
            echo "[pre-push] FAIL: check-all for ${repo}" >&2
            OVERALL_EXIT=1
        fi
    else
        echo "[pre-push] WARNING: check-all.sh not found at ${CHECK_ALL}" >&2
    fi

    if [[ -x "$RUN_TESTS" ]]; then
        if ! bash "$RUN_TESTS" --repo "$repo"; then
            echo "[pre-push] FAIL: run-all-tests for ${repo}" >&2
            OVERALL_EXIT=1
        fi
    else
        echo "[pre-push] WARNING: run-all-tests.sh not found at ${RUN_TESTS}" >&2
    fi
done

# ── Legacy gates from WRK-1070 (secrets + coverage) ─────────────────────────
if command -v gitleaks >/dev/null 2>&1; then
    bash "${REPO_ROOT}/scripts/security/secrets-scan.sh" || OVERALL_EXIT=1
else
    echo "[pre-push] gitleaks not installed — skipping secrets scan (install via pre-commit)" >&2
fi

BASELINE="${REPO_ROOT}/config/testing/coverage-baseline.yaml"
RATCHET="${REPO_ROOT}/scripts/testing/check_coverage_ratchet.py"

if [[ -f "$BASELINE" && -f "$RATCHET" ]]; then
    if [[ -n "${SKIP_COVERAGE_REASON:-}" ]]; then
        echo "[pre-push] Coverage gate bypassed. Reason: ${SKIP_COVERAGE_REASON}" >&2
        DATESTAMP="$(date +%Y%m%d)"
        REPORT_OUT="${REPO_ROOT}/scripts/testing/coverage-reports/bypass-coverage-${DATESTAMP}.txt"
        mkdir -p "${REPO_ROOT}/scripts/testing/coverage-reports"
        uv run --no-project python "$RATCHET" \
            --baseline "$BASELINE" \
            --results  "${REPO_ROOT}/scripts/testing/coverage-results.json" \
            --report-out "$REPORT_OUT" 2>/dev/null || true
    else
        bash "$RUN_TESTS" --coverage || OVERALL_EXIT=1
    fi
else
    echo "[pre-push] Coverage baseline or ratchet script not found — skipping coverage gate." >&2
fi

# ── Mypy ratchet gate (WRK-1092) — opt-in via MYPY_RATCHET_GATE=1 ───────────
# Mypy runs can take 60-180s across all repos; opt-in avoids slowing every push.
if [[ "${MYPY_RATCHET_GATE:-0}" == "1" ]]; then
    MYPY_RATCHET_SCRIPT="${REPO_ROOT}/scripts/quality/check_mypy_ratchet.py"
    MYPY_RATCHET_BASELINE="${REPO_ROOT}/config/quality/mypy-baseline.yaml"
    if [[ -f "$MYPY_RATCHET_SCRIPT" && -f "$MYPY_RATCHET_BASELINE" ]]; then
        echo "[pre-push] Running mypy ratchet gate..." >&2
        if ! uv run --no-project python "$MYPY_RATCHET_SCRIPT" \
                --baseline "$MYPY_RATCHET_BASELINE" \
                --repo-root "$REPO_ROOT"; then
            echo "[pre-push] FAIL: mypy ratchet gate" >&2
            OVERALL_EXIT=1
        fi
    else
        echo "[pre-push] WARNING: mypy ratchet script or baseline not found — skipping" >&2
    fi
fi

# ── Complexity ratchet gate (WRK-1095) — opt-in via COMPLEXITY_RATCHET_GATE=1 ─
# Radon runs can take 30-90s across all repos; opt-in avoids slowing every push.
if [[ "${COMPLEXITY_RATCHET_GATE:-0}" == "1" ]]; then
    COMPLEXITY_RATCHET_SCRIPT="${REPO_ROOT}/scripts/quality/check_complexity_ratchet.py"
    COMPLEXITY_RATCHET_BASELINE="${REPO_ROOT}/config/quality/complexity-baseline.yaml"
    if [[ -f "$COMPLEXITY_RATCHET_SCRIPT" && -f "$COMPLEXITY_RATCHET_BASELINE" ]]; then
        echo "[pre-push] Running complexity ratchet gate..." >&2
        if ! uv run --no-project python "$COMPLEXITY_RATCHET_SCRIPT" \
                --baseline "$COMPLEXITY_RATCHET_BASELINE" \
                --repo-root "$REPO_ROOT"; then
            echo "[pre-push] FAIL: complexity ratchet gate" >&2
            OVERALL_EXIT=1
        fi
    else
        echo "[pre-push] WARNING: complexity ratchet script or baseline not found — skipping" >&2
    fi
fi

# ── Config drift check — RUN_ALL path (WRK-1094) ────────────────────────────
# When RUN_ALL=true (new branch or --all flag), CHANGED_FILES is not set so the
# harness-change detection inside the else branch above did not run.  Run the
# full drift check unconditionally for new-branch / --all pushes.
if [[ "$RUN_ALL" == "true" ]]; then
    _CD_SCRIPT="${REPO_ROOT}/scripts/quality/check_config_drift.py"
    if [[ -f "$_CD_SCRIPT" ]]; then
        echo "[pre-push] RUN_ALL — running config drift check..." >&2
        uv run --no-project python "$_CD_SCRIPT" 2>&1 || OVERALL_EXIT=1
    fi
fi

# Propagate any harness-drift failure captured before the early-exit point.
if [[ "${_HARNESS_DRIFT_EXIT:-0}" -ne 0 ]]; then
    OVERALL_EXIT=1
fi

exit "$OVERALL_EXIT"
