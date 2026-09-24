---
name: crossprovider codex completeness-gates-split-pure-scoring-from-repo-
description: Completeness gates split pure scoring from repo integration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, portability, workflow]
---

Completeness scoring logic (pure function over artifact metadata) can be ported across repos, but completeness gates also depend on GitHub issue/workflow/label integration specific to the host repo. Portability requires separating those concerns; the pure function can be reused but the gate integration is repo-specific.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
