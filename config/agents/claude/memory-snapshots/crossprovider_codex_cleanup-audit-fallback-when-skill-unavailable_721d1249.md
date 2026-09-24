---
name: crossprovider codex cleanup-audit-fallback-when-skill-unavailable
description: Cleanup audit fallback when skill unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, tooling-gaps, audit, fallback]
---

When configured cleanup-audit skill is absent from a checkout, apply the audit intent manually: VCS residue, ignored/scratch files, and lock artifacts. This enables defensive cleanup verification when local tooling is missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
