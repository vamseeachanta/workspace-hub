---
name: crossprovider codex fixture-validation-tests-must-invoke-semantic-ve
description: Fixture validation tests must invoke semantic verifiers, not just schema validators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, validation, schema]
---

If a semantic correctness verifier exists (e.g., computing actual file hashes for checksums), the fixture test must call it explicitly via `assert_manifest_checksums_match_files(manifest)` in the fixture validation test. Schema validation alone proves format, not semantic correctness. Both gates must fire.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
