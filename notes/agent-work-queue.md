# Agent Work Queue — Week of 2026-04-07

> This file is auto-generated from GitHub label queries. It is a read-only view — the `agent:` labels on issues are the source of truth.
> 
> **Source of truth**: GitHub Issues with `agent:gemini`, `agent:claude`, `agent:codex`, or `agent:any` labels.
> **Refresh**: Run `scripts/refresh-agent-work-queue.sh` or `uv run scripts/refresh-agent-work-queue.py` to regenerate this file.
> 
> **How it works**: Assign `agent:X` labels to issues → this file updates → agents pick from their lane.

---

## Queue Summary

| Agent       | High Priority | Medium Priority | Low Priority | Total |
|-------------|---------------|-----------------|--------------|-------|
| **GEMINI**  | 19            | 27              | 22           | 68    |
| **CLAUDE**  | 19            | 15              | 12           | 46    |
| **CODEX**   | 16            | 24              | 21           | 61    |
| **ANY**     | 0             | 0               | 0            | 0     |
| **UNASSIGNED** | 321        |                 |              | 321   |

> **321 issues still need agent assignment** — mostly legacy WRK items and GTM sub-tasks. These will be assigned as needed or batch-labeled in a follow-up pass.

---

## Gemini Queue (Advance Scout / Prep / Research)

### Priority: High — Start These Now

| # | Issue | What to Do |
|---|-------|------------|
| 1 | #1863 | Migrate DDE remote literature (5,456 PDFs) — reservoir eng + field dev |
| 2 | #1862 | Index 38,526 conference papers (OTC, OMAE, ISOPE, DOT, SPE) |
| 3 | #1860 | Scrape SubseaIQ field development database |
| 4 | #1823 | Map 825 hydrodynamics functions to standards |
| 5 | #1821 | Close 24 structural standards gaps (4 of 72 implemented) |
| 6 | #1776 | Review: Mount drive resource intelligence audit + legal scan restoration |
| 7 | #1772 | OCR + semantic-search index for 6 newly migrated standards orgs |
| 8 | #1769 | Phase B summarization — 394K unsummarized documents |
| 9 | #1757 | Cross-drive deduplication audit |
| 10 | #1676 | Market-Driven Repo Development Roadmap |
| 11 | #1671 | GTM: US-Wide Job Market Scan |
| 12 | #1649 | Run batch processor on live ledger — marine domain |
| 13 | #1621 | Batch-process 26 reference marine standards |
| 14 | #1612 | Expand ASTM standards-transfer-ledger |
| 15 | #1608 | Index /mnt/ace/docs/conferences/ |
| 16 | #1575 | Holistic Document & Resource Intelligence |
| 17 | #1397 | Open-source engineering software catalog |
| 18 | #1294 | Curate extracted worked examples into TDD fixtures |
| 19 | #1291 | Naval architecture knowledge extraction from SNAME |

### Priority: Medium — After High Cleared

| # | Issue | What to Do |
|---|-------|------------|
| 20 | #1865 | Acquire field development + reservoir references |
| 21 | #1864 | Acquire geotechnical textbooks (Das, Bowles, Poulos, Coduto) |
| 22 | #1825 | Create promotion feedback loop — extraction → digitalmodel → ledger |
| 23 | #1822 | Close 13 pipeline standards gaps |
| 24 | #1819 | Close 93 materials domain standards gaps |
| 25 | #1817 | Extract 4 skipped POC workbooks with streaming mode |
| 26 | #1816 | Run extraction pipeline on CONTENT_INDEX marine Excel files |
| 27 | #1771 | Index DDE-unique project files after dedup audit |
| 28 | #1770 | Expand standards-ledger — SNAME, OnePetro, BSI, Norsok |
| 29 | #1658 | Improve cross-reference match rate |
| 30 | #1655 | Apply taxonomy classifier to all domains |
| 31 | #1653 | Improve marine taxonomy coverage |
| 32 | #1651 | Extend batch processor to all domains |
| 33 | #1643 | Register OCR parser in registry |
| 34 | #1642 | Execute conference indexing Phases 2-4 |
| 35 | #1640 | Install tesseract-ocr + validate |
| 36 | #1624 | Acquire marine hydrodynamics texts (Faltinsen, Pinkster, Newman) |
| 37 | #1623 | Index /mnt/ace-data/digitalmodel/docs/domains/ |
| 38 | #1622 | Create marine sub-domain taxonomy |
| 39 | #1618 | Add DWG/DXF parser for CAD text extraction |
| 40 | #1312 | Phase 1 manual entry for ship dimensions template |
| 41 | #1295 | Promoted table curation — clean 3,683 CSVs |
| 42 | #182 | Install Semantic Scholar MCP server |
| 43 | #152 | Extract ship plan drawings via CAD pipeline |
| 44 | #140 | Research speech-to-text tool |
| 45 | #120 | Automate paper → action-item capture |
| 46 | #55 | Research chart library implementation |

