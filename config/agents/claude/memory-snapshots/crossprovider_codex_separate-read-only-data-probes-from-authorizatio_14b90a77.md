---
name: crossprovider codex separate-read-only-data-probes-from-authorizatio
description: Separate read-only data probes from authorization write paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-gating, authorization, read-only-access, architecture]
---

In scoped-execution frameworks (e.g., Deckhand), route read-only data queries through independent scope-gating rather than reusing write-authorization semantics. Enables safe domain-intelligence exposure (query LNG terminals, incident databases) without changing execution controls or command/git authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
