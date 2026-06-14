#!/usr/bin/env bash
# Status line for workspace-hub — portable across machines
# Shows: model | branch | WRK counts + active | AI usage | cost | context
set -euo pipefail

input=$(cat)

# Optional segment mode (#2893): emit only a sub-part of the statusline so a
# wrapper can compose this with another statusline (e.g. the vendored GSD one,
# which has no quota/reset display). Recognized:
#   --usage-tail  -> AI-usage segment (C:|O:|G: with weekly-reset) + cost + ctx
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
# falls back to agent-quota file. O: and G: from agent-quota files.
# Env overrides keep the script testable with fixture quota files (#2992);
# they fall back to the real locations in normal use.
quota_primary="${STATUSLINE_QUOTA_PRIMARY:-$ws_root/config/ai-tools/agent-quota-latest.json}"
quota_cache="${STATUSLINE_QUOTA_CACHE:-${HOME}/.cache/agent-quota.json}"
# Gemini genuine usage: manual /usage snapshot (agy persists no quota to disk —
# workspace-hub#3087). Written by scripts/ai/assessment/agy-usage-snapshot.py.
gemini_snapshot="${STATUSLINE_GEMINI_SNAPSHOT:-${HOME}/.cache/agy-usage-snapshot.json}"

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

# Emit "<pct> <fresh|stale>" (or "- none" when unknown) for a provider,
# choosing the freshest file that has a value: fresh primary > fresh cache >
# stale primary > stale cache. Preserves the historical field-per-file
# convention (primary: week_pct, cache: pct_remaining).
extract_pct() {
    local provider="$1" p_val="" c_val="" v
    if [[ -f "$quota_primary" ]]; then
        v=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .week_pct // empty' \
            "$quota_primary" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && \
            p_val=$(awk -v w="$v" 'BEGIN { printf "%d", 100 - w }')
    fi
    if [[ -f "$quota_cache" ]]; then
        v=$(jq -r --arg p "$provider" \
            '.agents[] | select(.provider == $p) | .pct_remaining // empty' \
            "$quota_cache" 2>/dev/null)
        [[ -n "$v" && "$v" != "null" ]] && c_val="$v"
    fi
    if [[ -n "$p_val" && "$primary_state" == fresh ]]; then echo "$p_val fresh"
    elif [[ -n "$c_val" && "$cache_state" == fresh ]]; then echo "$c_val fresh"
    elif [[ -n "$p_val" ]]; then echo "$p_val stale"
    elif [[ -n "$c_val" ]]; then echo "$c_val stale"
    else echo "- none"
    fi
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
    local provider="$1" file resets_at="" hours="" source="" file_state=""
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
        if [[ -n "$source" || -n "$resets_at" || ( -n "$hours" && "$hours" != "null" ) ]]; then
            [[ "$file" == "$quota_primary" ]] && file_state="$primary_state" \
                                              || file_state="$cache_state"
            break
        fi
    done
    case "$source" in
        unavailable|estimated) return ;;
    esac
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

# Detect an ACTIVE Gemini throttle from the gemini CLI's error reports — FREE,
# no API call (workspace-hub#3087). On a 429 the gemini CLI writes
# /tmp/gemini-client-error-*.json whose filename carries the error time and whose
# `message` says "...reset after XhYmZs". absolute_reset = file_time + duration;
# if still in the future the shared Google AI Pro Gemini pool (same quota agy
# draws on) is exhausted. Prints hours-until-reset (float) or nothing. Cheap-
# guarded: python only runs when a report file actually exists.
gemini_throttle_hours() {
    local dir="${GEMINI_ERROR_DIR:-/tmp}"
    compgen -G "${dir}/gemini-client-error-*.json" >/dev/null 2>&1 || return 0
    python3 - "$dir" 2>/dev/null <<'PY'
import glob, os, re, sys
from datetime import datetime, timezone

d = sys.argv[1]
now = datetime.now(timezone.utc).timestamp()
best = None  # latest future reset across all reports
for path in glob.glob(os.path.join(d, "gemini-client-error-*.json")):
    m = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})-(\d{3})Z", os.path.basename(path))
    if not m:
        continue
    try:
        ferr = datetime.fromisoformat(
            f"{m.group(1)}T{m.group(2)}:{m.group(3)}:{m.group(4)}.{m.group(5)}+00:00"
        ).timestamp()
    except ValueError:
        continue
    try:  # raw read — the "reset after" text may be nested (error.message / .stack)
        msg = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    dm = re.search(r"reset after\s+(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", msg, re.I)
    if not dm or not any(dm.groups()):
        continue
    reset = ferr + int(dm.group(1) or 0)*3600 + int(dm.group(2) or 0)*60 + int(dm.group(3) or 0)
    if reset > now:
        best = reset if best is None else max(best, reset)
