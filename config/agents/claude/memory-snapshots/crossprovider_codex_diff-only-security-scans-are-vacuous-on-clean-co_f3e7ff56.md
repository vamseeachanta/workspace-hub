---
name: crossprovider codex diff-only-security-scans-are-vacuous-on-clean-co
description: Diff-only security scans are vacuous on clean committed branches
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security-gate, diff-only-scans, false-confidence, vacuous-passes]
---

Security gates using `--diff-only` scan zero files when run on a clean committed PR (no working-tree changes), producing a vacuous PASS. llm-wiki PR #682: PR body cited `--diff-only legal scan: PASS` but the script scanned zero files. Full repo scans may reveal unrelated pre-existing baseline violations. PR evidence claims should be independently re-executed, not trusted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
