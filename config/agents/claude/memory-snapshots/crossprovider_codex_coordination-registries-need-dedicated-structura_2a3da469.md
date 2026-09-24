---
name: crossprovider codex coordination-registries-need-dedicated-structura
description: Coordination registries need dedicated structural parsers, not prose scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, validation, coordination-documents]
---

When a coordination document defines a registry (Wave Gate Registry, manifest gate tables, etc.), parse it as a dedicated structured block with schema enforcement in code. Session 2 approved the #51 validator specifically because it used `dedicated structural registry parser` (lines 233, 655–671) rather than prose-only manifest scanning, which would have missed schema violations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
