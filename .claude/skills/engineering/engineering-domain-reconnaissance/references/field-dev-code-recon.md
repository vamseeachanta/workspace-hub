# Archived Skill: `field-dev-code-recon`

Original path: `/home/vamsee/.hermes/skills/field-dev-code-recon`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/field-dev-code-recon`
Consolidation date: 2026-04-29

---

---
name: field-dev-code-recon
description: Extract field development information from external sources (LinkedIn posts, technical content), map against digitalmodel codebase coverage, document gaps, and create actionable GitHub issues.
category: workflow
tags: [field-development, reconnaissance, github-issues, coverage-mapping]
effort: 2h
model: haiku
---

# Field Development Code Reconnaissance

## Trigger

User asks to review field development content from external sources (LinkedIn posts, articles, documentation) and extract actionable intelligence with codebase mapping.

## Workflow

### Phase 1: Content Extraction

1. Use browser_navigate to load the source URL
2. Dismiss sign-in dialogs (click @e1 button if present)
3. Use browser_snapshot with full=true to capture complete content
4. Extract: component names, standards references, operational workflows, hazards, mitigations
5. Close browser when done

### Phase 2: Code Coverage Mapping

Map extracted components against digitalmodel using STRONG/PARTIAL/NO coverage tiers:

- **STRONG**: Native Python module with tests covering the functionality
- **PARTIAL**: OrcaFlex skill only, incomplete module, or partial standards coverage
- **NO COVERAGE (GAP)**: No code exists at all

Use this terminal command to survey top-level modules (filtering out noise):
```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
find src/digitalmodel -mindepth 1 -maxdepth 2 -type d | sort
```
The output is clean — only top-level subpackages, no .mypy_cache, .venv, tests/, web/, or __pycache__ noise.

For deep inspection of a specific module:
```bash
find src/digitalmodel/<module> -name '*.py' -not -path '*/__pycache__/*' | sort
```

For standards/skills coverage:
```bash
skills_list  # in Python/hermes context
```

Mapping template:
| Component | Standard/Ref | Coverage | digitalmodel Module |
|-----------|-------------|----------|-------------------|
| ...       | API 17D      | STRONG   | subsea/trees/     |
| ...       | DNV-RP-F101 | PARTIAL  | (skill only)      |
| ...       | --          | GAP      | --                |

### Phase 3: Documentation

Create `docs/field-development/<topic-name>-mapping.md` with:
- Source descriptions and extraction date
- Component inventory with standards references
- Operational workflow diagrams (ASCII)
- Full coverage map (STRONG/PARTIAL/GAP tables)
- API/standards quick reference table
- Architecture diagram (ASCII) showing component relationships
- Issue tracker table linking each GAP to its GitHub issue number

ALSO create a GitHub milestone to group all related issues:
```bash
gh api repos/vamseeachanta/digitalmodel/milestones \
  --method POST \
  --field title="Descriptive Milestone Name" \
  --field description="Scope description" \
  --field state=open
```
Returns milestone `number` (e.g., 1). Assign all new issues:
```bash
gh api repos/vamseeachanta/digitalmodel/issues/<ISSUE_NUM> \
  --method PATCH --field milestone=<MILESTONE_NUM>
```
For multiple issues, loop over the issue numbers.

### Phase 4: Issue Creation

Create one GitHub issue per GAP or significant PARTIAL component:

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
gh issue create \
  --title "Implement <component name> (<standard ref>)" \
  --label "cat:engineering,enhancement,priority:medium" \
  --body "<structured body>"
```

Issue body must include:
- Background/context linking to the mapping doc
- Problem statement
- Scope (module path, key capabilities)
- Acceptance criteria (checklist of files to create)
- Standards references
- Related issues

### Phase 5: Commit & Push

```bash
git add docs/field-development/
git commit -m "docs: <topic> coverage mapping (#issue-numbers)"
git push
```

## Pitfalls

- `search_files` with very broad paths (entire workspace) hits output limits AND can error with JSON decode — avoid it entirely for filesystem exploration. Use `terminal` find commands in digitalmodel/src/ instead.
- `find src/digitalmodel -name '*.py'` returns thousands of lines including .mypy_cache, .venv, __pycache__, tests/, web/ — filter carefully.
- `gh milestone create` may fail (not supported by older gh versions) — use `gh api repos/<owner>/<repo>/milestones --method POST --field title="Name" --field description="Desc" --field state=open` to create, then assign issues one at a time via `gh api repos/<owner>/<repo>/issues/<N> --method PATCH --field milestone=<M>`.
- Don NOT create issues for STRONG coverage areas
- Prioritize medium over low for core subsea components, low for operational/installation topics
- All issues should reference the mapping doc at top of body
- Commit documentation BEFORE creating issues (or reference pending issue numbers)

## Standards Quick Reference

API 17 subsea: 17A=General, 17B=Flexible pipe, 17D=Trees, 17E=Umbilicals, 17F=Controls, 17G=Workover riser, 17H=ROV interface, 17P=Manifolds/Structures, 17R=Connectors/Jumpers, 17W=Capping stack

Key DNV standards: DNV-OS-F101 (pipe), DNV-RP-F105 (free span), DNV-RP-F109 (on-bottom), DNV-RP-B401 (CP), DNV-RP-H103 (hydro), DNV-ST-N001 (marine ops)
