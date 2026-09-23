#!/usr/bin/env bash
# equality-preflight.sh — THIN wrapper: fast-forward the checkout, then `exec` the real
# equality entry point (#3702).
#
# This file must stay tiny and must not source or run any other repo script after the
# merge, because the merge can replace those files on disk while bash is reading them
# (r1 M3). `exec` hands the process over AFTER the fast-forward has landed, so the cron
# script that actually runs is the post-merge version, opened fresh by a new bash.
#
# Scheduled callers should point at THIS file rather than equality-matrix-cron.sh.
# Arguments are forwarded verbatim.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
[[ -n "$REPO_ROOT" ]] || REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=scripts/readiness/lib/ff-preflight.sh
. "${SCRIPT_DIR}/lib/ff-preflight.sh"
ff_preflight "$REPO_ROOT"

exec bash "$REPO_ROOT/scripts/readiness/equality-matrix-cron.sh" "$@"
