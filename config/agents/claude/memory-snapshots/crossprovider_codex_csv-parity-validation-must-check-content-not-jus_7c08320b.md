---
name: crossprovider codex csv-parity-validation-must-check-content-not-jus
description: CSV parity validation must check content, not just row count
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, generated-artifacts, csv]
---

Generated artifact validators that compare only row counts miss content drift. Two CSV/JSONL pairs can have matching rows but different field values, appearing valid while actually mismatched. Validation must compare actual cell contents or use deterministic hashing across rows. Caught in llm-wiki #77 where validator accepted header-only CSV paired with non-empty JSONL.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
