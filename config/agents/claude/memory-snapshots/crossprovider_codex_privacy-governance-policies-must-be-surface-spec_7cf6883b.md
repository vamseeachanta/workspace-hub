---
name: crossprovider codex privacy-governance-policies-must-be-surface-spec
description: Privacy/governance policies must be surface-specific, not blanket
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, privacy, policy-design, testing]
---

Rules like "no source labels" fail when the same label type is required in different surfaces (page frontmatter vs issue comment vs report). Define allowed fields per surface: frontmatter, generated section, JSON/HTML report, issue closeout. Blanket policy language creates testability gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
