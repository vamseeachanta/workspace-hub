#!/usr/bin/env bash
# ABOUTME: Resolves Claude Code's auto-memory directory for a repo, across workspace moves.
#
# Claude Code stores per-project auto-memory under
#   $HOME/.claude/projects/<absolute-repo-path-with-slashes-as-dashes>/memory
# and the harness pins that slug at SESSION START. When a workspace is moved on
# disk, Claude Code keeps writing to the ORIGINAL slug, so anything deriving the
# slug from the CURRENT path silently stops finding it.
#
# That is what happened when the ecosystem moved from /mnt/local-analysis to
# /mnt/ace/ws: the bridge derived a slug for the new path, the directory did not
# exist, and a bare `if [[ -f ... ]]` with no else meant the mirror quietly
# stopped while the summary still printed a tick for the stale file left behind.
#
# Design rules, in order of importance:
#   1. failing to resolve is a LOUD non-zero exit that emits no path -- never a
#      silent skip, and never a guess;
#   2. AMBIGUITY IS FATAL. Slugification maps '/' and '-' to the same character,
#      so '/tmp/x/my-workspace-hub' and '/mnt/ace/ws/workspace-hub' both end in
#      '-workspace-hub' and cannot be told apart by shape. Rather than pick by
#      mtime -- which an editor, backup or unrelated session can flip -- the
#      search refuses to choose between multiple candidates and prints them.
#   3. a candidate counts only if it holds MEMORY.md; an empty directory is not
#      a memory store, and selecting one would mirror nothing while reporting
#      success.
#
# Usage:  source resolve-auto-memory.sh
#         dir="$(resolve_claude_memory_dir "$REPO_ROOT" "$HOME")" || handle-failure

# Slugify an absolute path the way Claude Code does.
_auto_memory_slug() { printf '%s' "$1" | tr '/' '-'; }

# A candidate directory is only a memory store if it carries the index.
# Namespaced and top-level: defining it inside the resolver would leak a
# generic name into any shell that sources this file.
_auto_memory_has_index() { [[ -f "$1/MEMORY.md" ]]; }

# Rewrite only a LEADING workspace prefix. Substring replacement would rewrite a
# path that merely contains the prefix further along, or one that repeats it.
_auto_memory_alias() {
    local path="$1" from="$2" to="$3"
    [[ "${path}" == "${from}"/* ]] || return 1
    printf '%s' "${to}/${path#"${from}"/}"
}

# Echo the resolved memory directory on stdout; return 1 and explain on stderr.
resolve_claude_memory_dir() {
    local repo_root="$1" home_dir="${2:-$HOME}"
    local projects="${home_dir}/.claude/projects"
    local abs base cand
    abs="$(cd "${repo_root}" 2>/dev/null && pwd -P)" || abs="${repo_root%/}"
    base="$(basename "${abs}")"

    # 1. the exact current path
    cand="${projects}/$(_auto_memory_slug "${abs}")/memory"
    if _auto_memory_has_index "${cand}"; then printf '%s\n' "${cand}"; return 0; fi

    # 2. known workspace aliases, anchored to the leading prefix.
    #    /mnt/local-analysis is a compatibility symlink to the /mnt/ace/ws
    #    surface, so the two spellings name the same repo.
    local alias_path
    while read -r from to; do
        [[ -n "${from}" ]] || continue
        alias_path="$(_auto_memory_alias "${abs}" "${from}" "${to}")" || continue
        cand="${projects}/$(_auto_memory_slug "${alias_path}")/memory"
        if _auto_memory_has_index "${cand}"; then printf '%s\n' "${cand}"; return 0; fi
    done <<'ALIASES'
/mnt/ace/ws /mnt/local-analysis
/mnt/local-analysis /mnt/ace/ws
ALIASES

    # 3. last resort: any project slug ending in this repo's basename. Because a
    #    slug cannot be unambiguously reversed, MORE THAN ONE MATCH IS FATAL --
    #    picking by mtime here would let '/tmp/x/my-workspace-hub' shadow
    #    '/mnt/ace/ws/workspace-hub'. A single match is reported on stderr so a
    #    wrong guess is visible rather than silent.
    local -a found=()
    while IFS= read -r cand; do
        [[ -n "${cand}" ]] || continue
        _auto_memory_has_index "${cand}" && found+=("${cand}")
    done < <(find "${projects}" -maxdepth 2 -type d -name memory 2>/dev/null \
             | grep -- "-$(_auto_memory_slug "${base}")/memory$" || true)

    if [[ "${#found[@]}" -eq 1 ]]; then
        echo "[resolve-auto-memory] NOTE: no exact or alias slug matched; falling back to" >&2
        echo "[resolve-auto-memory]   ${found[0]}" >&2
        echo "[resolve-auto-memory]   (sole slug ending in '-${base}'). Verify this is the right repo." >&2
        printf '%s\n' "${found[0]}"
        return 0
    fi
    if [[ "${#found[@]}" -gt 1 ]]; then
        echo "[resolve-auto-memory] FATAL: ${#found[@]} candidate memory stores end in '-${base}':" >&2
        printf '[resolve-auto-memory]   %s\n' "${found[@]}" >&2
        echo "[resolve-auto-memory]   Slugs are not reversible, so choosing between these would be a" >&2
        echo "[resolve-auto-memory]   guess. Add an explicit alias to this script instead." >&2
        return 1
    fi

    echo "[resolve-auto-memory] FATAL: no Claude auto-memory directory found for ${abs}" >&2
    echo "[resolve-auto-memory]   looked under ${projects} for the exact slug, known" >&2
    echo "[resolve-auto-memory]   workspace aliases, and any slug ending in '-${base}'." >&2
    echo "[resolve-auto-memory]   Refusing to report success for a mirror that would copy nothing." >&2
    return 1
}
