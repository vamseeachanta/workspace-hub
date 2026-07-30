---
name: crossprovider codex out-of-scope-files-in-secure-commits-bypass-revi
description: Out-of-scope files in secure commits bypass review gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-workflow, security, commit-scope]
---

Accidentally staging residue files (reports, temp state, debug artifacts) outside the intended pathspec skips required review and can leak information. Use `git rm --cached` to untrack locally while preserving the file, or explicitly filter commit contents before staging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
