#!/usr/bin/env bash
# skill-autoresearch-nightly.sh — Automated skill improvement loop (WRK-5087)
#
# Follows karpathy/autoresearch pattern:
#   1. Create branch autoresearch/skills-YYYY-MM-DD
#   2. Pick skills with most warnings from skill-eval
#   3. Claude proposes SKILL.md amendment (with time budget)
#   4. Run skill-eval — keep if score improves, revert if not
#   5. Log result to results.tsv
#   6. Human reviews branch diff next morning
#
# Safety: NEVER modifies main. All work on autoresearch/ branch.
# The branch is never auto-merged — human reviews and merges.
#
# Usage:
#   bash scripts/cron/skill-autoresearch-nightly.sh [--dry-run] [--max-attempts N]
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
source "${SCRIPT_DIR}/lib/git-safe.sh"
DATE=$(date -u +%Y-%m-%d)
BRANCH="autoresearch/skills-${DATE}"
RESULTS_FILE="${WS_HUB}/.claude/state/skill-autoresearch/results.tsv"
TIME_BUDGET=180  # 3 minutes per improvement attempt
MAX_ATTEMPTS="${MAX_ATTEMPTS:-5}"
DRY_RUN=false
EVAL_SCRIPT="${WS_HUB}/.claude/skills/development/skill-eval/scripts/eval-skills.py"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --max-attempts) MAX_ATTEMPTS="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--max-attempts N]"
            echo "  --dry-run       Show what would be done without making changes"
            echo "  --max-attempts  Max improvement attempts per run (default: 5)"
            exit 0
            ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# --- Setup ---
mkdir -p "$(dirname "$RESULTS_FILE")"

# Initialize results.tsv header if new
if [ ! -f "$RESULTS_FILE" ]; then
    echo -e "date\tskill\twarnings_before\twarnings_after\tresult\tduration_s" > "$RESULTS_FILE"
fi

echo "=== [skill-autoresearch] Starting $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "  Branch: ${BRANCH}"
echo "  Max attempts: ${MAX_ATTEMPTS}"
echo "  Time budget: ${TIME_BUDGET}s per attempt"
echo "  Dry run: ${DRY_RUN}"

# --- Ensure clean state ---
cd "$WS_HUB"
git_safe_init "$WS_HUB"
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "WARNING: working tree not clean — stashing changes"
    git stash --include-untracked -m "autoresearch-pre-stash-${DATE}" || true
fi

# --- Create or switch to branch ---
ORIGINAL_BRANCH=$(git branch --show-current)
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo "  Branch ${BRANCH} already exists — resuming"
    git switch "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
else
    echo "  Creating branch ${BRANCH} from main"
    git switch -c "$BRANCH" main 2>/dev/null || git checkout -b "$BRANCH" main
fi

# --- Identify improvement candidates ---
# Run skill-eval and find skills with most warnings (improvement opportunities)
echo ""
echo "--- Identifying improvement candidates ---"
EVAL_JSON=$(uv run --no-project python "$EVAL_SCRIPT" --format json 2>/dev/null) || {
    echo "ERROR: skill-eval failed"
    git switch "$ORIGINAL_BRANCH" 2>/dev/null || git checkout "$ORIGINAL_BRANCH"
    exit 1
}

