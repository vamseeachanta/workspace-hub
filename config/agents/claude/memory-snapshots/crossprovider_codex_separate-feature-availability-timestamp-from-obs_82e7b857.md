---
name: crossprovider codex separate-feature-availability-timestamp-from-obs
description: Separate feature-availability timestamp from observation date in time-series data
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [data-modeling, machine-learning, time-series]
---

For cost/data time-series used in predictive models, track published_at/available_at (when data became known) separately from event_date (when the event occurred). Retrospective disclosures can otherwise leak future information into historical training sets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
