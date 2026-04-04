# Overnight 5-Terminal Agent Prompts — 2026-04-07

Generated: 2026-04-04 8:00 PM CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub
Source: notes/agent-work-queue.md

## Provider Allocation

| Terminal | Provider      | Workstream                                          | Est. Time |
|----------|---------------|-----------------------------------------------------|-----------|
| 1        | Gemini        | Standards mapping + research prep (3 high-pri)        | 2-3 hrs   |
| 2        | Claude (Opus) | Field dev + naval arch implementation (2 epics)       | 2-3 hrs   |
| 3        | Codex seat 1  | Test coverage uplift + solver queue fixes             | 2-3 hrs   |
| 4        | Codex seat 2  | Harness hardening + security + config protection      | 2-3 hrs   |
| 5        | Claude/Hermes | Orchestration: work-queue system + credit tracker     | 2-3 hrs   |

## Git Contention Avoidance Map

Terminal 1 writes: docs/document-intelligence/, data/document-index/, notes/prep/
Terminal 2 writes: digitalmodel/src/digitalmodel/field_development/, naval_architecture/, geotechnical/, fatigue/
Terminal 3 writes: digitalmodel/tests/ (new test files only)
Terminal 4 writes: config/harness/, scripts/harness/, .githooks/, skills/
Terminal 5 writes: notes/agent-work-queue.md, config/ai-tools/, scripts/cron/, docs/plans/

ZERO FILE OVERLAP confirmed.
Each terminal does: git pull origin main before every push.

## Issue-to-Terminal Reverse Mapping

| Issue | Title                                          | Terminal | Agent  |
|-------|------------------------------------------------|----------|--------|
| #1823 | Map 825 hydrodynamics functions to standards   | T1       | Gemini |
| #1821 | Close 24 structural standards gaps             | T1       | Gemini |
| #1860 | Scrape SubseaIQ field development database      | T1       | Gemini |
| #1842 | Field development analysis system epic         | T2       | Claude |
| #1849 | Naval architecture expansion epic              | T2       | Claude |
| #1811 | Promote SN curve POC v2 to digitalmodel        | T2       | Claude |
| #1824 | Uplift test coverage 2.95% to 20%              | T3       | Codex  |
| #1830 | Review and close solver queue bugs #1703-#1706 | T3       | Codex  |
| #1805 | Security hardening for AI agent workflows      | T4       | Codex  |
| #1801 | Adopt pre:config-protection hook               | T4       | Codex  |
| #1802 | Implement batch-at-Stop pattern                | T4       | Codex  |
| #1857 | Rolling 1-week agent work queue system         | T5       | Claude |
| #1855 | Weekly AI credit utilization tracker           | T5       | Claude |
| #1839 | Workflow hard-stops and session governance     | T5       | Claude |

## Terminal 1 — Gemini Standards Mapping

### Issue #1823: Map 825 hydrodynamics functions to standards
Research which API/DNV/ISO/NORSOK standards apply to each of the 825 hydrodynamics functions in digitalmodel. Create mapping with:
- Function name and file
- Applicable standard(s) with section/paragraph reference
- Gap flag (function has no corresponding standard)
Output: docs/document-intelligence/standards-mapping/hydrodynamics-standards-map.csv

### Issue #1821: Close 24 structural standards gaps
For each structural gap: identify standard requirement, summarize implementation need, estimate complexity.
Output: docs/document-intelligence/standards-mapping/structural-gaps-analysis.md

### Issue #1860: Scrape SubseaIQ field development database
Collect public field development project data from SubseaIQ: field names, operators, water depths, pipeline lengths, vessel types.
Output: data/field-development/subseaiq-scan-latest.json and notes/prep/subseaiq-summary.md

## Terminal 2 — Claude Epic Implementation

### Issue #1842: Field development analysis system (epic)
Plan and begin implementation of field development analysis system covering concept selection, economics, facility sizing, and FDP generation. Begin with concept selection framework (#1843). TDD: write tests first.
Target: digitalmodel/src/digitalmodel/field_development/concept_selection.py

### Issue #1849: Naval architecture expansion (epic)
Begin naval architecture expansion: floating platform stability (#1850) and gyradius calculator (#1851). Support FPSO, semi-sub, spar, TLP, barge.
Target: digitalmodel/src/digitalmodel/naval_architecture/

### Issue #1811: Promote SN curve POC v2 to digitalmodel/fatigue
Promote SN curve POC extraction output to proper module with type hints, docstrings, unit tests. Register in specs/module-registry.yaml.
Target: digitalmodel/src/digitalmodel/fatigue/sn_curves.py

## Terminal 3 — Codex Test Coverage + Bug Fixes

### Issue #1824: Uplift test coverage 2.95% to 20%
Add tests to packages with near-zero coverage: field_development/, naval_architecture/, geotechnical/, infrastructure/. Import tests + happy path + 1-2 edge cases per function. All tests must pass: uv run pytest digitalmodel/tests/
Target: digitalmodel/tests/

### Issue #1830: Review and close solver queue bugs #1703-#1706
Review each bug, reproduce, fix if needed, add regression test, close issue.
Target: scripts/solver-queue/, tests/solver_queue/

## Terminal 4 — Codex Harness Hardening

### Issue #1805: Security hardening for AI agent workflows
Implement security scans for: skill files (detect hardcoded secrets), memory files (detect poisoning attempts), config files (detect unauthorized changes).
Output: scripts/security/agent-security-scan.sh

### Issue #1801: Adopt pre:config-protection hook
Create git pre-commit hook that prevents agents from weakening linter/formatter configs. Block removal of lint rules from pyproject.toml. Block changes to CLAUDE.md that remove safety gates.
Output: .githooks/pre-config-protection.sh

### Issue #1802: Implement batch-at-Stop pattern
Defer format + typecheck to session end. Track modified files during session, run ruff + mypy batch on session close.
Output: scripts/batch-at-stop.sh

## Terminal 5 — Claude Orchestration

### Issue #1857: Agent work queue system
The queue file (notes/agent-work-queue.md) is created. Tasks:
1. Verify queue reflects current issue assignments
2. Create auto-refresh script for weekly Sunday refresh
3. Create the overnight prompts (this file)

### Issue #1855: Weekly AI credit utilization tracker
Create script that queries GitHub Issues for completion stats per agent, reads hermes logs for tool-call counts, outputs utilization report to notes/ai-utilization/.
Target: scripts/ai/credit-utilization-tracker.sh

### Issue #1839: Workflow hard-stops and session governance
Implement hard-stops: 200 tool-call ceiling per session, mandatory plan approval gate, pre-push review gate.
Target: scripts/governance/session-gates.sh

## What You Have By Morning

From Terminal 1 (Gemini):
  Standard mappings for 825 hydro functions + 24 structural gaps + SubseaIQ data summary

From Terminal 2 (Claude):
  Concept selection framework scaffold + floating platform stability module + SN curve promotion

From Terminal 3 (Codex 1):
  Test coverage uplifted from 2.95% toward 20% + solver queue bugs reviewed/closed

From Terminal 4 (Codex 2):
  Security scan script + config protection hook + batch-at-stop pattern

From Terminal 5 (Claude/Hermes):
  Work queue cron refresh + credit utilization tracker + session governance hard-stops

Total: 13 issues across 5 terminals. Zero file overlap. Each terminal commits independently.

Dependency notes:
  Terminal 2 work on #1811 benefits from Terminal 1 #1823 standards mapping output
  Terminal 2 work on #1842/#1849 benefits from Terminal 1 #1860 SubseaIQ data (if available in cache)
