---
name: crossprovider gemini iterative-edge-case-hardening-in-large-scale-ope
description: Iterative edge-case hardening in large-scale operations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [robustness, platform-hazards, migration-design]
---

WRK-188 migration plan evolved v1.5 → v1.7 → v1.9, each iteration catching platform hazards (case-folding, disk space, submodule status, Unicode normalization, control-char filenames). Silent failures in large operations are catastrophic; explicit edge-case handling is non-negotiable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
