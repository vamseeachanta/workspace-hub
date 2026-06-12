---
name: crossprovider codex plan-schema-divergence-is-a-blocking-defect-clas
description: Plan-schema divergence is a blocking defect class
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, scope-creep, review-gate]
---

When a revised implementation plan changes scope/filepaths but the canonical WRK artifact is not updated in parallel, review and implementation diverge. Example: WRK-1066 Rev 9→10 switched from env-audit.sh to ai-tools-status.sh, but WRK-1066.md still described the old paths until explicitly synced. Approval gates should require WRK artifact and plan to be in sync before APPROVE.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
