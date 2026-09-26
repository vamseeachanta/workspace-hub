#!/usr/bin/env bash
# install-fleet-collector-cron.sh — preflight for the hourly AI account usage
# job on the fleet collector VM (the host that already publishes
# docs/reports/fleet-snapshots/). Idempotent and NON-MUTATING: it verifies the
# prerequisites, prints the scheduler entry to register, and can run the job
# once by hand. It never writes a scheduler itself.
#
# Run ON the collector VM, from the workspace-hub checkout:
#   bash scripts/fleet/install-fleet-collector-cron.sh           # preflight + print the entry
#   bash scripts/fleet/install-fleet-collector-cron.sh --check   # preflight only (exit 1 on a MISSING item)
#   bash scripts/fleet/install-fleet-collector-cron.sh --run     # preflight, then run the job once now
#
# Prerequisites it verifies: python3 + PyYAML, ssh BatchMode reachability of
# every host in config/ai-tools/ai-accounts.yaml (aliases = fleet labels, as
# in ~/.ssh/config), and a push-capable origin. Missing items are printed with
# the fix.
#
# WHY IT DOES NOT WRITE THE SCHEDULER (2026-09-26): a system-crontab line does
# NOT survive a VM restart here — /var (including /var/spool/cron) is ephemeral,
# and the line this script used to install was wiped the same day it was
# created. The durable scheduler on this VM is its runtime scheduler: entry
# `ai-account-usage-hourly` (hourly, ~:13 past the hour), whose body recreates
# the /root/.ssh/config symlink if a restart wiped it, then runs
# scripts/fleet/account-usage-cron.sh. Register or update THAT entry with the
# command this script prints. Scheduler writes in this repository are governed
# by config/scheduled-tasks/mutation-surfaces.yaml (scheduler-mutation-safety);
# a preflight that prints the entry stays outside that surface by design.
#
# The catalogue rule (config/scheduled-tasks/schedule-tasks.yaml is the single
# source of truth) still applies: this VM is not yet in
# config/workstations/registry.yaml; registering it and declaring the job there
# is follow-up D1 in docs/plans/2026-09-26-fleet-ai-account-usage-and-collector-cron.md.
set -euo pipefail

MODE="print"
case "${1:-}" in
    --check) MODE="check" ;;
    --run)   MODE="run" ;;
    "") ;;
    *) echo "usage: $0 [--check|--run]" >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENTRY_NAME="ai-account-usage-hourly"
LOG_DIR="${HUB}/logs/fleet"
JOB_CMD="cd ${HUB} && bash scripts/fleet/account-usage-cron.sh >> ${LOG_DIR}/account-usage-\$(date +%Y%m%d).log 2>&1"
CONFIG="${HUB}/config/ai-tools/ai-accounts.yaml"
ok=1

say()  { printf '  %-12s %s\n' "$1" "$2"; }
fail() { say "MISSING" "$1"; ok=0; }

echo "== fleet collector job: prerequisites =="
if python3 -c 'import yaml' 2>/dev/null; then
    say "OK" "python3 + PyYAML"
else
    fail "PyYAML  ->  sudo apt install -y python3-yaml"
fi

if git -C "${HUB}" ls-remote --exit-code origin main >/dev/null 2>&1; then
    say "OK" "origin main reachable ($(git -C "${HUB}" remote get-url origin))"
else
    fail "origin main not reachable (gh auth login / ssh key)"
fi

echo "== fleet hosts (ssh BatchMode, alias = label) =="
mapfile -t HOSTS < <(python3 - "${CONFIG}" <<'PY'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for label, h in (cfg.get("hosts") or {}).items():
    if not (h or {}).get("local"):
        print((h or {}).get("ssh") or label)
PY
) || true
for h in "${HOSTS[@]}"; do
    if ssh -o BatchMode=yes -o ConnectTimeout=8 "${h}" 'exit 0' 2>/dev/null; then
        say "OK" "${h}"
    else
        say "WARN" "${h}: not reachable now (add to ~/.ssh/config or fix key); the job skips it and reports"
    fi
done

# Scheduler-agnostic liveness: the job writes a dated log on every run, so a
# fresh log proves the entry exists and fires, whichever scheduler holds it.
echo "== job liveness (from ${LOG_DIR}) =="
newest="$(ls -t "${LOG_DIR}"/account-usage-*.log 2>/dev/null | head -1 || true)"
if [[ -n "${newest}" ]]; then
    age_min=$(( ( $(date +%s) - $(stat -c %Y "${newest}") ) / 60 ))
    if (( age_min <= 120 )); then
        say "OK" "last run ${age_min} min ago ($(basename "${newest}"))"
    else
        say "WARN" "last run ${age_min} min ago; the hourly entry may be missing (see below)"
    fi
else
    say "INFO" "no run log yet; register the entry below, or --run once"
fi

if [[ "${MODE}" == "check" ]]; then
    exit $(( ok ? 0 : 1 ))
fi
(( ok )) || { echo "fix the MISSING items above before registering the job" >&2; exit 1; }

mkdir -p "${LOG_DIR}"
echo "== scheduler entry to register (runtime scheduler on this VM) =="
echo "  name:     ${ENTRY_NAME}"
echo "  schedule: hourly (~:13 past the hour)"
echo "  command:  ${JOB_CMD}"
echo "  note:     the entry body should first restore /root/.ssh/config if a restart wiped it"

if [[ "${MODE}" == "run" ]]; then
    echo "== running the job once now =="
    bash "${HUB}/scripts/fleet/account-usage-cron.sh"
fi
