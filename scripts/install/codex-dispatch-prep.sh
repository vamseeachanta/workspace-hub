#!/usr/bin/env bash
# codex-dispatch-prep.sh — prepare a WRITE-ISOLATED local clone as the dispatch
# root for an OpenAI Codex broker job, nested under Claude Code (#2822).
#
# WHY: Codex sandbox_mode=workspace-write grants write to ONE contiguous root.
# A git worktree splits its metadata out (its .git is a gitlink to
# <main>/.git/worktrees/<n>; shared objects/refs live in the main .git), all
# OUTSIDE the worktree root — so the sandbox mounts them read-only and
# `git commit` fails. A self-contained clone sidesteps this. But `git clone
# --local` HARDLINKS objects: the clone's .git/objects shares inodes with the
# source, so a write-capable sandbox could corrupt the source repo. Therefore
# the DEFAULT is `git clone --no-hardlinks` (distinct inodes = true isolation).
# `--local` is an opt-in for READ-ONLY dispatch only.
#
# This helper only PREPARES the clone and EMITS the broker invocation; it does
# not run the broker. The operator drives the dispatch. See the route report
# docs/reports/2026-05-26-codex-under-claude-pilot.md §"Isolated dispatch".
#
# Prerequisite: the #2804 base route (setup-codex-sandbox.sh --accept-userns-lpe-risk
# + network_access) must already be in place, or Codex cannot run at all.
#
# Usage:
#   codex-dispatch-prep.sh                                  # --check (report, no changes)
#   codex-dispatch-prep.sh --prepare <branch> [--base <ref>] [--allow-hardlinks] [--dest <dir>] [--prompt-file <f>]
#   codex-dispatch-prep.sh --prepare <branch> --dry-run     # print actions, no changes
#   codex-dispatch-prep.sh --cleanup <dir>                  # guarded removal of a managed clone
#   codex-dispatch-prep.sh --help
#
# SECURITY: --allow-hardlinks (`git clone --local`) shares object inodes with the
# source repo. Even so, the helper withholds `--write` from the emitted broker
# command for a hardlinked clone, so it cannot produce a write+shared-inode setup.
#
# PLATFORM: Linux + GNU coreutils (realpath -m, stat -c, find -print -quit, xargs -r,
# sort -V). Same Linux-only scope as the #2804 base route (AppArmor-based); not for macOS/BSD.

# NOTE: options are enabled inside main() (not at source time) so this file is
# safely sourceable by the test harness without altering the caller's shell.

SENTINEL_REL=".git/codex-dispatch-managed"   # marker (inside .git → never committed) → cleanup guard

# ── Read seams (overridable in tests) ───────────────────────────────────────
git_toplevel()   { git -C "${1:-$PWD}" rev-parse --show-toplevel; }
git_object_dir() { git -C "${1:-$PWD}" rev-parse --git-path objects | xargs -r realpath -m; }
git_origin_url() { git -C "${1:-$PWD}" remote get-url origin 2>/dev/null || true; }
path_dev() {  # device id of the nearest existing ancestor of $1 (handles non-existent dest)
    local p="$1"
    while [[ ! -e "$p" && "$p" != "/" ]]; do p="$(dirname "$p")"; done
    stat -c %d "$p" 2>/dev/null || echo 0
}

# ── Mutation seams (overridable in tests) ───────────────────────────────────
do_mkdir_p()           { mkdir -p "$1"; }
do_git_clone()         { git clone "$@"; }
do_git_remote_seturl() { git -C "$1" remote set-url origin "$2"; }
do_git_fetch()         { git -C "$1" fetch origin --quiet; }
do_git_checkout_b()    { git -C "$1" checkout -q -b "$2" "$3"; }
do_touch()             { : > "$1"; }
do_rm_rf()             { rm -rf "$1"; }

