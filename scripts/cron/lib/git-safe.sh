#!/usr/bin/env bash
# git-safe.sh — Shared git synchronization library for cron scripts
#
# Provides safe, flock-coordinated git operations for all cron scripts
# that touch workspace-hub. ALL cron scripts should source this instead
# of implementing their own git pull/commit/push.
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/lib/git-safe.sh"
#   git_safe_init "/path/to/repo"
#   git_safe_pull        # flock-protected pull --rebase
#   git_safe_commit "msg" [files...]  # flock-protected add/commit
#   git_safe_push        # flock-protected push with retry
#   git_safe_sync "msg" [files...]    # pull + commit + push in one locked block
#
# Issue: #1548 | Policy: all cron git ops must use this library

# Guard against double-sourcing
if [[ -n "${_GIT_SAFE_LOADED:-}" ]]; then
    return 0
fi
_GIT_SAFE_LOADED=1

# ============================================================================
# Configuration (override before calling git_safe_init if needed)
# ============================================================================
GIT_SAFE_LOCK="${GIT_SAFE_LOCK:-/tmp/workspace-hub-git.lock}"
GIT_SAFE_FLOCK_TIMEOUT="${GIT_SAFE_FLOCK_TIMEOUT:-120}"
GIT_SAFE_PUSH_RETRIES="${GIT_SAFE_PUSH_RETRIES:-3}"
GIT_SAFE_PUSH_BACKOFF="${GIT_SAFE_PUSH_BACKOFF:-5}"  # seconds, doubles each retry
GIT_SAFE_REPO=""
GIT_SAFE_LOG_PREFIX="${GIT_SAFE_LOG_PREFIX:-[git-safe]}"

# ============================================================================
# Logging
# ============================================================================
_git_safe_log() {
    echo "${GIT_SAFE_LOG_PREFIX} $(date '+%H:%M:%S') $*" >&2
}

# ============================================================================
# Master disable switch (surgical sync pause)
# ============================================================================
# If the flag file exists, all mutating git_safe_* ops (pull/commit/push/sync)
# no-op. Cron scripts still run their actual work; they just don't stash,
# commit, or push to origin — eliminating main-branch contention and
# auto-stash orphaning. Re-enable by removing the flag file:
#   rm ~/.workspace-hub-git-safe-disabled
GIT_SAFE_DISABLE_FLAG="${GIT_SAFE_DISABLE_FLAG:-${HOME}/.workspace-hub-git-safe-disabled}"
_git_safe_disabled() {
    [[ -f "$GIT_SAFE_DISABLE_FLAG" ]] || return 1
    _git_safe_log "DISABLED via ${GIT_SAFE_DISABLE_FLAG} — skipping git sync op"
    return 0
}

# ============================================================================
# Initialization
# ============================================================================
git_safe_init() {
    local repo_path="${1:-.}"
    GIT_SAFE_REPO="$(cd "$repo_path" && git rev-parse --show-toplevel 2>/dev/null)" || {
        _git_safe_log "ERROR: not a git repository: $repo_path"
        return 1
    }
    _git_safe_log "Initialized for ${GIT_SAFE_REPO}"
}

# ============================================================================
# Core: flock-wrapped execution using file descriptor
# ============================================================================
# Uses fd-based flock to avoid bash -c patterns.
# Each function acquires the lock, does work, and releases.
_git_safe_lock_acquire() {
    exec 9>"$GIT_SAFE_LOCK"
    if ! flock --timeout "$GIT_SAFE_FLOCK_TIMEOUT" 9; then
        _git_safe_log "WARNING: could not acquire git lock within ${GIT_SAFE_FLOCK_TIMEOUT}s"
        return 1
    fi
}

_git_safe_lock_release() {
    flock -u 9 2>/dev/null || true
    exec 9>&- 2>/dev/null || true
}

# ============================================================================
# Index healing — recovers from corrupt .git/index
# ============================================================================
git_heal_index() {
    local git_dir="${GIT_SAFE_REPO:-.}"
    if ! git -C "$git_dir" status >/dev/null 2>&1; then
        _git_safe_log "WARNING: git index appears corrupt, attempting recovery"
        # Remove stale lock if present
        rm -f "${git_dir}/.git/index.lock" 2>/dev/null || true
        # Rebuild index from HEAD
        if git -C "$git_dir" read-tree HEAD 2>/dev/null; then
            _git_safe_log "Index recovered via read-tree HEAD"
            return 0
        else
            _git_safe_log "ERROR: index recovery failed"
            return 1
        fi
    fi
    return 0
}

