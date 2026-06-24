---
name: crossprovider codex real-git-untracked-existing-file-validation-inco
description: Real-git untracked existing-file validation incomplete in test seams
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [tdd-testability, git-safety, llm-wiki-dnv]
---

Sessions #759–#763 note existing tests cover the positive case (file is tracked via `git ls-files`) but not the negative: a file that exists on disk but is untracked. This gate prevents accidentally re-writing untracked local content. Add an explicit RED test that verifies untracked existing files are rejected and not clobbered.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
