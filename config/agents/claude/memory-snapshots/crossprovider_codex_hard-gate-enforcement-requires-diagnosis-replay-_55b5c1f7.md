---
name: crossprovider codex hard-gate-enforcement-requires-diagnosis-replay-
description: Hard-gate enforcement requires diagnosis, replay, audit, and executable logic
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow-gating, enforcement, completeness]
---

A gate is incomplete without: (1) documented root cause (not just symptom description); (2) replay of at least one observed bypass on real logs to confirm the bypass mode; (3) audit classifying each entry path as official (scripts/agents/plan.sh) vs. downstream (validators) vs. manual mutation; (4) executable logic in the canonical path, not just policy text; (5) minimal, defined artifact set required to pass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
