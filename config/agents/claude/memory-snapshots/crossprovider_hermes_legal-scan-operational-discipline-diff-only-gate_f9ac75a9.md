---
name: crossprovider hermes legal-scan-operational-discipline-diff-only-gate
description: Legal scan operational discipline: diff-only gate vs baseline violations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [compliance, legal-scan, diff-only, baseline]
---

Full repo legal scans show pre-existing violations that are non-blocking baseline context. Actual compliance gate is `--diff-only` scan on changed files only. Full-repo green claim is invalid; baseline violations are load-bearing and must be tracked separately from new-code violations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
