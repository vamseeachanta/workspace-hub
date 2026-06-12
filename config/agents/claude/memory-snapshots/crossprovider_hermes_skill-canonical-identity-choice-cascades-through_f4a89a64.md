---
name: crossprovider hermes skill-canonical-identity-choice-cascades-through
description: Skill canonical identity choice cascades through dedup and carry-forward
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [design, identity, canonicalization, architecture]
---

Choosing frontmatter `name` (vs. path vs. other fields) as canonical identity for skills is load-bearing: it governs duplicate detection, carry-forward matching, and reporting. This choice must be explicit and documented early; changing it later requires migration.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
