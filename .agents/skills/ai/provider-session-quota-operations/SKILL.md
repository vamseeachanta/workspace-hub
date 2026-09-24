---
name: provider-session-quota-operations
version: 1.0.0
category: ai
description: Class-level provider/session operations for Claude, Codex, Gemini, Hermes, quotas, audit exporters, readiness dispatch, and utilization scorecards.
tags: [providers, sessions, quota, audit]
---

# Provider Session Quota Operations

## When to Use
Use when auditing provider session logs, routing work based on readiness/quota, creating utilization scorecards, or recovering provider-specific review capacity.

## Class-Level Workflow
1. Bootstrap paths/exporters and classify provider artifacts before deriving metrics.
2. Distinguish quota/readiness dispatch from session-corpus learning transfer.
3. Keep utilization scorecards computable and evidence-backed.
4. Use provider-specific recovery notes for Gemini/Codex/Claude only as subcases under this broader workflow.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `inventory-readiness-provider-dispatch`

- Former skill demoted to `references/inventory-readiness-provider-dispatch.md`.
- Preserved insight: Build and operate a computable readiness matrix that connects raw-data-to-GTM package stages with Claude/Codex/Gemini dispatch lanes and weekly credit pacing.

### `provider-utilization-scorecard`

- Former skill demoted to `references/provider-utilization-scorecard.md`.
- Preserved insight: Refresh provider quota snapshots and generate a weekly Claude/Codex/Gemini utilization scorecard grounded in quota data when available and session-activity fallback when not.

### `provider-audit-bootstrap-and-path-classification`

- Former skill demoted to `references/provider-audit-bootstrap-and-path-classification.md`.
- Preserved insight: Fix provider-session ecosystem audit failures caused by source-checkout imports and over-aggressive symbolic-path classification.

### `provider-session-ecosystem-audit`

- Former skill demoted to `references/provider-session-ecosystem-audit.md`.
- Preserved insight: Audit Claude/Codex/Hermes/Gemini session logs, normalize provider-specific quirks, and wire recurring exports/reporting for ongoing ecosystem health checks.

### `provider-session-ecosystem-audit-and-exporters`

- Former skill demoted to `references/provider-session-ecosystem-audit-and-exporters.md`.
- Preserved insight: Build and maintain cross-provider session-log audits for Claude, Codex, Hermes, and Gemini, including exporter design, normalization, and behavioral verification.

### `provider-session-learning-transfer`

- Former skill demoted to `references/provider-session-learning-transfer.md`.
- Preserved insight: Refresh provider session audit, identify post-audit/unassessed sessions, extract actionable learnings, and transfer them into repo notes and GitHub issues before a follow-up implementation session.

### `gemini-review-capacity-recovery`

- Former skill demoted to `references/gemini-review-capacity-recovery.md`.
- Preserved insight: Handle Gemini adversarial-review runs that emit repeated 429 capacity errors before either recovering with a real verdict or failing unavailable.

### `workstation-aware-provider-orchestration`

- Former skill demoted to `references/workstation-aware-provider-orchestration.md`.
- Preserved insight: Plan and operate a Hermes-led control plane that routes AI provider work across workstations using quota urgency, machine readiness, GitHub issue gates, and a dispatch ledger.
