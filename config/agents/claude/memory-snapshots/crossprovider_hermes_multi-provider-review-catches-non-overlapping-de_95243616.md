---
name: crossprovider hermes multi-provider-review-catches-non-overlapping-de
description: Multi-provider review catches non-overlapping defect classes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, multi-provider]
---

Codex R7 and Gemini R7 adversarial reviews on same codebase found different MAJOR defects: Codex caught non-Linux local host fail-open, Gemini caught remote evidence redaction leak. Neither found both. Confirms value of parallel multi-provider review despite cost.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
