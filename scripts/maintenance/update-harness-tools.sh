#!/usr/bin/env bash
#
# update-harness.sh — Update the key harness CLI programs.
#
#   hermes  -> hermes update
#   claude  -> claude update
#   codex   -> codex update
#   gemini  -> npm install -g @google/gemini-cli@latest
#
# Each step is independent: a failure is reported but does not abort the rest.
# Run with --dry-run to print the commands without executing them.

set -uo pipefail

# Ensure tool dirs are on PATH. Cron and Windows Task Scheduler launch this with a
# minimal environment, so the npm-global / ~/.local/bin dirs where the CLIs live
# are not on PATH by default. Mirrors scripts/cron/harness-update-windows.sh.
if [[ -n "${APPDATA:-}" ]] && command -v cygpath >/dev/null 2>&1; then
  PATH="$(cygpath "$APPDATA")/npm:${PATH}"   # Windows npm-global (Git Bash / MINGW64)
fi
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" || "${1:-}" == "-n" ]] && DRY_RUN=1

# Track results for the summary.
declare -a NAMES=()
declare -a STATUS=()

run_step() {
  local name="$1"; shift
  echo
  echo "==> ${name}: $*"
  NAMES+=("$name")

  if ! command -v "$1" >/dev/null 2>&1; then
    echo "    SKIP: '$1' not found on PATH"
    STATUS+=("skipped (missing)")
    return
  fi

  if (( DRY_RUN )); then
    echo "    (dry-run, not executed)"
    STATUS+=("dry-run")
    return
  fi

  if "$@"; then
    STATUS+=("ok")
  else
    echo "    FAILED (exit $?)"
    STATUS+=("FAILED")
  fi
}

echo "Harness update — $(date '+%Y-%m-%d %H:%M:%S')"
(( DRY_RUN )) && echo "(dry-run mode)"

run_step hermes hermes update
run_step claude claude update
run_step codex  codex  update
run_step gemini npm install -g @google/gemini-cli@latest

echo
echo "================ Summary ================"
for i in "${!NAMES[@]}"; do
  printf '  %-8s %s\n' "${NAMES[$i]}" "${STATUS[$i]}"
done

# Non-zero exit if any step failed.
for s in "${STATUS[@]}"; do
  [[ "$s" == "FAILED" ]] && exit 1
done
exit 0
