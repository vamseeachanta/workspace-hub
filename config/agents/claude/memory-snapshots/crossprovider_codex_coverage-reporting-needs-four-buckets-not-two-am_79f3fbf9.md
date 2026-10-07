---
name: crossprovider codex coverage-reporting-needs-four-buckets-not-two-am
description: Coverage reporting needs four buckets, not two: ambiguous is worse than missing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [coverage-reporting, label-buckets, semantics, assignment]
---

missing (no label) vs routable (one label) is not enough. ambiguous (multiple labels on one axis) routes by API label order and looks healthy but behaves unpredictably. terminal (deliberately unscheduled: machine:unassigned, status:icebox) is a valid end state, distinct from a gap. skipped (status:plan-review, wip, blocked) is in flight, not a finding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
