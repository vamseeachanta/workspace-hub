---
name: crossprovider hermes orphan-list-truncation-creates-silent-clarity-lo
description: Orphan-list truncation creates silent clarity loss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, reporting, summary, clarity]
---

Summary schema may cap orphan/unresolved lists to 100 entries but actual counts can exceed that. Report text claiming "showing 25 of 100" is misleading if true orphan count is 150+. Validator should emit warning when `actual_count > report_limit` so truncation is explicit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
