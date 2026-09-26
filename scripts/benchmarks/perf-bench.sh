#!/usr/bin/env bash
# perf-bench.sh — minimal CPU/git benchmark harness for workspace-hub.
#
# Runs four short workloads and appends timings (TSV) to results.tsv so
# successive runs are comparable. No external Python deps — pure stdlib.
#
# Usage:
#   scripts/benchmarks/perf-bench.sh [label]
#   numactl --cpunodebind=0 --membind=0 scripts/benchmarks/perf-bench.sh numa0
#
# Each run captures: governor, thread count, 1-min load, wall ms per workload.
# Compare runs:
#   column -t -s $'\t' scripts/benchmarks/results.tsv | tail -20

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
RESULTS="${REPO_ROOT}/scripts/benchmarks/results.tsv"
LABEL="${1:-baseline}"
HOST="$(hostname)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GOV="$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown)"
THREADS="$(nproc)"
LOAD="$(cut -d' ' -f1 < /proc/loadavg)"

if [[ ! -f "$RESULTS" ]]; then
    printf 'timestamp\thost\tlabel\tgovernor\tthreads\tload\tworkload\twall_ms\n' > "$RESULTS"
fi

run_bench() {
    local name="$1" cmd="$2"
    local start end ms
    start=$(date +%s%N)
    bash -c "$cmd" >/dev/null 2>&1
    end=$(date +%s%N)
    ms=$(( (end - start) / 1000000 ))
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$TS" "$HOST" "$LABEL" "$GOV" "$THREADS" "$LOAD" "$name" "$ms" >> "$RESULTS"
    printf '  %-15s %6d ms\n' "$name" "$ms"
}

echo "perf-bench host=${HOST} label=${LABEL} governor=${GOV} threads=${THREADS} load=${LOAD}"
echo "results -> ${RESULTS}"
echo ""

run_bench cpu_single "python3 -c 'sum(i*i for i in range(5_000_000))'"
run_bench cpu_multi  "seq 1 ${THREADS} | xargs -P ${THREADS} -I{} python3 -c 'sum(i*i for i in range(5_000_000))'"
run_bench git_status "cd ${REPO_ROOT} && git status --porcelain"
run_bench git_log    "cd ${REPO_ROOT} && git log --oneline -100"

echo ""
echo "rows in ${RESULTS}: $(($(wc -l < "$RESULTS") - 1))"
