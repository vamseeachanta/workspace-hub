---
name: crossprovider codex semantic-requirements-in-classifiers-are-silentl
description: Semantic requirements in classifiers are silently violated when field selection differs from documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-semantics, curation-risk, field-mapping]
---

Domain rules like 'only ROW_NO=SHUT-IN becomes WHP_shut_in' can be bypassed if the code checks a different field (e.g., source_row_no omitted) or uses different conditional logic than documented. Tests may even assert the incorrect behavior. Adversarial review must trace which field is actually checked, not assume code matches prose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
