#!/usr/bin/env bash
# session-review-page.sh — emit the lean live-link session-review page (#3316).
#
# Closes the live-link stream (#3298 → #3306 render, #3311 --from-git derive):
# at session end the page assembles itself from the session's git footprint.
#
# Modes:
#   start  (SessionStart): record origin/main SHA as the session's git base.
#   emit   (SessionEnd):   derive refs from <base>..origin/main and render the
#                          lean page into the working tree, then notify.
#
# SAFETY: ALWAYS exits 0 (fail-open — never block or error a session). It does
# NOT commit or push by default (auto-push across a shared checkout is a known
# hazard). Opt-in SESSION_REVIEW_STAGE=1 only `git add`s the page (no branch
# switch, no push) so it is queued for the session's normal commit.
#
# Disable entirely: SESSION_REVIEW_PAGE=false
# Platform: Linux, macOS, Windows (Git Bash). Deps: bash, git; uv or python3.
set -uo pipefail

[ "${SESSION_REVIEW_PAGE:-true}" != "true" ] && exit 0

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
[ -n "${WS:-}" ] && [ -d "${WS}/.git" ] || exit 0   # not a repo root → nothing to do
STATE_DIR="${WS}/.claude/state/session-review"
REF_FILE="${STATE_DIR}/start-ref"
MODE="${1:-emit}"
mkdir -p "$STATE_DIR" 2>/dev/null || true

if [ "$MODE" = "start" ]; then
  git -C "$WS" rev-parse origin/main >"$REF_FILE" 2>/dev/null || true
  exit 0
fi
[ "$MODE" = "emit" ] || exit 0

# best-effort refresh so squash-merged PR subjects ((#NNN)) are present in the range
timeout 20 git -C "$WS" fetch --quiet origin main 2>/dev/null || true

BASE=""
[ -s "$REF_FILE" ] && BASE="$(cat "$REF_FILE" 2>/dev/null)"
[ -n "$BASE" ] || BASE="$(git -C "$WS" merge-base HEAD origin/main 2>/dev/null)" || exit 0
[ -n "$BASE" ] || exit 0

COUNT="$(git -C "$WS" rev-list --count "${BASE}..origin/main" 2>/dev/null || echo 0)"
[ "${COUNT:-0}" -eq 0 ] && exit 0   # trivial session — nothing landed; skip

GEN="${WS}/scripts/workflow/build_session_review.py"
[ -f "$GEN" ] || exit 0
if command -v uv >/dev/null 2>&1; then PY=(uv run --with pyyaml python)
elif command -v python3 >/dev/null 2>&1; then PY=(python3)
else exit 0; fi

( cd "$WS" && "${PY[@]}" "$GEN" --from-git --since "$BASE" ) >/dev/null 2>&1 || exit 0

PAGE="$(ls -t "${WS}/docs/reports/sessions/"*.html 2>/dev/null | grep -v '/index\.html$' | head -1)"
REL="${PAGE#"${WS}"/}"

if [ "${SESSION_REVIEW_STAGE:-0}" = "1" ] && [ -n "$PAGE" ]; then
  git -C "$WS" add docs/reports/sessions/ 2>/dev/null || true   # stage only; no commit/push
fi

bash "${WS}/scripts/notify.sh" cron session-review-page pass \
  "generated ${REL:-session page} from ${COUNT} commit(s); commit it to publish the live link" 2>/dev/null || true
echo "[session-review] generated ${REL:-session page} (${COUNT} commits since session start) — commit to publish." >&2
exit 0
