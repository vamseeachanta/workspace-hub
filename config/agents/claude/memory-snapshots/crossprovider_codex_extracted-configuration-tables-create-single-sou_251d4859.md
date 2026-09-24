---
name: crossprovider codex extracted-configuration-tables-create-single-sou
description: Extracted configuration tables create single-source-of-truth conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, configuration, data-integrity]
---

Copying configuration data (e.g., pricing tables) from a registry into a separate static file creates maintenance drift unless generation/sync is explicitly defined. The copy becomes de facto truth when the original is incomplete, violating the single authoritative source principle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
