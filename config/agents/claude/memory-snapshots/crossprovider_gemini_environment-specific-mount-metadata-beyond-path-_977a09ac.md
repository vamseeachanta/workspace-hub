---
name: crossprovider gemini environment-specific-mount-metadata-beyond-path-
description: Environment-specific mount metadata beyond path mapping
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [infrastructure, mount-management, multi-environment]
---

Mount registry entries should record auth_posture, auth_mechanism, credential_reference, fallback_posture, cached_evidence_ttl, and degradation_rule—not just source_id→mount_root. Enables automated handling of mount state changes and environment-specific auth without hardcoding logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
