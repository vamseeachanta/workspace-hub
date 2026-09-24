---
name: crossprovider codex validator-self-blocking-requires-narrow-sentinel
description: Validator self-blocking requires narrow sentinels, not blanket exemptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, enforcement, self-scan]
---

Enforcement scripts that scan their own artifacts must use per-line sentinels (matching prior art like check-no-conflict-markers.sh) or path-restricted whole-file allowlists, never blanket file exemptions. Blanket exempts are backdoors that defeat the scan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
