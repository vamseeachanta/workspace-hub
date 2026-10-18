#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
config_path="${JOB_QUEUE_CONFIG:-$script_dir/job-queue.local.conf}"
script="${1:?script required}"
job_id="${2:?job id required}"
issue="${3:-none}"
case "$script" in ""|*[!A-Za-z0-9._-]*) echo "bad script name"; exit 1;; esac
case "$script" in *.sh) ;; *) echo "bad script name"; exit 1;; esac
bash "$script_dir/$script" start "$job_id" "$issue" "$config_path" >/dev/null 2>&1 &
echo "launched $job_id pid=$!"
