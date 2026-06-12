---
name: crossprovider codex orcaflex-import-does-not-prove-license-availabil
description: OrcaFlex import does not prove license availability
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [licensing, software-licensing, solver-capability]
---

Importing OrcFxAPI proves SDK presence, not license entitlement. OrcaFlex licensing is enforced at activity/DLL-protection level, not import. Use explicit license-status signal; classify import-only as 'present', not 'licensed'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
