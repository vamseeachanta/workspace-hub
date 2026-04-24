# Adversarial Plan Re-Review — Issue #2441 v4 governance hygiene

Date: 2026-04-23
Issue: #2441
Plan: docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md
Reviewer: Hermes delegated adversarial reviewer
Verdict: APPROVE

## Scope
Fast re-review after v4 patches for the following Wave 4 / follow-up findings:
- stale v3/Wave3 metadata
- stale `status:plan-approved` evidence after rollback to `status:plan-review`
- stale r3-only review-artifact acceptance wording
- bare `python3` / direct `pip` command-policy drift
- obvious stale governance contradictions

## Findings
- Header/status is coherent: the plan now says draft v4, Wave 4 findings patched, fresh real re-review pending.
- Current issue state is correctly recorded as `status:plan-review`, not `status:plan-approved`.
- Acceptance now requires fresh current-draft adversarial-review artifacts and explicitly says not to rely on older `-r3.md` self-review artifacts as approval evidence.
- Command policy drift is corrected: setup/install flow uses `uv venv` and `uv pip`; remaining `/tmp/pre-2441-venv/bin/python` references are venv interpreter invocations or descriptions of existing CI behavior, not bare `python3`.
- No obvious stale governance contradiction remains.

## Minor note
The Artifact Map still lists the original provider review files rather than all later attempts. This is not a blocker because the header and review summary now identify the later Wave 4 artifacts and current-draft re-review requirement.

## Verdict
APPROVE for governance-hygiene patch. This does not mean #2441 is user-approval-ready; the plan still correctly requires fresh current-draft adversarial review with no MAJOR findings before user approval.
