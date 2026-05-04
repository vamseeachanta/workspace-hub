---
name: domain-gap-to-issue-roadmap
description: "Deep multi-repo ecosystem audit \u2192 domain gap matrix \u2192 structured\
  \ GitHub issue roadmap with epics. Use when the user wants to assess capabilities\
  \ across repos and create a backlog of work items covering code, data, and documentation\
  \ gaps."
version: 1.0.0
category: github
type: skill
trigger: manual
related_skills:
- issue-portfolio-triage
- dark-intelligence-workflow
- research-literature
tags:
- ecosystem-audit
- issue-creation
- gap-analysis
- roadmap
- field-development
- naval-architecture
- geotechnical
---

# Domain Gap → Issue Roadmap

> Audit engineering domains across a multi-repo ecosystem, map what exists vs what's missing
> (code, data, standards, documentation), then create structured GitHub issues organized
> into epics and phases.

## When to Use

- User asks to "assess", "map", or "inventory" capabilities across repos
- User wants GitHub issues for future work based on gap analysis
- Multiple repos contribute to the same engineering domain (e.g., digitalmodel + worldenergydata)
- Dark intelligence / Excel extraction needs to be mapped against existing code
- User wants to understand code-vs-data-vs-documentation coverage

## Methodology — 3 Phases

### Phase 1: Parallel Deep Audit (delegate_task with 3 subagents)

Spawn 3 parallel subagents, each covering a different investigation axis:

**Subagent 1 — Code & Extraction Inventory**
- Search for all source files by domain (module counts, function counts, LOC)
- Find dark-intelligence extraction outputs (YAML archives, calculations.py stubs)
- Map extraction pipeline scripts and their current state
- Identify what's been extracted but NOT promoted to code

**Subagent 2 — Conversion Infrastructure & Data Assets**
- Search for Excel files, scraping outputs, CSV databases
- Find existing conversion scripts and their capabilities
- Map data registries, catalogs, and indexes
- Check external data sources (SubseaIQ, BSEE, SODIR, etc.)

**Subagent 3 — Standards, Documentation & Module Registries**
- Search standards-transfer-ledger for done/gap/reference status
- Find domain coverage reports and capability vision docs
- Map downloaded vs cataloged-only reference documents
- Identify test coverage by domain

### Phase 2: Cross-Reference & Gap Matrix

After subagent results return, build the gap matrix:

```
Domain | Code Files | Standards Done/Gap | Excel Sources | Extractions | Tests | Docs
-------|-----------|-------------------|---------------|-------------|-------|-----
struct |    166    |     12/24         |     yes       |    2 POC    | some  | good
hydro  |    154    |      0/0          |     yes       |    none     | some  | good
geotech|      4    |      2/0          |     1 yaml    |    1 POC    | some  | weak
...
```

Key cross-references to build:
- Excel dark intelligence → existing code modules (what's extracted but not wired?)
- Standards ledger gaps → code gaps (which standards have no implementation?)
- Documentation → code (which docs have no corresponding module?)
- Data sources → analysis modules (which data exists but isn't used?)
- Cross-repo overlap (worldenergydata economics vs digitalmodel field_dev)

### Phase 3: Structured Issue Creation

#### Issue Hierarchy Pattern
```
Epic (domain-level)
├── Phase 1: Wire existing extractions (quick wins)
├── Phase 2: Batch extraction (new data processing)
├── Phase 3: Systematic gap closure (standards-driven)
├── Phase 4: Infrastructure & test coverage
├── Cross-repo integration issues
├── Data acquisition issues
└── Documentation gap issues
```

#### Issue Creation Best Practices (learned from experience)

1. **Use execute_code for batch creation** — 10+ issues in one script with shlex.quote
   for shell safety. Each issue gets title, labels, and full body.

2. **Label taxonomy** — use existing labels, check with `gh label list` first:
   - `dark-intelligence` for extraction/promotion work
   - `domain:code-promotion` for Excel→code wiring
   - `domain:extraction-pipeline` for new extractions
   - `cat:engineering-calculations` for calculation implementations
   - `cat:data-pipeline` for data processing
   - `cat:document-intelligence` for documentation work
   - `priority:high/medium/low` for triage

3. **Epic body structure** — include:
   - Current state summary with metrics
   - Vision statement
   - Child issue list with `#number` references
   - Related epics cross-references
   - Key reference file paths

4. **Work item body structure** — include:
   - ### What (one sentence)
   - ### Source (where the input data/code lives)
   - ### Target (where the output goes)
   - ### Scope (checkboxes for each deliverable)
   - ### Acceptance Criteria (testable conditions)
   - ### Standards (applicable codes/standards)

5. **Update epics AFTER creating children** — use gh issue edit to add child
   issue references. Do this in a second pass, not inline.

6. **Onshore vs Offshore split** — for geotechnical and other domains where
   onshore/offshore have different standards, split into separate issues early.
   The user expects this distinction.

7. **Cross-repo integration issues** — when Module A in repo X feeds Module B
   in repo Y, create explicit "wire X into Y" issues. Don't assume the
   connection is obvious.

## Pitfalls

1. **SubseaIQ assumption** — user may believe data was scraped that doesn't exist.
   Always verify with `search_files` + `git log --all -S` before creating
   "process existing data" issues. Create "scrape fresh" issues instead.

2. **worldenergydata is massive** — 1,021 Python files, 27 modules. Don't just
   search workspace-hub; always check worldenergydata separately. It often has
   economics/production/vessel modules that duplicate or complement digitalmodel.

3. **Standards transfer ledger is THE source of truth** for what's done vs gap.
   Path: `data/document-index/standards-transfer-ledger.yaml` (425+ entries).

4. **Dark intelligence outputs are gitignored** — the knowledge/dark-intelligence/
   directory has extraction results that exist on disk but not in git. Don't
   assume they're missing just because grep of tracked files shows nothing.

5. **Conference papers (38K+) are 0% indexed** — always flag this as a data
   acquisition priority. It's the highest-value unprocessed resource.

6. **Test coverage is very low** (digitalmodel 2.95%) — every issue should
   include a test deliverable, not just code.

## Verification

After creating all issues:
- `gh issue list --label dark-intelligence` to verify labels applied
- Check epic bodies have correct `#number` cross-references
- Verify no duplicate issues (search titles before creating)
- Count total issues created and report summary to user

## Output Format

Always end with a structured summary:
```
TOTAL: N issues (M epics + K work items)

EPIC #XXXX — Title
  #YYYY  Child issue title                    priority:level
  ...

CROSS-CUTTING
  #ZZZZ  Data/doc issue                       priority:level
  ...

KEY FINDINGS
  1. Finding that changes the user's understanding
  2. ...
```
