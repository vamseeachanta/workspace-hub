# Multi-Machine Setup

> Covers SSH helpers, hostname identity, and CLI consistency across dev-primary and dev-secondary.

## Path Differences Between Machines

| Machine | workspace-hub path |
|---|---|
| dev-primary | `/mnt/local-analysis/workspace-hub` |
| dev-secondary | `/mnt/workspace-hub` |

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
| `ace1` | SSH to dev-primary as `$ACE_SSH_USER` (default: vamsee) |
| `ace2` | SSH to dev-secondary as `$ACE_SSH_USER` |
| `ace1-tmux` | SSH to dev-primary and attach/create tmux session `main` |
| `ace2-tmux` | SSH to dev-secondary and attach/create tmux session `main` |
| `whoami-machine` | Print hostname, LAN IP, and Tailscale IP |

Override the SSH user without editing the script:

```bash
export ACE_SSH_USER=yourname
```

## Recommended .bashrc Additions

```bash
# 1. Source SSH helpers (path-safe)
_WH_PATH="/mnt/local-analysis/workspace-hub"          # dev-primary
# _WH_PATH="/mnt/workspace-hub"                        # dev-secondary
[[ -f "${_WH_PATH}/scripts/operations/system/ssh-helpers.sh" ]] && \
    source "${_WH_PATH}/scripts/operations/system/ssh-helpers.sh"

# 2. Confirm machine on new shell open
echo "Machine: $(hostname) | $(hostname -I | awk '{print $1}')"
```

## Claude Code Statusline

`.claude/statusline-command.sh` now prepends `[hostname]` to every status line:

```
[dev-primary] Claude  workspace-hub  main  WRK:3p/1w/0b  ...
[dev-secondary] Claude  workspace-hub  main  WRK:3p/1w/0b  ...
```

No configuration required — `hostname -s` is read at runtime.

## Machine Audit Table

| Item | dev-primary | dev-secondary | Status |
|---|---|---|---|
| workspace-hub path | `/mnt/local-analysis/workspace-hub` | `/mnt/workspace-hub` | Diverged — standardise or symlink |
| Tailscale IP | 10.1.0.1 | 10.1.0.2 | OK |
| uv installed | Yes | TBD | Verify on dev-secondary |
| Claude CLI | Yes | TBD | Verify on dev-secondary |
| Codex CLI | Yes | TBD | Verify on dev-secondary |
| Gemini CLI | TBD | TBD | Audit both |
| tmux config | TBD | TBD | Sync ~/.tmux.conf |
| .bashrc aliases | TBD | TBD | Diff and sync |
| SSH keys (bidirectional) | TBD | TBD | See WRK-295 |

## Related Work Items

- WRK-295 — Bidirectional SSH key auth (foundation)
- WRK-296 — Tailscale on dev-secondary (foundation)
- WRK-297 — SSHFS mounts dev-primary to dev-secondary
- WRK-307 — KVM display fix dev-secondary
- WRK-308 — Remote desktop dev-secondary
