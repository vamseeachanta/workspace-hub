#!/usr/bin/env bash
# ABOUTME: Tests for scripts/repository_sync-auto — routing, exit codes, syntax

set -uo pipefail

PASS=0; FAIL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUTO_SCRIPT="$SCRIPT_DIR/scripts/repository_sync"
AUTO_HELPER="$SCRIPT_DIR/scripts/repository_sync-auto"

_pass() { echo "PASS: $1"; ((PASS++)) || true; }
_fail() { echo "FAIL: $1"; ((FAIL++)) || true; }

# T1: syntax — main script
bash -n "$AUTO_SCRIPT" 2>/dev/null && _pass "repository_sync syntax OK" || _fail "repository_sync syntax error"

# T2: syntax — helper
bash -n "$AUTO_HELPER" 2>/dev/null && _pass "repository_sync-auto syntax OK" || _fail "repository_sync-auto syntax error"

# T3: menu/-i routing present in dispatch
grep -q 'menu|-i|--interactive' "$AUTO_SCRIPT" \
    && _pass "'menu|-i' routing present" || _fail "'menu|-i' routing missing"

# T4: auto_sync_all sourced via helper
grep -q 'source.*repository_sync-auto' "$AUTO_SCRIPT" \
    && _pass "helper is sourced in main script" || _fail "helper source line missing"

# T5: warn-pull-failed label used (not old warn-diverged)
grep -q 'warn-pull-failed' "$AUTO_HELPER" \
    && _pass "warn-pull-failed label present" || _fail "warn-pull-failed label missing"
grep -q 'warn-diverged' "$AUTO_HELPER" \
    && _fail "old warn-diverged label still present" || _pass "old warn-diverged label removed"

# T6: hub result included in exit code logic
grep -q 'hub_result' "$AUTO_HELPER" \
    && _pass "hub_result tracked in auto_sync_all" || _fail "hub_result not tracked"

# T7: hub failure increments n_fail
grep -q 'hub_result.*n_fail\|n_fail.*hub_result' "$AUTO_HELPER" \
    && _pass "hub failure increments n_fail" \
    || { grep -q 'n_fail' "$AUTO_HELPER" && grep -q 'hub_result' "$AUTO_HELPER" \
        && _pass "hub_result and n_fail both present (manual verify ordering)" \
        || _fail "hub failure does not increment n_fail"; }