# ============================================================================
# Safe pull — lock + heal + stash + rebase
# ============================================================================
git_safe_pull() {
    _git_safe_disabled && return 0
    local git_dir="${GIT_SAFE_REPO:-.}"

    _git_safe_lock_acquire || {
        _git_safe_log "WARNING: running pull without lock"
    }

    cd "$git_dir" || { _git_safe_lock_release; return 1; }

    # Heal index if corrupt
    git_heal_index

    # Stash any dirty state before rebase
    local stash_needed=false
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        if git stash push -m "git-safe-auto-stash" --quiet 2>/dev/null; then
            stash_needed=true
        fi
    fi

    # Pull with rebase
    if git pull --rebase --quiet origin main 2>/dev/null; then
        _git_safe_log "Pull succeeded"
    else
        _git_safe_log "WARNING: pull failed — continuing with local state"
        git rebase --abort 2>/dev/null || true
    fi

    # Restore stash if we created one
    if [[ "$stash_needed" == "true" ]]; then
        git stash pop --quiet 2>/dev/null || {
            _git_safe_log "WARNING: stash pop failed — stash preserved"
        }
    fi

    _git_safe_lock_release
}

# ============================================================================
# Safe commit — lock + heal + add + commit
# ============================================================================
git_safe_commit() {
    _git_safe_disabled && return 0
    local msg="${1:?commit message required}"
    shift
    local files=("$@")
    local git_dir="${GIT_SAFE_REPO:-.}"

    _git_safe_lock_acquire || {
        _git_safe_log "WARNING: running commit without lock"
    }

    cd "$git_dir" || { _git_safe_lock_release; return 1; }

    # Heal index if corrupt
    git_heal_index

    # Add files
    if [[ ${#files[@]} -gt 0 ]]; then
        git add "${files[@]}" 2>/dev/null || {
            _git_safe_log "WARNING: git add failed"
            _git_safe_lock_release
            return 1
        }
    else
        git add -A 2>/dev/null || {
            _git_safe_log "WARNING: git add -A failed"
            _git_safe_lock_release
            return 1
        }
    fi

    # Skip if nothing staged
    if git diff --staged --quiet 2>/dev/null; then
        _git_safe_log "Nothing to commit"
        _git_safe_lock_release
        return 0
    fi

    # Commit
    if git commit -m "$msg" --quiet 2>/dev/null; then
        _git_safe_log "Committed: $msg"
    else
        _git_safe_log "WARNING: git commit failed"
        _git_safe_lock_release
        return 1
    fi

    _git_safe_lock_release
}

# ============================================================================
# Safe push — lock + rebase + retry with exponential backoff
# ============================================================================
git_safe_push() {
    _git_safe_disabled && return 0
    local git_dir="${GIT_SAFE_REPO:-.}"
    local retries="${GIT_SAFE_PUSH_RETRIES}"
    local backoff="${GIT_SAFE_PUSH_BACKOFF}"
    local attempt=0

    while [[ $attempt -lt $retries ]]; do
        attempt=$((attempt + 1))

        _git_safe_lock_acquire || {
            _git_safe_log "WARNING: push attempt $attempt without lock"
        }

        cd "$git_dir" || { _git_safe_lock_release; return 1; }

        # Rebase before push to handle remote changes
        if ! git pull --rebase --quiet origin main 2>/dev/null; then
            git rebase --abort 2>/dev/null || true
            _git_safe_lock_release
            if [[ $attempt -lt $retries ]]; then
                _git_safe_log "Push failed (attempt $attempt/$retries), retrying in ${backoff}s..."
                sleep "$backoff"
                backoff=$((backoff * 2))
            fi
            continue
        fi

        if git push origin main --quiet 2>/dev/null; then
            _git_safe_log "Push succeeded (attempt $attempt)"
            _git_safe_lock_release
            return 0
        fi

        _git_safe_lock_release

        if [[ $attempt -lt $retries ]]; then
            _git_safe_log "Push failed (attempt $attempt/$retries), retrying in ${backoff}s..."
            sleep "$backoff"
            backoff=$((backoff * 2))
        fi
    done

    _git_safe_log "WARNING: push failed after $retries attempts — will sync on next repo-sync cycle"
    return 1
}

# ============================================================================
# Safe sync — pull + commit + push in one operation
# ============================================================================
git_safe_sync() {
    _git_safe_disabled && return 0
    local msg="${1:?commit message required}"
    shift
    local files=("$@")

    git_safe_pull || true  # non-fatal
    git_safe_commit "$msg" "${files[@]}" || return 1
    git_safe_push || return 1
}
