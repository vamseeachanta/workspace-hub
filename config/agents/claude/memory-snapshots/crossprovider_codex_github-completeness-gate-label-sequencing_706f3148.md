---
name: crossprovider codex github-completeness-gate-label-sequencing
description: GitHub completeness gate label sequencing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-workflow, issue-closeout, completeness-gate, label-freshness]
---

Closing issues via a completeness gate requires specific order: add body fenced record with validation (cls, completeness_pct, passed, closeout_state fields), apply status labels (plan-approved, gate:completeness), then apply owner-verification label (status:completeness-verified). Label freshness check compares body edit timestamp to label application timestamp; stale review artifacts can misrepresent gate state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
