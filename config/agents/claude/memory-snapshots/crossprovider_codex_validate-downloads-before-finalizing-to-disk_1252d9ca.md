---
name: crossprovider codex validate-downloads-before-finalizing-to-disk
description: Validate downloads before finalizing to disk
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [network-io, error-handling, issue-265]
---

Writing HTTP response to disk before validating content-type/size/checksum leaves partial files if validation fails. Issue #265: download_static_candidates() wrote response, renamed, then validated, allowing failures to leave orphaned files. Validate first, write/rename second.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