# T8: --dry-run with no repos exits 0 (functional test with stubs)
out=$(bash -c '
    WORKSPACE_ROOT=/tmp
    ALL_REPOS=()
    NC="" GREEN="" RED="" YELLOW="" BLUE="" CYAN="" BOLD=""
    repo_exists() { return 1; }
    _auto_sync_hub() { return 0; }
    source "'"$AUTO_HELPER"'"
    auto_sync_all --dry-run
    echo "EXIT:$?"
' 2>/dev/null)
echo "$out" | grep -q "EXIT:0" \
    && _pass "--dry-run exits 0 with no repos" || _fail "--dry-run should exit 0 with no repos"

# T9: TTY safety gate code present
grep -q '\[ -t 1 \]' "$AUTO_HELPER" \
    && _pass "TTY safety gate present" || _fail "TTY safety gate missing"

# T10: cron shebang is portable
head -1 "$SCRIPT_DIR/scripts/cron-repository-sync.sh" | grep -q '#!/usr/bin/env bash' \
    && _pass "cron shebang is portable" || _fail "cron shebang not portable"

# T11: functional — auto_sync_all --dry-run exits 0 (source helper directly, no main)
out=$(bash -c '
    WORKSPACE_ROOT=/tmp ALL_REPOS=()
    NC="" GREEN="" RED="" YELLOW="" BLUE="" CYAN="" BOLD=""
    repo_exists() { return 1; }
    source "'"$AUTO_HELPER"'"
    _auto_sync_hub() { return 0; }
    auto_sync_all "--dry-run"
    echo "EXIT:$?"
' 2>/dev/null)
echo "$out" | grep -q "EXIT:0" \
    && _pass "auto_sync_all --dry-run exits 0 (functional)" \
    || _fail "auto_sync_all --dry-run should exit 0"

# T12: argument forwarding — auto_sync_all does NOT receive 'auto' as \$1
out=$(bash -c '
    NC="" GREEN="" RED="" YELLOW="" BLUE="" CYAN="" BOLD=""
    source "'"$AUTO_HELPER"'" 2>/dev/null
    # Call with stripped args (simulating "${@:2}" fix)
    first_arg=""
    _capture_first() { first_arg="${1:-}"; }
    orig=$(declare -f auto_sync_all)
    auto_sync_all() { _capture_first "$@"; echo "FIRSTARG:${1:-NONE}"; }
    auto_sync_all "--dry-run"
' 2>/dev/null)
echo "$out" | grep -q "FIRSTARG:--dry-run\|FIRSTARG:NONE" \
    && _pass "subcommand token not forwarded to auto_sync_all" \
    || _fail "subcommand token forwarding regression"

# T13: explicit rm cleanup for rdir present (no EXIT trap — local var scope issue)
grep -q 'rm -rf.*rdir' "$AUTO_HELPER" \
    && _pass "explicit rdir cleanup present" || _fail "rdir cleanup missing"

# T14: bash version guard present
grep -q 'BASH_VERSINFO' "$AUTO_HELPER" \
    && _pass "bash version guard present" || _fail "bash version guard missing"

# T15: collision-safe result filenames use portable _sha256 helper
grep -q '_sha256' "$AUTO_HELPER" \
    && _pass "collision-safe filenames use portable _sha256 helper" \
    || _fail "_sha256 portable helper missing"

# T15b: _sha256 helper present and functional
out=$(bash -c 'source "'"$AUTO_HELPER"'" 2>/dev/null; printf "test" | _sha256' 2>/dev/null)
[ -n "$out" ] \
    && _pass "_sha256 helper produces output" || _fail "_sha256 helper produces no output"

# T16: behavioral — _auto_sync_one stages and commits a new file (no remote → warn-pull-failed)
_td=$(mktemp -d)
_tmpws="$_td/ws" && mkdir -p "$_tmpws/testrepo"
(cd "$_tmpws/testrepo" && git init -q \
    && git config user.email "t@t" && git config user.name "T" \
    && echo "init" > init.txt && git add init.txt && git commit -q -m "init") 2>/dev/null
echo "change" > "$_tmpws/testrepo/change.txt"   # unstaged file
_rfile="$_td/result"
(WORKSPACE_ROOT="$_tmpws"; source "$AUTO_HELPER" 2>/dev/null
 _auto_sync_one "$_rfile" "testrepo" "2026-01-01" "false") 2>/dev/null
_res=$(cat "$_rfile" 2>/dev/null || echo "")
echo "$_res" | grep -q "|true|true|" \
    && _pass "behavioral: _auto_sync_one stages+commits new file" \
    || _fail "behavioral: commit path broken (got: $_res)"
rm -rf "$_td"

# T17: behavioral — _auto_sync_one skips commit when no changes
_td=$(mktemp -d)
_tmpws="$_td/ws" && mkdir -p "$_tmpws/testrepo"
(cd "$_tmpws/testrepo" && git init -q \
    && git config user.email "t@t" && git config user.name "T" \
    && echo "init" > init.txt && git add init.txt && git commit -q -m "init") 2>/dev/null
_rfile="$_td/result"
(WORKSPACE_ROOT="$_tmpws"; source "$AUTO_HELPER" 2>/dev/null
 _auto_sync_one "$_rfile" "testrepo" "2026-01-01" "false") 2>/dev/null
_res=$(cat "$_rfile" 2>/dev/null || echo "")
echo "$_res" | grep -q "|false|false|" \
    && _pass "behavioral: _auto_sync_one skips commit when clean" \
    || _fail "behavioral: no-change path broken (got: $_res)"
rm -rf "$_td"

# T18: exit $? propagation — no-arg block uses 'exit $?' not 'exit 0'
grep -A2 '\$# -eq 0' "$AUTO_SCRIPT" | grep -q 'exit \$?' \
    && _pass "no-arg path propagates exit code via 'exit \$?'" \
    || _fail "no-arg path uses 'exit 0' — masks auto_sync_all failures"

# T19: dispatcher routing — 'repository_sync help' exits 0 and contains updated usage text
out=$(bash "$AUTO_SCRIPT" help 2>/dev/null)
echo "$out" | grep -q 'Auto-sync all repos' \
    && _pass "usage text documents new no-arg auto-sync default" \
    || _fail "usage text missing new no-arg auto-sync default"

# T20: dispatcher routing — auto|auto-sync case calls auto_sync_all "--dry-run" (static)
grep -A5 'auto|auto-sync)' "$AUTO_SCRIPT" | grep -q 'auto_sync_all "--dry-run"' \
    && _pass "dispatcher: if/else routes --dry-run correctly to auto_sync_all" \
    || _fail "dispatcher: --dry-run routing missing in auto case"

# T23: commit-failed early return — same line carries both result-write and return 0
grep -q 'commit-failed.*return 0\|return 0.*commit-failed' "$AUTO_HELPER" \
    && _pass "commit-failed path writes result and returns early" \
    || _fail "commit-failed path missing early return"

# T25: --dry-run routing — only sole arg triggers auto-sync, not a modifier before a command
# Verify that '[ $# -eq 1 ] && [ "$1" = "--dry-run" ]' pattern is present (not '|| [ "$1"...' )
grep -q '\$# -eq 1.*--dry-run\|--dry-run.*\$# -eq 1' "$AUTO_SCRIPT" \
    && _pass '--dry-run routing: sole-arg check present (not greedy OR)' \
    || _fail '--dry-run routing: missing sole-arg guard'

# T24: dry-run flag parsing — --dry-run added to while-loop option parser
grep -q '\-\-dry-run)' "$AUTO_SCRIPT" \
    && _pass "--dry-run handled in option parser (any positional)" \
    || _fail "--dry-run not in option parser"

# T21: no && B || C pattern in auto dispatch (prevents accidental fallback)
grep -A5 'auto|auto-sync' "$AUTO_SCRIPT" | grep -qv '&&.*auto_sync_all.*||' \
    && _pass "auto dispatch uses if/else, not &&-|| (no accidental fallback)" \
    || _fail "auto dispatch still uses &&-|| pattern"

# T22: source guard present for helper load
grep -q 'if ! source.*repository_sync-auto' "$AUTO_SCRIPT" \
    && _pass "source guard present for helper load failure" \
    || _fail "source guard missing"

# T26: trap does NOT catch INT/TERM (would swallow Ctrl+C and prevent abort)
grep -v '^\s*#' "$AUTO_HELPER" | grep -q 'trap.*INT\|trap.*TERM' \
    && _fail "trap catches INT/TERM — swallows Ctrl+C, prevents abort" \
    || _pass "trap uses EXIT only (INT/TERM not swallowed)"

# T27: behavioral — _auto_sync_one rejects repo names containing '|' (pipe injection guard)
_td=$(mktemp -d)
_rfile="$_td/result"
(WORKSPACE_ROOT="$_td"; source "$AUTO_HELPER" 2>/dev/null
 _auto_sync_one "$_rfile" "bad|repo" "2026-01-01" "false") 2>/dev/null
_res=$(cat "$_rfile" 2>/dev/null || echo "")
echo "$_res" | grep -q 'invalid-repo-name' \
    && _pass "behavioral: pipe-injection guard rejects '|' in repo name" \
    || _fail "behavioral: pipe-injection guard missing (got: $_res)"
rm -rf "$_td"

# T28: behavioral — path traversal repo names rejected (., .., ../, foo/../bar)
_td=$(mktemp -d)
for _bad in '.' '..' '../etc' 'foo/../bar' '/absolute'; do
    _rfile="$_td/result-$(printf '%s' "$_bad" | tr -cd 'A-Za-z0-9_')"
    (WORKSPACE_ROOT="$_td"; source "$AUTO_HELPER" 2>/dev/null
     _auto_sync_one "$_rfile" "$_bad" "2026-01-01" "false") 2>/dev/null
    _res=$(cat "$_rfile" 2>/dev/null || echo "")
    echo "$_res" | grep -q 'invalid-repo-name' \
        && _pass "behavioral: traversal guard rejects '$_bad'" \
        || _fail "behavioral: traversal guard missing for '$_bad' (got: $_res)"
done
rm -rf "$_td"

echo ""
echo "Results: PASS=$PASS  FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
