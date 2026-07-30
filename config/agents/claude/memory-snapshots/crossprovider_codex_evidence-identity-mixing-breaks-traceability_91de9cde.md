---
name: crossprovider codex evidence-identity-mixing-breaks-traceability
description: Evidence identity mixing breaks traceability
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [provenance, data-quality, identity]
---

When multiple distinct entities (e.g., original FER model and generated first-pass model) are assigned the same run ID and status, their contributions become ambiguous and untraced in evidence. Each distinct entity—model version, run, result—must have unambiguous identity in the evidence record.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
