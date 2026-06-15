---
name: crossprovider codex tests-encode-happy-path-only-miss-failure-modes-
description: Tests encode happy path only, miss failure modes and negative cases
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, test-adequacy, negative-testing]
---

Manifest test suites pass even when malformed rows go undetected (e.g., a promoted support-asset row with candidate extraction_status). Tests need explicit negative fixtures: rows with ONE defect (missing extraction_status, wrong page_disposition, etc.) that MUST fail the gate. The test passing is not proof the gate is correct.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
