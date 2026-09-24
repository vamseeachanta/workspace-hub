---
name: crossprovider codex file-format-changes-to-shared-automation-state-n
description: File format changes to shared automation state need coordinated audits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-automation, backwards-compatibility]
---

When changing formats of files read by multiple scripts (e.g., `active-wrk` from single-line to two-line), audit every consumer and update them together. Format changes without coordination cause silent breakage across the automation suite.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
