#!/usr/bin/env bash
# Status line for workspace-hub — portable across machines
# Shows: model | branch | WRK counts | cost | context usage
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

# Work queue counts (fast find, no recursion)
wq="$ws_root/.claude/work-queue"
if [[ -d "$wq/pending" ]]; then
    p=$(find "$wq/pending" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
    w=$(find "$wq/working" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
    b=$(find "$wq/blocked" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | wc -l | tr -d ' ')
else
    p=0; w=0; b=0
fi

# AI usage remaining percentages
# Primary: agent-quota-latest.json (OAuth API, week_pct = % used → invert to remaining)
# Fallback: ~/.cache/agent-quota.json (computed from stats-cache, may be stale)
quota_primary="$ws_root/config/ai-tools/agent-quota-latest.json"
quota_cache="${HOME}/.cache/agent-quota.json"
ai_usage="C:-|O:-|G:-"

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

c_pct=$(extract_pct "claude")
o_pct=$(extract_pct "codex")
g_pct=$(extract_pct "gemini")
ai_usage="C:${c_pct:--}%|O:${o_pct:--}%|G:${g_pct:--}%"

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

# Build output
parts=()
parts+=("\033[1;35m${model}\033[0m")
parts+=("\033[1;37m${repo_name}\033[0m")
parts+=("\033[33m${branch}\033[0m")
parts+=("\033[36mWRK:${p}p/${w}w/${b}b\033[0m")
parts+=("\033[35m${ai_usage}\033[0m")
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
