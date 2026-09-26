#!/usr/bin/env bash
# private_path_guard.sh — is a directory outside the public repository? (C19b)
#
# Source this file, then:
#
#     private_path_outside_repo DIR REPO
#
# Returns 0 only when DIR is an absolute, existing directory with no '..'
# component that lies outside REPO. Containment is checked on the logical
# (pwd -L) AND the physical (pwd -P) form of DIR, each against both forms of
# REPO, case-insensitively on Windows shells (MINGW/MSYS/Cygwin). Any path
# component of DIR that is a symlink or junction under REPO is refused.
# Checking only the physical path would let a link under the repository that
# points outside pass. Prints nothing; the caller names the key, never a path.
# Mirrors check_private_dir() in scripts/lib/private_overlay.py.

_ppg_fold() {
    case "$(uname -s 2>/dev/null)" in
        MINGW*|MSYS*|CYGWIN*) printf '%s' "$1" | tr '[:upper:]' '[:lower:]' ;;
        *) printf '%s' "$1" ;;
    esac
}

# _ppg_within PATH ROOT -> 0 when PATH is ROOT or below it (component-wise).
_ppg_within() {
    local p r
    p="$(_ppg_fold "${1%/}")"
    r="$(_ppg_fold "${2%/}")"
    [ -n "$r" ] || return 1
    [ "$p" = "$r" ] && return 0
    case "$p/" in
        "$r"/*) return 0 ;;
    esac
    return 1
}

private_path_outside_repo() {
    local dir="$1" repo="$2" dir_l dir_p repo_l repo_p prefix part rest
    case "$dir" in
        /*|[A-Za-z]:/*|[A-Za-z]:\\*) ;;
        *) return 1 ;;
    esac
    case "/${dir//\\//}/" in
        */../*) return 1 ;;
    esac
    dir_l="$(cd "$dir" 2>/dev/null && pwd -L)" || return 1
    dir_p="$(cd "$dir" 2>/dev/null && pwd -P)" || return 1
    repo_l="$(cd "$repo" 2>/dev/null && pwd -L)" || return 1
    repo_p="$(cd "$repo" 2>/dev/null && pwd -P)" || return 1
    local a b
    for a in "$dir_l" "$dir_p"; do
        for b in "$repo_l" "$repo_p"; do
            _ppg_within "$a" "$b" && return 1
        done
    done
    # A component that is a link under the repository (its own location or
    # where it points) is refused even when the whole path resolves outside.
    prefix=""
    rest="${dir_l#/}"
    while [ -n "$rest" ]; do
        part="${rest%%/*}"
        if [ "$part" = "$rest" ]; then rest=""; else rest="${rest#*/}"; fi
        prefix="$prefix/$part"
        if [ -L "$prefix" ]; then
            local target_p
            target_p="$(cd "$prefix" 2>/dev/null && pwd -P)" || return 1
            for b in "$repo_l" "$repo_p"; do
                _ppg_within "$prefix" "$b" && return 1
                _ppg_within "$target_p" "$b" && return 1
            done
        fi
    done
    return 0
}
