#!/usr/bin/env bash
# Status line for workspace-hub — portable across machines
# Shows: model | branch | WRK counts + active | AI usage | cost | context
set -euo pipefail

input=$(cat)

# Optional segment mode (#2893): emit only a sub-part of the statusline so a
# wrapper can compose this with another statusline (e.g. the vendored GSD one,
# which has no quota/reset display). Recognized:
#   --usage-tail  -> AI-usage segment (C:|O:|G:|H=O with reset/burst data) + cost + ctx
# Any other/empty value renders the full statusline unchanged.
SEGMENT="${1:-}"

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
if [[ "$SEGMENT" != "--usage-tail" && "$branch" != "?" ]]; then
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
# falls back to local/cache data. O: and G: from quota/usage helpers; H aliases O.
# Env overrides keep the script testable with fixture quota files (#2992);
# they fall back to the real locations in normal use.
quota_primary="${STATUSLINE_QUOTA_PRIMARY:-$ws_root/config/ai-tools/agent-quota-latest.json}"
quota_cache="${STATUSLINE_QUOTA_CACHE:-${HOME}/.cache/agent-quota.json}"
claude_stats_cache="${STATUSLINE_CLAUDE_STATS_CACHE:-${HOME}/.claude/stats-cache.json}"
claude_creds="${STATUSLINE_CLAUDE_CREDS:-${HOME}/.claude/.credentials.json}"

# Parse an ISO-8601 timestamp to epoch seconds; emits nothing on failure.
iso_epoch() {
    python3 - "$1" 2>/dev/null <<'PY'
import datetime
import sys

raw = sys.argv[1].strip()
if raw.endswith("Z"):
    raw = raw[:-1] + "+00:00"
try:
    dt = datetime.datetime.fromisoformat(raw)
except ValueError:
    if len(raw) > 5 and raw[-5] in "+-" and raw[-3] != ":":
        raw = f"{raw[:-2]}:{raw[-2:]}"
        dt = datetime.datetime.fromisoformat(raw)
    else:
        raise
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=datetime.timezone.utc)
print(int(dt.timestamp()))
PY
}

# Quota-file freshness (#3034): the repo-tracked primary can be a days-old
# git-propagated snapshot of another machine's refresh (observed 2026-06-10:
# primary said codex 79% remaining while live was 29%). Each file's embedded
# `timestamp` (written by query-quota.sh) is age-gated; values sourced from a
# stale or undatable file render a `?` marker so the number is never silently
# trusted. Threshold env is bounds-validated to (0, 168] hours so a local
# override cannot silently disable the warning; anything else falls back to 6.
quota_max_age_h=$(awk -v t="${STATUSLINE_QUOTA_MAX_AGE_HOURS:-6}" \
    'BEGIN { if (t+0 != t || t+0 <= 0 || t+0 > 168) t = 6; printf "%s", t }')

quota_file_state() {   # <file> -> fresh | stale | missing
    local file="$1" ts epoch
    [[ -f "$file" ]] || { echo missing; return; }
    ts=$(jq -r '.timestamp // empty' "$file" 2>/dev/null)
    [[ -n "$ts" ]] || { echo stale; return; }       # undatable = stale
    epoch=$(iso_epoch "$ts") || epoch=""
    [[ -n "$epoch" ]] || { echo stale; return; }
    awk -v e="$epoch" -v n="$(date +%s)" -v m="$quota_max_age_h" \
        'BEGIN { print ((n - e) / 3600 <= m) ? "fresh" : "stale" }'
}

primary_state=$(quota_file_state "$quota_primary")
cache_state=$(quota_file_state "$quota_cache")

is_estimate_source() {
    case "${1:-}" in
        estimated|*-estimate|stats-cache.json-estimate|statusline-stats-cache-estimate)
            return 0 ;;
    esac
    return 1
}

entry_source() {  # <provider> <file>
    jq -r --arg p "$1" \
        '.agents[]? | select(.provider == $p) | .source // empty' "$2" 2>/dev/null
}

file_state_for_source() {  # <file> <source>
    local file="$1" source="$2" state
    [[ "$file" == "$quota_primary" ]] && state="$primary_state" || state="$cache_state"
    if is_estimate_source "$source"; then
        echo estimate
    else
        echo "$state"
    fi
}

