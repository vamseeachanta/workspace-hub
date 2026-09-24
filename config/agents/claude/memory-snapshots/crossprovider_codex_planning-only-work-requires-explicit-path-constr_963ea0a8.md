---
name: crossprovider codex planning-only-work-requires-explicit-path-constr
description: Planning-only work requires explicit path-constraint enforcement: document forbidden writes and validate staged diff
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance-workflow, scope-constraint, approval-gates]
---

Constrained planning-only runs (e.g., dossier preparation without code edits) must document which paths are owned (allowed writes) and which are forbidden (scripts/**, tests/**, config/**, .claude/**). Before commit, validate that `git status` and the staged diff include only owned paths, catching accidental out-of-scope edits. This is a governance pattern to preserve approval-gate clarity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
