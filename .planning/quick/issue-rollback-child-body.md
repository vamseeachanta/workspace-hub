## Summary
Design the rollback/recovery layer for enforcement bypasses detected after commit or push.

## Parent
- Parent issue: #2018

## Why
Issue #2018 requires technical enforcement against workflow bypasses and its current plan delegates auto-rollback to a mandatory child issue. This child exists to prevent rollback from being silently dropped while keeping the parent plan focused on detection/prevention gates.

## Scope
- Define rollback trigger conditions for detected bypasses
- Compare rollback mechanisms:
  - automatic revert
  - guided/manual revert with generated instructions
  - quarantine/disable branch path
- Define audit trail requirements for rollback actions and bypass evidence preservation
- Define correctness and safety tests for rollback behavior
- Specify integration points with existing enforcement surfaces and logs

## Out of scope
- Implementing rollback in this issue body alone
- Rewriting #2018 acceptance criteria without a reviewed plan

## Deliverables
- A reviewed plan file under `docs/plans/`
- Decision on rollback mechanism and trigger policy
- TDD list for rollback correctness and evidence preservation
- GitHub linkage back to #2018

## Acceptance criteria
- A concrete rollback plan exists and is independently reviewable
- The selected rollback approach preserves audit evidence
- The plan defines tests for false positives, partial failures, and multi-file changes
- #2018 can reference this issue by real number instead of placeholder text
