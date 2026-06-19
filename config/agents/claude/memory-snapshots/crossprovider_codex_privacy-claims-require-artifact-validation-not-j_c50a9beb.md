---
name: crossprovider codex privacy-claims-require-artifact-validation-not-j
description: Privacy claims require artifact validation, not just code inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, code-review, artifact-verification]
---

Code may intend to suppress raw labels but generated artifacts still expose semantic names (#733: plan claims 'opaque lane IDs' but JSON/HTML emit 'personal_mixed_owner', 'AceEngineer'). Adversarial reviews must compare stated privacy boundaries against actual generated outputs, not trust implementation intent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