remaining_from_used() {  # <used-pct>
    awk -v u="$1" 'BEGIN {
        if (u+0 != u) exit 1
        r = 100 - u
        if (r < 0) r = 0
        if (r > 100) r = 100
        printf "%d", r
    }' 2>/dev/null || true
}

select_quota_value() {  # <primary-val> <primary-state> <cache-val> <cache-state>
    local p_val="$1" p_state="$2" c_val="$3" c_state="$4"
    # Freshness remains the top-level ordering, but within a freshness tier a
    # non-estimate source wins. Shared quota collectors should not persist
    # estimates; if they ever do, the visible "?" marker is still mandatory.
    if [[ -n "$p_val" && "$primary_state" == fresh && "$p_state" != estimate ]]; then
        echo "$p_val $p_state"
    elif [[ -n "$c_val" && "$cache_state" == fresh && "$c_state" != estimate ]]; then
        echo "$c_val $c_state"
    elif [[ -n "$p_val" && "$primary_state" == fresh ]]; then
        echo "$p_val $p_state"
    elif [[ -n "$c_val" && "$cache_state" == fresh ]]; then
        echo "$c_val $c_state"
    elif [[ -n "$p_val" && "$p_state" != estimate ]]; then
        echo "$p_val $p_state"
    elif [[ -n "$c_val" && "$c_state" != estimate ]]; then
        echo "$c_val $c_state"
    elif [[ -n "$p_val" ]]; then
        echo "$p_val $p_state"
    elif [[ -n "$c_val" ]]; then
        echo "$c_val $c_state"
    else
        echo "- none"
    fi
}

# Emit "<pct> <fresh|stale>" (or "- none" when unknown) for a provider,
# choosing the freshest file that has a value: fresh primary > fresh cache >
# stale primary > stale cache. Preserves the historical field-per-file
# convention (primary: week_pct, cache: pct_remaining).
extract_pct() {
    local provider="$1" p_val="" c_val="" p_src="" c_src="" p_out_state="" c_out_state="" v
    if [[ -f "$quota_primary" ]]; then
        v=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .week_pct // empty' \
            "$quota_primary" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && p_val=$(remaining_from_used "$v")
        p_src=$(entry_source "$provider" "$quota_primary")
        p_out_state=$(file_state_for_source "$quota_primary" "$p_src")
    fi
    if [[ -f "$quota_cache" ]]; then
        v=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .pct_remaining // empty' \
            "$quota_cache" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && c_val="$v"
        c_src=$(entry_source "$provider" "$quota_cache")
        c_out_state=$(file_state_for_source "$quota_cache" "$c_src")
    fi
    select_quota_value "$p_val" "$p_out_state" "$c_val" "$c_out_state"
}

codex_five_hour_remaining() {
    # `five_hour_pct` is used-polarity from scripts/ai/assessment/query-codex-usage.sh:
    # live app-server `.primary.usedPercent` and session `.payload.rate_limits.primary.used_percent`.
    # The statusline displays remaining-polarity, so it renders 100 - five_hour_pct.
    local p_val="" c_val="" p_src="" c_src="" p_out_state="" c_out_state="" v
    if [[ -f "$quota_primary" ]]; then
        v=$(jq -r '.agents[] | select(.provider == "codex") | .five_hour_pct // empty' \
            "$quota_primary" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && p_val=$(remaining_from_used "$v")
        p_src=$(entry_source codex "$quota_primary")
        p_out_state=$(file_state_for_source "$quota_primary" "$p_src")
    fi
    if [[ -f "$quota_cache" ]]; then
        v=$(jq -r '.agents[] | select(.provider == "codex") | .five_hour_pct // empty' \
            "$quota_cache" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && c_val=$(remaining_from_used "$v")
        c_src=$(entry_source codex "$quota_cache")
        c_out_state=$(file_state_for_source "$quota_cache" "$c_src")
    fi
    select_quota_value "$p_val" "$p_out_state" "$c_val" "$c_out_state"
}

jq_supports_iso_dates() {
    jq -n '"2000-01-01T00:00:00Z" | fromdateiso8601' >/dev/null 2>&1
}

positive_ratio() {
    awk -v r="${CLAUDE_MESSAGE_RATIO:-15}" 'BEGIN {
        if (r+0 != r || r+0 <= 0) r = 15
        printf "%s", r
    }'
}

claude_weekly_limit_from_creds() {
    [[ -f "$claude_creds" ]] || return 0
    local tier rate_tier key
    tier=$(jq -r '.claudeAiOauth.subscriptionType // empty' "$claude_creds" 2>/dev/null) || return 0
    rate_tier=$(jq -r '.claudeAiOauth.rateLimitTier // empty' "$claude_creds" 2>/dev/null) || return 0
    key="${rate_tier:-$tier}"
    case "$key" in
        pro) echo 2000 ;;
        max) echo 10000 ;;
        default_claude_max_20x) echo 20000 ;;
        team) echo 3500 ;;
        "") return 0 ;;
        *) echo 10000 ;;
    esac
}

