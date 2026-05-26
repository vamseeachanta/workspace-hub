#!/usr/bin/env bash
# Intentional dependency-injection test idiom: override functions are invoked
# indirectly (after `source`), some vars are read inside subshells/`eval`, and
# a few single-quoted strings are deliberately passed to `eval` unexpanded.
# shellcheck disable=SC2016,SC2034,SC2329,SC2001,SC2015,SC2018,SC2019
# test_codex_dispatch_prep.sh — TDD tests for scripts/install/codex-dispatch-prep.sh
# Issue: vamseeachanta/workspace-hub#2822
#
# Strategy (mirrors tests/setup/test_install_provider_clis.sh):
#   The helper is sourceable (main runs only when executed directly). Each test
#   sources it inside an isolated ( ) subshell, redefines the read seams
#   (git_toplevel/git_object_dir/git_origin_url/path_dev) to return fixtures and
#   the mutation seams (do_*) to append to a log, then calls the function under
#   test and asserts on the log / stdout / exit code.
#
# Three layers:
#   (a) unit         — prepare decision/emission logic with stubbed seams
#   (b) cleanup guard — real temp-dir fixtures (fail-closed on every guard)
#   (c) integration   — real clones: the inode-isolation property itself
#
# Run: bash tests/setup/test_codex_dispatch_prep.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/install/codex-dispatch-prep.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
_fail() {
    echo "  FAIL  $1"; [[ -n "${2:-}" ]] && echo "        $2"
    FAIL=$((FAIL + 1)); FAILED_TESTS+=("$1")
}
_assert_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then _pass "$name"
    else _fail "$name" "expected substring: $needle"; echo "$haystack" | sed 's/^/          /'; fi
}
_assert_not_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then _fail "$name" "forbidden substring present: $needle"
    else _pass "$name"; fi
}
_assert_rc() {  # name expected_rc actual_rc
    if [[ "$2" == "$3" ]]; then _pass "$1"; else _fail "$1" "expected rc=$2 got rc=$3"; fi
}

# Common stub preamble for unit tests: deterministic read seams + logging mutation seams.
# Writes the action log to $LOG (path passed in). path_dev returns per-arg device ids from
# an associative map serialized as "path=dev;..." in $DEVMAP (default: everything dev 1).
_unit_prelude() {
cat <<'PRE'
    git_toplevel()   { echo "/src/repo"; }
    git_object_dir() { echo "/src/repo/.git/objects"; }
    git_origin_url() { echo "https://github.com/vamseeachanta/workspace-hub.git"; }
    path_dev()       { # honor DEVMAP "path=dev;..."; default 1
        local p="$1" pair k v
        IFS=';' read -ra _pairs <<<"${DEVMAP:-}"
        for pair in "${_pairs[@]}"; do k="${pair%%=*}"; v="${pair#*=}"; [[ "$p" == "$k" ]] && { echo "$v"; return; }; done
        echo 1; }
    do_mkdir_p()           { echo "mkdir -p $1" >>"$LOG"; }
    do_git_clone()         { echo "clone $*" >>"$LOG"; }
    do_git_remote_seturl() { echo "remote set-url origin in=$1 url=$2" >>"$LOG"; }
    do_git_fetch()         { echo "fetch origin in=$1" >>"$LOG"; }
    do_git_checkout_b()    { echo "checkout -b in=$1 branch=$2 base=$3" >>"$LOG"; }
    do_touch()             { echo "touch $1" >>"$LOG"; }
    do_rm_rf()             { echo "rm -rf $1" >>"$LOG"; }
    preflight_target()     { :; }   # exercised in integration layer, not here
PRE
}

echo "=== test_codex_dispatch_prep.sh (issue #2822) ==="
echo ""

if [[ ! -f "$HELPER" ]]; then
    echo "  FAIL  helper script missing: $HELPER (expected in TDD RED phase)"
    echo ""; echo "=== Summary: 0 PASS, 1 FAIL ==="; exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# (a) UNIT — prepare decision/emission logic
