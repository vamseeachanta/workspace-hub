---
name: crossprovider codex raw-private-alias-root-rejection-needs-concrete-
description: Raw/private alias-root rejection needs concrete safe allowlist or deny-list fixture
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [security-validation, alias-root-control, llm-wiki-dnv]
---

Sessions #759, #760, #762, #763 found plans forbid using the DNV source manifest as implementation input but require alias-root rejection without naming a forbidden-root catalog. Current validator accepts any regex-valid root (dnv_batch_page_updates.py:125). A narrow literal-root test can pass while unsafe roots remain accepted. Provide a concrete allowlist/denylist source for the RED test—e.g., a fixture that specifies allowed source-root patterns or a guard against common private paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
