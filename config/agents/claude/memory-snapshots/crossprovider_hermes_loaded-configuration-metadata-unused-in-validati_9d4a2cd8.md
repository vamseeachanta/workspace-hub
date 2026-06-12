---
name: crossprovider hermes loaded-configuration-metadata-unused-in-validati
description: Loaded configuration metadata unused in validation is a code smell for gate bypass
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, gate-bypass, unused-metadata]
---

Dispatch policy loaded `repos` and `data_repos` fields from registry but never enforced them during host selection. A workspace-hub issue could be routed to a host lacking workspace-hub access. Unused metadata in control flow suggests missing validation; audit all loaded config for enforcement.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
