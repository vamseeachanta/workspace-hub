---
name: crossprovider codex fixture-corpus-blocker-schema-and-validator-must
description: Fixture corpus blocker: schema and validator must exist before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, blockers]
---

Do not write fixture corpus (valid, invalid, edge cases) before canonical schema definition and validator CLI exist and are merged. If parent issues are open, stop and refresh blocker evidence; do not invent fixture behavior in advance of upstream specs. This prevents rework when real schemas diverge from speculated ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
