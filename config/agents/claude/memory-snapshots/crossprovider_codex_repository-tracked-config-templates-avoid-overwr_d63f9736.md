---
name: crossprovider codex repository-tracked-config-templates-avoid-overwr
description: Repository-tracked config templates avoid overwrites from machine-local sync
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration, codex, durability]
---

Hand-edited home-directory config files are overwritten by sync processes. Durable configuration requires canonical templates in the repository with merge-aware sync logic and per-machine attestation, not ad-hoc edits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
