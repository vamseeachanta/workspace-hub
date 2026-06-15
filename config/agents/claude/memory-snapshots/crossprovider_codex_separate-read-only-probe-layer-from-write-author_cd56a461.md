---
name: crossprovider codex separate-read-only-probe-layer-from-write-author
description: Separate read-only probe layer from write authorization
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [architecture, deckhand, governance]
---

worldenergydata exposes structured databases (marine_safety.db, hse_incidents.db) and query APIs (LNG terminals). Route them to deckhand as a scoped read-only "probe layer" distinct from write-path authorization, with citation and redaction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
