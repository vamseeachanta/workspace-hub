---
name: crossprovider codex use-diff-only-for-legal-audit-scans-in-review-wo
description: Use --diff-only for legal/audit scans in review workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-workflow, scoping, tooling]
---

Repo-wide legal scans generate thousands of pre-existing violations, drowning review findings in noise. Using `--diff-only` scopes output to staged/reviewed changes only and makes violations actionable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
