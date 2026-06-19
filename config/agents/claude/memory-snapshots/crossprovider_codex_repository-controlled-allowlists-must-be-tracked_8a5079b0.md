---
name: crossprovider codex repository-controlled-allowlists-must-be-tracked
description: Repository-controlled allowlists must be tracked files, not mutable issue text
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [configuration, governance, vcs]
---

When a plan depends on "labels already present in the issue," it reads a non-code-reviewed, mutable source. Instead, track allowlists in .yml/.json with explicit approval gates. Observed in llm-wiki #733 — plan depending on issue-body text for subfolder routing policy, which can drift without review or audit trail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
