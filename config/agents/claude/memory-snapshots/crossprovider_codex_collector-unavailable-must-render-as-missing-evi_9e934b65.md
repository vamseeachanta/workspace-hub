---
name: crossprovider codex collector-unavailable-must-render-as-missing-evi
description: Collector-unavailable must render as MISSING-EVIDENCE, not ABSENT
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [measurement-semantics, fail-closed, collector-errors]
---

When a measurement tool fails or is unavailable, that state must be explicitly distinct from 'tool ran and found nothing absent'. Collapsing both into ABSENT produces false verdicts. Fail-closed rendering requires a three-way status: PRESENT, ABSENT, MISSING-EVIDENCE.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
