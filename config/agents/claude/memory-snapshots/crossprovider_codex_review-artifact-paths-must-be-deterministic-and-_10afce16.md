---
name: crossprovider codex review-artifact-paths-must-be-deterministic-and-
description: Review artifact paths must be deterministic and verified at approval time
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-management, approval-readiness, cross-provider]
---

Artifacts belong in `scripts/review/results/YYYY-MM-DD-plan-NNNN-{claude,codex,gemini}.md`. When artifact locations in the plan text don't match actual file locations, or files are missing, the approval gate becomes unverifiable. Approval review must check that artifacts actually exist at cited paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
