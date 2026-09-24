---
name: crossprovider codex registry-and-file-tree-cleanup-are-orthogonal-co
description: Registry and file-tree cleanup are orthogonal concerns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dedup, registry, skills]
---

Skill deduplication involves both .claude/skills/ tree cleanup AND .claude/agent-skills-map.yaml registry updates. These require separate verification passes; cleanup of one does not cover the other.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
