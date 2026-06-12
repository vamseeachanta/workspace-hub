---
name: crossprovider hermes provider-specific-unresolved-read-classification
description: Provider-specific unresolved-read classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, provider-drift, data-quality]
---

When auditing unresolved reads across providers, distinguish: file-missing (path not in repo), symbolic-reference (skill name with no slashes, not a file path), blank (empty entry). Reduces false positives in missing-file reports and enables provider-specific budget tracking (e.g., Codex symbolic reads vs Claude file reads).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