### This Week's Focus (Top 7)

1. **#1823** Map 825 hydro functions → standards. This unblocks Claude's #1811 SN curve promotion.
2. **#1769** Phase B summarization batch. Highest-impact volume work (394K docs).
3. **#1860** Scrape SubseaIQ database. Feeds Claude's field development work.
4. **#1821** Structural standards gaps. Research phase before Codex implements.
5. **#1676** Job market research → repo roadmap. Informs all engineering priorities.
6. **#1671** GTM job market scan. Direct revenue impact.
7. **#1862** Conference paper index. Largest single data ingestion task.

**Dependency chain**: Gemini #1823 → Claude #1811. Gemini #1860 → Claude #1861.

---

## Claude Queue (Implementation / Architecture / Orchestration)

### Priority: High — Start These Now

| # | Issue | What to Do |
|---|-------|------------|
| 1 | #1861 | Build SubseaIQ-to-field-development bridge |
| 2 | #1859 | Integrate worldenergydata vessel fleet + hull models |
| 3 | #1858 | Integrate worldenergydata FDAS + economics |
| 4 | #1857 | **THIS ISSUE** — Rolling 1-week agent work queue |
| 5 | #1856 | Hermes quick model switching — aliases, fallbacks |
| 6 | #1855 | Weekly AI credit utilization tracker |
| 7 | #1851 | Gyradius calculator — mass distribution & inertia |
| 8 | #1850 | Floating platform stability — FPSO, semi-sub, spar, TLP |
| 9 | #1849 | Naval architecture expansion epic |
| 10 | #1844 | CAPEX/OPEX estimation models |
| 11 | #1843 | Concept selection framework |
| 12 | #1842 | Field development analysis system epic |
| 13 | #1839 | Workflow hard-stops and session governance |
| 14 | #1838 | AI credit utilization governance |
| 15 | #1814 | Promote API RP 2GEO → digitalmodel/geotechnical |
| 16 | #1812 | Promote conductor length assessment → digitalmodel |
| 17 | #1811 | Promote SN curve POC v2 → digitalmodel/fatigue |
| 18 | #1782 | Zero-loss agent learnings — git-track all memories |
| 19 | #1297 | Naval architect expert skill |
| 20 | #1296 | Naval architecture expert skill |

### Priority: Medium — After High Cleared

| # | Issue | What to Do |
|---|-------|------------|
| 21 | #1866 | Unified production client as FD data backbone |
| 22 | #1853 | Complete curves_of_form.py — hydrostatic tables |
| 23 | #1852 | Trim and ballast optimization |
| 24 | #1848 | Wire scattered modules into integrated FDP workflow |
| 25 | #1847 | Subsea architecture optimizer |
| 26 | #1846 | Facility sizing — separator, compressor, water injection |
| 27 | #1845 | Production profile generator — decline curves |
| 28 | #1841 | Geotechnical offshore gaps |
| 29 | #1840 | Geotechnical onshore foundations |
| 30 | #1815 | Promote flowback calculator → production_engineering |
| 31 | #1813 | Promote surface wellhead SITP calculation |
| 32 | #1698 | ANSYS solver queue integration |
| 33 | #1545 | Agentic feature progression |
| 34 | #72 | Calculation-implementation-workflow skill |
| 35 | #65 | Structured progress log for cross-session continuity |
| 36 | #31 | Workspace cleanup |

### This Week's Focus (Top 5)

1. **#1839** Workflow hard-stops. Gate that protects credit utilization.
2. **#1842** Field development system epic. Foundation for #1843, #1844, #1845, #1846, #1847, #1848.
3. **#1849** Naval arch expansion epic. Prerequisite for #1850, #1851, #1852, #1853, #1859.
4. **#1811** SN curve promotion (blocks on Gemini #1823 standards mapping).
5. **#1861** SubseaIQ bridge (blocks on Gemini #1860 database scrape).

**Dependency chain**: Gemini #1823 → #1811. Gemini #1860 → #1861.

---

## Codex Queue (Tests / Bounded Implementation / Review)

### Priority: High — Start These Now

| # | Issue | What to Do |
|---|-------|------------|
| 1 | #1824 | Uplift test coverage 2.95% → 20% |
| 2 | #1810 | Epic: Excel-to-code promotion — 3,600 calcs |
| 3 | #1805 | Security hardening — skill scanning, memory poisoning |
| 4 | #1803 | Context-budget audit skill |
| 5 | #1775 | Claude Code best-practice adoption — 8-week plan |
| 6 | #1628 | OrcaWave/OrcaFlex Phase 1 — solver queue + tests |
| 7 | #894 | Knowledge persistence architecture |
| 8 | #209 | Multi-agent execution contract for WRK planning |
| 9 | #113 | ROADMAP: Repo ecosystem 3-6 month horizon |
| 10 | #107 | Bulk review 38 existing open issues |
| 11 | #106 | Patch archive-item.sh for GitHub Issue creation |
| 12 | #105 | Delete HTML infrastructure |
| 13 | #104 | Wire Issue updater into stage lifecycle |
| 14 | #103 | Archive synthesis + knowledge backfill |
| 15 | #102 | GitHub Issue body template renderer |
| 16 | #86 | Enforce 200-line hard limit on SKILL.md |

