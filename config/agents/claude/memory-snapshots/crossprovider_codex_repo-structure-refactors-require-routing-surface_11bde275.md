---
name: crossprovider codex repo-structure-refactors-require-routing-surface
description: Repo-structure refactors require routing-surface audits before approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [repo-structure, refactoring, impact-analysis]
---

Large file-move refactors must verify all import/reference maps (operator-maps, routing registries, CI artifact contracts) won't break; changes to `.gitignore` can hide tracked files requiring explicit `git rm --cached` decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
