---
name: crossprovider codex past-tense-drift-in-plans-signals-unshipped-arti
description: Past-tense drift in plans signals unshipped artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, artifact-verification, defect-pattern]
---

Plans frequently claim artifacts are 'removed', 'added', 'created', or 'committed' when git shows they don't exist at the cited commit. Verify every past-tense claim with `git show HEAD:<path>` or `git ls-files` before accepting it as fact; unverified past-tense claims are correctness defects, not optimistic phrasing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
