---
name: crossprovider codex consolidation-requires-exhaustive-reference-inve
description: Consolidation requires exhaustive reference inventory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, consolidation, scope]
---

Before retiring, archiving, or replacing artifacts, prove ALL references have been found (code, tests, docs, config, automation, comments). Pattern-matching and assumed consumers leave stale references and silent breakage. Live-filesystem enumeration via grep/find is mandatory; assumption-based scope is a defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
