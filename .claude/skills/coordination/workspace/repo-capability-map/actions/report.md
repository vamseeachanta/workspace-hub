# Repo Capability Map: Report Action

> Generate a console summary and/or full markdown report of workspace capabilities.

## Trigger

Invoked when `/repo-capability-map report` is called, or when `--format=markdown` is passed to any subcommand.

## Prerequisites

Requires a completed scan. If no scan data exists, execute the `scan` action first.

## Procedure

### Step 1 -- Gather Data

Collect from the completed scan:
- All repo profiles with capability areas and maturity levels
- Domain groupings
- Gap analysis results (if available, otherwise run `gaps` action)

### Step 2 -- Generate Console Summary

Output a compact summary to the terminal:

```
WORKSPACE CAPABILITY MAP | YYYY-MM-DD | Repos: <count>
========================================================

DOMAIN: Engineering Analysis (ENG)
  Repos: digitalmodel, seanation, doris, saipem
  | Capability Area        | Maturity    | Lead Repo     |
  |------------------------|-------------|---------------|
  | OrcaFlex Modeling      | Mature      | digitalmodel  |
  | Mooring Design         | Mature      | digitalmodel  |
  | Fatigue Analysis       | Established | digitalmodel  |
  | Vessel Motion          | Emerging    | seanation     |

DOMAIN: Data & Analytics (DATA)
  Repos: worldenergydata, energy
  | Capability Area        | Maturity    | Lead Repo        |
  |------------------------|-------------|------------------|
  | Energy Data Pipelines  | Established | worldenergydata  |
  | Statistical Analysis   | Emerging    | energy           |

[... additional domains ...]

MATURITY DISTRIBUTION
  Mature:      ██████░░░░  12 capabilities (28%)
  Established: ████████░░  18 capabilities (42%)
  Emerging:    ████░░░░░░   8 capabilities (19%)
  Nascent:     ██░░░░░░░░   5 capabilities (12%)

GAP SUMMARY
  Covered:     24 objectives
  In Progress:  5 objectives
  Gaps:         3 objectives
  At Risk:      2 objectives
```

### Step 3 -- Generate Markdown Report

If `--format=markdown` or subcommand is `report`, generate a full markdown report.

**Output path**: `reports/capability-map/capability-report-YYYY-MM-DD.md`

Create the directory if it doesn't exist:
```bash
mkdir -p reports/capability-map
```

Use the `templates/capability-report.md` template. Fill in:

1. **Executive Summary**
   - Total repos scanned
   - Total capability areas discovered
   - Maturity distribution (counts and percentages)
   - Key findings (top 3 strengths, top 3 gaps)

2. **Domain Breakdowns**
   - One section per domain
   - Capability matrix (area × maturity × lead repo)
   - Notable observations per domain

3. **Cross-Domain Dependencies**
   - Repos that serve multiple domains
   - Shared utilities and infrastructure repos
   - Dependency chains between capability areas

4. **Gap Analysis**
   - Full gap analysis output (from `gaps` action)
   - Covered vs uncovered objectives
   - Trend comparison if previous reports exist

5. **Recommendations**
   - Prioritized list of actions
   - Each recommendation includes: priority, description, suggested approach, target repo

6. **Appendix: Per-Repo Profiles**
   - One profile per repo using `templates/repo-profile.md`

### Step 4 -- Handle Output Options

| Option | Behavior |
|--------|----------|
| `--format=console` (default) | Print summary to terminal only |
| `--format=markdown` | Generate markdown report file |
| `--format=both` | Console summary + markdown file |
| `--output=<path>` | Override default report output path |

### Step 5 -- Report Previous Comparisons

If previous reports exist in `reports/capability-map/`:
- Note date of last report
- Highlight changes: new capabilities, maturity upgrades, new gaps
- Include a "Changes Since Last Report" section in markdown output

## Output Artifacts

| Artifact | Path |
|----------|------|
| Markdown report | `reports/capability-map/capability-report-YYYY-MM-DD.md` |
| Console output | Terminal (stdout) |

## Error Handling

- No scan data: run scan inline
- Report directory creation fails: fall back to console-only output
- Previous report parsing fails: skip trend comparison, note in output
