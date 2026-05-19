# Machine registry — fleet roster + control-plane assessment

The fleet's per-machine state lives in two surfaces:

1. **Git-tracked per-machine status files** at `config/machine-baselines/<token>.{md,yaml}` — one pair per machine, refreshed by `scripts/setup/emit-machine-status.sh`.
2. **GitHub operational tracker [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753)** — evergreen issue where operators post the `.md` form as comments after each bootstrap event.

The control-plane (currently `ace-linux-1`) reads both surfaces to assess fleet drift.

## Hostname → token policy

Per r1 m4 absorption (PII protection): the file basename is **never the raw hostname**. Token resolution policy:

1. **Alias from `config/agents/machines.yaml`** if defined. E.g., `aliases: { dell-laptop-tx-vamsee-01: ace-linux-1 }` → file is `ace-linux-1.{md,yaml}`. Aliases are user-curated and deliberately stable.
2. **Sha256 fallback** — `sha256(<raw-hostname>) | head -c 8` (8 hex chars). No PII leak via filename. Stable across re-runs as long as hostname doesn't change.

To set up an alias before first bootstrap:

```yaml
# config/agents/machines.yaml
aliases:
  vamsee-laptop-tx-bjk-01: ace-linux-1
  vamsee-mac-mini-01: vamsee-mac-1
  win-build-host-01: licensed-win-1
```

(The file is currently optional. v1.1 may make it required; v1 ships sha256 fallback as default.)

## What a per-machine status file looks like

```yaml
# config/machine-baselines/ace-linux-1.yaml
hostname: "ace-linux-1"
os: "linux"
last_updated: "2026-05-19T13:56:09Z"

dimensions:
  soul_contracts: PASS
  skills: PASS
  rules: PASS
  bridged_memory: PASS
  claude_global_pointer: PASS
  codex_agents_symlink: PASS
  hermes_soul_symlink: PASS
  claude_cli_auth: PASS
  codex_cli_auth: PASS
  gh_cli_auth: PASS
  gemini_cli_auth: PASS
  hermes_can_boot: PASS
  raw_session_state: "machine-local-by-design"
  submodules_initialized: PASS
  git_hooks_installed: PASS
  shell_profile_wired: PASS
  npm_global_prefix: PASS
  scheduler_entries: PASS
  ssh_key_present: PASS
  env_file_present: PASS
  uv_or_python_available: PASS
  git_bash_available: "n/a"

cli_versions:
  claude: "Code)"
  codex: "0.123.0"
  gh: "(2026-01-21)"
  gemini: "0.42.0"
  hermes: "(2026.5.16)"
  node: "v24.15.0"
  npm: "11.12.1"
  uv: "0.10.0"
```

The MD form is a human-readable rendering of the same data — that's what operators paste as a comment on #2753.

## Refresh cadence

Manual in v1 — run `bash scripts/setup/emit-machine-status.sh` after any setup or audit:

```bash
bash scripts/setup/emit-machine-status.sh
git add config/machine-baselines/
git commit -m "chore(setup): refresh <hostname> baseline"
git push
```

v1.1 may add a cron entry (e.g., daily at 03:00) per machine. v1 keeps it manual to surface intent.

## Control-plane workflow (ace-linux-1)

The control plane reads the entire registry via git and aggregates:

```bash
git pull
bash scripts/setup/aggregate-machine-status.sh
```

Output: `docs/reports/fleet-harness-status.md` — a 22-dimension × N-machine matrix with per-dimension coverage rows.

### Reading the fleet report

The report has two main tables:

1. **Per-machine status** — rows = machines, cols = 22 dimensions. Cells are ✅ (PASS), ⚠️ (WARN), ❌ (FAIL), • (machine-local-by-design), — (n/a). Scan eyeballs row-by-row to find drift.
2. **Per-dimension coverage** — rows = dimensions, cols = PASS/WARN/FAIL counts + coverage summary. Use this to find dimensions where the fleet isn't fully aligned.

### Drift remediation

When the report shows drift (WARN or FAIL in a cell):

1. Identify the affected machine + dimension.
2. Use the operator's playbook in [EXISTING_MACHINE_AUDIT.md](EXISTING_MACHINE_AUDIT.md#common-repair-commands-by-dimension) to apply a targeted fix.
3. On that machine: re-run `bash scripts/setup/emit-machine-status.sh`, commit, push.
4. On the control plane: `git pull && bash scripts/setup/aggregate-machine-status.sh` to refresh the report.

## Drift detection semantics (v1 vs v1.1)

**v1 (this iteration):** aggregator marks "drift" when any dimension has WARN or FAIL on at least one machine. This is a flat indicator — it doesn't distinguish whether drift is *expected* (e.g., worker machines don't need `claude_cli_auth`) or *problematic*.

**v1.1 (deferred per r1 m7):** add `role: control-plane | worker | developer` to the YAML schema + per-role expected-value matrix. Drift = a dimension value deviates from role-expected value.

## Known machines (as of 2026-05-19)

| Token | Raw hostname (private) | OS | Role | Baseline file |
|---|---|---|---|---|
| `0a36d305` | ace-linux-1 | linux | control-plane | [`config/machine-baselines/0a36d305.yaml`](../../config/machine-baselines/0a36d305.yaml) |
| _(more machines bootstrap themselves and append entries here)_ | | | | |

To add yourself to this table, after running `bash scripts/setup/new-machine-setup.sh`, edit this file and add your row.

## Cross-references

- **Status registry directory**: [`config/machine-baselines/`](../../config/machine-baselines/) (`README.md` documents policy + workflow)
- **Aggregator**: [`scripts/setup/aggregate-machine-status.sh`](../../scripts/setup/aggregate-machine-status.sh)
- **Emit helper**: [`scripts/setup/lib/emit-machine-status.sh`](../../scripts/setup/lib/emit-machine-status.sh)
- **Generated fleet report**: [`docs/reports/fleet-harness-status.md`](../reports/fleet-harness-status.md)
- **Operational tracker**: [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753)
- **Build issue**: [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751)