# ─────────────────────────────────────────────────────────────────────────────
_run_prepare() {  # $1 extra setup lines (env/overrides); emits LOG then '---STDOUT---' then prepare stdout
    local extra="$1"
    local tmp; tmp="$(mktemp -d)"; local log="$tmp/act.log"; : >"$log"
    local out
    out="$(
        # shellcheck disable=SC1090
        source "$HELPER"
        LOG="$log"
        eval "$(_unit_prelude)"
        eval "$extra"
        prepare "${BRANCH:-feat/2822-codex-dispatch-prep}" 2>>"$log"
    )"
    cat "$log"; echo "---STDOUT---"; echo "$out"
    rm -rf "$tmp"
}

# Test: default write dispatch uses --no-hardlinks (isolation), never --local
out="$(_run_prepare 'CLONE_MODE="$(resolve_clone_mode)"')"
_assert_contains   "default_mode_no_hardlinks"    "clone --no-hardlinks" "$out"
_assert_not_contains "default_mode_not_local"     "clone --local"        "$out"

# Test: --allow-hardlinks opt-in flips to --local (same filesystem)
out="$(_run_prepare 'ALLOW_HARDLINKS=1; CLONE_MODE="$(resolve_clone_mode)"')"
_assert_contains   "allow_hardlinks_opt_in_local" "clone --local" "$out"

# Test: --local across devices falls back to --no-hardlinks (+ warn)
#   parent dir on dev 1, object dir on dev 2  → not same filesystem
out="$(_run_prepare 'ALLOW_HARDLINKS=1; CLONE_MODE="$(resolve_clone_mode)"; DEVMAP="/src/repo/.git/objects=2"')"
_assert_contains   "local_xdevice_falls_back"     "clone --no-hardlinks" "$out"
_assert_contains   "local_xdevice_warns"          "cross device"         "$(tr 'A-Z-' 'a-z ' <<<"$out")"

# Test: origin re-pointed at the GitHub URL (so Codex can push)
out="$(_run_prepare '')"
_assert_contains   "remote_wired_to_github"       "set-url origin in=" "$out"
_assert_contains   "remote_wired_github_url"      "github.com/vamseeachanta/workspace-hub.git" "$out"

# Test: fetch precedes checkout -b (base on TRUE remote main, not stale source ref)
out="$(_run_prepare '')"
fetch_line="$(grep -n 'fetch origin' <<<"$out" | head -1 | cut -d: -f1)"
checkout_line="$(grep -n 'checkout -b' <<<"$out" | head -1 | cut -d: -f1)"
if [[ -n "$fetch_line" && -n "$checkout_line" && "$fetch_line" -lt "$checkout_line" ]]; then
    _pass "fetch_before_checkout"
else _fail "fetch_before_checkout" "fetch(line $fetch_line) must precede checkout(line $checkout_line)"; fi

# Test: emitted broker invocation uses --cwd, never --cd
out="$(_run_prepare '')"
stdout="${out#*---STDOUT---}"
_assert_contains     "emits_cwd"        "--cwd" "$stdout"
_assert_not_contains "no_cd_flag_leak"  "--cd " "$stdout"

