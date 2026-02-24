# New-Machine Setup Guide

> **WRK-313** | Created: 2026-02-24 | Status: active
> Platform: Linux (primary) + Windows Git Bash / MINGW64 (secondary)

## Quick Start

```bash
git clone git@github.com:<org>/workspace-hub.git /mnt/local-analysis/workspace-hub
cd /mnt/local-analysis/workspace-hub
bash scripts/setup/new-machine-setup.sh
source ~/.bashrc
bash scripts/setup/verify-setup.sh
```

---

## Components

### 1. Git Hooks (WRK-312)

Hooks live in `scripts/hooks/` and are copied to `.git/hooks/` by the installer.

| Hook | Purpose |
|------|---------|
| `pre-commit` | Legal scan + encoding check before every commit |
| `post-merge` | Re-runs `install-all-hooks.sh --quiet` after `git pull` |
| `post-rewrite` | Same as post-merge — triggered by `git rebase` |

**Install:**
```bash
bash scripts/setup/install-all-hooks.sh
```

**Verify:** `ls -la .git/hooks/pre-commit .git/hooks/post-merge .git/hooks/post-rewrite`

The `post-merge` hook means subsequent `git pull` operations automatically
keep hooks up to date — no manual reinstall needed after hook changes land.

---

### 2. Claude Statusline

Statusline shows the current model, token usage, and session state in the
terminal status bar (iTerm2, Windows Terminal, Warp, or any OSC-compatible
terminal).

**Enable via CLI:**
```bash
claude config set statusBarEnabled true
```

**Or via settings file** (`~/.claude/settings.json`):
```json
{
  "statusBarEnabled": true
}
```

The bootstrap script handles this automatically.  Toggle off with:
```bash
claude config set statusBarEnabled false
```

---

### 3. Shell Aliases + Prompt

Source file: `config/shell/bashrc-snippets.sh`

Add to `~/.bashrc` (Linux) or `~/.bash_profile` (Windows Git Bash):
```bash
source "/mnt/local-analysis/workspace-hub/config/shell/bashrc-snippets.sh"
```

The bootstrap script appends this line automatically.

**Available aliases after sourcing:**

| Alias | Expands to |
|-------|-----------|
| `ws` | `cd $WORKSPACE_HUB` |
| `wrk` | `bash $WORKSPACE_HUB/scripts/work-queue/queue-status.sh` |
| `wh-verify` | `bash $WORKSPACE_HUB/scripts/setup/verify-setup.sh` |
| `wh-legal` | `bash $WORKSPACE_HUB/scripts/legal/legal-sanity-scan.sh --diff-only` |
| `wh-ready` | `bash $WORKSPACE_HUB/scripts/readiness/nightly-readiness.sh` |

**Shell prompt** (PS1) shows `branch|WRK-NNN` from the last commit message.
Disabled automatically when Starship or oh-my-bash is detected.

---

### 4. PATH Setup

| Platform | Tool | Path |
|----------|------|------|
| Linux | npm global (`claude`, `codex`) | `~/.npm-global/bin` |
| Linux | pip `--user` installs | `~/.local/bin` |
| Windows Git Bash | npm global | managed by Git Bash — no action needed |

Set npm prefix (Linux one-time):
```bash
npm config set prefix ~/.npm-global
```

The snippets file adds `~/.npm-global/bin` and `~/.local/bin` to `PATH`
automatically when sourced.

---

### 5. Cron Jobs

#### Machine Roles

| Hostname | Role | Variant |
|----------|------|---------|
| `ace-linux-1` | Nightly pipeline host | `full` |
| `ace-linux-2` | Contributing machine | `contribute` |
| `ACMA-ANSYS05` | Windows dev workstation | `contribute-minimal` |
| `acma-ws014` | Windows dev workstation | `contribute-minimal` |
| other | Default | `contribute` |

#### Install (Linux)

```bash
bash scripts/cron/setup-cron.sh
```

Dry-run preview: `bash scripts/cron/setup-cron.sh --dry-run`

#### Full Schedule (ace-linux-1 only)

