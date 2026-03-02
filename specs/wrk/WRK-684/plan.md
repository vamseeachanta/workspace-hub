# Plan: WRK-684 — Advanced Learning Roll-up into /today

## Goal
Standardize and integrate advanced "Learning Outcomes" from the `comprehensive-learning` pipeline into the `/today` report, focusing on orchestrator compliance, work quality, resource intelligence, and ecosystem improvement trends.

## Proposed Changes

### 1. New `/today` Section: `learning-outcomes.sh`
- Create `scripts/productivity/sections/learning-outcomes.sh`.
- **Orchestrator Compliance:** Extract "Agent gate-skip rate" and "Agent scope drift" from Phase 1.
- **Work Quality:** Extract "TDD pairing rate", "Low consensus scores", and "Plan-to-implementation drift" metrics.
- **Resource Intelligence:** Track the coverage of RI artifacts across active tasks.
- **Improvement Trends:** Roll up "Action Candidates" from Phase 7 (Skills, Scripts, Hooks, Agents) and "Correction Trends" from Phase 5.
- **System Health:** Include "AI agent readiness" status and "Stale memory entries" count.

### 2. Orchestrator Integration
- Update `scripts/productivity/daily_today.sh` to include `run_section learning-outcomes.sh`.

### 3. Metric Harvesting Logic
- Use structured regex parsing to extract counts and lists from the nightly learning report artifacts.

## Verification Plan

### Automated Tests
- None.

### Smoke Tests (Variation Tests)
1. **Trend Check**: Verify that newly identified skill or script candidates appear in the `/today` output.
2. **Compliance Check**: Confirm that gate violations are highlighted.
3. **RI Metric Check**: Confirm RI coverage is reported correctly.

## Acceptance Criteria
- [ ] `/today` includes an "Orchestrator Compliance" section.
- [ ] `/today` includes a "Work Quality & System Health" section.
- [ ] `/today` includes an "Ecosystem Improvement Trends" section listing top action candidates.
