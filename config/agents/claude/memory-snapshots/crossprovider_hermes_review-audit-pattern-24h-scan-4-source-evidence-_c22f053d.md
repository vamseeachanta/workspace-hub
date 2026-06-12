---
name: crossprovider hermes review-audit-pattern-24h-scan-4-source-evidence-
description: Review audit pattern: 24h scan + 4-source evidence check + GitHub issue creation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-enforcement, audit-pattern, github-automation]
---

Audit recent commits by conventional prefix (feat/fix/perf need review; chore/docs/test/ci skip). Check 4 evidence sources: review results dir, .planning/*/REVIEWS.md, .claude/reports/*review*, git commit keywords. Create GitHub issue if compliance <80% listing unreviewed commits. Pair with daily morning review-backlog session.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
