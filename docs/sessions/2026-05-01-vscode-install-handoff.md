# VS Code .deb install — handoff

**Date:** 2026-05-01
**Machine:** ace-linux-1 (`/mnt/local-analysis/workspace-hub`)
**Status:** ⏸ paused — awaiting interactive sudo

## Artifact

- File: `/home/vamsee/Downloads/code_1.118.1-1777474985_amd64.deb`
- Size: 142 MB
- Verified present: 2026-05-01

## Install command (run in terminal — needs sudo TTY)

```bash
sudo apt install -y /home/vamsee/Downloads/code_1.118.1-1777474985_amd64.deb
```

Equivalently from inside a Claude Code session:

```
!sudo apt install -y /home/vamsee/Downloads/code_1.118.1-1777474985_amd64.deb
```

## Why this couldn't complete in-session

Claude Code's Bash tool runs without a TTY, so `sudo` cannot prompt for the password. The first attempt errored with:

> sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper

`apt` was chosen over `dpkg -i` so dependency resolution happens automatically.

## Post-install verification

```bash
code --version
dpkg -l code | tail -1
ls /etc/apt/sources.list.d/vscode.list   # confirm Microsoft repo registered for future upgrades
```

## Cleanup (optional, after successful install)

```bash
rm /home/vamsee/Downloads/code_1.118.1-1777474985_amd64.deb
```

Future updates flow through `apt upgrade` once the Microsoft repo is registered — no need to re-download .debs.
