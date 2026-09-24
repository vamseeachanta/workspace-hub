---
name: crossprovider codex handoff-contracts-must-bind-transitive-upstream-
description: Handoff contracts must bind transitive upstream acceptance state, not just artifact hashes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [handoff-contracts, transitive-acceptance, revision-ancestry]
---

Acceptance gates for downstream handoffs (e.g., comparison, CFD) should require current accepted upstream revisions, manifest ancestry chains, and non-superseded state—not just immediate artifact hashes. Binding only paths/hashes allows a downstream consumer to use stale, nonaccepted, or fabricated upstream evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
