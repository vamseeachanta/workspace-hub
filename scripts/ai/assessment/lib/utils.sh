#!/usr/bin/env bash
# ABOUTME: Portable helper functions shared across AI assessment scripts

# Portable file modification time (seconds since epoch)
file_mtime() {
    stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0
}

# Portable ISO-8601 datetime
iso_now() {
    date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z
}

# Monday of the current week in YYYY-MM-DD
last_monday_date() {
    local dow days_back
    dow=$(date +%u 2>/dev/null || date +%w)
    [[ "$dow" == "0" ]] && dow=7
    days_back=$(( dow - 1 ))
    (( days_back == 0 )) && days_back=7
    date -d "-${days_back} days" +%Y-%m-%d 2>/dev/null && return
    date -v-${days_back}d +%Y-%m-%d 2>/dev/null && return
    date -d "-7 days" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d
}

# Monday of the current week in YYYYMMDD (for ccusage --since)
this_monday_yyyymmdd() {
    local dow days_back
    dow=$(date +%u 2>/dev/null || echo 1)
    [[ "$dow" == "0" ]] && dow=7
    days_back=$(( dow - 1 ))
    date -d "-${days_back} days" +%Y%m%d 2>/dev/null \
        || date -v-${days_back}d +%Y%m%d 2>/dev/null \
        || date -d "-7 days" +%Y%m%d
}

# Portable touch-to-midnight (for day-marker files)
touch_midnight() {
    local marker="$1" today="$2"
    touch -d "${today} 00:00:00" "$marker" 2>/dev/null && return
    touch -t "$(echo "${today}" | tr -d '-')0000" "$marker" 2>/dev/null || true
}
