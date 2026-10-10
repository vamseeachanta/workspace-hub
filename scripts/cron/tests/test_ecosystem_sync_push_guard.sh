#!/usr/bin/env bash
# test_ecosystem_sync_push_guard.sh — Tests for .claude/cron/ecosystem-sync.sh
#
# The script is a registered direct-main exemption
# (.claude/rules/merge-authorization.md): it may push only
# .claude/state/ecosystem-sync/last-sync.yaml and docs/sync-reports/ to main.
# These tests check that the script enforces that path restriction.
#
# Every push goes to a local bare repository in a temp dir; nothing reaches a
# real remote. `uv` (and `flock` where absent) are replaced by PATH stubs.
# Run: bash scripts/cron/tests/test_ecosystem_sync_push_guard.sh
#
# Issue: #3985

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$(cd "$SCRIPT_DIR/../../.." && pwd)/.claude/cron/ecosystem-sync.sh"

# Isolate fixture git processes from any caller repository binding.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE

PASSES=0
FAILS=0
pass() { PASSES=$((PASSES + 1)); echo "  PASS: $1"; }
fail() { FAILS=$((FAILS + 1)); echo "  FAIL: $1"; }

assert_eq() {
    if [[ "$2" == "$3" ]]; then pass "$1"; else fail "$1 (expected '$2', got '$3')"; fi
}
assert_ne() {
    if [[ "$2" != "$3" ]]; then pass "$1"; else fail "$1 (got '$3')"; fi
}

# Creates <tmp>/remote.git (bare) and <tmp>/local (clone carrying the script),
# plus <tmp>/bin with a stub `uv`. Prints <tmp>.
setup_fixture() {
    local tmp
    tmp="$(mktemp -d)"
    git init --bare --quiet --initial-branch=main "$tmp/remote.git"
    git clone --quiet "$tmp/remote.git" "$tmp/local" 2>/dev/null
    (
        cd "$tmp/local" || exit 1
        git config user.email "test@example.invalid"
        git config user.name "test"
        git config core.autocrlf false
        git checkout --quiet -B main
        mkdir -p .claude/cron .claude/state/ecosystem-sync docs/sync-reports
        cp "$SYNC_SCRIPT" .claude/cron/ecosystem-sync.sh
        echo "last_sync: never" > .claude/state/ecosystem-sync/last-sync.yaml
        echo "initial" > README.md
        printf 'logs/\n' > .gitignore
        git add -A
        git commit --quiet -m "fixture"
        git push --quiet origin main 2>/dev/null
    )

    mkdir -p "$tmp/bin"
    # Stub uv: emulates run.py writing state + a report. Options via env:
    #   STUB_UV_RC=<n>              exit code
    #   STUB_ADVANCE_REMOTE=1       push an unrelated commit to the remote mid-run
    #   STUB_REPORT_NAME=<path>     report path below docs/sync-reports/
    cat > "$tmp/bin/uv" <<'STUB'
#!/usr/bin/env bash
echo "last_sync: $(date -u +%FT%TZ)" > .claude/state/ecosystem-sync/last-sync.yaml
report="${STUB_REPORT_NAME:-digest.md}"
mkdir -p "docs/sync-reports/$(dirname "$report")"
echo "# digest" > "docs/sync-reports/$report"
if [[ "${STUB_ADVANCE_REMOTE:-0}" == "1" ]]; then
    other="$(mktemp -d)"
    git clone --quiet "$(git config --get remote.origin.url)" "$other/c" 2>/dev/null
    (cd "$other/c" && git -c user.email=o@example.invalid -c user.name=o \
        commit --quiet --allow-empty -m "other machine" && git push --quiet origin main 2>/dev/null)
    rm -rf "$other"
fi
exit "${STUB_UV_RC:-0}"
STUB
    chmod +x "$tmp/bin/uv"
    real_mktemp="$(command -v mktemp)"
    cat > "$tmp/bin/mktemp" <<STUB
#!/usr/bin/env bash
if [[ "\${STUB_MKTEMP_FULL:-0}" == "1" ]]; then
    path="$tmp/write-fails-\$\$-\$RANDOM"
    rm -f "\$path"
    mkfifo "\$path"
    python3 -c 'import sys; f = open(sys.argv[1], "rb"); f.close()' "\$path" >/dev/null 2>&1 &
    echo "\$path"
else
    exec "$real_mktemp" "\$@"
fi
STUB
    chmod +x "$tmp/bin/mktemp"
    if ! command -v flock >/dev/null 2>&1; then
        printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp/bin/flock"
        chmod +x "$tmp/bin/flock"
    fi
    echo "$tmp"
}

