---
name: crossprovider codex firewall-rules-for-public-private-artifact-redac
description: Firewall rules for public/private artifact redaction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-redaction, public-private-split, llm-wiki-publishing]
---

workspace-hub applies strict rules before publishing internal artifacts to public OSS repos (llm-wiki): remove internal paths (`/mnt/`, `/home/`, machine names), workspace-hub provenance fields (issue:, plan:, scope:, source_issue, audit), `.claude` rule references, knowledge/wikis paths, digitalmodel/ACE ecosystem language, and local-PDF/machine-specific blocker notes. Be conservative—when unsure whether content is internal, remove it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
