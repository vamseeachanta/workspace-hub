#!/usr/bin/env bash
# session-curation-preflight.sh — THIN wrapper: fast-forward the checkout, then `exec`
# curate-session-memory.sh (#3702, r1 M2).
#
# WHY a SECOND wrapper: curate-session-memory.sh:75-83 runs collect-equality.sh +
# build-equality-matrix.py every 6 hours on six machines and never publishes. It is the
# higher-frequency of the two collection paths and the one where behind_main actually
# ratchets. A preflight that reached only equality-matrix-cron.sh would leave the ratchet
# running and this issue would not land.
#
# Same `exec` discipline as scripts/readiness/equality-preflight.sh: nothing else in the
# repo is sourced or run after the merge, so no script is rewritten while bash reads it.
# Scheduled callers should point at THIS file. Arguments are forwarded verbatim.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
[[ -n "$REPO_ROOT" ]] || REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=scripts/readiness/lib/ff-preflight.sh
. "$REPO_ROOT/scripts/readiness/lib/ff-preflight.sh"
ff_preflight "$REPO_ROOT"

exec bash "$REPO_ROOT/scripts/curation/curate-session-memory.sh" "$@"
