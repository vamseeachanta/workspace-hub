#!/usr/bin/env bash
# validate-file-placement.sh — Enforce file placement rules from repo-structure and file-taxonomy skills.
# Exit 0 = pass (only warnings), Exit 1 = fail (hard violations found).
# Usage: scripts/operations/validate-file-placement.sh [<repo-path>...]
#        Defaults to digitalmodel and worldenergydata submodules if no args given.
#
# WRK-414, WRK-576 (B5 enhancement)

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
FAIL=0
WARN_COUNT=0
FAIL_COUNT=0

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
YEL='\033[0;33m'
GRN='\033[0;32m'
NC='\033[0m'

fail() { echo -e "${RED}[FAIL]${NC} $*"; FAIL_COUNT=$((FAIL_COUNT + 1)); FAIL=1; }
warn() { echo -e "${YEL}[WARN]${NC} $*"; WARN_COUNT=$((WARN_COUNT + 1)); }
ok()   { echo -e "${GRN}[ OK ]${NC} $*"; }

# ── Repos to check ────────────────────────────────────────────────────────────
if [ "$#" -gt 0 ]; then
    REPOS=("$@")
else
    REPOS=(
        "${REPO_ROOT}/digitalmodel"
        "${REPO_ROOT}/worldenergydata"
        "${REPO_ROOT}/assetutilities"
        "${REPO_ROOT}/assethold"
    )
fi

echo "=== File Placement Validation ==="
echo "Checking ${#REPOS[@]} repo(s)..."
echo ""

