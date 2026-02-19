#!/usr/bin/env bash
# propagate-ecosystem.sh — Unified hook + skill propagation for all submodules
# Replaces propagate-hooks.sh. Cross-platform: Windows (MINGW64), Linux, macOS.
# Usage: bash scripts/propagate-ecosystem.sh [--hooks-only|--skills-only] [--dry-run] [--verbose]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$SCRIPT_DIR/.." && pwd)"

HOOK_MARKER="post-task-review.sh"
SHARED_SKILL_DIRS=("guidelines" "meta" "workflows")
SKIP_DIRS=("session-logs" "_runtime" "_internal" "_core")
EXCLUDE_DIRS=(".claude" "scripts" "specs" "docs" "node_modules" ".git"
              "_archive" "_temp" "config" "coordination" "data" "docker"
              "examples" "logs" "modules" "monitoring-dashboard" "reports"
              "skills" "src" "templates" "tests" "flow-nexus" "ruv-swarm" "claude-flow")
LINK_MARKER=".link-marker"

OPT_HOOKS=true; OPT_SKILLS=true; OPT_DRY_RUN=false; OPT_VERBOSE=false
HOOKS_ADDED=0; HOOKS_SKIPPED=0; HOOKS_FAILED=0
SKILLS_LINKED=0; SKILLS_SKIPPED_MODIFIED=0; SKILLS_ALREADY_LINKED=0; SKILLS_CREATED=0

# Colors (disabled in pipes)
if [[ -t 1 ]]; then
    C_GREEN='\033[0;32m'; C_YELLOW='\033[0;33m'; C_RED='\033[0;31m'
    C_CYAN='\033[0;36m'; C_DIM='\033[0;90m'; C_BOLD='\033[1m'; C_RESET='\033[0m'
else
    C_GREEN=''; C_YELLOW=''; C_RED=''; C_CYAN=''; C_DIM=''; C_BOLD=''; C_RESET=''
fi

log_ok()      { printf "  ${C_GREEN}OK${C_RESET}   %s\n" "$*"; }
log_add()     { printf "  ${C_CYAN}ADD${C_RESET}  %s\n" "$*"; }
log_link()    { printf "  ${C_CYAN}LINK${C_RESET} %s\n" "$*"; }
log_skip()    { printf "  ${C_DIM}SKIP${C_RESET} %s\n" "$*"; }
log_fail()    { printf "  ${C_RED}FAIL${C_RESET} %s\n" "$*"; }
log_verbose() { [[ "$OPT_VERBOSE" == "true" ]] && printf "  ${C_DIM}     %s${C_RESET}\n" "$*" || true; }

# --- detect_platform: returns "windows" or "unix" ---
detect_platform() {
    case "${OSTYPE:-}" in msys*|mingw*|cygwin*) echo "windows"; return;; esac
    case "$(uname -s 2>/dev/null)" in MINGW*|MSYS*|CYGWIN*) echo "windows"; return;; esac
    echo "unix"
}
PLATFORM="$(detect_platform)"

# --- to_win_path: convert /d/foo to D:\foo for cmd.exe ---
to_win_path() {
    local p; p="$(echo "$1" | sed 's|/|\\|g')"
    [[ "$p" =~ ^\\([a-zA-Z])\\ ]] && p="${BASH_REMATCH[1]^^}:${p:2}"
    echo "$p"
}

