---
name: crossprovider codex domain-schema-incomplete-across-systems
description: Domain schema incomplete across systems
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema, architecture, consistency, scope]
---

Domain is first-class in reconciler + manifest, but scattered/missing in loader, dispatch rules, client-wiki registry. Adding `(repo, domain, project)` to one system creates inconsistency. Coordinate schema updates across loader/manifest/dispatch/config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