### Priority: Medium — After High Cleared

| # | Issue | What to Do |
|---|-------|------------|
| 17 | #1868 | Wire Google AI Studio API into Hermes |
| 18 | #1867 | Hermes provider config maintenance |
| 19 | #1830 | Review and close solver queue bugs #1703-#1706 |
| 20 | #1827 | Extract .sim model metadata to JSON |
| 21 | #1802 | Implement batch-at-Stop pattern |
| 22 | #1801 | Adopt pre:config-protection hook |
| 23 | #1760 | Operationalize /powerup, /insights, /improve |
| 24 | #1748 | Convert agents to SKILL.md |
| 25 | #1691 | Fatigue TDD Phase 2 |
| 26 | #1299 | FreeCAD skill improvement |
| 27 | #1258 | Fix work-queue GitHub issue workflow discrepancies |
| 28 | #1249 | Propagate AGENTS.md format to child repos |
| 29 | #201 | Update /today for unused preview AI models |
| 30 | #193 | Session scanner — extract learnings from historical sessions |
| 31 | #188 | Geotechnical module umbrella tracker |
| 32 | #101 | Codex /work adapter drift |
| 33 | #63 | Review session logs, eliminate recurring errors |
| 34 | #45 | Extend workstations skill |
| 35 | #43 | Unified provider assessment + compliance audit |
| 36 | #42 | Anthropic Claude Code in Action course |
| 37 | #38 | Data pipeline framework |
| 38 | #37 | Verify Codex config on acma-ansys05 |
| 39 | #32 | Increase context window limits |
| 40 | #30 | Restore /work skill compatibility in Codex CLI |
| 41 | #12 | Consistent terminal experience across Linux + Windows |

### This Week's Focus (Top 5)

1. **#1824** Test coverage uplift (paired with Claude's implementation work).
2. **#1830** Solver queue bug fixes — bounded, high-impact cleanup.
3. **#1801** pre:config-protection hook — safety gate.
4. **#1802** batch-at-Stop pattern — session performance optimization.
5. **#1775** Claude Code best-practice adoption — structured 8-week rollout.

---

## Overnight Batch Assignment — Template

Use these terminal assignments for overnight runs:

```
Terminal 1 (h-gemini):  Research/standards mapping — top 3 from Gemini queue
Terminal 2 (h-opus):    Heavy implementation — top 3 from Claude queue  
Terminal 3 (Codex seat 1):  Test writing + bounded features — top 3 from Codex queue
Terminal 4 (Codex seat 2):  Code review + infrastructure — next 3 from Codex queue
```

**Git Contention Avoidance**: Each terminal writes different paths:
- Gemini → docs/, data/document-index/, notes/prep/ (research output)
- Claude → digitalmodel/src/, scripts/ (new code modules)
- Codex 1 → digitalmodel/tests/, tests/ (new test files)
- Codex 2 → *.md docs, CLAUDE.md, skills/ (documentation only)

Each terminal does `git pull origin main` before `git push`.

---

## Agent Definitions

| Agent | Role | Strengths | Model |
|-------|------|-----------|-------|
| **GEMINI** | Advance Scout | Large context (1M tokens), research, document ingestion, standards mapping | gemini-2.5-pro |
| **CLAUDE** | Heavy Coding | Complex reasoning, architecture, TDD, multi-step logic | claude-opus-4-6 |
| **CODEX** | Bounded Work | Test writing, bounded implementation, review, refactoring | gpt-4.1 or gpt-4o |
| **ANY** | Capacity Spillover | Any agent with free quota | first-available |

---

## Label Schema

| Label | Color | Meaning |
|-------|-------|---------|
| `agent:gemini` | F5A623 | Research, prep, large-doc ingestion, reconnaissance |
| `agent:claude` | DA552F | Heavy coding, architecture, orchestration, complex TDD |
| `agent:codex` | 3182CE | Bounded implementation, test writing, review, refactoring |
| `agent:any` | 8E54E9 | No strong preference — whichever agent has capacity |

---

## How to Reassign

```bash
# Move #1234 from Gemini to Codex
gh issue edit 1234 --remove-label "agent:gemini" --add-label "agent:codex"

# Quick list of what each agent should do
gh issue list -L 50 --label "agent:gemini,priority:high"
gh issue list -L 50 --label "agent:claude,priority:high"
gh issue list -L 50 --label "agent:codex,priority:high"
```

---

*Auto-generated from GitHub label queries. Last refresh: 2026-04-04T20:45:00Z. 175 of 496 open issues labeled. 321 issues need agent assignment (mostly legacy WRK items and GTM sub-tasks).*
