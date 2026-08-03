---
name: crossprovider codex systematic-leak-scope-across-9-writers-not-isola
description: Systematic leak scope across 9 writers, not isolated
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [privacy, audit, dispatch]
---

Dispatch title leak (PR #95a10b5) fixes 1 of 9 writers; kanban boards hold the largest exposure (115 tracked files, 5,578 titles, 1,531 body excerpts). Fixing one writer creates false confidence that the surface is clean. Requires systematic audit of all 9 vectors before claiming control.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
