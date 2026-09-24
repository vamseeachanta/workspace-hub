---
name: crossprovider codex tool-availability-in-non-standard-user-paths-req
description: Tool availability in non-standard user paths requires fallback discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [portability, tooling, shell-patterns]
---

CLI tools installed via `npm install -g` may not appear in PATH but instead in `~/.npm-global/bin/`. Checking multiple known locations (PATH first, then user-local paths) provides better user experience than failing immediately when a tool isn't in standard locations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
