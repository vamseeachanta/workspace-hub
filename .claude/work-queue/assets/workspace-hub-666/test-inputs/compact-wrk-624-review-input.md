# WRK-624 Compact Review Input

## Executive Summary
WRK-624 defines a canonical 8-stage work-item lifecycle for workspace-hub. It adds mandatory planning-stage HTML review, route-based review enforcement, claim-stage quota and capability checks, close/archive gates, and migration/testing/dependency contracts.

## Key Gates
- User reviews draft plan HTML before multi-agent review.
- Multi-agent review runs.
- User reviews final plan HTML before execution approval.
- Claim checks best-fit agent and quota readiness.
- Close requires queue validation and HTML verification.
- Archive requires merge and sync completion.

## Review Matrix
- Route A: 1 reviewer by default, escalate on risk.
- Route B: Claude + Codex + Gemini.
- Route C: Claude + Codex + Gemini per plan, phase, and close.
- All review artifacts must use the same schema.

## Key Risks To Assess
- Workflow overhead for all WRKs.
- Migration complexity for legacy items.
- Authority conflicts between validators and readiness signals.
- Testing depth for lifecycle transitions.

## Required Review Schema
- Verdict
- Summary
- Issues Found
- Suggestions
- Questions for Author
