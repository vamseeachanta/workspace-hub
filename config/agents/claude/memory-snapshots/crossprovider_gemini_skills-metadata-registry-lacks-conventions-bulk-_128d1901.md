---
name: crossprovider gemini skills-metadata-registry-lacks-conventions-bulk-
description: Skills metadata registry lacks conventions; bulk automation requires audit first
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skills-management, metadata, automation, schema-risk]
---

Current 468 skills have inconsistent frontmatter (missing 'capabilities', 'requires', 'canonical_ref' fields). Automation for generating a central skills graph and fixing 115 diverged symlinks is feasible but depends on establishing metadata conventions first. Sequencing risk: automation may encode inconsistent schema if audit is skipped.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
