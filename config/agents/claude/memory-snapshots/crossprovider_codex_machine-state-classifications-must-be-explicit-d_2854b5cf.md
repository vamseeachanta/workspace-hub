---
name: crossprovider codex machine-state-classifications-must-be-explicit-d
description: Machine state classifications must be explicit data enums, not implicit prose
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [data-modeling, fleet-management, manifest-schema]
---

States like MISSING-EVIDENCE, DIVERGES, UNREACHABLE must be explicit enumerated values in the machine-readable manifest, not implied by prose notes or HTML text. Downstream consumers need deterministic state fields to make policy decisions; implicit states are invisible to automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
