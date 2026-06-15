---
name: crossprovider codex scope-tests-using-final-file-state-are-unreliabl
description: Scope tests using final file state are unreliable
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, scope-validation, pytest]
---

Assertions based on final file existence cannot prove which issue created a file (collisions across issues). Use deterministic `git diff --name-only <base>...HEAD` validation against explicit forbidden paths instead of pytest assertions on final state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
