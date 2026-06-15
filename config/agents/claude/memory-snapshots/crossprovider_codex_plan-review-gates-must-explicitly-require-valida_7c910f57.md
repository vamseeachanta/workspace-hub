---
name: crossprovider codex plan-review-gates-must-explicitly-require-valida
description: Plan-review gates must explicitly require validator-run and artifact-commit at closeout
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, plan-review, gate-definition, artifact-validation]
---

Issue #102 plan says validators must pass, but acceptance only requires 'no-MAJOR review' + run validator in future tense, not a required final artifact scan. This allows stale artifacts (missing dated reports) to unblock issues. Fix: acceptance criteria must name explicit commands (validate_public_graph_manifests.py --date 2026-06-03) as required gate steps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
