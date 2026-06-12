---
name: crossprovider hermes cli-output-contract-must-be-explicitly-frozen-be
description: CLI/output contract must be explicitly frozen before implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [implementation-readiness, api-design, acceptance-criteria]
---

CLI/output contract ambiguities (interface: CLI vs script? entry point? output format? filename conventions? exit codes? partial-output behavior?) are MAJOR blockers for implementation readiness. Freeze these up front in the plan, not as implementation decisions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
