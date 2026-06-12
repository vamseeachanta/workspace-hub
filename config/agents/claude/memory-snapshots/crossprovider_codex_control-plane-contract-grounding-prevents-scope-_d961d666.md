---
name: crossprovider codex control-plane-contract-grounding-prevents-scope-
description: Control-plane contract grounding prevents scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [control-plane, contracts, scope]
---

Plans touching harness/control-plane (scheduler, readiness, agent dispatch) must cite relevant governance standards (`CONTROL_PLANE_CONTRACT.md`, scheduler routing, per-machine placement contract) and avoid mixing concerns. #2762–#2765 reviews emphasized that scoping to documented contracts prevents silent out-of-spec designs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
