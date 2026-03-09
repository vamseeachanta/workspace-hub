#!/usr/bin/env bash
# generate-review-input.sh — Auto-generate cross-review input from WRK item + git diff
#
# Usage:
#   generate-review-input.sh WRK-NNN [--phase N]
#
# Outputs:
#   scripts/review/results/wrk-NNN-phase-N-review-input.md
#
# After generation, pipe into cross-review.sh:
#   scripts/review/cross-review.sh results/wrk-NNN-phase-N-review-input.md all
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
RESULTS_DIR="${SCRIPT_DIR}/results"

# ── Arg parsing ───────────────────────────────────────────────────────────────

usage() {
    echo "Usage: generate-review-input.sh WRK-NNN [--phase N]" >&2
    echo "  WRK-NNN   Work item ID (required)" >&2
    echo "  --phase N Phase number for output filename (default: 1)" >&2
    exit 1
}

WRK_ID=""
PHASE=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        WRK-[0-9]*)
            WRK_ID="$1"; shift ;;
        --phase)
            [[ $# -lt 2 ]] && { echo "ERROR: --phase requires a numeric value" >&2; exit 1; }
            PHASE="$2"
            [[ "$PHASE" =~ ^[0-9]+$ ]] || { echo "ERROR: --phase must be numeric, got: $PHASE" >&2; exit 1; }
            shift 2 ;;
        -h|--help)
            usage ;;
        *)
            echo "ERROR: unknown argument: $1" >&2; usage ;;
    esac
done

[[ -z "$WRK_ID" ]] && { echo "ERROR: WRK-NNN argument required" >&2; usage; }

# ── Locate WRK item ───────────────────────────────────────────────────────────

# Allow test override of queue root
QUEUE_DIR="${WRK_QUEUE_DIR:-${REPO_ROOT}/.claude/work-queue}"

WRK_FILE=""
for dir in pending working; do
    candidate="${QUEUE_DIR}/${dir}/${WRK_ID}.md"
    if [[ -f "$candidate" ]]; then
        WRK_FILE="$candidate"
        break
    fi
done

if [[ -z "$WRK_FILE" ]]; then
    echo "ERROR: WRK item not found: ${WRK_ID} (checked pending/ and working/)" >&2
    exit 1
fi

# ── Parse frontmatter ─────────────────────────────────────────────────────────

