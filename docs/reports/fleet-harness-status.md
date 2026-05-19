# Fleet harness-parity status

> Generated: 2026-05-19T13:56:12Z
> Source: `scripts/setup/aggregate-machine-status.sh` (issue #2751 G9)
> Operational tracker: #2753
> Machines registered: 1

## Per-machine status

| Machine | OS | Last-updated | soul_contracts | skills | rules | bridged_memory | claude_global_pointer | codex_agents_symlink | hermes_soul_symlink | claude_cli_auth | codex_cli_auth | gh_cli_auth | gemini_cli_auth | hermes_can_boot | raw_session_state | submodules_initialized | git_hooks_installed | shell_profile_wired | npm_global_prefix | scheduler_entries | ssh_key_present | env_file_present | uv_or_python_available | git_bash_available |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0a36d305 | linux | 2026-05-19T13:56:09Z | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | • | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

## Per-dimension coverage

| Dimension | PASS | WARN | FAIL | Coverage |
|---|---|---|---|---|
| soul_contracts | 1 | 0 | 0 | 1 of 1 machines |
| skills | 1 | 0 | 0 | 1 of 1 machines |
| rules | 1 | 0 | 0 | 1 of 1 machines |
| bridged_memory | 1 | 0 | 0 | 1 of 1 machines |
| claude_global_pointer | 1 | 0 | 0 | 1 of 1 machines |
| codex_agents_symlink | 1 | 0 | 0 | 1 of 1 machines |
| hermes_soul_symlink | 1 | 0 | 0 | 1 of 1 machines |
| claude_cli_auth | 1 | 0 | 0 | 1 of 1 machines |
| codex_cli_auth | 1 | 0 | 0 | 1 of 1 machines |
| gh_cli_auth | 1 | 0 | 0 | 1 of 1 machines |
| gemini_cli_auth | 1 | 0 | 0 | 1 of 1 machines |
| hermes_can_boot | 1 | 0 | 0 | 1 of 1 machines |
| raw_session_state | 1 | 0 | 0 | 1 of 1 machines |
| submodules_initialized | 1 | 0 | 0 | 1 of 1 machines |
| git_hooks_installed | 1 | 0 | 0 | 1 of 1 machines |
| shell_profile_wired | 1 | 0 | 0 | 1 of 1 machines |
| npm_global_prefix | 1 | 0 | 0 | 1 of 1 machines |
| scheduler_entries | 1 | 0 | 0 | 1 of 1 machines |
| ssh_key_present | 1 | 0 | 0 | 1 of 1 machines |
| env_file_present | 1 | 0 | 0 | 1 of 1 machines |
| uv_or_python_available | 1 | 0 | 0 | 1 of 1 machines |
| git_bash_available | 1 | 0 | 0 | 1 of 1 machines |

## All machines pass all dimensions ✅

## How to update

Run on each machine:
```
bash scripts/setup/emit-machine-status.sh
git add config/machine-baselines/ && git commit -m 'chore(setup): refresh machine baseline'
git push
```

Then on the control plane (`ace-linux-1`):
```
git pull
bash scripts/setup/aggregate-machine-status.sh
```
