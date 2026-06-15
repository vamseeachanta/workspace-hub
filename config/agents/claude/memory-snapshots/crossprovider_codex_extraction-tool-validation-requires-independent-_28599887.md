---
name: crossprovider codex extraction-tool-validation-requires-independent-
description: Extraction tool validation requires independent source parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [verification, extraction, binary-formats, testing-strategy]
---

When verifying extracted/enriched content from binary formats (PPTX, PDF, etc), test the extraction tool AND independently parse the source format to catch edge cases. PPTX example: python-pptx doesn't recursively walk shapes inside grouped shapes (p:grpSp), causing picture inventories to miss 5-15% of embedded media. Raw XML/ZIP parsing caught what tool-level testing wouldn't.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
