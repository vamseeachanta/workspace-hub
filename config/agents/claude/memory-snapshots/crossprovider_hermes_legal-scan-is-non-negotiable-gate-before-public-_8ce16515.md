---
name: crossprovider hermes legal-scan-is-non-negotiable-gate-before-public-
description: Legal scan is non-negotiable gate before public artifact closure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legal, validation, gate, public-artifacts]
---

All public-facing artifact validation must include legal scan (e.g., via scripts/legal/legal-sanity-scan.sh) before commit/close. Legal scan failures block closure; no workarounds.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
