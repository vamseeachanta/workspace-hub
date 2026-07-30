---
name: crossprovider codex storage-path-enforcement-needs-dual-coverage
description: Storage path enforcement needs dual coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [deployment, testing, configuration]
---

Code accepting any root while docs require a specific path leaves deployment safety gaps. Validator must reject non-compliant roots; tests must verify the rejection works.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
