---
name: crossprovider hermes git-diff-omits-untracked-artifacts-in-code-revie
description: git diff omits untracked artifacts in code reviews
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, review, artifacts]
---

`git diff --name-only` skips untracked files, causing cross-provider code reviews (Codex/Gemini) to miss generated Word/PDF/HTML artifacts. Use `git diff --others --name-only` or explicit file enumeration to surface untracked outputs for review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
