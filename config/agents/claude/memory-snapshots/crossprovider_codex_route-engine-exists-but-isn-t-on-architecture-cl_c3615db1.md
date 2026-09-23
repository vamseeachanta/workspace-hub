---
name: crossprovider codex route-engine-exists-but-isn-t-on-architecture-cl
description: Route engine exists but isn't on: architecture claims capabilities hosts don't have
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [dispatch, routing, infrastructure, provider-labels, phase-gates]
---

scripts/dispatch/route.py (assignment engine) and provider-autolabel.py exist and are tested, but route.py --apply is disabled in code (Phase B). Meanwhile four provider vocabularies coexist (lane:, agent:, ai:, model:) with different precedence. #579 routing rules claim OrcaFlex capability on a host with no Licence; reconciliation of vocabularies is urgent before enabling writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
