---
name: crossprovider codex yaml-validation-architecture-differs-between-aud
description: YAML validation architecture differs between audit and enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml-parsing, validation, architecture]
---

Audit-oriented frontmatter parsers return None on failure and exclude paths by policy; enforcement requires strict YAML parsing and comprehensive coverage including archived/diverged paths. Shell/grep validation is insufficient for strict YAML compliance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
