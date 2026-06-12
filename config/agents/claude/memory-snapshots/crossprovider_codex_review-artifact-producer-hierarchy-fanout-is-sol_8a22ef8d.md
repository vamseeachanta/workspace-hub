---
name: crossprovider codex review-artifact-producer-hierarchy-fanout-is-sol
description: Review artifact producer hierarchy: fanout is sole ingestion source
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-artifact-architecture, producer-consumer, continuous-planning]
---

continuous-planning ingests only canonical fanout artifacts at `scripts/review/results/YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md`. Adjacent tools (submit-to-*.sh, cross-review.sh, render-structured-review.py) produce timestamped audit logs outside this pattern. If adjacent wrappers need ingestion, future issue must add canonical copy/export mode with same metadata contract, not modify fanout pattern.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
