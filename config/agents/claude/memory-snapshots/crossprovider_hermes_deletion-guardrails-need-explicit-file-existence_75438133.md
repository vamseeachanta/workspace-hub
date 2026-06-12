---
name: crossprovider hermes deletion-guardrails-need-explicit-file-existence
description: Deletion guardrails need explicit file-existence assertions, not just text-search reference checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, artifact-cleanup, verification-gap]
---

When removing client-facing outputs (especially binary artifacts like PDFs), tests must explicitly verify those files no longer exist on disk. Text-search checks of index/reference documents are insufficient — a file can vanish from the index while the binary persists. Session #594-review caught GTM JSON/HTML/index guardrails passing while PDF outputs remained uncovered.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
