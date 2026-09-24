---
name: crossprovider codex consolidate-host-machine-metadata-to-single-regi
description: Consolidate host/machine metadata to single registry file
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture-pattern, single-source-of-truth]
---

Host/machine identity, capabilities, and dispatch metadata should live in one canonical location (e.g., config/workstations/registry.yaml) marked with a HARD RULE. Derived systems (readiness checks, dispatch loops, version validators) should read from that registry, not maintain competing host lists or hardcoded paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
