# Repo Capability Map: Gap Analysis Action

> Identify strategic capability gaps by comparing current workspace capabilities against mission objectives.

## Trigger

Invoked when `/repo-capability-map gaps` is called, or as part of a full `/repo-capability-map report`.

## Prerequisites

Requires a completed scan (either from cache or run inline). If no scan data exists, execute the `scan` action first.

## Procedure

### Step 1 -- Load Mission Objectives

Read the workspace-level mission and strategic objectives from:

1. **Primary source**: `.agent-os/product/mission.md` (workspace root)
2. **Fallback**: `README.md` at workspace root
3. **Per-repo missions**: Each repo's `.agent-os/product/mission.md`

Extract:
- High-level mission statement
- Strategic phases and their stated goals
- Success metrics and KPIs
- Stated dependencies on capabilities

### Step 2 -- Build Objective-to-Capability Map

For each strategic objective, identify the capabilities required:

| Objective Type | Required Capabilities |
|---------------|----------------------|
| "Deliver engineering analysis" | ENG: modeling, simulation, reporting |
| "Provide data insights" | DATA: pipelines, visualization, analytics |
| "Launch client portal" | WEB: frontend, auth, API integration |
| "Automate operations" | BIZ: invoicing, CRM, workflow automation |
| "Ensure reliability" | INFRA: CI/CD, monitoring, deployment |

Map each objective to one or more capability areas from the taxonomy.

### Step 3 -- Compare Against Scan Results

For each required capability:

1. **Check existence**: Does any repo provide this capability?
2. **Check maturity**: Is the capability at sufficient maturity?
   - Objectives in current phase require maturity >= 3 (Established)
   - Future phase objectives require maturity >= 1 (Nascent, at minimum planned)
3. **Check coverage**: Is the capability covered by a single repo or distributed?

### Step 4 -- Classify Gaps

Categorize findings into:

| Category | Symbol | Definition |
|----------|--------|------------|
| **Covered** | `[x]` | Capability exists at maturity >= 3 for current objectives |
| **In Progress** | `[~]` | Capability exists at maturity 1-2, development underway |
| **Gap** | `[ ]` | Capability required but no repo addresses it |
| **At Risk** | `[!]` | Capability exists but in a dormant or unhealthy repo |

### Step 5 -- Prioritize Gaps

Rank gaps by strategic impact:

1. **Critical**: Required for current-phase objectives, no coverage
2. **High**: Required for next-phase objectives, no coverage
3. **Medium**: Required capability exists but at insufficient maturity
4. **Low**: Future-phase requirement, partially addressed

### Step 6 -- Generate Recommendations

For each gap, suggest one of:

- **New repo**: Create a new repository for this capability
- **Extend existing**: Add the capability to an existing repo (name the best candidate)
- **Upgrade maturity**: Invest in tests/docs/skills for an existing implementation
- **External tool**: Capability may be better served by a third-party tool

### Step 7 -- Format Output

Produce a gap analysis summary:

```
GAP ANALYSIS vs MISSION OBJECTIVES
===================================

Phase: [Current Phase Name]

COVERED (maturity >= 3):
  [x] Engineering asset modeling      → digitalmodel (Mature)
  [x] Mooring design                  → digitalmodel (Mature)

IN PROGRESS (maturity 1-2):
  [~] Wind energy economics           → energy (Emerging)

GAPS (no coverage):
  [ ] Client portal frontend          → No repo addresses this
  [ ] Automated reporting pipeline    → Not started

AT RISK (dormant/unhealthy):
  [!] Team resume management          → teamresumes (no recent commits)

RECOMMENDATIONS:
  1. [Critical] Create web frontend repo for client portal
  2. [High] Add reporting module to digitalmodel or create dedicated repo
  3. [Medium] Increase test coverage in energy repo
```

## Integration

- When gaps are identified, offer to create work items via `/work add`
- Reference `repository-health-analyzer` results for "At Risk" classification
- Feed gap findings into `claude-reflect` for trend tracking

## Error Handling

- Missing mission files: warn that gap analysis requires mission objectives, suggest creating `.agent-os/product/mission.md`
- Ambiguous objectives: list objectives that couldn't be mapped to capabilities, ask for clarification
- No scan data: run scan inline before proceeding