if best is not None:
    print(f"{(best - now)/3600:.1f}")
PY
}

# Gemini (agy) usage for the G: segment. Precedence:
#   1. ACTIVE THROTTLE — a live 429 (gemini_throttle_hours) means 0% NOW with a
#      real ·N.Nh/·N.Nd reset countdown, regardless of any snapshot.
#   2. MANUAL SNAPSHOT — genuine weekly % AVAILABLE from /usage (agy persists no
#      quota to disk), age-gated against a gemini-specific threshold (a weekly
#      reading stays meaningful far longer than the 6h codex/claude gate).
#   3. MISSING — "- missing" → color_pct dims G: instead of faking 100%.
# Emits THREE fields: "<pct> <state> <suffix>" (suffix "-" = none) so the caller
# can append a reset countdown only when throttled.
gemini_snapshot_pct() {
    local thr suf pct cap max_h epoch now age_h
    thr=$(gemini_throttle_hours)
    if [[ -n "$thr" ]]; then
        suf=$(awk -v h="$thr" 'BEGIN { if (h>=24) printf "·%.1fd", h/24; else printf "·%.1fh", h }')
        echo "0 throttled ${suf}"; return
    fi
    [[ -f "$gemini_snapshot" ]] || { echo "- missing -"; return; }
    pct=$(jq -r '.gemini.weekly_pct_avail // empty' "$gemini_snapshot" 2>/dev/null)
    [[ -n "$pct" ]] || { echo "- missing -"; return; }
    pct=$(awk -v p="$pct" 'BEGIN { printf "%d", p }')   # int for color thresholds
    cap=$(jq -r '.captured_at // empty' "$gemini_snapshot" 2>/dev/null)
    max_h="${STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS:-48}"
    epoch=$(iso_epoch "$cap") || epoch=""
    [[ -n "$epoch" ]] || { echo "$pct stale -"; return; }   # undatable = stale
    now=$(date +%s)
    age_h=$(awk -v e="$epoch" -v n="$now" 'BEGIN { print (n-e)/3600 }')
    if awk -v a="$age_h" -v m="$max_h" 'BEGIN { exit !(a <= m) }'; then
        echo "$pct fresh -"
    else
        echo "$pct stale -"
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
week_resets_at=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
c_suffix=""
c_mark=""
if [[ -n "$week_used" ]]; then
    c_rem=$(awk -v u="$week_used" 'BEGIN { printf "%d", 100 - u }')
else
    # Fallback to agent-quota file (stale file -> ? marker on the percentage)
    read -r c_rem c_state <<< "$(extract_pct "claude")"
    [[ "$c_state" == stale ]] && c_mark="?"
    # Sonnet sub-bucket: show tighter limit with (S) indicator
    if [[ -f "$quota_primary" && -n "$c_rem" && "$c_rem" != "-" ]]; then
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
read -r g_pct g_state g_suffix <<< "$(gemini_snapshot_pct)"
[[ "$g_suffix" == "-" ]] && g_suffix=""
o_mark=""; [[ "$o_state" == stale ]] && o_mark="?"
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

ai_usage="$(color_pct C "$c_rem" "$c_suffix")|$(color_pct O "$o_pct" "$o_suffix")|$(color_pct G "$g_pct" "${g_mark}${g_suffix}")"

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
