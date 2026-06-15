---
name: crossprovider codex committed-json-html-report-contracts-must-match-
description: Committed JSON/HTML report contracts must match emitted fields
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-validation, report-contracts]
---

Report generators must not emit fields they claim don't exist (e.g., `private_visibility_recorded: false` while emitting `visibility_alias: "private-metadata-only"`). The contract—what the report claims it contains—must exactly match the JSON schema; add a test that verifies committed reports match generator output byte-for-byte.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
