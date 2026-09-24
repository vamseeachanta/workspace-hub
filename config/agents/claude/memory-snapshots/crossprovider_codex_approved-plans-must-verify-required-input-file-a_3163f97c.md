---
name: crossprovider codex approved-plans-must-verify-required-input-file-a
description: Approved plans must verify required input file availability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, execution, blocking-patterns]
---

Plans reference required execution inputs (e.g., index.jsonl) that may not be checked in to the worktree. Execution then stalls with no clear fallback. Plans should either verify inputs are accessible, document reconstruction/sharding fallbacks explicitly, or flag data dependencies before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
