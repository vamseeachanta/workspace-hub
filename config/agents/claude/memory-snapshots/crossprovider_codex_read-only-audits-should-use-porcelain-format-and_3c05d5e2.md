---
name: crossprovider codex read-only-audits-should-use-porcelain-format-and
description: Read-only audits should use porcelain format and abstract file paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [audit, privacy, git-tooling, reporting]
---

Avoid exposing raw file lists and private content in audit summaries. Use porcelain output formats (`git status --porcelain`, `git diff --name-only`) with aggregated counts instead of full paths. This keeps audits informative without leaking sensitive data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
