---
name: crossprovider hermes stale-artifact-publication-breaks-reviewer-trust
description: Stale artifact publication breaks reviewer trust
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-reports, artifact-management, code-review]
---

When code implementation changes significantly (e.g., adding hull-current loads to a rudder-only report), regenerated artifacts must be committed or explicitly removed. Checked-in stale artifacts create confusion: reviewers see outdated scope/titles in HTML/MD while code now does something different. Regenerate and commit-as-one, or block publication until artifacts match implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
