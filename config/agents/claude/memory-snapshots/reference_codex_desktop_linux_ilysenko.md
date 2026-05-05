---
name: Codex Desktop on Linux
description: Install OpenAI Codex Desktop on Linux via the ilysenko/codex-desktop-linux community wrapper, with disk-redirect tactics and CLI-shadow guarantees
type: reference
originSessionId: 5d5914b5-3c59-4241-936e-bfdb6458d108
---
# Codex Desktop on Linux — install reference

OpenAI ships Codex Desktop only for macOS and Windows. Linux install path is the community wrapper `ilysenko/codex-desktop-linux`, which downloads OpenAI's official macOS DMG from `https://persistent.oaistatic.com/codex-app-prod/Codex.dmg` (their CDN), extracts it with 7z, rebuilds native modules, and wraps in Electron.

## Pattern parallels Claude Desktop

This is the exact same pattern as `aaddrick/claude-desktop-debian` (`reference_claude_desktop_linux_aaddrick.md`): community Linux wrapper for an officially-Mac/Windows-only Electron app, repackaging the official binary.

## Disk-redirect tactics (verified 2026-05-03 ace-linux-1)

The `install-deps.sh` script hardcodes `source "$HOME/.cargo/env"`, so `RUSTUP_HOME`/`CARGO_HOME` env vars alone don't redirect cleanly. The working approach:

1. Pre-create build root on a non-`/` mount with ≥3GB free (e.g., `/mnt/ace/build/codex-desktop/` on ext4).
2. Symlink before any rust step:
   ```
   ln -s /mnt/ace/build/codex-desktop/.cargo $HOME/.cargo
   ln -s /mnt/ace/build/codex-desktop/.rustup $HOME/.rustup
   ```
3. Set `npm_config_cache=/mnt/ace/build/codex-desktop/.npm-cache` for the build.
4. Skip `install-deps.sh` if all distro packages are already present — only `p7zip-full` was missing on a typical Ubuntu 24.04 dev box. Skipping avoids NodeSource key install and zenity helper install.

Disk footprint: rustup ~605MB, electron+node_modules ~500MB, cargo target ~1GB, DMG ~150MB. Build dir ~3GB total.

## Build-then-install sequence

```bash
git clone --depth 1 https://github.com/ilysenko/codex-desktop-linux.git /mnt/ace/build/codex-desktop/repo
cd /mnt/ace/build/codex-desktop/repo
# (after symlinks + p7zip-full + rustup minimal stable)
export PATH="$HOME/.cargo/bin:$PATH"
export npm_config_cache=/mnt/ace/build/codex-desktop/.npm-cache
make build-app   # 3-5 min: DMG fetch + extract + patch + electron install + rust update-manager build
make package     # produces dist/codex-desktop_<timestamp>_amd64.deb (~220MB)
sudo dpkg -i dist/codex-desktop_*.deb
```

## CLI shadow guarantee

`codex-desktop` (Electron app) and `codex` (CLI) never collide:
- Desktop installs as `/usr/bin/codex-desktop` with bundled node at `/opt/codex-desktop/resources/node-runtime/`.
- CLI stays at wherever npm-global installed it (e.g., `~/.npm-global/bin/codex`).
- Verify after install: `which codex codex-desktop && codex --version`.

## Update manager (opt-in)

`/usr/lib/systemd/user/codex-update-manager.service` is installed but NOT enabled. To turn on auto-rebuild when OpenAI ships a new DMG: `systemctl --user enable --now codex-update-manager`. Otherwise rebuild manually with `make update` from the repo dir.

## Reusable artifacts

After install, `/mnt/ace/build/codex-desktop/repo/` (~3GB) is optional to keep. Delete to reclaim, or retain for future `make update` rebuilds without re-cloning.

## Skipped steps that the README recommends

- `install-deps.sh` — unnecessary when distro packages already present (build-essential, curl, unzip, python3, dpkg-dev, zenity all standard on Ubuntu 24.04 dev boxes).
- `bootstrap_7zz` — system 7z 23.01 from `p7zip-full` is new enough; the script self-detects this and skips.
- `make service-enable` — leave update-manager off unless you want auto-updates.