# Extract skills sorted by warning count (descending)
CANDIDATES=$(echo "$EVAL_JSON" | uv run --no-project python -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('results', d.get('skill_details', d.get('skills', [])))
ranked = []
for s in skills:
    warnings = sum(1 for i in s.get('issues', []) if i.get('severity') == 'WARNING')
    if warnings > 0:
        ranked.append((warnings, s['name']))
ranked.sort(reverse=True)
for w, name in ranked[:${MAX_ATTEMPTS}]:
    print(f'{w}\t{name}')
" 2>/dev/null) || CANDIDATES=""

if [ -z "$CANDIDATES" ]; then
    echo "  No improvement candidates found — all skills clean"
    git switch "$ORIGINAL_BRANCH" 2>/dev/null || git checkout "$ORIGINAL_BRANCH"
    echo "=== [skill-autoresearch] Done — nothing to improve ==="
    exit 0
fi

echo "  Candidates:"
echo "$CANDIDATES" | while IFS=$'\t' read -r warnings name; do
    echo "    ${name} (${warnings} warnings)"
done

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "=== [skill-autoresearch] Dry run — no changes made ==="
    git switch "$ORIGINAL_BRANCH" 2>/dev/null || git checkout "$ORIGINAL_BRANCH"
    exit 0
fi

# --- Improvement loop ---
ATTEMPT=0
echo "$CANDIDATES" | while IFS=$'\t' read -r warnings_before skill_name; do
    ATTEMPT=$((ATTEMPT + 1))
    echo ""
    echo "--- Attempt ${ATTEMPT}: ${skill_name} (${warnings_before} warnings) ---"
    START_EPOCH=$(date +%s)

    # Find the SKILL.md file
    SKILL_FILE=$(find "${WS_HUB}/.claude/skills" -path "*/${skill_name}/SKILL.md" -type f 2>/dev/null | head -1)
    if [ -z "$SKILL_FILE" ]; then
        echo "  SKIP: could not find SKILL.md for ${skill_name}"
        continue
    fi

    # Get specific warnings for this skill
    SKILL_WARNINGS=$(echo "$EVAL_JSON" | uv run --no-project python -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('results', d.get('skill_details', d.get('skills', [])))
for s in skills:
    if s['name'] == '${skill_name}':
        for i in s.get('issues', []):
            if i.get('severity') == 'WARNING':
                print(f'  - {i[\"check\"]}: {i[\"message\"]}')
" 2>/dev/null) || SKILL_WARNINGS="(could not extract)"

    echo "  Warnings:"
    echo "$SKILL_WARNINGS"

    # Use Claude to propose an amendment (with timeout)
    echo "  Proposing amendment (timeout: ${TIME_BUDGET}s)..."
    AMENDMENT_PROMPT="You are improving a SKILL.md file. Fix ONLY these skill-eval warnings:
${SKILL_WARNINGS}

Rules:
- Make minimal, targeted edits
- Do NOT change the skill's purpose or core content
- Do NOT add unnecessary sections
- Keep the file under 150 lines
- Output ONLY the complete updated file content, nothing else

Current file:
$(cat "$SKILL_FILE")"

    # Run Claude with timeout — if available
    if command -v claude >/dev/null 2>&1; then
        AMENDED=$(timeout "${TIME_BUDGET}" claude --print -p "$AMENDMENT_PROMPT" 2>/dev/null) || {
            echo "  SKIP: Claude timed out or failed"
            END_EPOCH=$(date +%s)
            echo -e "${DATE}\t${skill_name}\t${warnings_before}\t-\ttimeout\t$((END_EPOCH - START_EPOCH))" >> "$RESULTS_FILE"
            continue
        }
    else
        echo "  SKIP: claude CLI not available"
        END_EPOCH=$(date +%s)
        echo -e "${DATE}\t${skill_name}\t${warnings_before}\t-\tno-claude\t$((END_EPOCH - START_EPOCH))" >> "$RESULTS_FILE"
        continue
    fi

    # Write amended file
    echo "$AMENDED" > "$SKILL_FILE"

    # Re-run eval on this skill
    EVAL_AFTER=$(uv run --no-project python "$EVAL_SCRIPT" --skill "$skill_name" --format json 2>/dev/null) || {
        echo "  ERROR: post-amendment eval failed — reverting"
        git restore "$SKILL_FILE"
        END_EPOCH=$(date +%s)
        echo -e "${DATE}\t${skill_name}\t${warnings_before}\t-\teval-fail\t$((END_EPOCH - START_EPOCH))" >> "$RESULTS_FILE"
        continue
    }

    warnings_after=$(echo "$EVAL_AFTER" | uv run --no-project python -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('summary', {}).get('issues', {}).get('warning', 0))
" 2>/dev/null) || warnings_after=999

    criticals_after=$(echo "$EVAL_AFTER" | uv run --no-project python -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('summary', {}).get('issues', {}).get('critical', 0))
" 2>/dev/null) || criticals_after=999

    END_EPOCH=$(date +%s)
    DURATION=$((END_EPOCH - START_EPOCH))

    # Decision: keep or revert
    if [ "$criticals_after" -gt 0 ]; then
        echo "  REVERT: introduced ${criticals_after} critical(s)"
        git restore "$SKILL_FILE"
        echo -e "${DATE}\t${skill_name}\t${warnings_before}\t${warnings_after}\trevert-critical\t${DURATION}" >> "$RESULTS_FILE"
    elif [ "$warnings_after" -lt "$warnings_before" ]; then
        echo "  KEEP: warnings reduced ${warnings_before} -> ${warnings_after}"
        git_safe_commit "autoresearch: improve ${skill_name} (warnings ${warnings_before}->${warnings_after})" "$SKILL_FILE"
        echo -e "${DATE}\t${skill_name}\t${warnings_before}\t${warnings_after}\tkept\t${DURATION}" >> "$RESULTS_FILE"
    else
        echo "  REVERT: no improvement (${warnings_before} -> ${warnings_after})"
        git restore "$SKILL_FILE"
        echo -e "${DATE}\t${skill_name}\t${warnings_before}\t${warnings_after}\trevert-no-improve\t${DURATION}" >> "$RESULTS_FILE"
    fi
done

# --- Summary ---
echo ""
echo "=== [skill-autoresearch] Summary ==="
KEPT=$(grep -c "kept" "$RESULTS_FILE" 2>/dev/null) || KEPT=0
REVERTED=$(grep -c "revert" "$RESULTS_FILE" 2>/dev/null) || REVERTED=0
echo "  Kept: ${KEPT}, Reverted: ${REVERTED}"
echo "  Results: ${RESULTS_FILE}"
echo "  Review: git diff main..${BRANCH}"

# Return to original branch
git switch "$ORIGINAL_BRANCH" 2>/dev/null || git checkout "$ORIGINAL_BRANCH"

# Pop stash if we stashed earlier
git stash pop 2>/dev/null || true

echo "=== [skill-autoresearch] Done $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
