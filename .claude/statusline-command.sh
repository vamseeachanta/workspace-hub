#!/usr/bin/env bash
# Status line for workspace-hub — portable across machines
# Shows: model | branch | WRK counts + active | AI usage | cost | context
set -euo pipefail

input=$(cat)

# Extract fields (jq with null-safe defaults)
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
vim_mode=$(echo "$input" | jq -r '.vim.mode // empty')

# Workspace root (handles submodules)
ws_root=$(cd "$cwd" 2>/dev/null && git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo "$cwd")

# Git branch
branch=$(cd "$ws_root" 2>/dev/null && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")

# Git state markers — surface unpushed/uncommitted risk at a glance.
# GIT_OPTIONAL_LOCKS=0 avoids the index-lock contention the ecosystem hits
# in long sessions; -uno skips the untracked-file scan to keep this cheap on
# the ~33K-file workspace-hub checkout.
git_marker=""
if [[ "$branch" != "?" ]]; then
    if [[ -n "$(GIT_OPTIONAL_LOCKS=0 git -C "$ws_root" status --porcelain -uno 2>/dev/null | head -1)" ]]; then
        git_marker="\033[1;31m*\033[0m"   # bold red: dirty (tracked changes/staged)
    fi
    # ahead/behind vs upstream (rev-list is cheap — no working-tree scan)
    # `|| true` guards: under set -euo pipefail a failing substitution
    # (no upstream here; no digits in branch below) silently kills the
    # script -> blank statusline (same class as review-gate SIGPIPE fix).
    lr=$(GIT_OPTIONAL_LOCKS=0 git -C "$ws_root" rev-list --count --left-right '@{u}...HEAD' 2>/dev/null) || true
    if [[ -n "$lr" ]]; then
        behind=${lr%%[[:space:]]*}; ahead=${lr##*[[:space:]]}
        (( ahead  > 0 )) && git_marker="${git_marker}\033[32m↑${ahead}\033[0m"   # green: unpushed
        (( behind > 0 )) && git_marker="${git_marker}\033[31m↓${behind}\033[0m"  # red: behind remote
    fi
fi

# Issue badge — "GitHub issues only" ecosystem: derive the active issue from
# the branch name (e.g. fix/2795-... -> #2795) instead of local WRK counters.
issue_seg=""
issue_num=$(echo "$branch" | grep -oE '[0-9]{3,5}' | head -1) || true
[[ -n "$issue_num" ]] && issue_seg="\033[36m#${issue_num}\033[0m"

# AI usage remaining percentages
# C: uses Claude.ai 7-day subscription quota (from statusline JSON) as primary,
# falls back to agent-quota file. O: and G: from agent-quota files.
quota_primary="$ws_root/config/ai-tools/agent-quota-latest.json"
quota_cache="${HOME}/.cache/agent-quota.json"

extract_pct() {
    local provider="$1" val
    if [[ -f "$quota_primary" ]]; then
        val=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .week_pct // empty' \
            "$quota_primary" 2>/dev/null)
        if [[ -n "$val" && "$val" != "null" ]]; then
            awk -v w="$val" 'BEGIN { printf "%d", 100 - w }'
            return
        fi
    fi
    if [[ -f "$quota_cache" ]]; then
        jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .pct_remaining // empty' \
            "$quota_cache" 2>/dev/null
    fi
}

# Render a "LABEL:NN%" segment colored by remaining headroom so a throttle is
# glance-able for delegation: red <20%, yellow <40%, green otherwise, dim when
# the figure is unknown. Emits literal \033 escapes for the final printf %b.
color_pct() {
    local label="$1" rem="$2" suffix="${3:-}"
    if [[ -z "$rem" || "$rem" == "-" ]]; then
        echo "\033[2m${label}:-%${suffix}\033[0m"   # dim: unknown/unavailable
        return
    fi
    local color='\033[32m'                            # green: ample headroom
    (( rem < 40 )) && color='\033[33m'                # yellow: getting tight
    (( rem < 20 )) && color='\033[31m'                # red: near throttle
    echo "${color}${label}:${rem}%${suffix}\033[0m"
}

# Claude: prefer 7-day subscription remaining from API (most accurate)
week_used=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
c_suffix=""
if [[ -n "$week_used" ]]; then
    c_rem=$(awk -v u="$week_used" 'BEGIN { printf "%d", 100 - u }')
else
    # Fallback to agent-quota file
    c_rem=$(extract_pct "claude")
    # Sonnet sub-bucket: show tighter limit with (S) indicator
    if [[ -f "$quota_primary" && -n "$c_rem" ]]; then
        s_val=$(jq -r '.agents[] | select(.provider == "claude") | .sonnet_pct // empty' \
            "$quota_primary" 2>/dev/null)
        if [[ -n "$s_val" && "$s_val" != "null" ]]; then
            s_remaining=$(awk -v s="$s_val" 'BEGIN { printf "%d", 100 - s }')
            if (( s_remaining < c_rem )); then
                c_rem="$s_remaining"; c_suffix="(S)"
            fi
        fi
    fi
fi

o_pct=$(extract_pct "codex")
g_pct=$(extract_pct "gemini")
ai_usage="$(color_pct C "$c_rem" "$c_suffix")|$(color_pct O "$o_pct")|$(color_pct G "$g_pct")"

# Repo module name (basename of workspace root)
repo_name=$(basename "$ws_root")

# Shorten cwd relative to workspace root
rel_path="${cwd#"$ws_root"}"
[[ -z "$rel_path" ]] && rel_path="/"

# Format cost
cost_fmt=$(printf '$%.2f' "$cost")

# Context color: green <60%, yellow 60-80%, red >80%
ctx_int=${ctx_pct:-0}
if (( ctx_int > 80 )); then
    ctx="\033[31m${ctx_int}%\033[0m"
elif (( ctx_int > 60 )); then
    ctx="\033[33m${ctx_int}%\033[0m"
else
    ctx="\033[32m${ctx_int}%\033[0m"
fi

# Hostname prefix for multi-machine clarity
hostname_s=$(hostname -s 2>/dev/null || cat /etc/hostname 2>/dev/null | tr -d '[:space:]' || echo "?")

# Build output
parts=()
parts+=("\033[1;33m[${hostname_s}]\033[0m")
parts+=("\033[1;35m${model}\033[0m")
parts+=("\033[1;37m${repo_name}\033[0m")
parts+=("\033[33m${branch}\033[0m${git_marker}")
[[ -n "$issue_seg" ]] && parts+=("${issue_seg}")
parts+=("${ai_usage}")
parts+=("${cost_fmt}")
parts+=("ctx:${ctx}")

# Vim mode (if active)
if [[ -n "$vim_mode" ]]; then
    if [[ "$vim_mode" == "INSERT" ]]; then
        parts+=("\033[32mINS\033[0m")
    else
        parts+=("\033[34mNOR\033[0m")
    fi
fi

# Relative path
parts+=("\033[2m${rel_path}\033[0m")

# Join with separator
printf "%b" "${parts[0]}"
for ((i=1; i<${#parts[@]}; i++)); do
    printf " %b" "${parts[i]}"
done
