# WRK-690 Combined Plan

## Goal
Execute both tracks under WRK-690:
1. Workflow hardening: enforce skill-driven gatepass from session start through close/archive.
2. Outcome-informed log evaluation: analyze recent agent sessions and feed findings back into workflow skills.

## Track A — Workflow Hardening
1. Add and wire new skills:
   - `workflow-gatepass`
   - `wrk-lifecycle-testpack`
   - `work-queue-workflow` (explicit alias/entrypoint)
2. Update existing skills:
   - `work-queue`
   - `session-start`
   - `session-end`
   - `work-document-exit`
3. Enforce lifecycle chain in skill docs:
   `/session-start` -> `/work` -> plan/approval -> claim -> execute -> reclaim -> future-work -> close -> archive.
4. Require close-gate expectations in skill docs:
   - 9-stage verification ledger
   - integrated/repo tests count 3-5

## Track B — Log Evaluation and Feedback Loop
1. Catalog session stores and orchestrator logs for Claude/Codex/Gemini.
2. Review weekly evidence artifacts and identify gatepass coverage gaps.
3. Feed concrete findings into `work-queue` workflow guidance.
4. Document follow-up recommendations for instrumentation and coverage.

## Current Outcome Integration
- WRK-690 evidence already includes weekly gatepass summaries and agent/session audit artifacts.
- Skill updates in this work item must reference those outcomes and tighten close/readiness checks.

## Plan Review Confirmation

confirmed_by: user
confirmed_at: 2026-03-03T00:00:00Z
decision: passed
notes: approved to execute both workflow hardening and log-eval outcome integration
