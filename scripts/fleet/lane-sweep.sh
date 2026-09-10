#!/bin/bash
# lane-sweep.sh -- reconcile what is ACTUALLY running on the fleet against
# what the control surface thinks is running.
#
# WHY THIS EXISTS. On 2026-08-15 a poll loop launched on gpu-claw ran for
# 13.5 hours after its job finished, because it waited on `pgrep -f
# "stage45_driver"` -- a pattern that matches the ssh command carrying it.
# Nothing reported an error. It was found only by sweeping by hand.
#
# ace-linux-1 is the CONTROL SURFACE: it should show orchestration and git,
# never solver or provider-CLI compute. This script flags it if it does.
#
# Usage: lane-sweep.sh [--registry <file>]
set -eo pipefail

REGISTRY="${2:-$HOME/.claude/fleet-lanes.tsv}"
COMPUTE='[i]nterFoam|[s]impleFoam|[s]nappyHexMesh|[p]otentialFoam|[c]odex exec|[a]gy -p|[b]ench_run'
# A waiter that polls by process name can match its own ssh command line and
# never exit. Any `until ! pgrep` on a remote host is suspect by construction.
ZOMBIE='until . pgrep|while pgrep'

hosts=(gpu-claw-ts ace-linux-2)

# Match the EXECUTABLE name, not the command line. An `ssh host '...bench_run...'`
# has the pattern in its argv and is orchestration, not compute -- the first
# version of this check flagged its own dispatch commands as violations, which
# is the same self-match class it exists to detect.
COMPUTE_EXE='^(interFoam|simpleFoam|potentialFoam|snappyHexMesh|blockMesh|mpirun)$'
# Provider CLIs count as compute only in one-shot mode. `codex app-server` /
# `app-server-broker.mjs` / `codex-update-manager daemon` are long-lived MCP
# and update daemons -- flagging those as policy violations is crying wolf,
# and a detector that cries wolf gets ignored exactly when it is right.
PROVIDER_RUN='[c]odex exec|[a]gy -p'
PROVIDER_SKIP='app-server|broker|update-manager|daemon'

echo "=== ace-linux-1 (CONTROL SURFACE -- compute here is a policy violation)"
hits_local=$( { ps -eo comm=,etime= | awk -v re="$COMPUTE_EXE" '$1 ~ re {print}'
                ps -eo comm=,etime=,args= \
                  | grep -E "$PROVIDER_RUN" \
                  | grep -vE "$PROVIDER_SKIP" \
                  | awk '$1=="node"||$1=="codex"||$1=="agy" {print $1, $2}'
              } || true)
if [ -n "$hits_local" ]; then
  echo "  !! COMPUTE RUNNING ON THE CONTROL SURFACE:"
  printf '%s\n' "$hits_local" | sed 's/^/     /'
else
  echo "  clean (orchestration and git only)"
fi

for h in "${hosts[@]}"; do
  echo "=== $h"
  out=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$h" \
        "ps -eo etime=,args= 2>/dev/null" 2>/dev/null) || {
    echo "  UNREACHABLE"; continue; }

  # Summarise rather than dump: 8 identical solver ranks is one lane, not eight.
  live=$(printf '%s\n' "$out" | grep -E "$COMPUTE" | grep -v " grep " || true)
  if [ -n "$live" ]; then
    echo "  live work:"
    printf '%s\n' "$live" | awk '{
        et=$1; $1=""; cmd=substr($0,2,70);
        gsub(/^[ \t]+/,"",cmd); key=cmd; n[key]++; if (!(key in first)) first[key]=et
      } END { for (k in n) printf "     %-10s x%-3d %s\n", first[k], n[k], k }' \
      | sort -k2 -r
  else
    echo "  no live work"
  fi

  # Long-lived pollers are the failure mode this script was written for.
  zomb=$(printf '%s\n' "$out" | grep -E "$ZOMBIE" | grep -v " grep " | cut -c1-100 || true)
  if [ -n "$zomb" ]; then
    echo "  !! SUSPECTED ZOMBIE WAITER (poll-by-process-name can self-match):"
    printf '%s\n' "$zomb" | sed 's/^/     /'
    echo "     -> kill by PID; do NOT pkill -f with the same pattern, it kills your own ssh"
  fi
done

if [ -f "$REGISTRY" ]; then
  echo "=== registry ($REGISTRY)"
  column -t -s $'\t' "$REGISTRY" 2>/dev/null || cat "$REGISTRY"
  echo "  Reconcile by hand: a registry row with no live process is either"
  echo "  finished (check its marker file) or died silently."
else
  echo "=== no registry at $REGISTRY"
fi
