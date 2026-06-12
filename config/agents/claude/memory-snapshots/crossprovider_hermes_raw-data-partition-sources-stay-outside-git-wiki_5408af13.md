---
name: crossprovider hermes raw-data-partition-sources-stay-outside-git-wiki
description: Raw data partition: sources stay outside git, wiki receives summaries + metadata only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [knowledge-management, data-architecture, wiki, approval-gate]
---

For knowledge-management work (llm-wiki gaps, standards, entity coverage), raw data sources remain in `/mnt/ace` or external stores; only processed summaries, metadata, and entity references are committed to `knowledge/wikis/` after approval per gap. Enforces approval-gated data flow and prevents repo bloat.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