# --- create_directory_link(target, link_name) ---
create_directory_link() {
    local target="$1" link_name="$2"
    [[ "$OPT_DRY_RUN" == "true" ]] && { log_verbose "DRY-RUN: would link $link_name -> $target"; return 0; }

    if [[ "$PLATFORM" == "windows" ]]; then
        local wt; wt="$(to_win_path "$target")"
        local wl; wl="$(to_win_path "$link_name")"
        cmd //c "mklink /J $wl $wt" > /dev/null 2>&1 || return $?
        # Write marker as sibling file (not inside junction, which resolves to target)
        echo "ecosystem-link" > "$(dirname "$link_name")/.$(basename "$link_name")-link-marker" 2>/dev/null || true
    else
        local link_parent; link_parent="$(dirname "$link_name")"
        local rel; rel="$(uv run --no-project --quiet python -c "import os.path; print(os.path.relpath('$target','$link_parent'))" 2>/dev/null \
                       || perl -e "use File::Spec; print File::Spec->abs2rel('$target','$link_parent')" 2>/dev/null \
                       || echo "$target")"
        ln -s "$rel" "$link_name"
    fi
}

# --- is_link(path): symlink (unix) or junction (windows) ---
is_link() {
    local path="$1"
    if [[ "$PLATFORM" == "windows" ]]; then
        # Check sibling marker file
        local marker="$(dirname "$path")/.$(basename "$path")-link-marker"
        [[ -d "$path" && -f "$marker" ]] && return 0
        # Fallback: check via fsutil reparse point
        if [[ -d "$path" ]]; then
            fsutil reparsepoint query "$(to_win_path "$path")" > /dev/null 2>&1 && return 0
        fi
        return 1
    else
        [[ -L "$path" ]]
    fi
}

# --- directory_matches_template(sub_dir, tmpl_dir) ---
# Returns 0 if template files all exist in sub_dir with same content (superset ok).
# Ignores YAML frontmatter differences (internal copies have metadata headers).
# Uses python for reliable cross-platform frontmatter stripping.
directory_matches_template() {
    local sub_dir="$1" tmpl_dir="$2"
    [[ ! -d "$sub_dir" || ! -d "$tmpl_dir" ]] && return 1

    local py_cmd="uv run --no-project --quiet python"
    if ! command -v uv &>/dev/null; then
        # Fallback: simple diff (may false-negative on frontmatter differences)
        local issues; issues="$(diff -rq "$tmpl_dir" "$sub_dir" 2>/dev/null | grep -v "^Only in ${sub_dir}" || true)"
        [[ -z "$issues" ]]
        return $?
    fi

    $py_cmd - "$tmpl_dir" "$sub_dir" <<'PYEOF'
import sys, os, glob

def strip_fm(text):
    lines = text.split('\n')
    if lines and lines[0].strip() == '---':
        for i, l in enumerate(lines[1:], 1):
            if l.strip() == '---':
                return '\n'.join(lines[i+1:]).strip()
    return text.strip()

tmpl, sub = sys.argv[1], sys.argv[2]
for md in glob.glob(os.path.join(tmpl, '**', '*.md'), recursive=True):
    rel = os.path.relpath(md, tmpl)
    sub_f = os.path.join(sub, rel)
    if not os.path.isfile(sub_f):
        sys.exit(1)
    a = strip_fm(open(md, encoding='utf-8', errors='replace').read())
    b = strip_fm(open(sub_f, encoding='utf-8', errors='replace').read())
    if a != b:
        sys.exit(1)
sys.exit(0)
PYEOF
}

