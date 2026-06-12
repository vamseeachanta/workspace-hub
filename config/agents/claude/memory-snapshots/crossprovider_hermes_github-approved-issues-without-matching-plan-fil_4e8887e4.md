---
name: crossprovider hermes github-approved-issues-without-matching-plan-fil
description: GitHub-approved issues without matching plan files indicate drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-drift, plan-workflow, issue-execution]
---

Issues with local approval markers or GitHub status:plan-approved label but no corresponding `docs/plans/*` file represent governance drift. Do not execute until plan file exists and matches the approval status. Check both filesystem and GitHub before starting work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
