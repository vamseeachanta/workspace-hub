---
name: reference-claude-desktop-install-state
description: "Claude Desktop on ace-linux-1 = official dpkg 1.17377.0, pristine; old patched \"Frame Fix\" build already replaced"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 90151f0f-ec1e-4f2d-9bc5-13532692b1a7
---

On ace-linux-1 the installed Claude Desktop is the **official dpkg package `claude-desktop` 1.17377.0** (Maintainer: Anthropic PBC), at `/usr/lib/claude-desktop/` with `/usr/bin/claude-desktop` symlinked to it and an AppArmor profile at `/etc/apparmor.d/claude-desktop`. As of 2026-06-30 `dpkg -V claude-desktop` is empty → files are pristine/untampered.

Version gotcha: the `version` file in the app dir (`42.5.1`) is the bundled **Electron** runtime, NOT the app version. Real app version = the dpkg package version (`1.17377.0`).

History: a community/patched Linux build (`aaddrick/claude-desktop-debian` style) previously ran here — its "[Frame Fix]" launcher *replaced* `app.asar` at launch and ran Electron from `…/node_modules/electron/dist/`. That layout was **already overwritten** by the official `.deb` on 2026-06-29; no hacked binary remained. On 2026-06-30 I removed its two orphaned leftovers: `~/.cache/claude-desktop-debian/` (stale launcher.log) and `~/.config/Claude-3p/` (orphaned third-party config).

Still present (intentionally left): active config `~/.config/Claude/` contains a dangling `localAgentModeTrustedFolders` entry pointing at the old nonexistent path `…/node_modules/electron/dist/resources/app.asar` — inert (matches nothing), not yet cleaned.

How to re-verify install integrity: `dpkg -s claude-desktop` (version/status), `dpkg -V claude-desktop` (empty = pristine), `dpkg -L claude-desktop` (owned files). Linux "hacked" Claude builds are spotted by a patched/replaced `app.asar` or an Electron-in-`node_modules` launch layout vs the official single self-contained `claude-desktop` binary.
