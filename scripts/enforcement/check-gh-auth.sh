#!/usr/bin/env bash
# check-gh-auth.sh — wh#3368
# Verify GitHub auth is REALLY working before a push/PR workflow relies on it.
#
# `gh auth status` can report a logged-in ✓ while the stored token is actually
# invalid — the API then 401s on the first real call. This check hits the API
# directly (`gh api user`), which is the only reliable signal. Documented
# incident: memory `ace-linux-2-gh-token-expired` (a whole session's first half
# lost to a token that `gh auth status` still called good).
#
# Usage:
#   scripts/enforcement/check-gh-auth.sh [--quiet]
#
# Exit codes: 0 = authenticated (prints the login unless --quiet);
#             1 = not authenticated / token invalid;
#             2 = gh CLI not installed.
# Override the binary for testing: GH_BIN=/path/to/fake-gh.

set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
QUIET=0
case "${1:-}" in
  --quiet) QUIET=1 ;;
  "" ) ;;
  * ) echo "check-gh-auth: unknown flag: $1" >&2; exit 2 ;;
esac

if ! command -v "$GH_BIN" >/dev/null 2>&1; then
  echo "check-gh-auth: '$GH_BIN' not found on PATH — install the GitHub CLI." >&2
  exit 2
fi

# The authoritative probe: an actual authenticated API call. Do NOT trust
# `gh auth status` — it reads local config and can pass on a dead token.
if login="$("$GH_BIN" api user -q .login 2>/dev/null)" && [[ -n "$login" ]]; then
  (( QUIET )) || echo "check-gh-auth: authenticated as $login"
  exit 0
fi

echo "check-gh-auth: GitHub auth is NOT working (gh api user failed)." >&2
echo "  'gh auth status' may still show a stale ✓ — re-authenticate:" >&2
echo "    gh auth login -h github.com" >&2
exit 1
