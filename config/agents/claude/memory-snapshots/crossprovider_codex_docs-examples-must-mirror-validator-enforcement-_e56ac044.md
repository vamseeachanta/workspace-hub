---
name: crossprovider codex docs-examples-must-mirror-validator-enforcement-
description: Docs examples must mirror validator enforcement scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [docs, consistency]
---

Shell snippets in governance docs should include private-path markers (`/mnt/ace`, `/mnt/ace-data`) that the validator enforces. Inconsistency between documented examples and validation logic creates drift and confusion about what is actually allowed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
