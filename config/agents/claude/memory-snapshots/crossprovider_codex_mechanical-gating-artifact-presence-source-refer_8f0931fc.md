---
name: crossprovider codex mechanical-gating-artifact-presence-source-refer
description: Mechanical gating: artifact presence + source reference, not just labels
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [dependency-gating, governance]
---

Plans that depend on upstream work must verify the upstream artifact exists and is referenced with `source_issue:` or equivalent. Label checks alone miss cases where upstream labels changed but artifacts were never created.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
