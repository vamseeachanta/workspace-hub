---
name: crossprovider codex sandbox-writable-root-claim-vs-actual
description: Sandbox writable-root claim vs. actual
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [sandbox, workspace-write, permissions]
---

A session claiming `workspace-write` mode may not have `/mnt/local-analysis/llm-wiki` in its actual `writable_roots` list. Test `test -w /path` before bulk edits; mismatches surface as read-only errors partway through. Codex sessions especially: verify write access empirically, not by mode name.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
