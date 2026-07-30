---
name: crossprovider codex configuration-driven-names-create-validation-byp
description: Configuration-driven names create validation bypass holes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [config-safety, validation-architecture, naming-semantics]
---

When stable identifiers (primary key, canonical path) are configuration-driven but validation uses hardcoded position checks or string matching, misconfigured names that happen to contain substrings like 'body' or 'text' can bypass content-type guards. Use explicit closed role/column contracts instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
