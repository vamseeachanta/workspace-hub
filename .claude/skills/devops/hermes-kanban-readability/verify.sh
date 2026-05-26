#!/usr/bin/env bash
#
# Verify the Hermes Kanban readability override is correctly installed on this
# machine. Run after `git pull` + `bash scripts/memory/bootstrap-machine.sh`
# (or after `install.sh` directly).
#
#   Exit 0 = PASS, or N/A (no Hermes dashboard here — override not applicable)
#   Exit 1 = Hermes present but override missing/incorrect (run install.sh)
#
# Honors HERMES_HOME / HERMES_AGENT_REPO / HERMES_BUNDLED_PLUGINS, same as
# install.sh. Read-only — never modifies anything.
#
set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO="${HERMES_AGENT_REPO:-$HERMES_HOME/hermes-agent}"
BUNDLED="${HERMES_BUNDLED_PLUGINS:-$REPO/plugins}/kanban/dashboard"
DEST="$HERMES_HOME/plugins/kanban/dashboard"

fail=0
pass() { printf '  [PASS] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; fail=1; }
info() { printf '  [ .. ] %s\n' "$1"; }

echo "host        : $(hostname)"
echo "HERMES_HOME : $HERMES_HOME"
echo "bundled     : $BUNDLED"
echo "override    : $DEST"
echo

# 0. Is this even a Hermes-dashboard machine?
if [ ! -d "$BUNDLED" ]; then
  echo "N/A — no bundled Hermes kanban plugin found."
  echo "      This machine does not run a Hermes dashboard; the override is"
  echo "      not applicable and the bootstrap guard correctly no-ops. OK."
  exit 0
fi

echo "== override files present =="
[ -f "$DEST/dist/index.js" ]  && pass "dist/index.js"  || bad "dist/index.js MISSING — run install.sh / bootstrap"
[ -f "$DEST/dist/style.css" ] && pass "dist/style.css" || bad "dist/style.css MISSING — run install.sh / bootstrap"

echo "== fixes applied =="
if [ -f "$DEST/dist/index.js" ]  && grep -Fq "bare-URL autolinker" "$DEST/dist/index.js"; then
  pass "bare-URL autolink fix"
else
  bad "bare-URL autolink fix ABSENT"
fi
if [ -f "$DEST/dist/style.css" ] && grep -Fq "kanban-readability skill override" "$DEST/dist/style.css"; then
  pass "readable-font override"
else
  bad "readable-font override ABSENT"
fi

echo "== sanity =="
if [ -f "$DEST/dist/index.js" ]; then
  if command -v node >/dev/null 2>&1; then
    node --check "$DEST/dist/index.js" 2>/dev/null && pass "index.js parses" || bad "index.js does NOT parse"
  else
    info "node not available — skipped parse check"
  fi
  nul=$(tr -cd '\000' < "$DEST/dist/index.js" | wc -c | tr -d ' ')
  [ "$nul" = "0" ] && pass "index.js clean text (no raw NUL bytes)" || bad "index.js contains $nul raw NUL byte(s)"
fi

echo "== live dashboard (optional) =="
port="$(ss -ltnp 2>/dev/null | grep -oE '127\.0\.0\.1:9[0-9]{3}' | head -1 | cut -d: -f2 || true)"
if [ -n "${port:-}" ] && command -v curl >/dev/null 2>&1; then
  body="$(curl -fsS "http://127.0.0.1:${port}/api/dashboard/plugins" 2>/dev/null || true)"
  if [ -n "$body" ] && command -v python3 >/dev/null 2>&1; then
    src="$(printf '%s' "$body" | python3 -c "import sys,json
try:
    d=json.load(sys.stdin); k=[p for p in d if p.get('name')=='kanban']
    print(k[0].get('source') if k else 'absent')
except Exception:
    print('parse-error')" 2>/dev/null)"
    case "$src" in
      user) pass "dashboard serving kanban from USER override (:$port)";;
      bundled) bad "dashboard still serving BUNDLED kanban (:$port) — rescan or restart the dashboard";;
      absent) bad "dashboard reports no kanban plugin (:$port)";;
      *) info "couldn't determine kanban source on :$port ($src)";;
    esac
  else
    info "dashboard on :$port but couldn't read plugin list — hard-refresh the Kanban tab"
  fi
else
  info "no local dashboard on :9xxx (headless check) — files verified above"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS — override installed and correct."
  exit 0
else
  echo "RESULT: FAIL — see [FAIL] lines above. Fix: bash \"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh\""
  exit 1
fi