run_sync() {
    local tmp="$1"
    (
        cd "$tmp/local" || exit 99
        PATH="$tmp/bin:$PATH" ECOSYSTEM_SYNC_LOCKFILE="$tmp/sync.lock" \
            bash .claude/cron/ecosystem-sync.sh
    )
}

remote_head() { git --git-dir="$1/remote.git" rev-parse main; }
remote_files() { git --git-dir="$1/remote.git" ls-tree -r --name-only main | sort | tr '\n' ' '; }

echo "=== allowed paths are committed and pushed ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
run_sync "$T"; rc=$?
assert_eq "exit code 0" "0" "$rc"
assert_ne "remote main advanced" "$before" "$(remote_head "$T")"
changed="$(git --git-dir="$T/remote.git" diff --name-only "$before" main | sort | tr '\n' ' ')"
assert_eq "pushed commit touches only allowed paths" \
    ".claude/state/ecosystem-sync/last-sync.yaml docs/sync-reports/digest.md " "$changed"
rm -rf "$T"

echo "=== pre-staged file outside the allowlist blocks commit and push ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
local_before="$(git -C "$T/local" rev-parse HEAD)"
echo "secret-ish" > "$T/local/unrelated.txt"
git -C "$T/local" add unrelated.txt
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
assert_eq "no local commit created" "$local_before" "$(git -C "$T/local" rev-parse HEAD)"
assert_eq "foreign file remains staged, not committed" "unrelated.txt" \
    "$(git -C "$T/local" diff --cached --name-only -- unrelated.txt)"
rm -rf "$T"

echo "=== unpushed local commit outside the allowlist blocks push ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
(
    cd "$T/local" || exit 1
    # Reach the run with an unpushed foreign commit already on main (the
    # script's ff-only pull leaves it in place).
    echo "change" >> README.md
    git commit --quiet -am "unrelated local work"
)
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
assert_eq "remote tree unchanged" ".claude/cron/ecosystem-sync.sh .claude/state/ecosystem-sync/last-sync.yaml .gitignore README.md " \
    "$(remote_files "$T")"
rm -rf "$T"

echo "=== foreign path added then reverted in unpushed commits still blocks push ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
(
    cd "$T/local" || exit 1
    echo "x" > scripts.txt && git add scripts.txt && git commit --quiet -m "add"
    git rm --quiet scripts.txt && git commit --quiet -m "revert"
)
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
rm -rf "$T"

echo "=== temp-file write failure blocks mixed outgoing commit ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
(
    cd "$T/local" || exit 1
    mkdir -p config docs/sync-reports
    echo "foreign" > config/foreign.yaml
    echo "allowed" > docs/sync-reports/mixed.md
    git add config/foreign.yaml docs/sync-reports/mixed.md
    git commit --quiet -m "mixed outgoing paths"
)
STUB_MKTEMP_FULL=1 run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
rm -rf "$T"

