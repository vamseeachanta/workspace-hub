---
name: Claude Desktop on Linux — aaddrick build
description: Unofficial Linux Claude Desktop is at aaddrick/claude-desktop-debian; APT repo at pkg.claude-desktop-debian.dev (post-April-2026 migration)
type: reference
originSessionId: 18bce6d9-ceec-4424-a580-1ffee5eb430f
---
**Project:** `aaddrick/claude-desktop-debian` (Cloudflare Worker fronting GitHub Releases)

**Install paths:**
- Debian/Ubuntu: APT repo at `https://pkg.claude-desktop-debian.dev stable main`, signed by `/usr/share/keyrings/claude-desktop.gpg`
- Fedora/RHEL: DNF repo at same host
- Arch: AUR package `claude-desktop-appimage`
- NixOS: `nix profile install github:aaddrick/claude-desktop-debian`

**APT migration (April 2026):** old `aaddrick.github.io` URL fails on `apt update` (HTTPS scheme-downgrade rejection). Fix: `sed -i` rewrite of `sources.list.d/claude-desktop.list` to new host. DNF unaffected (follows redirect transparently).

**How it works:** maintainer extracts Windows `.nupkg`, swaps native modules for Linux equivalents, repacks as `.deb` / AppImage. Releases ride upstream Windows version + maintainer revision (e.g. `1.5354.0-2.0.8`).

**Trust note:** third-party (`aaddrick`), not Anthropic. Removable via `sudo apt remove claude-desktop && sudo rm /etc/apt/sources.list.d/claude-desktop.list /usr/share/keyrings/claude-desktop.gpg`.

**Verified working on:** ace-linux-1 (Ubuntu 24.04.4) at version `1.5354.0-2.0.8`, 2026-05-03.
