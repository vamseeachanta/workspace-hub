---
name: crossprovider hermes data-promotion-architecture-gates-legality-clien
description: Data promotion architecture: gates, legality, client separation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, client-data, llm-wiki, promotion-gates]
---

Data promotion to `llm-wiki` requires provenance tracking, legal/license review, and sanitization gates. Client data must be routed to private `/mnt/local-analysis/<client>-llm-wiki` repos, not public. Raw execution outputs are not automatically deliverables; report-derived knowledge is first-class. `/mnt/ace-data` symlink is confusing; migrate or remove references.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
