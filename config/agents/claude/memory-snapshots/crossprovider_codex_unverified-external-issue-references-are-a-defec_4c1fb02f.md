---
name: crossprovider codex unverified-external-issue-references-are-a-defec
description: Unverified external issue references are a defect class in plan scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, scope-control, evidence]
---

Plans that cite other issues' bodies, comments, or existence without attesting that content (via `gh issue view --json` or similar) fail review. If scope depends on `vamseeachanta/sibling-repo#31`, the plan must include verified evidence that issue exists and its scope matches the boundary claim.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
