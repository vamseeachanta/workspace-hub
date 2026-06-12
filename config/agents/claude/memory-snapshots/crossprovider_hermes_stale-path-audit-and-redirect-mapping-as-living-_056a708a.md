---
name: crossprovider hermes stale-path-audit-and-redirect-mapping-as-living-
description: Stale path audit and redirect mapping as living docs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [migration, documentation, architecture-drift]
---

When architecture migrates (e.g., work-queue scripts → GitHub issues + hooks), maintain a canonical redirect map documenting old-path → new-equivalents with explicit rationale (why no 1:1 replacement exists, what conceptual shift occurred). This guides documentation updates and tooling migrations across the repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