| Time | Schedule | Script |
|------|----------|--------|
| 02:00 daily | `0 2 * * *` | `comprehensive-learning-nightly.sh` |
| 03:00 daily | `0 3 * * *` | `session-analysis-nightly.sh` |
| 03:30 Sunday | `30 3 * * 0` | `update-model-ids.sh` |
| 04:00 Monday | `0 4 * * 1` | `skills-curation.sh` |
| Every 4h | `0 */4 * * *` | `repository-sync-auto` |

Reference: `scripts/cron/crontab-template.sh`

#### Windows Task Scheduler (contribute-minimal)

Two tasks required — see `scripts/cron/crontab-template.sh` for the exact
arguments.  `setup-cron.sh` prints the instructions when run on Windows.

---

### 6. SSH Key Setup

Required for `rsync` between machines (ace-linux-1 pulls sessions from others).

```bash
ssh-keygen -t ed25519 -C "$(hostname)"
ssh-copy-id vamsee@ace-linux-1         # office → home/lab (requires Tailscale)
```

**Cross-network:** office (192.168.0.x) and home/lab (192.168.1.x) are
isolated. Tailscale must be running for SSH between networks.
See `config/tabby/` for Tailscale configuration.

---

### 7. Environment Variables

Copy `.env.example` to `.env` and fill in secrets:
```bash
cp .env.example .env
# edit .env — never commit it
```

Required variables are listed in `.env.example`.  Secrets are validated at
session start by `scripts/readiness/ai-agent-readiness.sh` (check R-AI-CLI).

---

### 8. Submodule Initialisation

After cloning, initialise all submodules:
```bash
git submodule update --init --recursive
```

The bootstrap script does this automatically.

---

## Machine Inventory

| Machine | OS | Network | Role |
|---------|-----|---------|------|
| ACMA-ANSYS05 | Windows / MINGW64 | 192.168.0.x (office) | Dev workstation |
| acma-ws014 | Windows / MINGW64 | 192.168.0.x (office) | Dev workstation |
| ace-linux-1 | Linux | 192.168.1.x (home/lab) | Nightly cron host |
| ace-linux-2 | Linux | 192.168.1.x (home/lab) | Contributing machine |

---

## Verification

After setup, run the full verification report:

```bash
bash scripts/setup/verify-setup.sh
```

With strict mode (fails if any FAIL):
```bash
bash scripts/setup/verify-setup.sh --strict
```

Checks performed: git repo, submodules, hooks (pre-commit/post-merge/post-rewrite),
claude CLI, codex/gemini CLIs, bashrc-snippets sourced, statusBarEnabled,
crontab entries, SSH key, env vars, Python + PyYAML.

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/setup/new-machine-setup.sh` | Master bootstrap script |
| `scripts/setup/install-all-hooks.sh` | Git hook installer (WRK-312) |
| `scripts/setup/verify-setup.sh` | Post-setup health check |
| `scripts/cron/setup-cron.sh` | Crontab installer |
| `scripts/cron/crontab-template.sh` | Canonical cron schedule reference |
| `config/shell/bashrc-snippets.sh` | Shell aliases + PS1 prompt |
| `.claude/docs/new-machine-setup.md` | This document |

---

## Windows Git Bash Notes

- Always use Git Bash (MINGW64) — do NOT use PowerShell for these scripts
- Line endings: `core.autocrlf=input` is enforced via `.gitattributes`
- The bashrc-snippets file sets `GIT_CONFIG_PARAMETERS` to enforce LF
- Default workspace path example: `D:/workspace-hub` — adjust alias in
  `config/shell/bashrc-snippets.sh` to match your drive

---

## Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| `post-merge` re-installs hooks | Hooks stay current automatically after every `git pull`; no manual step needed |
| `statusBarEnabled` via settings.json fallback | `claude config set` requires an active session; JSON write works on fresh installs |
| npm prefix `~/.npm-global` | Avoids `sudo npm install -g`; keeps global CLIs in user space |
| Idempotent setup script | Safe to re-run after rebuild; no side effects on configured machines |
| Aliases use `$WORKSPACE_HUB` var | Works even if workspace is not at the default Linux path |
| `verify-setup.sh` separate from `new-machine-setup.sh` | Allows validation-only runs and CI integration without re-running setup |