get_field() {
    local field="$1" file="$2"
    awk -v f="$field" '
        /^---$/ { fm_count++; if (fm_count == 2) exit; next }
        fm_count == 1 && $0 ~ "^"f":" {
            sub("^"f":[ ]*", "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
    ' "$file"
}

TITLE="$(get_field "title" "$WRK_FILE")"
COMPLEXITY="$(get_field "complexity" "$WRK_FILE")"
ROUTE="$(get_field "route" "$WRK_FILE")"
SUBCATEGORY="$(get_field "subcategory" "$WRK_FILE")"
TARGET_REPOS_RAW="$(get_field "target_repos" "$WRK_FILE")"

# Defaults for missing fields
TITLE="${TITLE:-not specified}"
COMPLEXITY="${COMPLEXITY:-not specified}"
ROUTE="${ROUTE:-not specified}"
SUBCATEGORY="${SUBCATEGORY:-not specified}"

# Extract mission paragraph (content after ## Mission, before next ##)
MISSION="$(awk '
    /^## Mission/ { in_mission=1; next }
    in_mission && /^## / { exit }
    in_mission { print }
' "$WRK_FILE" | sed '/^$/d' | head -20)"
MISSION="${MISSION:-not specified}"

# Extract acceptance criteria (lines starting with - [ ] or - [x])
ACS="$(grep -E '^\s*- \[[ x]\]' "$WRK_FILE" 2>/dev/null || echo "not specified")"

# Parse target_repos from YAML list (handles [a, b] and empty [])
TARGET_REPOS=()
if [[ -n "$TARGET_REPOS_RAW" && "$TARGET_REPOS_RAW" != "[]" ]]; then
    while IFS= read -r repo; do
        repo="$(echo "$repo" | tr -d ' [],')"
        [[ -n "$repo" ]] && TARGET_REPOS+=("$repo")
    done < <(echo "$TARGET_REPOS_RAW" | tr ',' '\n')
fi

# ── Git diff (scoped or full) ─────────────────────────────────────────────────

# Verify we're in a git repo
if ! git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: not inside a git repository: ${REPO_ROOT}" >&2
    exit 1
fi

# Allow test injection of diff line count for truncation test
if [[ -n "${_TEST_INJECT_DIFF_LINES:-}" ]] && [[ "$_TEST_INJECT_DIFF_LINES" -gt 0 ]]; then
    # Generate synthetic diff for testing
    DIFF_CONTENT="$(awk -v n="$_TEST_INJECT_DIFF_LINES" 'BEGIN{for(i=1;i<=n;i++) print "+line "i}')"
    DIFF_LINE_COUNT="$_TEST_INJECT_DIFF_LINES"
else
    # Build scoped or full diff
    VALID_REPOS=()
    for repo in "${TARGET_REPOS[@]:-}"; do
        repo_path="${REPO_ROOT}/${repo}"
        if [[ -d "$repo_path" ]]; then
            VALID_REPOS+=("$repo")
        else
            echo "WARN: target_repo not found, skipping: ${repo}" >&2
        fi
    done

    if [[ ${#VALID_REPOS[@]} -gt 0 ]]; then
        DIFF_CONTENT="$(git -C "$REPO_ROOT" diff HEAD -- "${VALID_REPOS[@]}" 2>/dev/null || true)"
    else
        DIFF_CONTENT="$(git -C "$REPO_ROOT" diff HEAD 2>/dev/null || true)"
    fi

    DIFF_LINE_COUNT=0
    [[ -n "$DIFF_CONTENT" ]] && DIFF_LINE_COUNT="$(echo "$DIFF_CONTENT" | wc -l | tr -d ' ')"
fi

# Truncate diff if >300 lines
DIFF_TRUNCATED=false
DIFF_MAX=300
if [[ "$DIFF_LINE_COUNT" -gt "$DIFF_MAX" ]]; then
    DIFF_CONTENT="$(echo "$DIFF_CONTENT" | head -n "$DIFF_MAX")"
    DIFF_TRUNCATED=true
fi

# Changed files list
if [[ -n "${_TEST_INJECT_DIFF_LINES:-}" ]]; then
    CHANGED_FILES="(synthetic diff — ${DIFF_LINE_COUNT} lines)"
else
    CHANGED_FILES="$(git -C "$REPO_ROOT" diff HEAD --name-only 2>/dev/null || echo "(no changes detected)")"
    [[ -z "$CHANGED_FILES" ]] && CHANGED_FILES="(no changes detected)"
fi

# ── Checkpoint summary ────────────────────────────────────────────────────────

CHECKPOINT_FILE="${QUEUE_DIR}/assets/${WRK_ID}/checkpoint.yaml"
CHECKPOINT_SUMMARY="not available"
if [[ -f "$CHECKPOINT_FILE" && -s "$CHECKPOINT_FILE" ]]; then
    CHECKPOINT_SUMMARY="$(awk '/^context_summary:/ {
        sub(/^context_summary:[ ]*/, "")
        gsub(/^["'"'"']|["'"'"']$/, "")
        print; exit
    }' "$CHECKPOINT_FILE")"
    CHECKPOINT_SUMMARY="${CHECKPOINT_SUMMARY:-not available}"
fi

# ── Test snapshot ─────────────────────────────────────────────────────────────

TEST_SNAPSHOT="not available"
TEST_RESULTS_DIR="${REPO_ROOT}/scripts/testing/results"
if [[ -d "$TEST_RESULTS_DIR" ]]; then
    LATEST_TEST="$(ls -t "${TEST_RESULTS_DIR}"/*.md 2>/dev/null | head -n 1 || true)"
    if [[ -n "$LATEST_TEST" && -s "$LATEST_TEST" ]]; then
        TEST_SNAPSHOT="$(head -30 "$LATEST_TEST")"
    fi
fi

# ── Review focus prompts ──────────────────────────────────────────────────────

generate_focus_prompts() {
    local subcategory="$1" complexity="$2"
    local prompts=()

    case "$complexity" in
        complex)
            prompts+=("1. Assess architectural decisions — are abstractions appropriate for the scope?")
            prompts+=("2. Check for unintended side effects on shared infrastructure.")
            ;;
        medium)
            prompts+=("1. Verify correctness of core logic against each acceptance criterion.")
            prompts+=("2. Check error handling — are all failure modes handled gracefully?")
            ;;
        *)
            prompts+=("1. Confirm the change does exactly what the AC specifies, nothing more.")
            ;;
    esac

    case "$subcategory" in
        *cross-review*)
            prompts+=("3. Verify the output format is valid input for cross-review.sh.")
            prompts+=("4. Check that all 3 provider review sections are structurally consistent.")
            ;;
        *security*)
            prompts+=("3. Check for injection vulnerabilities or exposed secrets.")
            ;;
        *test*|*tdd*)
            prompts+=("3. Verify test isolation — no shared state between test cases.")
            ;;
        *harness*|*automation*)
            prompts+=("3. Confirm the automation is idempotent — safe to re-run.")
            prompts+=("4. Check that failure modes produce clear error messages.")
            ;;
        *)
            prompts+=("3. Assess test coverage — are edge cases covered?")
            ;;
    esac

    prompts+=("$(( ${#prompts[@]} + 1 )). Confirm no hardcoded paths or secrets introduced.")

    printf '%s\n' "${prompts[@]}"
}