# ── Logging ─────────────────────────────────────────────────────────────────
log()  { printf '%s\n' "$*" >&2; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

# ── Pure helpers ─────────────────────────────────────────────────────────────
resolve_clone_mode() {
    if [[ "${ALLOW_HARDLINKS:-0}" == "1" ]]; then echo "--local"; else echo "--no-hardlinks"; fi
}

detect_broker() {  # echoes the codex-companion.mjs path (or a bare name if not found)
    if [[ -n "${BROKER:-}" ]]; then printf '%s' "$BROKER"; return; fi
    local b
    b="$(find "$HOME/.claude/plugins/cache/openai-codex/codex" -path '*/scripts/codex-companion.mjs' 2>/dev/null | sort -V | tail -1 || true)"
    printf '%s' "${b:-codex-companion.mjs}"
}

slugify() { printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '-' | sed -E 's/-+/-/g; s/^-|-$//g'; }

resolve_dest() {  # $1 branch → echoes the default dispatch clone path (sibling of source)
    local branch="$1" src root
    src="$(git_toplevel)"
    root="${CODEX_DISPATCH_ROOT:-$(dirname "$src")}"
    printf '%s/%s-cxc-%s' "$root" "$(basename "$src")" "$(slugify "$branch")"
}

same_filesystem() { [[ "$(path_dev "$1")" == "$(path_dev "$2")" ]]; }

# Preflight the dispatch target: fail closed on a worktree / out-of-root objects;
# warn on a hardlinked object store (not write-isolated).
preflight_target() {
    local dir="$1" srcobjs rel cl_inode src_inode
    if [[ -f "$dir/.git" ]]; then
        fail "TARGET IS A WORKTREE — .git is a gitlink pointing outside the root. Prepare a clone (recommended) or apply the 3-layer worktree grant (route doc §Isolated dispatch)."
    fi
    [[ -d "$dir/.git" ]] || fail "no .git directory at $dir — not a self-contained checkout."
    if [[ -e "$dir/.git/objects/info/alternates" ]]; then
        fail "alternates present — objects live OUTSIDE this root (--shared/--reference); commit will fail read-only. Re-clone with --no-hardlinks."
    fi
    srcobjs="$(git_object_dir "$(git_toplevel)")"
    # `find -print -quit` stops at the first match in find itself — NOT `find | head`,
    # which SIGPIPEs find on a large object store and (under pipefail) aborts the caller.
    local cl_obj
    cl_obj="$(find "$dir/.git/objects" -type f -path '*/??/*' -print -quit 2>/dev/null || true)"
    if [[ -n "$cl_obj" ]]; then
        rel="${cl_obj#"$dir/.git/objects/"}"
        if [[ -e "$srcobjs/$rel" ]]; then
            cl_inode="$(stat -c %i "$cl_obj")"
            src_inode="$(stat -c %i "$srcobjs/$rel")"
            if [[ "$cl_inode" == "$src_inode" ]]; then
                warn "object store is HARDLINKED to the source (shared inode) — a write sandbox could corrupt source objects. OK for read-only dispatch; re-clone with --no-hardlinks for write dispatch."
            fi
        fi
    fi
    return 0
}

# Emit the exact broker invocation for the prepared clone. Prompt path is made
# ABSOLUTE (the broker resolves --prompt-file relative to --cwd, so a relative
# path in the original checkout would not be found from the clone).
# $2 write_safe: "1" → emit a --write dispatch; "0" → emit a READ-ONLY dispatch
# (no --write). A hardlinked clone is NOT write-isolated, so --write is withheld
# mechanically — the helper cannot emit the unsafe write+hardlink combination.
# All interpolated paths are double-quoted so the command survives spaces.
emit_broker_commands() {
    local dest="$1" write_safe="${2:-1}" broker prompt write_flag
    broker="$(detect_broker)"
    prompt="${PROMPT_FILE:+$(realpath -m "$PROMPT_FILE")}"
    prompt="${prompt:-/ABSOLUTE/PATH/TO/your-codex-prompt.md}"
    if [[ "$write_safe" == "1" ]]; then
        write_flag="--write "
    else
        write_flag=""
        echo "# READ-ONLY dispatch: this clone is HARDLINKED to the source (shared object inodes),"
        echo "# so the write flag is intentionally withheld to protect the source repo's objects."
        echo "# Re-run WITHOUT --allow-hardlinks for a write-isolated clone if you need to commit."
    fi
    echo "# Dispatch Codex (jobs are keyed by the clone's git toplevel → status/result also need --cwd):"
    echo "node \"$broker\" task   --cwd \"$dest\" ${write_flag}--background --prompt-file \"$prompt\""
    echo "node \"$broker\" status --cwd \"$dest\""
    echo "node \"$broker\" result --cwd \"$dest\" <JOB_ID>"
}

prepare() {
    local branch="${1:-}"
    [[ -n "$branch" ]] || fail "usage: --prepare <branch>"
    if [[ "$branch" == -* ]]; then fail "branch name cannot start with '-' (got '$branch') — did you forget the branch argument before a flag?"; fi
    local src dest mode parent
    src="$(git_toplevel)"
    dest="${DEST_OVERRIDE:-$(resolve_dest "$branch")}"
    mode="${CLONE_MODE:-$(resolve_clone_mode)}"
    parent="$(dirname "$dest")"

    # Cross-device fallback only matters for --local (hardlinks can't cross devices).
    if [[ "$mode" == "--local" ]] && ! same_filesystem "$parent" "$(git_object_dir "$src")"; then
        warn "--local cannot cross-device; falling back to --no-hardlinks (real object-copy disk cost)."
        mode="--no-hardlinks"
    fi
    # Write-safety is determined by the FINAL mode: only --no-hardlinks gives distinct
    # object inodes. A hardlinked (--local) clone → read-only dispatch (no --write emitted).
    local write_safe=1; [[ "$mode" == "--no-hardlinks" ]] || write_safe=0

    if [[ "${DRY_RUN:-0}" == "1" ]]; then
        log "DRY-RUN — would prepare $dest (mode $mode, base ${BASE_REF:-origin/main}, write_safe=$write_safe)"
        emit_broker_commands "$dest" "$write_safe"
        return 0
    fi

    if [[ -e "$dest" ]]; then fail "destination exists: $dest — run --cleanup first."; fi
    local origin_url; origin_url="$(git_origin_url "$src")"
    [[ -n "$origin_url" ]] || fail "source repo has no 'origin' remote — cannot wire a push target for Codex."
    do_mkdir_p "$parent"
    do_git_clone "$mode" --no-checkout "$src" "$dest"
    do_git_remote_seturl "$dest" "$origin_url"
    do_git_fetch "$dest"
    do_git_checkout_b "$dest" "$branch" "${BASE_REF:-origin/main}"
    do_touch "$dest/${SENTINEL_REL}"
    preflight_target "$dest"
    if [[ "$write_safe" == "1" ]]; then
        log "Prepared WRITE-ISOLATED dispatch clone at: $dest"
    else
        log "Prepared HARDLINKED (read-only) dispatch clone at: $dest — --write will be withheld."
    fi
    emit_broker_commands "$dest" "$write_safe"
}

# Guarded removal — fail closed on EVERY guard, not just the sentinel.
cleanup() {
    local dir="$1" d src root
    d="$(realpath -m "$dir" 2>/dev/null)"
    [[ -n "$d" ]]                                      || fail "cannot resolve path: $dir"
    [[ "$d" != "/" ]]                                  || fail "refusing to delete /"
    [[ "$d" != "$(realpath -m "$HOME" 2>/dev/null)" ]] || fail "refusing to delete \$HOME"
    src="$(git_toplevel)"
    [[ "$d" != "$(realpath -m "$src" 2>/dev/null)" ]]  || fail "refusing to delete the source repo"
    case "$(basename "$d")" in *-cxc-*) : ;; *) fail "name does not match dispatch pattern '*-cxc-*': $d" ;; esac
    root="$(realpath -m "${CODEX_DISPATCH_ROOT:-$(dirname "$src")}" 2>/dev/null)"
    case "$d/" in "$root"/*) : ;; *) fail "outside the dispatch root ($root): $d" ;; esac
    [[ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null | xargs -r realpath -m 2>/dev/null)" == "$d" ]] \
        || fail "not a git toplevel: $d"
    # Reject a mount boundary: a bind/other mount under the dispatch root has a different
    # device id than its parent dir, and could delete content that isn't really ours.
    [[ "$(stat -c %d "$d" 2>/dev/null)" == "$(stat -c %d "$(dirname "$d")" 2>/dev/null)" ]] \
        || fail "target sits on a different filesystem than its parent (possible mount point) — refusing rm -rf: $d"
    [[ -e "$d/${SENTINEL_REL}" ]]                      || fail "no $SENTINEL_REL sentinel — not a managed clone: $d"
    do_rm_rf "$d"
    log "Removed managed dispatch clone: $d"
}

report_state() {
    local src broker
    src="$(git_toplevel 2>/dev/null || echo '(not in a git repo)')"
    broker="$(detect_broker)"
    log "── Codex dispatch-prep state ──"
    log "source repo:        $src"
    log "default dispatch root: ${CODEX_DISPATCH_ROOT:-$(dirname "$src" 2>/dev/null)}"
    log "default clone mode:  $(resolve_clone_mode) (write-isolated unless --allow-hardlinks)"
    log "broker:             ${broker:-(codex-companion.mjs not found — check the openai-codex plugin)}"
    log "base route (#2804): run scripts/install/setup-codex-sandbox.sh --check to verify userns + network_access"
    log ""
    log "NEXT: $0 --prepare <branch>   (then run the emitted broker commands)"
}

usage() { sed -n '2,33p' "${BASH_SOURCE[0]}"; }

main() {
    set -euo pipefail
    local mode="check"
    BRANCH=""; CLEANUP_DIR=""; BASE_REF="${BASE_REF:-origin/main}"
    ALLOW_HARDLINKS="${ALLOW_HARDLINKS:-0}"; DRY_RUN="${DRY_RUN:-0}"
    DEST_OVERRIDE="${DEST_OVERRIDE:-}"; PROMPT_FILE="${PROMPT_FILE:-}"
    while (( $# > 0 )); do
        case "$1" in
            --check)            mode="check" ;;
            --prepare)          mode="prepare"; BRANCH="${2:-}"; shift ;;
            --cleanup)          mode="cleanup"; CLEANUP_DIR="${2:-}"; shift ;;
            --dry-run)          DRY_RUN=1 ;;
            --allow-hardlinks)  ALLOW_HARDLINKS=1 ;;
            --base)             BASE_REF="${2:-}"; shift ;;
            --dest)             DEST_OVERRIDE="${2:-}"; shift ;;
            --prompt-file)      PROMPT_FILE="${2:-}"; shift ;;
            --help|-h)          usage; exit 0 ;;
            *)                  fail "unknown arg: $1 (see --help)" ;;
        esac
        shift
    done
    case "$mode" in
        check)   report_state ;;
        prepare) prepare "$BRANCH" ;;
        cleanup) [[ -n "$CLEANUP_DIR" ]] || fail "usage: --cleanup <dir>"; cleanup "$CLEANUP_DIR" ;;
    esac
}

# Run main only when executed directly, not when sourced (tests source this file).
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
