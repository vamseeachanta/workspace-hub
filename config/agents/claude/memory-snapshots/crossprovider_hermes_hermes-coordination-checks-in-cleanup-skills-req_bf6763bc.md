---
name: crossprovider hermes hermes-coordination-checks-in-cleanup-skills-req
description: Hermes coordination checks in cleanup skills require run manifests, not just pgrep
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [disk-safety, hermes-coordination, infrastructure]
---

When reviewing cleanup routines that operate on shared Hermes directories (e.g., /mnt/local-analysis/codex-burn-YYYYMMDD/), verifying 'no active Hermes lanes' via `pgrep -af hermes` is insufficient — need explicit run manifests (.md, .json), session/PID/status files, and lane paths, because Hermes may create multiple launches per day in the same dated dir and `pgrep` shows only the parent agent, not active child lanes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
