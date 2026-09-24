---
name: crossprovider codex plan-internal-consistency-is-a-correctness-gate-
description: Plan internal consistency is a correctness gate, not style
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, ci-workflows, review-pattern]
---

When a plan's Deliverable, Acceptance, Detailed Spec, and TDD sections contradict each other (e.g., install methods, trigger paths, file lists), the plan cannot be executed as written. This recurs across CI workflow plans — mismatches between `uv sync` vs `uv pip install`, trigger specs including `uv.lock` but acceptance excluding it, or Deliverable claiming `src/**+tests/**` scope while Spec uses broad `paths-ignore`. These are discovery-time failures, not minor formatting issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
