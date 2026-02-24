# Multi-Machine Setup

> Covers SSH helpers, hostname identity, and CLI consistency across ace-linux-1 and ace-linux-2.

## Path Differences Between Machines

| Machine | workspace-hub path |
|---|---|
| ace-linux-1 | `/mnt/local-analysis/workspace-hub` |
| ace-linux-2 | `/mnt/workspace-hub` |

Workaround until paths are standardised: add a `~/workspace-hub` symlink on each machine
pointing to the local path. Scripts that resolve via `git rev-parse` are already path-agnostic.

## Sourcing ssh-helpers.sh

Add to `~/.bashrc` on each machine:

```bash
# Multi-machine SSH helpers
WH="${HOME}/workspace-hub"   # or the machine-local path
if [[ -f "${WH}/scripts/operations/system/ssh-helpers.sh" ]]; then
    source "${WH}/scripts/operations/system/ssh-helpers.sh"
fi
```

This gives you:

| Command | Effect |
|---|---|
| `ace1` | SSH to ace-linux-1 as `$ACE_SSH_USER` (default: vamsee) |
| `ace2` | SSH to ace-linux-2 as `$ACE_SSH_USER` |
| `ace1-tmux` | SSH to ace-linux-1 and attach/create tmux session `main` |
| `ace2-tmux` | SSH to ace-linux-2 and attach/create tmux session `main` |
| `whoami-machine` | Print hostname, LAN IP, and Tailscale IP |

Override the SSH user without editing the script:

```bash
export ACE_SSH_USER=yourname
```

## Recommended .bashrc Additions

```bash
# 1. Source SSH helpers (path-safe)
_WH_PATH="/mnt/local-analysis/workspace-hub"          # ace-linux-1
# _WH_PATH="/mnt/workspace-hub"                        # ace-linux-2
[[ -f "${_WH_PATH}/scripts/operations/system/ssh-helpers.sh" ]] && \
    source "${_WH_PATH}/scripts/operations/system/ssh-helpers.sh"

# 2. Confirm machine on new shell open
echo "Machine: $(hostname) | $(hostname -I | awk '{print $1}')"
```

## Claude Code Statusline

`.claude/statusline-command.sh` now prepends `[hostname]` to every status line:

```
[ace-linux-1] Claude  workspace-hub  main  WRK:3p/1w/0b  ...
[ace-linux-2] Claude  workspace-hub  main  WRK:3p/1w/0b  ...
```

No configuration required — `hostname -s` is read at runtime.

## Machine Audit Table

| Item | ace-linux-1 | ace-linux-2 | Status |
|---|---|---|---|
| workspace-hub path | `/mnt/local-analysis/workspace-hub` | `/mnt/workspace-hub` | Diverged — standardise or symlink |
| Tailscale IP | 100.107.64.76 | 100.93.161.27 | OK |
| uv installed | Yes | TBD | Verify on ace-linux-2 |
| Claude CLI | Yes | TBD | Verify on ace-linux-2 |
| Codex CLI | Yes | TBD | Verify on ace-linux-2 |
| Gemini CLI | TBD | TBD | Audit both |
| tmux config | TBD | TBD | Sync ~/.tmux.conf |
| .bashrc aliases | TBD | TBD | Diff and sync |
| SSH keys (bidirectional) | TBD | TBD | See WRK-295 |

## Related Work Items

- WRK-295 — Bidirectional SSH key auth (foundation)
- WRK-296 — Tailscale on ace-linux-2 (foundation)
- WRK-297 — SSHFS mounts ace-linux-1 to ace-linux-2
- WRK-307 — KVM display fix ace-linux-2
- WRK-308 — Remote desktop ace-linux-2
