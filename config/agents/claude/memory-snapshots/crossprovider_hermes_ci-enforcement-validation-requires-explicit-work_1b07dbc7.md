---
name: crossprovider hermes ci-enforcement-validation-requires-explicit-work
description: CI enforcement validation requires explicit workflow binding
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-cd, enforcement-gates, workflows]
---

Plans that specify verification commands (e.g., 'run pre-commit --all-files') often fail to bind them to named GitHub Actions workflows. Path-filter gaps (docs.yml only watching docs/api) are common omissions. Verification must explicitly name the workflow and matrix row, not remain local-only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
