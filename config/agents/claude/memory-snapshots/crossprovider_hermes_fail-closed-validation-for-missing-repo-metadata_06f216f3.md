---
name: crossprovider hermes fail-closed-validation-for-missing-repo-metadata
description: Fail-closed validation for missing repo metadata
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, fail-closed, config-safety]
---

When validating required repos: fail-closed if upstream is missing (not just warn); optional repos may warn. For remote placement evidence, reject entries missing `code` or `message` fields as blocker-level issues instead of silently accepting underspecified dicts. Prevents silent configuration drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
