---
name: crossprovider codex readback-recall-system-does-not-consume-captured
description: Readback/recall system does not consume captured learnings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [memory-system, architecture, cross-provider]
---

Learnings are captured into snapshots (4,621 Codex entries, etc.) but recall.py searches only `.claude/memory/topics/` (empty). No observable route from distilled learnings back into retrieval. Indexing route must be established and tested before capture-only deployments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
