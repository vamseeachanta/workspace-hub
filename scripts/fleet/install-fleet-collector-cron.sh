#!/usr/bin/env bash
# install-fleet-collector-cron.sh — one-shot setup of the hourly AI account
# usage job on the fleet collector VM (the host that already publishes
# docs/reports/fleet-snapshots/). Idempotent: re-running replaces the marked
# crontab line and re-checks prerequisites.
#
# Run ON the collector VM, from the workspace-hub checkout:
#   bash scripts/fleet/install-fleet-collector-cron.sh          # check + install
#   bash scripts/fleet/install-fleet-collector-cron.sh --check  # report only
#   bash scripts/fleet/install-fleet-collector-cron.sh --run    # install, then run once now
#
# Prerequisites it verifies: python3 + PyYAML, ssh BatchMode reachability of
# every host in config/ai-tools/ai-accounts.yaml (aliases = fleet labels, as
# in ~/.ssh/config), and a push-capable origin. Missing items are printed with
# the fix; nothing is installed while a required item is missing.
#
# The catalogue rule (config/scheduled-tasks/schedule-tasks.yaml is the single
# source of truth) still applies: this VM is not yet in
# config/workstations/registry.yaml, so the job is installed here directly, as
# the existing fleet-daily-collector is, until the registry entry and the
# scheduler attestation (#3475) are added. Marker: workspace-hub:account-usage
#
# DURABILITY NOTE (2026-09-26): a system-crontab line does NOT survive a VM
# restart here — /var (including /var/spool/cron) is ephemeral, and the entry
# installed this way was wiped the same day it was created. On this VM the
# durable scheduler is the runtime scheduler: entry `ai-account-usage-hourly`
# (hourly, ~:13 past the hour), whose body recreates the /root/.ssh/config
# symlink if a restart wiped it. Prefer registering/updating that runtime
# entry over re-running this installer for the crontab line.
set -euo pipefail

MODE="install"
case "${1:-}" in
    --check) MODE="check" ;;
    --run)   MODE="run" ;;
    "") ;;
    *) echo "usage: $0 [--check|--run]" >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
MARKER="# workspace-hub:account-usage"
SCHEDULE="7 * * * *"
LOG_DIR="${HUB}/logs/fleet"
CRON_LINE="${SCHEDULE} cd ${HUB} && bash scripts/fleet/account-usage-cron.sh >> ${LOG_DIR}/account-usage-\$(date +\\%Y\\%m\\%d).log 2>&1 ${MARKER}"
CONFIG="${HUB}/config/ai-tools/ai-accounts.yaml"
ok=1

say()  { printf '  %-12s %s\n' "$1" "$2"; }
fail() { say "MISSING" "$1"; ok=0; }

echo "== fleet collector cron: prerequisites =="
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

if command -v crontab >/dev/null 2>&1; then
    say "OK" "crontab available"
else
    fail "crontab missing  ->  sudo apt install -y cron"
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

if [[ "${MODE}" == "check" ]]; then
    (crontab -l 2>/dev/null | grep -qF "${MARKER}") && say "OK" "cron line installed" || say "INFO" "cron line not installed"
    exit $(( ok ? 0 : 1 ))
fi
(( ok )) || { echo "not installing: fix the MISSING items above" >&2; exit 1; }

echo "== install =="
mkdir -p "${LOG_DIR}"
{ crontab -l 2>/dev/null | grep -vF "${MARKER}" || true; echo "${CRON_LINE}"; } | crontab -
say "OK" "crontab: ${SCHEDULE} account-usage-cron.sh (marker ${MARKER})"

if [[ "${MODE}" == "run" ]]; then
    echo "== first run =="
    bash "${HUB}/scripts/fleet/account-usage-cron.sh"
fi
