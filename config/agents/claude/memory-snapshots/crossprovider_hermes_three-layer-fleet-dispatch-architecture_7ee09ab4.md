---
name: crossprovider hermes three-layer-fleet-dispatch-architecture
description: Three-layer fleet dispatch architecture
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, dispatch, architecture]
---

Multi-machine dispatch should separate Linux control/data (ace-linux-1), Linux execution worker (ace-linux-2), and Windows licensed hosts. Each layer has distinct readiness/constraints; do not flatten until boundaries are formalized.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
