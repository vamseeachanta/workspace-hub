---
name: crossprovider codex pre-commit-verification-gates-frontmatter-confli
description: Pre-commit verification gates: frontmatter + conflict-markers + diff-check
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [quality-gate, commit-verification, ingest-workflow]
---

Before committing ingest work, run: frontmatter/link probe, check-no-conflict-markers.sh, and git diff --check. These three gates catch common integration errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
