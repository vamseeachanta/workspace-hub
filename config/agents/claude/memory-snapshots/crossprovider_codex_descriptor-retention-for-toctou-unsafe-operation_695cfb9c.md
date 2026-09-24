---
name: crossprovider codex descriptor-retention-for-toctou-unsafe-operation
description: Descriptor-retention for TOCTOU-unsafe operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [TOCTOU, attestation, file-descriptors, security-pattern]
---

Reopening attacker-controlled pathnames (config, target files) between sensitive operations creates TOCTOU windows. Retain file descriptors across operation boundaries; use one held clone/manifest context instead of reopening for each attestation step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