# Test: emitted --prompt-file path is absolute (resolved relative to --cwd otherwise).
# The emitted command double-quotes paths, so strip an optional leading quote.
promptline="$(grep -- '--prompt-file' <<<"$stdout" | head -1)"
promptval="$(sed -n 's/.*--prompt-file[= ]"\?\([^" ]*\).*/\1/p' <<<"$promptline")"
if [[ "$promptval" == /* ]]; then _pass "prompt_file_absolute"
else _fail "prompt_file_absolute" "emitted prompt path not absolute: '$promptval'"; fi

# Test: emitted status + result carry --cwd
_assert_contains "status_has_cwd" "status --cwd" "$stdout"
_assert_contains "result_has_cwd" "result --cwd" "$stdout"

# Test: default (write-isolated) dispatch emits --write
out="$(_run_prepare '')"
stdout="${out#*---STDOUT---}"
_assert_contains "default_emits_write" "--write" "$stdout"

# Test: --allow-hardlinks (hardlinked, read-only) dispatch must NOT emit --write
out="$(_run_prepare 'ALLOW_HARDLINKS=1; CLONE_MODE="$(resolve_clone_mode)"')"
stdout="${out#*---STDOUT---}"
_assert_not_contains "allow_hardlinks_no_write" "--write" "$stdout"
_assert_contains     "allow_hardlinks_readonly_note" "READ-ONLY" "$stdout"

# Test: --dry-run performs zero mutation (log empty of do_* actions)
out="$(_run_prepare 'DRY_RUN=1')"
logpart="${out%%---STDOUT---*}"
_assert_not_contains "dry_run_no_clone"    "clone "    "$logpart"
_assert_not_contains "dry_run_no_remote"   "set-url"   "$logpart"
_assert_not_contains "dry_run_no_fetch"    "fetch origin" "$logpart"
_assert_not_contains "dry_run_no_rm"       "rm -rf"    "$logpart"

# Test: default dest is a sibling of the source repo, named *-cxc-*
dest="$(
    # shellcheck disable=SC1090
    source "$HELPER"; git_toplevel(){ echo /home/u/workspace-hub; }
    CODEX_DISPATCH_ROOT=""; resolve_dest "feat/2822-x"
)"
_assert_contains "dest_sibling_of_src"   "/home/u/workspace-hub-cxc-" "$dest"
_assert_contains "dest_slug_no_slash"    "feat-2822-x" "$dest"

# ─────────────────────────────────────────────────────────────────────────────
# (b) CLEANUP GUARD — fail closed on every guard (Codex#3); real temp fixtures
# ─────────────────────────────────────────────────────────────────────────────
# Build a fake source repo + dispatch root + a valid managed clone fixture.
GUARD_TMP="$(mktemp -d)"
SRC_REPO="$GUARD_TMP/workspace-hub"; DISPATCH="$GUARD_TMP/dispatch"
mkdir -p "$SRC_REPO" "$DISPATCH"
git init -q "$SRC_REPO"

_make_managed_clone() {  # $1 dir-name → creates a git repo with sentinel under $DISPATCH
    local d="$DISPATCH/$1"; git init -q "$d"; mkdir -p "$d/.git"; touch "$d/.git/codex-dispatch-managed"; echo "$d"
}
_run_cleanup() {  # $1 target dir, $2 extra setup → emits log; sets global RC
    local target="$1" extra="$2"
    local log="$GUARD_TMP/cleanup.log"; : >"$log"
    (
        # shellcheck disable=SC1090
        source "$HELPER"
        git_toplevel(){ echo "$SRC_REPO"; }
        CODEX_DISPATCH_ROOT="$DISPATCH"
        do_rm_rf(){ echo "rm -rf $1" >>"$log"; }
        eval "$extra"
        cleanup "$target"
    ) >/dev/null 2>&1
    RC=$?
    CLEAN_LOG="$(cat "$log")"
}

valid_clone="$(_make_managed_clone "workspace-hub-cxc-feat-x")"
_run_cleanup "$valid_clone" ''
_assert_rc "cleanup_managed_ok_rc" 0 "$RC"
_assert_contains "cleanup_managed_ok_rm" "rm -rf $valid_clone" "$CLEAN_LOG"

# missing sentinel → refuse
nosentinel="$DISPATCH/workspace-hub-cxc-nosentinel"; git init -q "$nosentinel"
_run_cleanup "$nosentinel" ''
_assert_rc "cleanup_requires_sentinel" 1 "$RC"
_assert_not_contains "cleanup_no_rm_without_sentinel" "rm -rf" "$CLEAN_LOG"

# name not matching *-cxc-* → refuse
badname="$DISPATCH/workspace-hub-plain"; git init -q "$badname"; touch "$badname/.git/codex-dispatch-managed"
_run_cleanup "$badname" ''
_assert_rc "cleanup_rejects_non_pattern" 1 "$RC"

# outside the dispatch root → refuse (valid-looking but wrong parent)
outside="$GUARD_TMP/workspace-hub-cxc-outside"; git init -q "$outside"; touch "$outside/.git/codex-dispatch-managed"
_run_cleanup "$outside" ''
_assert_rc "cleanup_rejects_outside_root" 1 "$RC"

# the source repo itself → refuse
_run_cleanup "$SRC_REPO" ''
_assert_rc "cleanup_rejects_source_repo" 1 "$RC"

# / and $HOME → refuse
_run_cleanup "/" ''
_assert_rc "cleanup_rejects_root" 1 "$RC"
_run_cleanup "$HOME" ''
_assert_rc "cleanup_rejects_home" 1 "$RC"

rm -rf "$GUARD_TMP"

# ─────────────────────────────────────────────────────────────────────────────
# (c) INTEGRATION — the isolation property (real clones)
# ─────────────────────────────────────────────────────────────────────────────
# One temp workdir so src + clones share a device (so --local hardlinks can succeed).
INT_TMP="$(mktemp -d)"
ISRC="$INT_TMP/src"; git init -q "$ISRC"
( cd "$ISRC" && git config user.email t@t && git config user.name t \
  && echo hello > f.txt && git add f.txt && git commit -q -m init )
# Compare the SAME relative object path across repos (not the first object in each).
_first_obj_rel() { ( cd "$1/.git/objects" 2>/dev/null && find . -type f -path './??/*' | head -1 | sed 's|^\./||' ); }
rel="$(_first_obj_rel "$ISRC")"
_inode_of() { stat -c %i "$1/.git/objects/$rel" 2>/dev/null || echo "NONE"; }
src_inode="$(_inode_of "$ISRC")"

# --no-hardlinks → DISTINCT inode (write-isolated), no alternates
git clone --no-hardlinks --no-checkout "$ISRC" "$INT_TMP/nohl" >/dev/null 2>&1
nohl_inode="$(_inode_of "$INT_TMP/nohl")"
if [[ "$src_inode" != "NONE" && "$nohl_inode" != "NONE" && "$nohl_inode" != "$src_inode" ]]; then _pass "nohardlinks_distinct_inode"
else _fail "nohardlinks_distinct_inode" "rel=$rel src=$src_inode nohl=$nohl_inode (must both exist & differ)"; fi
[[ ! -e "$INT_TMP/nohl/.git/objects/info/alternates" ]] \
    && _pass "no_alternates_after_nohardlinks" || _fail "no_alternates_after_nohardlinks" "alternates present"

# --local → SHARED inode (documents the hazard the default avoids)
git clone --local --no-checkout "$ISRC" "$INT_TMP/local" >/dev/null 2>&1
local_inode="$(_inode_of "$INT_TMP/local")"
if [[ "$src_inode" != "NONE" && "$local_inode" == "$src_inode" ]]; then _pass "local_shares_inode_hazard"
else _fail "local_shares_inode_hazard" "rel=$rel src=$src_inode local=$local_inode (expected shared)"; fi

# preflight_target rejects a real worktree (gitlink .git is a FILE)
( cd "$ISRC" && git worktree add -q "$INT_TMP/wt" -b wtbranch ) >/dev/null 2>&1
wt_rc=0
(
    # shellcheck disable=SC1090
    source "$HELPER"; git_toplevel(){ echo "$ISRC"; }; git_object_dir(){ echo "$ISRC/.git/objects"; }
    preflight_target "$INT_TMP/wt"
) >/dev/null 2>&1 || wt_rc=$?
_assert_rc "preflight_rejects_worktree" 1 "$wt_rc"

# preflight_target warns when object store is hardlinked to the source (--local clone)
hl_warn="$(
    # shellcheck disable=SC1090
    source "$HELPER"; git_toplevel(){ echo "$ISRC"; }; git_object_dir(){ echo "$ISRC/.git/objects"; }
    preflight_target "$INT_TMP/local" 2>&1
)"
_assert_contains "preflight_warns_hardlinked" "hardlink" "$(tr 'A-Z' 'a-z' <<<"$hl_warn")"

rm -rf "$INT_TMP"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then echo "    Failed: ${FAILED_TESTS[*]}"; exit 1; fi
exit 0
