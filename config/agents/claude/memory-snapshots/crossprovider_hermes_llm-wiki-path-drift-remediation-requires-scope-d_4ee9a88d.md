---
name: crossprovider hermes llm-wiki-path-drift-remediation-requires-scope-d
description: llm-wiki path-drift remediation requires scope discipline on reference types
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, path-drift, scope-discipline]
---

Not all `knowledge/wikis/` references are stale spinouts; some are historical evidence, generated artifacts, compatibility fallbacks, valid retained paths, or health artifacts. Remediation must discriminate between 'active stale' (remove from prompts) vs 'retained/historical' (keep documented) rather than naive global replacement.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