# --- discover_submodules: list dirs with .claude/skills/ ---
discover_submodules() {
    for repo_dir in "$WS_HUB"/*/; do
        [[ ! -d "$repo_dir" ]] && continue
        local dir_name; dir_name="$(basename "$repo_dir")"
        local excluded=false
        for ex in "${EXCLUDE_DIRS[@]}"; do [[ "$dir_name" == "$ex" ]] && excluded=true && break; done
        [[ "$excluded" == "true" ]] && continue
        [[ -d "$repo_dir/.claude/skills" ]] && echo "$repo_dir"
    done
}

# --- propagate_hooks(repo_dir) ---
propagate_hooks() {
    local repo_dir="$1" repo_name; repo_name="$(basename "$repo_dir")"
    local settings="$repo_dir/.claude/settings.json"

    if [[ ! -f "$settings" ]]; then
        log_skip "$repo_name — no .claude/settings.json"; HOOKS_SKIPPED=$((HOOKS_SKIPPED+1)); return; fi
    if grep -q "$HOOK_MARKER" "$settings" 2>/dev/null; then
        log_ok "$repo_name — already has post-task-review hook"; HOOKS_SKIPPED=$((HOOKS_SKIPPED+1)); return; fi
    if [[ "$OPT_DRY_RUN" == "true" ]]; then
        log_add "$repo_name — would add Stop hook (dry-run)"; HOOKS_ADDED=$((HOOKS_ADDED+1)); return; fi
    if ! command -v jq &>/dev/null; then
        log_fail "$repo_name — jq not available"; HOOKS_FAILED=$((HOOKS_FAILED+1)); return; fi

    local tmp_f; tmp_f="$(mktemp)"
    local jq_op="=" jq_rc=0
    grep -q '"Stop"' "$settings" 2>/dev/null && jq_op="+="
    jq "
        .hooks.Stop ${jq_op} [{
            \"hooks\": [{
                \"type\": \"command\",
                \"statusMessage\": \"Post-task learning check\",
                \"command\": \"bash -c 'SCRIPT=\\\"\${WORKSPACE_HUB:-\$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/.claude/hooks/post-task-review.sh\\\"; [ -f \\\"\$SCRIPT\\\" ] && bash \\\"\$SCRIPT\\\" 2>/dev/null || true'\"
            }]
        }]
    " "$settings" > "$tmp_f" 2>/dev/null || jq_rc=$?

    if [[ $jq_rc -eq 0 && -s "$tmp_f" ]]; then
        mv "$tmp_f" "$settings"
        log_add "$repo_name — ${jq_op/+=/appended to existing }${jq_op/=/created }Stop hooks section"
        HOOKS_ADDED=$((HOOKS_ADDED+1))
    else
        rm -f "$tmp_f"
        log_fail "$repo_name — jq failed, manual edit needed"; HOOKS_FAILED=$((HOOKS_FAILED+1))
    fi
}

# --- update_gitignore(repo_dir) ---
update_gitignore() {
    local repo_dir="$1" gitignore="$repo_dir/.claude/skills/.gitignore"
    local header="# Shared skills (linked from workspace-hub)"
    local dirs_to_add=()
    for dir in "${SHARED_SKILL_DIRS[@]}"; do
        [[ -f "$gitignore" ]] && grep -qx "${dir}/" "$gitignore" 2>/dev/null && continue
        dirs_to_add+=("$dir")
    done
    [[ ${#dirs_to_add[@]} -eq 0 ]] && return 0
    [[ "$OPT_DRY_RUN" == "true" ]] && { log_verbose "DRY-RUN: would update $gitignore"; return 0; }

    mkdir -p "$(dirname "$gitignore")"
    if [[ ! -f "$gitignore" ]] || ! grep -qF "$header" "$gitignore" 2>/dev/null; then
        [[ -f "$gitignore" && -s "$gitignore" ]] && printf '\n' >> "$gitignore"
        printf '%s\n' "$header" >> "$gitignore"
    fi
    for dir in "${dirs_to_add[@]}"; do printf '%s/\n' "$dir" >> "$gitignore"; done
}

# --- untrack_shared_dirs(repo_dir) ---
untrack_shared_dirs() {
    local repo_dir="$1"
    [[ "$OPT_DRY_RUN" == "true" ]] && return 0
    for dir in "${SHARED_SKILL_DIRS[@]}"; do
        local tracked
        tracked="$(git -C "$repo_dir" ls-files ".claude/skills/${dir}" 2>/dev/null || true)"
        if [[ -n "$tracked" ]]; then
            git -C "$repo_dir" rm -r --cached ".claude/skills/${dir}" > /dev/null 2>&1 || true
            log_verbose "Untracked .claude/skills/${dir} from git index"
        fi
    done
}

# --- propagate_skills(repo_dir) ---
propagate_skills() {
    local repo_dir="$1" repo_name; repo_name="$(basename "$repo_dir")"
    local skills_dir="$repo_dir/.claude/skills"
    local internal_dir="$WS_HUB/.claude/skills/_internal"
    [[ ! -d "$skills_dir" ]] && { log_skip "$repo_name — no .claude/skills/"; return; }

    for shared_dir in "${SHARED_SKILL_DIRS[@]}"; do
        local target="$internal_dir/$shared_dir" link_path="$skills_dir/$shared_dir"
        [[ ! -d "$target" ]] && { log_verbose "Template $shared_dir not in _internal/"; continue; }

        # Already linked — idempotent
        if is_link "$link_path"; then
            log_ok "$repo_name/$shared_dir (link exists)"; SKILLS_ALREADY_LINKED=$((SKILLS_ALREADY_LINKED+1)); continue; fi

        # Real directory exists
        if [[ -d "$link_path" ]]; then
            if directory_matches_template "$link_path" "$target"; then
                local backup="${link_path}.bak-$(date +%Y%m%d)"
                if [[ "$OPT_DRY_RUN" == "true" ]]; then
                    log_link "$repo_name/$shared_dir -> _internal/$shared_dir (would backup existing)"
                    SKILLS_LINKED=$((SKILLS_LINKED+1)); continue; fi
                [[ -d "$backup" ]] && rm -rf "$backup"
                mv "$link_path" "$backup"; log_verbose "Backed up to $backup"
                if create_directory_link "$target" "$link_path"; then
                    log_link "$repo_name/$shared_dir -> _internal/$shared_dir (backed up existing)"
                    SKILLS_LINKED=$((SKILLS_LINKED+1))
                else
                    mv "$backup" "$link_path"
                    log_fail "$repo_name/$shared_dir — link failed, restored backup"
                fi
            else
                log_skip "$repo_name/$shared_dir (local modifications detected)"
                SKILLS_SKIPPED_MODIFIED=$((SKILLS_SKIPPED_MODIFIED+1))
            fi
            continue
        fi

        # Nothing exists — create fresh
        if [[ "$OPT_DRY_RUN" == "true" ]]; then
            log_link "$repo_name/$shared_dir -> _internal/$shared_dir (new)"
            SKILLS_CREATED=$((SKILLS_CREATED+1)); continue; fi
        mkdir -p "$(dirname "$link_path")"
        if create_directory_link "$target" "$link_path"; then
            log_link "$repo_name/$shared_dir -> _internal/$shared_dir (new)"
            SKILLS_CREATED=$((SKILLS_CREATED+1))
        else log_fail "$repo_name/$shared_dir — link creation failed"; fi
    done
    update_gitignore "$repo_dir"
    untrack_shared_dirs "$repo_dir"
}

# --- parse_arguments ---
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --hooks-only)  OPT_HOOKS=true;  OPT_SKILLS=false;;
            --skills-only) OPT_HOOKS=false; OPT_SKILLS=true;;
            --dry-run)     OPT_DRY_RUN=true;;
            --verbose)     OPT_VERBOSE=true;;
            --help|-h)     usage; exit 0;;
            *) echo "Unknown option: $1" >&2; usage; exit 1;;
        esac; shift
    done
}

usage() {
    cat <<'EOF'
Usage: bash scripts/propagate-ecosystem.sh [OPTIONS]

Propagate hooks and shared skills to all workspace-hub submodules.

Options:
  --hooks-only    Only propagate hooks (skip skill linking)
  --skills-only   Only propagate skill links (skip hooks)
  --dry-run       Preview changes without modifying anything
  --verbose       Show detailed output
  --help, -h      Show this help message
EOF
}

preflight_checks() {
    if [[ ! -d "$WS_HUB/.claude" ]]; then
        echo "ERROR: workspace-hub root not found at $WS_HUB" >&2; exit 1; fi
    [[ "$OPT_HOOKS" == "true" ]] && ! command -v jq &>/dev/null && \
        echo "WARNING: jq not found — hook propagation will skip repos needing edits" >&2
    if [[ "$OPT_SKILLS" == "true" && ! -d "$WS_HUB/.claude/skills/_internal" ]]; then
        echo "ERROR: _internal/ not found at $WS_HUB/.claude/skills/_internal/" >&2
        [[ "$OPT_HOOKS" == "false" ]] && exit 1
        OPT_SKILLS=false; echo "WARNING: Disabling skill propagation" >&2
    fi
}

# --- main ---
main() {
    parse_arguments "$@"
    preflight_checks

    local submodules=()
    while IFS= read -r line; do submodules+=("$line"); done < <(discover_submodules)
    local count=${#submodules[@]}
    [[ $count -eq 0 ]] && { echo "No submodules with .claude/skills/ found."; exit 0; }

    printf "${C_BOLD}Propagating ecosystem to %d submodules...${C_RESET}\n" "$count"
    [[ "$PLATFORM" == "windows" ]] \
        && printf "Platform: ${C_CYAN}windows${C_RESET} (using directory junctions)\n" \
        || printf "Platform: ${C_CYAN}unix${C_RESET} (using symlinks)\n"
    [[ "$OPT_DRY_RUN" == "true" ]] && printf "${C_YELLOW}DRY-RUN MODE — no changes will be made${C_RESET}\n"
    echo ""

    if [[ "$OPT_HOOKS" == "true" ]]; then
        printf "${C_BOLD}HOOKS:${C_RESET}\n"
        for r in "${submodules[@]}"; do propagate_hooks "$r"; done
        echo ""
    fi
    if [[ "$OPT_SKILLS" == "true" ]]; then
        printf "${C_BOLD}SKILLS:${C_RESET}\n"
        for r in "${submodules[@]}"; do propagate_skills "$r"; done
        echo ""
    fi

    if [[ "$OPT_SKILLS" == "true" ]]; then
        printf "${C_BOLD}PROVIDER ADAPTERS:${C_RESET}\n"
        for provider in codex gemini; do
            for repo_dir in "${submodules[@]}"; do
                local repo_name; repo_name="$(basename "$repo_dir")"
                local adapter_dir="$repo_dir/.$provider"
                local link="$adapter_dir/skills"
                local target="../../.claude/skills"
                if [[ "$OPT_DRY_RUN" == "true" ]]; then
                    [[ -L "$link" ]] \
                        && log_ok "$repo_name/.$provider/skills (exists)" \
                        || log_add "$repo_name/.$provider/skills -> $target (would create)"
                    continue
                fi
                mkdir -p "$adapter_dir"
                if [[ ! -L "$link" ]]; then
                    ln -sf "$target" "$link"
                    log_link "$repo_name/.$provider/skills -> $target"
                else
                    log_ok "$repo_name/.$provider/skills (exists)"
                fi
            done
        done
        echo ""
    fi

    printf "${C_BOLD}Summary:${C_RESET}\n"
    if [[ "$OPT_HOOKS" == "true" ]]; then
        printf "  Hooks:  %d added, %d skipped" "$HOOKS_ADDED" "$HOOKS_SKIPPED"
        [[ $HOOKS_FAILED -gt 0 ]] && printf ", ${C_RED}%d failed${C_RESET}" "$HOOKS_FAILED"
        echo ""
    fi
    if [[ "$OPT_SKILLS" == "true" ]]; then
        printf "  Skills: %d linked, %d skipped (modified), %d already linked\n" \
            "$((SKILLS_LINKED+SKILLS_CREATED))" "$SKILLS_SKIPPED_MODIFIED" "$SKILLS_ALREADY_LINKED"
    fi
    [[ "$OPT_DRY_RUN" == "true" ]] && printf "  ${C_YELLOW}(dry-run — no changes were made)${C_RESET}\n"
}

main "$@"
exit 0
