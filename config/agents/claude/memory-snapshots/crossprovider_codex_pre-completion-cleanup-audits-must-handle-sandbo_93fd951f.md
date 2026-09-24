---
name: crossprovider codex pre-completion-cleanup-audits-must-handle-sandbo
description: Pre-completion cleanup audits must handle sandboxed tool constraints
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-audit, sandboxing, tool-constraints]
---

Cleanup must use narrow tool calls (e.g., `rm file1 file2`) rather than broad patterns (`rm -rf dir/`) when running in sandboxed environments that may reject sweep commands. Audit residue by class (expected caches, scratch files, pre-existing dirty state) and document what remains preserved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
