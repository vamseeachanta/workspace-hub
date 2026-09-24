---
name: crossprovider codex public-safe-summaries-must-stay-downstream-of-co
description: Public-safe summaries must stay downstream of corpus traversal, stripping all identifying detail
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, architecture, abstraction]
---

Root-level traversal can produce metadata (visibility, sensitivity, route_target, llm_wiki_value_tier). But downstream public summaries must strip root names, local paths, filenames, raw text, and low-count buckets. Public graph manifests expose only whitelisted node/edge metadata. This keeps private lanes abstracted even when upstream metadata is preserved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
