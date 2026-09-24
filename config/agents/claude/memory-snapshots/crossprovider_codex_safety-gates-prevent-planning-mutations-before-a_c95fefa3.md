---
name: crossprovider codex safety-gates-prevent-planning-mutations-before-a
description: Safety gates prevent planning mutations before auth scope available
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety, auth, scope-boundaries]
---

Don't plan automated remote mutations (Gmail delete, archive) before the required auth scope (gmail.modify) is available. Distinguish local queue-state changes from remote mutations in title and scope. Scope shifts are acceptable if explicit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
