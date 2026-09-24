---
name: crossprovider codex lifecycle-html-as-single-authoritative-stage-log
description: Lifecycle HTML as single authoritative stage log, updated at every stage exit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-design, lifecycle-tracking, audit-trail]
---

One WRK-NNN-lifecycle.html per WRK replaces separate plan-draft.html, implementation.html, review.html. Each of 20 stages has a schema: reviewed_by, confirmed_by, decision, notes. Updated at stage exit by exit-stage.sh calling generate-html-review.py --stage N --update. Provides single durable record of stage progression and decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