echo "=== path filter propagates disallowed-path write failure ==="
STATE_FILE=".claude/state/ecosystem-sync/last-sync.yaml"
REPORT_DIR="docs/sync-reports/"
source <(sed -n '/^outside_allowlist_z()/,/^}/p' "$SYNC_SCRIPT")
printf 'config/foreign.yaml\0docs/sync-reports/allowed.md\0' | outside_allowlist_z > /dev/full
rc=$?
assert_eq "write failure returns nonzero" "1" "$rc"

echo "=== merge commit in outgoing range blocks push ==="
T="$(setup_fixture)"
(
    cd "$T/local" || exit 1
    other="$(mktemp -d)"
    git clone --quiet "$(git config --get remote.origin.url)" "$other/c" 2>/dev/null
    (
        cd "$other/c" || exit 1
        git config user.email "remote@example.invalid"
        git config user.name "remote"
        echo "remote update" >> README.md
        git commit --quiet -am "remote readme update"
        git push --quiet origin main 2>/dev/null
    )
    rm -rf "$other"
    git fetch --quiet origin main
    echo "local report" > docs/sync-reports/local.md
    git add docs/sync-reports/local.md
    git commit --quiet -m "allowed local report"
    git merge --quiet -s ours origin/main -m "merge origin/main with local report"
)
before="$(remote_head "$T")"
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
rm -rf "$T"

echo "=== missing origin/main blocks instead of failing open ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
(
    cd "$T/local" || exit 1
    git config remote.origin.fetch "+refs/heads/not-main:refs/remotes/origin/not-main"
    git update-ref -d refs/remotes/origin/main
)
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
rm -rf "$T"

echo "=== staged rename from outside into report dir blocks before commit ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
local_before="$(git -C "$T/local" rev-parse HEAD)"
(
    cd "$T/local" || exit 1
    mkdir -p scripts
    echo "helper" > scripts/helper.sh
    git add scripts/helper.sh
    git commit --quiet -m "add helper"
    git push --quiet origin main 2>/dev/null
    git mv scripts/helper.sh docs/sync-reports/helper.sh
)
before="$(remote_head "$T")"
local_before="$(git -C "$T/local" rev-parse HEAD)"
run_sync "$T"; rc=$?
assert_eq "exit code 6" "6" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
assert_eq "no local commit created" "$local_before" "$(git -C "$T/local" rev-parse HEAD)"
rm -rf "$T"

echo "=== report paths with spaces and newlines are accepted ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
odd_name=$'space dir/report with space\nand newline.md'
STUB_REPORT_NAME="$odd_name" run_sync "$T"; rc=$?
assert_eq "exit code 0" "0" "$rc"
assert_ne "remote main advanced" "$before" "$(remote_head "$T")"
git --git-dir="$T/remote.git" cat-file -e "main:docs/sync-reports/$odd_name"
assert_eq "odd report path was pushed" "0" "$?"
rm -rf "$T"

echo "=== rejected push rebases and re-pushes only allowed paths ==="
T="$(setup_fixture)"
STUB_ADVANCE_REMOTE=1 run_sync "$T"; rc=$?
assert_eq "exit code 0" "0" "$rc"
assert_eq "remote main is the sync commit on top of the other machine's commit" \
    "other machine" "$(git --git-dir="$T/remote.git" log -1 --format=%s main~1)"
changed="$(git --git-dir="$T/remote.git" diff --name-only main~1 main | sort | tr '\n' ' ')"
assert_eq "sync commit touches only allowed paths" \
    ".claude/state/ecosystem-sync/last-sync.yaml docs/sync-reports/digest.md " "$changed"
rm -rf "$T"

echo "=== failed sync run neither commits nor pushes ==="
T="$(setup_fixture)"
before="$(remote_head "$T")"
STUB_UV_RC=2 run_sync "$T"; rc=$?
assert_eq "exit code propagates run.py failure" "2" "$rc"
assert_eq "remote main unchanged" "$before" "$(remote_head "$T")"
rm -rf "$T"

echo ""
echo "Results: $PASSES passed, $FAILS failed"
[[ "$FAILS" == "0" ]]
