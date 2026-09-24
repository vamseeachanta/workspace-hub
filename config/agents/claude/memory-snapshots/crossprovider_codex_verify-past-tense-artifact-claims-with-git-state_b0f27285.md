---
name: crossprovider codex verify-past-tense-artifact-claims-with-git-state
description: Verify past-tense artifact claims with git state before trusting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, artifact-verification, past-tense-audit]
---

Plans frequently claim things 'have been removed', 'exist', or 'have been wired' in past tense, but repo state at the cited commit often contradicts this. Always inspect actual file presence, event fields, and commit diffs rather than accepting plan prose. Non-existent files, missing event fields, and changes not present in the commit are MAJOR defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