for REPO in "${REPOS[@]}"; do
    if [ ! -d "$REPO" ]; then
        warn "Repo not found, skipping: $REPO"
        continue
    fi
    REPO_NAME=$(basename "$REPO")
    echo "── $REPO_NAME ──────────────────────────────"

    # ── CHECK 1 (FAIL): tests/ inside src/ ───────────────────────────────────
    # maxdepth 3 = src/<pkg>/<domain>/tests — covers 95% of violations quickly
    TESTS_IN_SRC=$([ -d "$REPO/src" ] && find "$REPO/src" -maxdepth 3 -type d -name "tests" 2>/dev/null || true)
    if [ -n "$TESTS_IN_SRC" ]; then
        while IFS= read -r dir; do
            fail "tests/ inside src/: $dir"
        done <<< "$TESTS_IN_SRC"
    else
        ok "No tests/ inside src/"
    fi

    # ── CHECK 2 (FAIL): Generated output dirs not gitignored in tests/ ───────
    for output_dir in "tests/output" "tests/outputs"; do
        if [ -d "$REPO/$output_dir" ]; then
            dir_base=$(basename "$output_dir")
            if grep -qE "^(tests/)?${dir_base}/?$" "$REPO/.gitignore" 2>/dev/null; then
                ok "$output_dir is gitignored"
            else
                fail "Generated artifacts dir not in .gitignore: $REPO_NAME/$output_dir"
            fi
        fi
    done

    # ── CHECK 3 (FAIL): kebab-case dirs in src/ Python tree ──────────────────
    # Exclude .egg-info/.dist-info; depth 2 = src/<pkg>/<domain>/ (fast)
    KEBAB_DIRS=$([ -d "$REPO/src" ] && find "$REPO/src" -maxdepth 2 -type d -name "*-*" \
        ! -name "*.egg-info" ! -name "*.dist-info" 2>/dev/null || true)
    if [ -n "$KEBAB_DIRS" ]; then
        while IFS= read -r dir; do
            fail "kebab-case dir in src/ (cannot be Python package): $dir"
        done <<< "$KEBAB_DIRS"
    else
        ok "No kebab-case dirs in src/"
    fi

    # ── CHECK 4 (WARN): tests/unit/ wrapper (use flat tests/<domain>/ instead) ──
    if [ -d "$REPO/tests/unit" ]; then
        warn "tests/unit/ wrapper found — use flat tests/<domain>/ layout: $REPO_NAME/tests/unit/"
    fi

    # ── CHECK 5 (WARN): results/ not in .gitignore ────────────────────────────
    if [ -d "$REPO/results" ]; then
        if grep -qE "^/?results/?$" "$REPO/.gitignore" 2>/dev/null; then
            ok "results/ is in .gitignore"
        else
            warn "results/ exists but not in .gitignore: $REPO_NAME"
        fi
    fi

    # ── CHECK 6 (WARN): WRK deliverable files in docs/ ──────────────────────
    WRK_IN_DOCS=$([ -d "$REPO/docs" ] && find "$REPO/docs" -maxdepth 2 \( -name "wrk-*.md" -o -name "WRK-*.md" \) 2>/dev/null || true)
    if [ -n "$WRK_IN_DOCS" ]; then
        while IFS= read -r f; do
            warn "WRK deliverable in docs/ (belongs in workspace-hub work-queue/): $f"
        done <<< "$WRK_IN_DOCS"
    fi

    # ── CHECK 7 (WARN): catch-all dirs in tests/ ─────────────────────────────
    for catch_dir in "phase2" "phase3" "phase4" "phase5"; do
        if [ -d "$REPO/tests/$catch_dir" ]; then
            warn "Catch-all test dir (migrate to domain dirs): $REPO_NAME/tests/$catch_dir/"
        fi
    done

    # ── CHECK 8 (WARN): multiple archive dirs in tests/ ──────────────────────
    ARCHIVE_COUNT=0
    for arc_dir in "_archived" "_archived_tests" "legacy_tests" "_archive"; do
        [ -d "$REPO/tests/$arc_dir" ] && ((ARCHIVE_COUNT++)) || true
    done
    if [ "$ARCHIVE_COUNT" -gt 1 ]; then
        warn "Multiple test archive dirs found (consolidate to tests/_archive/): $REPO_NAME/tests/"
    fi

    # ── CHECK 9 (WARN): src/modules/ catch-all at package level ─────────────
    if [ -d "$REPO/src" ]; then
        for pkg_dir in "$REPO/src"/*/; do
            if [ -d "${pkg_dir}modules" ]; then
                warn "Catch-all modules/ at package level (assign to domain packages): ${pkg_dir}modules/"
            fi
        done
    fi

    # ── CHECK 10 (FAIL): test files inside src/ ───────────────────────────────
    # maxdepth 6 covers all nested src layouts; grep filters __pycache__
    TESTS_IN_SRC_FILES=$(find "$REPO/src" -maxdepth 6 \
        \( -name "test_*.py" -o -name "*_test.py" \) \
        ! -path "*/__pycache__/*" 2>/dev/null || true)
    if [ -n "$TESTS_IN_SRC_FILES" ]; then
        while IFS= read -r f; do
            fail "Test file inside src/ (move to tests/): $f"
        done <<< "$TESTS_IN_SRC_FILES"
    else
        ok "No test files inside src/"
    fi

    # ── CHECK 11 (FAIL): committed output artifacts at root ───────────────────
    if [ -d "$REPO/.git" ] || git -C "$REPO" rev-parse --git-dir &>/dev/null; then
        COMMITTED_ARTIFACTS=$(git -C "$REPO" ls-files 2>/dev/null | \
            grep -E '^(report_.*\.(xlsx|csv|json)|test_export.*\.json|COVERAGE_ANALYSIS\.txt|verdict\.txt|coverage\.wrk.*\.xml)$' || true)
        if [ -n "$COMMITTED_ARTIFACTS" ]; then
            while IFS= read -r f; do
                fail "Committed output artifact at root (git rm --cached, then gitignore): $REPO_NAME/$f"
            done <<< "$COMMITTED_ARTIFACTS"
        else
            ok "No committed output artifacts at root"
        fi
    fi

    # ── CHECK 12 (WARN): agent harness files in docs/ ────────────────────────
    if [ -d "$REPO/docs" ]; then
        HARNESS_IN_DOCS=$(find "$REPO/docs" -maxdepth 1 \
            \( -name "AGENT_OS_COMMANDS*" -o -name "MANDATORY_SLASH*" \
               -o -name "AI_AGENT_ORCHESTRATION*" \) 2>/dev/null || true)
        if [ -n "$HARNESS_IN_DOCS" ]; then
            while IFS= read -r f; do
                warn "Agent harness file in docs/ (move to .claude/docs/ or delete): $f"
            done <<< "$HARNESS_IN_DOCS"
        fi
    fi

    # ── CHECK 13 (WARN): loose .py files at repo root ────────────────────────
    LOOSE_PY=$(find "$REPO" -maxdepth 1 -name "*.py" ! -name "setup.py" 2>/dev/null || true)
    if [ -n "$LOOSE_PY" ]; then
        while IFS= read -r f; do
            warn "Loose .py at root (move to scripts/ or src/<pkg>/tools/): $f"
        done <<< "$LOOSE_PY"
    fi

    # ── CHECK 14 (WARN): setup.py alongside pyproject.toml ───────────────────
    if [ -f "$REPO/setup.py" ] && [ -f "$REPO/pyproject.toml" ]; then
        warn "setup.py alongside pyproject.toml (setup.py is superseded — remove it): $REPO_NAME"
    fi

    echo ""
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo "=== Summary ==="
echo "  FAIL: $FAIL_COUNT violation(s)"
echo "  WARN: $WARN_COUNT warning(s)"
echo ""

if [ "$FAIL" -eq 1 ]; then
    echo -e "${RED}FAILED — $FAIL_COUNT violation(s) must be resolved.${NC}"
    exit 1
else
    echo -e "${GRN}PASSED — no hard violations.${NC}"
    exit 0
fi
