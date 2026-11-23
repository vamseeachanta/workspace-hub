#!/usr/bin/env bash
# rotate-cost-tracking.sh — Rotate cost-tracking.jsonl into a gzipped archive.
# Issue: #2070 (https://github.com/vamseeachanta/workspace-hub/issues/2070)
# Plan:  docs/plans/2026-04-16-issue-2070-state-size-guard.md
#
# Behavior:
# 1. Refuses to run unless verify-consumer-compat.sh exits 0.
# 2. No-op if cost-tracking.jsonl is below ROTATE_AT_MB.
# 3. Otherwise: mv → gzip → truncate live to 0 bytes.
# 4. Does NOT auto-commit. Prints the `git add`/`git commit` follow-up commands
#    so the user can review the pre-commit hook stack before committing.
#
# Env overrides (testing):
#   STATE_ROTATE_SRC       — override source file path
#   STATE_ROTATE_ARCHIVE   — override archive dir path
#   STATE_ROTATE_AT_MB     — override floor below which rotation is skipped (default 30)
#   STATE_VERIFY_SCRIPT    — override consumer-compat verifier (e.g., for tests)
#   STATE_ROTATE_DATE      — override date stamp (default $(date +%Y-%m-%d))
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SRC="${STATE_ROTATE_SRC:-${REPO_ROOT}/.claude/state/session-signals/cost-tracking.jsonl}"
ARCHIVE_DIR="${STATE_ROTATE_ARCHIVE:-$(dirname "$SRC")/archive}"
ROTATE_AT_MB="${STATE_ROTATE_AT_MB:-30}"
VERIFY_SCRIPT="${STATE_VERIFY_SCRIPT:-${REPO_ROOT}/scripts/state/verify-consumer-compat.sh}"
DATE_STAMP="${STATE_ROTATE_DATE:-$(date +%Y-%m-%d)}"

# ── 1. Pre-flight: consumer compat check ───────────────────────────────
echo "[rotate] running consumer compatibility verifier..."
if ! bash "$VERIFY_SCRIPT" >/dev/null 2>&1; then
    echo "REFUSED: consumer-compat verifier did not pass." >&2
    echo "  Run: bash $VERIFY_SCRIPT" >&2
    echo "  Update failing consumers before rotation." >&2
    exit 2
fi

# ── 2. Size check ──────────────────────────────────────────────────────
if [[ ! -f "$SRC" ]]; then
    echo "[rotate] no source file at $SRC — nothing to do."
    exit 0
fi

size_bytes=$(stat -c %s "$SRC" 2>/dev/null || stat -f %z "$SRC" 2>/dev/null || echo 0)
size_mb=$(( size_bytes / 1048576 ))

if (( size_mb < ROTATE_AT_MB )); then
    echo "[rotate] $SRC is ${size_mb}MB (< ${ROTATE_AT_MB}MB floor) — skipping."
    exit 0
fi

# ── 3. Rotate ──────────────────────────────────────────────────────────
mkdir -p "$ARCHIVE_DIR"
ARC_PATH="$ARCHIVE_DIR/cost-tracking-${DATE_STAMP}.jsonl"

if [[ -e "$ARC_PATH" || -e "${ARC_PATH}.gz" ]]; then
    echo "REFUSED: archive for $DATE_STAMP already exists at $ARC_PATH(.gz)" >&2
    echo "  Use STATE_ROTATE_DATE=YYYY-MM-DD-suffix to disambiguate." >&2
    exit 3
fi

mv "$SRC" "$ARC_PATH"
gzip "$ARC_PATH"
: > "$SRC"   # explicit truncate (touch is non-portable for in-place truncation)

echo "[rotate] OK — archived ${size_mb}MB to ${ARC_PATH}.gz; live file truncated."

# ── 4. Print follow-up commands (NOT auto-committed) ──────────────────
REL_SRC="${SRC#${REPO_ROOT}/}"
REL_ARC="${ARC_PATH}.gz"
REL_ARC="${REL_ARC#${REPO_ROOT}/}"
echo
echo "Next, manually run:"
echo "  git add $REL_SRC $REL_ARC"
echo "  git commit -m 'chore(state): rotate cost-tracking.jsonl ${DATE_STAMP}'"
echo
echo "(Not auto-committed — review pre-commit hook stack first.)"
