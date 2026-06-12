---
name: crossprovider hermes report-template-requirements-must-be-enforced-as
description: Report template requirements must be enforced as schema, not pseudocode
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reporting, validation, templates, contracts]
---

When an approved plan specifies report structure in pseudocode (e.g., 'explicit blocked/partial/missing section'), the renderer must validate that structure or tests must assert its presence. #2487 report was missing the section initially because the pseudocode wasn't translated to a validator rule or test assertion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
