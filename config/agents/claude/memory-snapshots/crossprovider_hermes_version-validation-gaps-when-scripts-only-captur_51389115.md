---
name: crossprovider hermes version-validation-gaps-when-scripts-only-captur
description: Version validation gaps when scripts only capture, never reject
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [runtime-validation, acceptance-criteria, contracts]
---

Plans requiring version checks (WM_PROJECT_VERSION=v2312, foamVersion contains 2312) are silent when implementations only read and log values without conditional rejection. Script exits 0 with invalid environment. Acceptance criteria must enforce validation, not just logging.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
