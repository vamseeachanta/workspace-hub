---
name: crossprovider codex public-safe-governance-artifact-layout-docs-gove
description: Public-safe governance artifact layout: docs/governance/ + docs/plans/
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, governance, data-handling, repo-structure]
---

Store durable clearance checklists, input-readiness templates, and data-governance rules under `docs/governance/`. Keep corresponding execution plans under `docs/plans/`. This separation keeps policy artifacts stable while plans remain implementation-gated. Non-overlapping filenames allow safe batching across multiple governance issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
