# Adversarial Re-Review — Plan #2269 (Claude, wave 2)

Date: 2026-04-15
Issue: #2269
Plan: docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md
Reviewer: Claude CLI
Reviewer mode: adversarial
Overall verdict: MINOR
Ready for user approval: Not yet
Retrieval adequacy: strong

Top blockers
1. both-paths-exist bootstrap behavior needs to be pinned
2. wrapper↔runner YAML handoff mechanism needs an explicit chosen strategy

Critical findings
- none

High findings
- add explicit both-paths-exist policy plus version-mismatch guard
- choose and state one YAML handoff strategy: parse/merge or runner-refactor-to-rows

Medium findings
- map the plan more explicitly to the Engineering Delivery Checklist tier
- add field-type/enum constraints for the YAML schema
- state pytest host/skip strategy for dev-primary vs dev-secondary

Low findings
- decide definitively whether `docs/README.md` is the required discoverability surface
- clarify `damBreak` status relative to the runner and wrapper tiers

Required revisions before user approval
1. Add first-found-wins or dual-path error policy plus version-mismatch guard.
2. Pick one wrapper↔runner YAML handoff strategy and state it explicitly.
3. Add YAML field type/enum constraints.
4. State `@pytest.mark.openfoam` / fixture-based schema-test strategy.
5. Clarify whether `damBreak` remains in runner scope or is dropped from the baseline contract.