claude_stats_estimate() {
    [[ -f "$claude_stats_cache" && -f "$claude_creds" ]] || { echo "- none"; return; }
    jq_supports_iso_dates || { echo "- none"; return; }
    local limit messages ratio pct_remaining
    limit=$(claude_weekly_limit_from_creds) || { echo "- none"; return; }
    [[ -n "$limit" ]] || { echo "- none"; return; }
    messages=$(jq -r '
        def day_epoch:
          ((.date? // "") | tostring | . + "T00:00:00Z") as $date
          | try ($date | fromdateiso8601) catch 0;
        [.dailyActivity[]? | select(day_epoch > (now - 604800)) | (.messageCount // 0)] | add // 0
    ' "$claude_stats_cache" 2>/dev/null) || { echo "- none"; return; }
    [[ "$messages" =~ ^[0-9]+$ ]] || { echo "- none"; return; }
    ratio=$(positive_ratio)
    pct_remaining=$(awk -v m="$messages" -v r="$ratio" -v l="$limit" 'BEGIN {
        if (l+0 != l || l <= 0 || r+0 != r || r <= 0) exit 1
        approx = m / r
        pct = int((approx / l) * 100)
        if (pct > 100) pct = 100
        if (pct < 0) pct = 0
        printf "%d", 100 - pct
    }' 2>/dev/null) || { echo "- none"; return; }
    [[ -n "$pct_remaining" ]] && echo "$pct_remaining estimate" || echo "- none"
}

# Convert an ISO-8601 timestamp into days-from-now, 1 decimal, floored at 0.
# Emits nothing on a parse failure so a malformed timestamp can't blank the
# whole statusline under `set -euo pipefail`.
days_until_iso() {
    local resets_at="$1" reset_epoch
    reset_epoch=$(iso_epoch "$resets_at") || reset_epoch=""
    [[ -n "$reset_epoch" ]] || return 0
    awk -v r="$reset_epoch" -v n="$(date +%s)" \
        'BEGIN { d=(r-n)/86400; if (d<0) d=0; printf "%.1f", d }'
}

# Days until a provider's weekly quota resets, to 1 decimal (e.g. "2.5") so
# work can be planned around the refill (#2992). Prefers the absolute
# `resets_at` timestamp — `hours_to_reset` is pre-rounded to whole hours and so
# loses the decimal — and falls back to `hours_to_reset` only when no timestamp
# is present. Emits nothing when neither field is available, so a provider with
# `source: unavailable` (Claude today) never shows a fabricated countdown.
# date-parse misses and empty substitutions are swallowed so a bad field can't
# blank the whole statusline under `set -euo pipefail`.
reset_days() {
    local provider="$1" file resets_at="" hours="" source="" file_state="" selected=0
    # Freshest file first (#3034) — same selection principle as extract_pct,
    # so a fresh HOME cache supplies the countdown instead of a stale primary.
    local -a file_order=("$quota_primary" "$quota_cache")
    [[ "$primary_state" != fresh && "$cache_state" == fresh ]] && \
        file_order=("$quota_cache" "$quota_primary")
    for file in "${file_order[@]}"; do
        [[ -f "$file" ]] || continue
        source=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .source // empty' "$file" 2>/dev/null)
        resets_at=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .resets_at // empty' "$file" 2>/dev/null)
        hours=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .hours_to_reset // empty' "$file" 2>/dev/null)
        case "$source" in
            unavailable|estimated|*-estimate|stats-cache.json-estimate|statusline-stats-cache-estimate)
                resets_at=""; hours=""
                continue ;;
        esac
        if [[ -n "$source" || -n "$resets_at" || ( -n "$hours" && "$hours" != "null" ) ]]; then
            [[ "$file" == "$quota_primary" ]] && file_state="$primary_state" \
                                              || file_state="$cache_state"
            selected=1
            break
        fi
    done
    [[ "$selected" == 1 ]] || return
    if [[ -n "$resets_at" ]]; then
        local days
        days=$(days_until_iso "$resets_at") || days=""
        if [[ -n "$days" ]]; then
            printf '%s %s' "$days" "$file_state"
            return
        fi
    fi
    if [[ -n "$hours" && "$hours" != "null" ]]; then
        printf '%s %s' \
            "$(awk -v h="$hours" 'BEGIN { printf "%.1f", h/24 }')" "$file_state"
    fi
}

# Gemini (agy) usage LEFT for the G: segment, via the shared source of truth
# scripts/ai/assessment/gemini-usage.py (same object the agent-quota collector
# uses — no logic drift). agy persists no quota to disk (workspace-hub#3087). The
# helper reports the % REMAINING of the BINDING window (weekly or 5h, whichever
# has least left) plus that window's reset countdown; a 429 NEWER than the last
# /usage snapshot overrides to 0% (live exhaustion the snapshot can't know yet).
# Emits THREE fields "<pct> <state> <suffix>" (suffix "-" = none):
#   "<%left> fresh ·N.Nd"   genuine % LEFT + reset (days, or ·N.Nh sub-day / throttle)
#   "<%left> stale -"        snapshot older than the age gate → caller adds "?"
#   "- missing -"            no signal → color_pct dims G: instead of faking 100%.
gemini_snapshot_pct() {
    local helper line src pct hrs stale suf
    helper="${ws_root}/scripts/ai/assessment/gemini-usage.py"
    [[ -f "$helper" ]] || { echo "- missing -"; return; }
    line=$(AGY_USAGE_SNAPSHOT="${STATUSLINE_GEMINI_SNAPSHOT:-${HOME}/.cache/agy-usage-snapshot.json}" \
        python3 "$helper" 2>/dev/null \
        | jq -r '[.source, (.pct_remaining|tostring), (.hours_to_reset|tostring), (.stale|tostring)] | join(" ")') \
        || { echo "- missing -"; return; }
    read -r src pct hrs stale <<< "$line"
    [[ -z "$src" || "$src" == "unavailable" ]] && { echo "- missing -"; return; }
    # Reset countdown (days if >=24h else hours) applies to BOTH the snapshot's
    # binding-window reset and the 429 throttle reset.
    suf="-"
    if [[ -n "$hrs" && "$hrs" != "null" ]]; then
        suf=$(awk -v h="$hrs" 'BEGIN { if (h>=24) printf "·%.1fd", h/24; else printf "·%.1fh", h }')
    fi
    # Only a stale manual snapshot earns the "?" — a live 429 is current.
    local state=fresh
    [[ "$src" == "manual-snapshot" && "$stale" == "true" ]] && state=stale
    echo "${pct} ${state} ${suf}"
}

# Render a "LABEL:NN%" segment colored by remaining headroom so a throttle is
# glance-able for delegation: red <20%, yellow <40%, green otherwise, dim when
# the figure is unknown. Emits literal \033 escapes for the final printf %b.
color_pct() {
    local label="$1" rem="$2" suffix="${3:-}"
    if [[ -z "$rem" || "$rem" == "-" || ! "$rem" =~ ^[0-9]+$ ]]; then
        echo "\033[2m${label}:-%${suffix}\033[0m"   # dim: unknown/unavailable
        return
    fi
    local color='\033[32m'                            # green: ample headroom
    (( rem < 40 )) && color='\033[33m'                # yellow: getting tight
    (( rem < 20 )) && color='\033[31m'                # red: near throttle
    echo "${color}${label}:${rem}%${suffix}\033[0m"
}

color_5h_suffix() {
    local rem="$1" state="${2:-fresh}" mark=""
    if [[ -z "$rem" || "$rem" == "-" || ! "$rem" =~ ^[0-9]+$ ]]; then
        return
    fi
    [[ "$state" == stale || "$state" == estimate ]] && mark="?"
    local color='\033[32m'
    (( rem < 40 )) && color='\033[33m'
    (( rem < 20 )) && color='\033[31m'
    echo "${color}5h${rem}%${mark}\033[0m"
}

hermes_alias() {
    local rem="$1" state="${2:-none}" mark=""
    if [[ -z "$rem" || "$rem" == "-" || ! "$rem" =~ ^[0-9]+$ ]]; then
        echo "\033[2mH=O?\033[0m"
        return
    fi
    [[ "$state" == stale || "$state" == estimate ]] && mark="?"
    local color='\033[32m'
    (( rem < 40 )) && color='\033[33m'
    (( rem < 20 )) && color='\033[31m'
    echo "${color}H=O${mark}\033[0m"
}

# Claude: prefer 7-day subscription remaining from API (most accurate)
week_used=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_resets_at=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
c_suffix=""
c_mark=""
if [[ -n "$week_used" ]]; then
    c_rem=$(remaining_from_used "$week_used")
    [[ -n "$c_rem" ]] || c_rem="-"
else
    # Fallback to agent-quota file (stale file -> ? marker on the percentage)
    read -r c_rem c_state <<< "$(extract_pct "claude")"
    if [[ "$c_state" == none || -z "${c_state:-}" ]]; then
        read -r c_rem c_state <<< "$(claude_stats_estimate)"
    fi
    [[ "$c_state" == stale || "$c_state" == estimate ]] && c_mark="?"
    # Sonnet sub-bucket: show tighter limit with (S) indicator
    if [[ "$c_state" != estimate && -f "$quota_primary" && -n "$c_rem" && "$c_rem" != "-" ]]; then
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

read -r o_pct o_state <<< "$(extract_pct "codex")"
read -r o_5h_pct o_5h_state <<< "$(codex_five_hour_remaining)"
read -r g_pct g_state g_suffix <<< "$(gemini_snapshot_pct)"
[[ "$g_suffix" == "-" ]] && g_suffix=""
o_mark=""; [[ "$o_state" == stale || "$o_state" == estimate ]] && o_mark="?"
g_mark=""; [[ "$g_state" == stale ]] && g_mark="?"

# Append a "·N.Nd" weekly-reset countdown (days, 1 decimal) to the weekly-quota
# providers so delegation can see how long until headroom refills (#2992).
# Claude prefers the session JSON's rate_limits.seven_day.resets_at — the same
# live source already trusted for the percentage — since the quota file's
# claude entry is source:unavailable. Gemini is a daily limit, no reset suffix.
# Both fields must come from the same session snapshot: a resets_at without a
# used_percentage would pair a countdown with an unknown (or file-sourced) %.
c_days=""
c_days_mark=""
[[ -n "$week_used" && -n "$week_resets_at" ]] && c_days=$(days_until_iso "$week_resets_at")
if [[ -z "$c_days" ]]; then
    # File-sourced countdown: marked independently of the (possibly live)
    # percentage so a live percent never lends false freshness to stale
    # reset telemetry (#3034).
    read -r c_days c_days_state <<< "$(reset_days claude)"
    [[ "${c_days_state:-}" == stale && -n "$c_days" ]] && c_days_mark="?"
fi
read -r o_days o_days_state <<< "$(reset_days codex)"
o_days_mark=""; [[ "${o_days_state:-}" == stale && -n "${o_days:-}" ]] && o_days_mark="?"
[[ -n "$c_days" ]] && c_suffix="${c_suffix}·${c_days}d${c_days_mark}"
c_suffix="${c_mark}${c_suffix}"
o_suffix="$o_mark"
[[ -n "${o_days:-}" ]] && o_suffix="${o_mark}·${o_days}d${o_days_mark}"
if [[ -n "${o_5h_pct:-}" && "$o_5h_pct" != "-" ]]; then
    o_5h_segment=$(color_5h_suffix "$o_5h_pct" "${o_5h_state:-fresh}")
    [[ -n "$o_5h_segment" ]] && o_suffix="${o_suffix}·${o_5h_segment}"
fi

ai_usage="$(color_pct C "$c_rem" "$c_suffix")|$(color_pct O "$o_pct" "$o_suffix")|$(color_pct G "$g_pct" "${g_mark}${g_suffix}")|$(hermes_alias "$o_pct" "$o_state")"

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

# Segment mode (#2893): emit just the usage tail (quota/reset + cost + context)
# and stop. Composed by .claude/statusline-combined.sh onto the GSD statusline,
# which otherwise shows no AI-usage or weekly-reset info. Emitted after the
# fields exist but before the host/branch/path assembly the wrapper omits.
if [[ "$SEGMENT" == "--usage-tail" ]]; then
    printf "%b %b ctx:%b" "$ai_usage" "$cost_fmt" "$ctx"
    exit 0
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
