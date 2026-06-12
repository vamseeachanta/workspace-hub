---
name: crossprovider codex missing-threat-model-for-new-data-flows-and-stor
description: Missing threat model for new data flows and storage is a security defect
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, security, threat-modeling]
---

Plans introducing new filesystem paths, mount writes, scheduled execution, or external API calls without a threat-model section omit mandatory security checks. Threat model must cover path traversal, symlink escape, malformed input, secret handling, and failure modes for each new surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
