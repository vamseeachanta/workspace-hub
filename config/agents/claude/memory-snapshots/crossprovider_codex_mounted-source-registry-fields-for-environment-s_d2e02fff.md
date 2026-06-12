---
name: crossprovider codex mounted-source-registry-fields-for-environment-s
description: Mounted-source registry: fields for environment-specific resources
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [resource-registry, multi-environment, fallback-strategy]
---

When tracking remote or environment-specific document sources, record: `mount_root_ref` (env var), `mount_root_example` (concrete path), `environment_specific` (bool), auth posture/mechanism, fallback policy, TTL on cached evidence, and degradation rule (what to do when source unavailable). This set handles workstation mobility and graceful degradation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
