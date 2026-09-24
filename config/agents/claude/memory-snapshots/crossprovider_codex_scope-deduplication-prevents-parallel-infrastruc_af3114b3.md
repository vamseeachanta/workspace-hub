---
name: crossprovider codex scope-deduplication-prevents-parallel-infrastruc
description: Scope deduplication prevents parallel infrastructure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope, architecture, planning, digitalmodel]
---

When starting an issue that shares infrastructure with an open `status:plan-approved` issue, the first implementation step should extract shared helpers into a common path rather than maintaining parallel code. Issue #605 (OrcaWave package generation) must reconcile with #500 (mesh pre-flight validation) before implementing — do not duplicate the resolver/converter path-resolution surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
