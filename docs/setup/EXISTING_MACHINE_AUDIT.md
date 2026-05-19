# Existing-machine audit + repair

You have an existing machine in the fleet and want to confirm it's still aligned with the canonical state. Or you suspect drift after a manual change. This doc walks the diff-and-repair flow.

## TL;DR

```bash
cd workspace-hub
git pull                                            # sync repo state
bash scripts/setup/new-machine-setup.sh             # idempotent — safe to re-run
bash scripts/setup/verify-setup.sh                  # PASS/WARN/FAIL report
bash scripts/setup/emit-machine-status.sh           # refresh config/machine-baselines/<token>.{md,yaml}
```

Then push the updated baseline and post the new `<token>.md` as a follow-up comment on operational tracker [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753).

## Three audit modes

### 1. Quick local audit (< 1 minute)

Run `verify-setup.sh` and read the report:

```bash
bash scripts/setup/verify-setup.sh
```

Output classifies every dimension as PASS, WARN, or FAIL with remediation hints. WARN items typically mean optional infrastructure (e.g., no SSH key yet); FAIL items block productive work and should be resolved.

### 2. Fleet-wide audit (control plane = ace-linux-1)

```bash
git pull
bash scripts/setup/aggregate-machine-status.sh
cat docs/reports/fleet-harness-status.md
```

Shows a 22-dimension × N-machine matrix. Any cell with ❌ or ⚠️ flags drift. Read the per-dimension coverage table at the bottom — if a dimension shows `X of Y machines PASS` with X < Y, that's the drift surface.

### 3. Deep diff (when a single machine has unexplained drift)

Compare the machine's current baseline against its last-known-good:

```bash
# Get the file from when the machine last passed verification:
git log --oneline -- config/machine-baselines/<token>.yaml | head -5
# Diff the current state against the last clean commit:
git diff <last-clean-sha> -- config/machine-baselines/<token>.yaml
```

Each line-level diff in the YAML maps to a specific dimension that changed. Read the dimension's check function in `scripts/setup/lib/emit-machine-status.sh` for what it inspects.

## Common repair commands by dimension

| Dimension WARN/FAIL | Quick fix |
|---|---|
| `submodules_initialized` | `git submodule update --init --recursive` |
| `git_hooks_installed` | `bash scripts/setup/install-all-hooks.sh` |
| `claude_global_pointer` | `bash scripts/memory/bootstrap-machine.sh` |
| `codex_agents_symlink` / `hermes_soul_symlink` | `bash scripts/agents/install-soul-runtime.sh` (or re-run bootstrap-machine.sh which calls it) |
| `claude_cli_auth` | `claude auth login` |
| `codex_cli_auth` | `codex auth login` |
| `gh_cli_auth` | `gh auth login` |
| `gemini_cli_auth` | `gemini -p "ping"` (triggers OAuth) |
| `hermes_can_boot` | `bash -c 'source scripts/setup/lib/instantiate-hermes-config.sh && instantiate_hermes_config "$(pwd)" --force'` |
| `shell_profile_wired` | Add `source /path/to/workspace-hub/config/shell/bashrc-snippets.sh` to `~/.bashrc` |
| `npm_global_prefix` | `npm config set prefix ~/.npm-global` |
| `scheduler_entries` | Linux: `bash scripts/cron/setup-cron.sh`; Windows: `pwsh scripts/windows/setup-scheduler-tasks.ps1` |
| `ssh_key_present` | `ssh-keygen -t ed25519 -C "$(hostname)"` |
| `env_file_present` | `cp .env.example .env` then populate secrets |
| `uv_or_python_available` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `git_bash_available` (Windows) | `winget install -e --id Git.Git` |

## When `new-machine-setup.sh` re-run is the right answer

For most WARN/FAIL items, just re-running the bootstrap script is the cleanest fix. It's idempotent — no destructive overwrites — and it handles all dimensions in one pass.

```bash
bash scripts/setup/new-machine-setup.sh
```

You don't need to identify which dimension drifted. Just run the script, then re-emit:

```bash
bash scripts/setup/emit-machine-status.sh
git add config/machine-baselines/
git commit -m "chore(setup): refresh <hostname> baseline post-audit"
git push
```

## When `new-machine-setup.sh` is NOT enough

Rare cases where a re-run can't repair:

1. **Manual edit conflict in `~/.claude/CLAUDE.md`**: re-run regenerates from canonical content. If you had a manual edit you wanted to keep, capture it first; the script overwrites silently.
2. **Auth token expired** (per provider's policy): you must re-do `claude auth login` etc. The script can't refresh expired tokens.
3. **Hermes binary version mismatch**: the script does NOT install or upgrade the Hermes binary — that's out-of-band. See [PROVIDER_AUTH_GUIDE.md](PROVIDER_AUTH_GUIDE.md#hermes).
4. **Operating-system upgrade broke something**: e.g., macOS upgrade reset a permission. Audit per-dimension and apply targeted fixes.
5. **Working tree dirty or in conflict state**: the script may refuse to operate. Resolve via `git status` first.

## Idempotency contract

Per r2 C5 patch in the plan: re-running on a fully-configured machine produces **zero git diff except for `config/machine-baselines/<token>.{md,yaml}` `last_updated` timestamp**. Home-runtime files (`~/.claude/CLAUDE.md` etc.) are also stable across re-runs.

If you see unexpected modifications after a re-run, that's a bug — file an issue.

## Cross-references

- [FRESH_MACHINE_SETUP.md](FRESH_MACHINE_SETUP.md) — initial bootstrap
- [PROVIDER_AUTH_GUIDE.md](PROVIDER_AUTH_GUIDE.md) — auth specifics
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — known issues
- [MACHINE_REGISTRY.md](MACHINE_REGISTRY.md) — fleet-wide audit
