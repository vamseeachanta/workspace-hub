# Plan: WRK-684 — Institutional Memory & Productivity Dashboard (v2)

## Goal
Transform the `/today` report from a simple status list into a high-resolution dashboard that tracks orchestrator compliance, execution efficiency, and ecosystem improvement trends based on raw session data.

## Proposed Changes

### 1. Data Aggregation Engine
- Create `scripts/productivity/aggregate-learning-data.py`.
- **Functionality:**
    - Parse `.claude/state/session-signals/*.jsonl` for tool-usage efficiency.
    - Parse `.claude/state/corrections/*.jsonl` for intervention density.
    - Aggregate Cross-Review feedback categories from `assets/WRK-*/review-*.md`.
    - Map RI artifact coverage against actual task implementation logs.

### 2. High-Resolution `/today` Section: `learning-dashboard.sh`
- Create `scripts/productivity/sections/learning-dashboard.sh` (replaces the minimal roll-up).
- **Dashboard Sections:**
    - **Orchestrator Compliance Table:** [Agent | Stage Adherence | Turn Efficiency | Drift Flags].
    - **Work Quality Metrics:** [TDD Pairing % | Review Effectiveness | Correction Density].
    - **Resource Intelligence Coverage:** [Tasks with RI | Source Utilization Rate].
    - **Active Ecosystem Trends:** [New Action Candidates | Escalated Recurring Issues].

### 3. Comprehensive-Learning Skill Integration
- Standardize the `comprehensive-learning` Phase 10 report to output a structured JSON artifact (`.claude/state/learning-reports/latest-metrics.json`) for fast, reliable parsing by the dashboard.

## Verification Plan

### Automated Tests
- Validate JSON schema of the `latest-metrics.json` artifact.
- Unit test the Python aggregator against diverse session signal patterns.

### Smoke Tests
1. **Efficiency Check:** Verify that "Turn-to-Commit" metrics appear correctly for a recent task.
2. **Quality Check:** Confirm that a "MAJOR" review verdict correctly impacts the "Work Quality" rating in the report.
3. **RI Check:** Verify that missing RI artifacts are flagged as compliance warnings.

## Acceptance Criteria
- [ ] `/today` displays a multi-table dashboard with compliance and efficiency metrics.
- [ ] Detailed "Improvement Candidates" are categorized by domain (Skill/Script/Hook).
- [ ] No regression in report generation speed (uses cached JSON where possible).
