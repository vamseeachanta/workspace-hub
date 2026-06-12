---
name: crossprovider hermes legal-sanity-scan-is-a-hard-commit-gate-on-plann
description: Legal sanity scan is a hard commit gate on planning artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, commit-gate, credentials, legal-scan]
---

Before `git add` on `.planning/plan-approved/<n>.md` or review synthesis files, run credential scanner for secrets/tokens. Commit is blocked if scan fails; must show clear `[REDACTED]` placeholders.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
