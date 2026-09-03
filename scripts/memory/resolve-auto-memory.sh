#!/usr/bin/env bash
# ABOUTME: Resolves Claude Code's auto-memory directory for a repo, across workspace moves.
#
# Claude Code stores per-project auto-memory under
#   $HOME/.claude/projects/<absolute-repo-path-with-slashes-as-dashes>/memory
# and the harness pins that slug at SESSION START. When a workspace is moved on
# disk, Claude Code keeps writing to the ORIGINAL slug, so anything that derives
# the slug from the CURRENT path silently stops finding it.
#
# That is exactly what happened when the ecosystem moved from
# /mnt/local-analysis/workspace-hub to /mnt/ace/ws/workspace-hub: the bridge
# derived a slug for the new path, the directory did not exist, and a bare
# `if [[ -f ... ]]` with no else meant the mirror quietly stopped while the
# summary still printed a tick for the stale file left behind.
#
# Two rules follow, and the second matters more than the first:
#   1. try the exact slug, then known aliases, then any project slug ending in
#      the repo's own basename;
#   2. a candidate only counts if it actually holds MEMORY.md, and failing to
#      resolve is a LOUD non-zero exit -- never a silent skip.
#
# Usage:  source resolve-auto-memory.sh
#         dir="$(resolve_claude_memory_dir "$REPO_ROOT" "$HOME")" || handle-failure

# Slugify an absolute path the way Claude Code does.
_auto_memory_slug() { printf '%s' "$1" | tr '/' '-'; }

# Echo the resolved memory directory on stdout; return 1 and explain on stderr.
resolve_claude_memory_dir() {
    local repo_root="$1" home_dir="${2:-$HOME}"
    local projects="${home_dir}/.claude/projects"
    local abs base cand
    abs="$(cd "${repo_root}" 2>/dev/null && pwd)" || abs="${repo_root}"
    base="$(basename "${abs}")"

    # A candidate counts only if it carries the MEMORY.md index. An empty
    # directory left by a stray session is not a memory store, and selecting one
    # would mirror nothing while reporting success.
    _has_memory() { [[ -f "$1/MEMORY.md" ]]; }

    # 1. the exact current path
    cand="${projects}/$(_auto_memory_slug "${abs}")/memory"
    if _has_memory "${cand}"; then printf '%s\n' "${cand}"; return 0; fi

    # 2. known workspace aliases. /mnt/local-analysis is a compatibility symlink
    #    to the /mnt/ace/ws surface, so the two spellings name the same repo.
    local alias_path
    for alias_path in \
        "${abs/\/mnt\/ace\/ws\//\/mnt\/local-analysis\/}" \
        "${abs/\/mnt\/local-analysis\//\/mnt\/ace\/ws\/}"; do
        [[ "${alias_path}" == "${abs}" ]] && continue
        cand="${projects}/$(_auto_memory_slug "${alias_path}")/memory"
        if _has_memory "${cand}"; then printf '%s\n' "${cand}"; return 0; fi
    done

    # 3. any project slug ending in this repo's basename -- catches moves we did
    #    not anticipate. Newest MEMORY.md wins, so a live store beats a fossil.
    local best="" best_mtime=0 mtime
    while IFS= read -r cand; do
        [[ -n "${cand}" ]] || continue
        _has_memory "${cand}" || continue
        mtime="$(stat -c %Y "${cand}/MEMORY.md" 2>/dev/null \
                 || stat -f %m "${cand}/MEMORY.md" 2>/dev/null || echo 0)"
        if [[ "${mtime}" -gt "${best_mtime}" ]]; then best="${cand}"; best_mtime="${mtime}"; fi
    done < <(find "${projects}" -maxdepth 2 -type d -name memory 2>/dev/null \
             | grep -- "-${base}/memory$" || true)
    if [[ -n "${best}" ]]; then printf '%s\n' "${best}"; return 0; fi

    echo "[resolve-auto-memory] FATAL: no Claude auto-memory directory found for ${abs}" >&2
    echo "[resolve-auto-memory]   looked under ${projects} for the exact slug, known" >&2
    echo "[resolve-auto-memory]   workspace aliases, and any slug ending in '-${base}'." >&2
    echo "[resolve-auto-memory]   Refusing to report success for a mirror that would copy nothing." >&2
    return 1
}
