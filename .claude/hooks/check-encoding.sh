#!/usr/bin/env bash
# check-encoding.sh — pre-commit / post-merge encoding guard
#
# Scans staged (pre-commit) or all (post-merge/post-checkout) work queue,
# skill, spec, and config .md/.yaml/.yml files for non-UTF-8 encoding.
# Fails the commit / emits a warning on pull so problems are caught BEFORE
# they reach generate-index.py or any parser at runtime.
#
# Install:
#   ln -sf ../../.claude/hooks/check-encoding.sh .git/hooks/pre-commit
#   ln -sf ../../.claude/hooks/check-encoding.sh .git/hooks/post-merge
#   ln -sf ../../.claude/hooks/check-encoding.sh .git/hooks/post-checkout
#
# The hook auto-detects which phase it's running in via $0.

set -euo pipefail

HOOK_NAME="$(basename "$0")"
REPO_ROOT="$(git rev-parse --show-toplevel)"

# ── Encoding check ────────────────────────────────────────────────────────────

check_file() {
    local f="$1"
    # Read first 4 bytes to detect BOMs
    local bom
    bom=$(dd if="$f" bs=1 count=4 2>/dev/null | od -An -tx1 | tr -d ' \n')
    case "$bom" in
        fffe*|feff*)
            echo "  UTF-16: $f"
            return 1
            ;;
        efbbbf*)
            echo "  UTF-8 BOM: $f (BOM will be stripped by .gitattributes)"
            return 0  # warn only — UTF-8 BOM is harmless but untidy
            ;;
    esac
    # Verify the file decodes as valid UTF-8
    if ! python3 -c "open('$f', encoding='utf-8').read()" 2>/dev/null; then
        echo "  Non-UTF-8: $f"
        return 1
    fi
    return 0
}

# ── Collect files to check ────────────────────────────────────────────────────

BAD=()
WARN=()

if [[ "$HOOK_NAME" == "pre-commit" ]]; then
    # Only check staged files
    while IFS= read -r f; do
        [[ -f "$REPO_ROOT/$f" ]] || continue
        case "$f" in
            *.md|*.yaml|*.yml|*.json) ;;
            *) continue ;;
        esac
        result=$(check_file "$REPO_ROOT/$f" 2>&1) || BAD+=("$result")
        [[ -n "$result" ]] && WARN+=("$result")
    done < <(git diff --cached --name-only --diff-filter=ACM)
else
    # post-merge / post-checkout — scan all tracked text files in key dirs
    while IFS= read -r f; do
        [[ -f "$REPO_ROOT/$f" ]] || continue
        case "$f" in
            *.md|*.yaml|*.yml|*.json) ;;
            *) continue ;;
        esac
        result=$(check_file "$REPO_ROOT/$f" 2>&1) || BAD+=("$result")
        [[ -n "$result" ]] && WARN+=("$result")
    done < <(git ls-files -- \
        '.claude/work-queue/pending' \
        '.claude/work-queue/working' \
        '.claude/work-queue/blocked' \
        '.claude/work-queue/archive' \
        '.claude/skills' \
        'specs' \
        'config' \
    )
fi

# ── Report ────────────────────────────────────────────────────────────────────

if [[ ${#BAD[@]} -gt 0 ]]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  check-encoding: ENCODING ERRORS DETECTED                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "The following files have incompatible encodings (UTF-16 or"
    echo "invalid UTF-8). These will crash generate-index.py and other"
    echo "parsers on Linux/Mac."
    echo ""
    for msg in "${BAD[@]}"; do echo "  $msg"; done
    echo ""
    echo "Fix: iconv -f UTF-16 -t UTF-8 <file> | sed 's/\\r//' > <file>"
    echo "     Or save the file as UTF-8 (no BOM) from your editor."
    echo ""
    if [[ "$HOOK_NAME" == "pre-commit" ]]; then
        echo "Commit blocked. Fix the encoding and re-stage the file(s)."
        exit 1
    else
        echo "WARNING: These files are already in the repo. Convert and"
        echo "         commit the fixed versions as soon as possible."
        exit 0  # post-merge/checkout: warn but don't block
    fi
fi

if [[ ${#WARN[@]} -gt 0 ]]; then
    echo "check-encoding: UTF-8 BOM found (harmless but untidy):"
    for msg in "${WARN[@]}"; do echo "  $msg"; done
fi

exit 0
