---
name: crossprovider codex mounted-source-registry-with-environment-specifi
description: Mounted-source registry with environment-specific fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, resource-management, multi-environment]
---

For multi-environment resource configurations, include: mount_root_ref (env-var binding), environment_specific boolean, auth_posture/mechanism, credential_reference, fallback_posture, cached_evidence_TTL, and degradation_rule. This enables heterogeneous local/remote/virtual sources to coexist with clear authentication and availability handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
