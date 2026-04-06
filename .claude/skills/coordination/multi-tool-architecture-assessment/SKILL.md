---
name: multi-tool-architecture-assessment
description: Systematic comparison of competing tools/approaches before committing to a multi-account, multi-tool architecture. Uses parallel subagents for research, system-state audit, and data quality analysis. Produces a decision matrix with explicit trade-offs.
version: 1.0.0
author: vamsee
tags: [architecture, tool-selection, assessment, parallel-research, decision-matrix]
metadata:
  hermes:
    tags: [architecture, tool-selection, assessment, parallel-research]
---

# Multi-Tool Architecture Assessment

Pattern: When choosing between 3+ competing approaches for a feature area, DO NOT guess. Systematically assess all options with parallel research before committing.

## When to Use
- Choosing between multiple tools, libraries, or approaches
- Need to support multiple accounts, tenants, or personas differently
- Existing tools have partial coverage but no single winner
- Decision will block dependent work for weeks

## Step Pattern (Parallel 3-Agent)

### Agent 1: External Research
Research all available tools/approaches on the open market.
```
goal: "Research [tool category] options. Check: 1) GitHub repos, 2) npm/PyPI packages, 
  3) Star counts and download stats. Compare: setup complexity, multi-account support, 
  feature completeness, auth methods. Provide a comparison table with recommendation."
toolsets: ["web", "terminal"]
```

### Agent 2: System State Audit
Check what's installed/missing locally.
```
goal: "Check current state of [tool candidates] on this machine. Run: which commands, 
  check config dirs, check for tokens/credentials, check installed packages, verify skill 
  scripts exist and their dependencies. Report exact state."
toolsets: ["terminal", "file"]
```

### Agent 3: Data Quality Analysis
Analyze the actual data the tools will operate on.
```
goal: "Analyze the input data files for [feature]. Check: row counts, data quality issues, 
  encoding, duplicates, missing fields, domain distribution. Recommend normalization steps."
toolsets: ["terminal", "file"]
```

### Synthesis
Combine results into:
1. Decision matrix table (approach × criteria)
2. Primary + fallback selection with rationale
3. Execution plan with phases and dependencies
4. Concrete GitHub issues (one per phase/component)

## Output Template
```
TOOL ASSESSMENT — WINNER: [primary] + [fallback]
================================================================

Evaluated N approaches:
| Approach | Multi | Setup | Auth | Feature X | Verdict |
| ... | ... | ... | ... | ... | ... |

CHOSEN (primary):  [name]
  - Reason 1
  - Reason 2

CHOSEN (fallback):  [name]
  - For [specific use case]

REJECTED:
  - [name]: reason
  - [name]: reason

KEY GAPS: [what no tool does natively]

EXECUTION PLAN — 3 PHASES
================================================================

 PHASE 1: Infrastructure (BLOCKING)
 PHASE 2: Data/Migration (PARALLEL)
 PHASE 3: Workflow/Feature (after 1+2)

AGENT ASSIGNMENT
================================================================
```

## Pitfalls
1. Don't pick the most popular tool — pick the one matching constraints (multi-account, CLI-only, etc.)
2. Always pick a fallback (not everything needs to go through the "primary" tool)
3. Identify what NO tool does — those become custom scripts/parsers you need to write
4. If data is messy (80%+ uncategorized), plan normalization BEFORE workflows
5. External repos may be in separate git clones or submodules — commit changes from within each repo
6. Don't block all work on the hardest-to-set-up component — run parallel work on data/prep
7. For skills: write-back to both ~/.hermes/skills/ AND .claude/skills/ in repo (per WRITE-BACK RULE)
