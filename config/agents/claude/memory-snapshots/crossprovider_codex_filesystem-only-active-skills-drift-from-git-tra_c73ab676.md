---
name: crossprovider codex filesystem-only-active-skills-drift-from-git-tra
description: Filesystem-only active skills drift from git tracking, creating loss risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skills-system, inventory-drift, operational-hazard]
---

Skills can exist on disk but not tracked in git (observed: 6 active, 72 total untracked as of 2026-04-25). Weekly audit detects this divergence but does not reconcile. Cleanup sweeps, tooling migrations, or changes to the skills curation script risk silent loss of untracked active skills. Any skills system work must account for this drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
