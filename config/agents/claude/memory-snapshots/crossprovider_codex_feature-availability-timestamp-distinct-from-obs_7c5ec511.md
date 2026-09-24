---
name: crossprovider codex feature-availability-timestamp-distinct-from-obs
description: Feature-availability timestamp distinct from observation date
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-modeling, governance, estimator-integrity]
---

Preventing leakage of retrospective data into historical predictions requires tracking `available_at` (when information became known) separately from `event_date` (when the event occurred). Retrospective disclosures can otherwise enter historical training/estimation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
