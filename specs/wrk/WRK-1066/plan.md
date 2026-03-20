# WRK-1066 Plan — Environment Parity Audit

Route: A (simple) — inline plan, single executor (claude on dev-primary).
Revised through 12 rounds of Codex cross-review.

## Steps

1. **`scripts/readiness/harness-config.yaml`** — add `linux_reachable: false` to licensed-win-1 block.

2. **`scripts/maintenance/ai-tools-status.sh`** — pure collector/analyzer:
   - Reads `harness-config.yaml` for connection details (no hardcoded hosts)
   - For each machine: if `linux_reachable: false` → mark unreachable, skip
   - SSH uses explicit PATH: `$HOME/.npm-global/bin:$HOME/.local/bin:$PATH`
   - Version extraction via `npm list -g --depth=0 --json` (same explicit PATH)
   - `status` per-machine: `ok | missing | error | unreachable`
   - `severity` cross-machine drift: `info | warn | block` (over reachable only)
   - Exit 0 always except YAML write failure → exit 1
   - Overwrites `config/ai_agents/ai-tools-status.yaml`

3. **`config/ai_agents/ai-tools-status.yaml` schema** — `last_updated`,
   `collection_summary {total, reachable, unreachable, unreachable_machines}`,
   per-machine `{reachable, tools}`, per-tool `{raw, semver, status}`,
   top-level `drift` per tool `{severity, machines, note}`.

4. **Cron: both cron files updated** (Sunday 03:15, `full` role, timeout 60):
   - `crontab-template.sh`: add comment entry
   - `setup-cron.sh`: add to ENTRIES array

## Deferred

- licensed-win-1 version collection: Windows, no SSH; requires local Git Bash session
- dev-secondary version collection: offline at execution time; auto-collects on next weekly cron