# ── Write output ──────────────────────────────────────────────────────────────

mkdir -p "$RESULTS_DIR"
WRK_LOWER="$(echo "$WRK_ID" | tr '[:upper:]' '[:lower:]')"
OUTPUT_FILE="${RESULTS_DIR}/${WRK_LOWER}-phase-${PHASE}-review-input.md"

{
    echo "# ${WRK_ID} Phase ${PHASE} Review Input"
    echo ""
    echo "## WRK Context"
    echo ""
    echo "- **Title:** ${TITLE}"
    echo "- **Route / Subcategory:** ${ROUTE} / ${SUBCATEGORY}"
    echo "- **Complexity:** ${COMPLEXITY}"
    echo ""
    echo "### Mission"
    echo ""
    echo "$MISSION"
    echo ""
    echo "### Acceptance Criteria"
    echo ""
    echo "$ACS"
    echo ""
    echo "## Changed Files"
    echo ""
    echo '```'
    echo "$CHANGED_FILES"
    echo '```'
    echo ""
    echo "## Diff"
    echo ""
    if [[ -n "$DIFF_CONTENT" ]]; then
        echo '```diff'
        echo "$DIFF_CONTENT"
        echo '```'
        if [[ "$DIFF_TRUNCATED" == "true" ]]; then
            echo ""
            echo "> **[System] Diff truncated at ${DIFF_MAX}/${DIFF_LINE_COUNT} lines.**"
            echo "> Reviewer: the diff shown is incomplete — assess visible changes only."
        fi
    else
        echo "_No diff detected (workspace is clean or no tracked changes)._"
    fi
    echo ""
    echo "## Test Snapshot"
    echo ""
    echo "$TEST_SNAPSHOT"
    echo ""
    echo "## Checkpoint Summary"
    echo ""
    echo "$CHECKPOINT_SUMMARY"
    echo ""
    echo "## Review Focus"
    echo ""
    generate_focus_prompts "$SUBCATEGORY" "$COMPLEXITY"
    echo ""
    echo "## Verdict Request"
    echo ""
    echo "Please review the above context and diff. Return:"
    echo "**APPROVE** / **REQUEST_CHANGES** / **REJECT** with specific findings."
} > "$OUTPUT_FILE"

echo "✔ Review input written: ${OUTPUT_FILE}"
