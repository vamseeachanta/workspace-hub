---
name: crossprovider codex version-extraction-via-cli-parsing-is-brittle-pa
description: Version extraction via CLI parsing is brittle; package-manager JSON is more reliable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [version-management, package-managers, parsing]
---

Parsing `tool --version` output with regex is fragile (format varies, pre-release suffixes, metadata). Prefer package-manager snapshots: `npm list -g --json` for npm, `dpkg -l` for apt. However, substring matching (e.g., 'if package in key') can select wrong package if names collide; require exact package-name matching for determinism.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
