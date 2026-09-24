---
name: crossprovider codex format-enum-values-must-sync-across-all-componen
description: Format enum values must sync across all components
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enums, consistency, cross-component]
---

BodyMeshFormat diverged silently between schema, backend mapping, CLI, and examples (Wamit dat vs Aqwa dat). Grep all callsites during plan review to ensure consistent enum values everywhere.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
