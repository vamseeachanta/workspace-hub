---
name: crossprovider gemini backward-compatibility-pattern-warn-for-legacy-f
description: Backward compatibility pattern: WARN for legacy, FAIL for new schema
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [schema-evolution, backward-compatibility, gate-validation]
---

When introducing new gate evidence fields, missing fields in old items should return WARN (non-blocking) while new items must satisfy FAIL criteria. Prevents breaking validation of existing artifacts while enforcing standard for future items. Requires explicit version/schema markers (e.g., `metadata_version: "1"`).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
