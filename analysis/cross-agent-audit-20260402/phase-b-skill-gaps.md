# Phase B — Skill Gap Detection from Session Corpus

## Issue: #1720 | Date: 2026-04-02

---

## 0. Analysis Summary

- **50 repeating manual workflow patterns** detected across sessions
- **50 top directories** analyzed for skill coverage
- **5 directories** with NO matching skill (coverage gaps)
- **40 skill gap candidates** produced (ranked by priority)
- **27 dead skills** cover domains with active work
- **118 hot skills** never invoked in session logs (discoverability issue)

---

## 1. Multi-Step Workflow Extraction

Sequences of >=5 consecutive tool calls that don't invoke a skill, touch related
files (same directory), and repeat across >=2 sessions. These are manual workflows
that should be automated as skills.

### Top 30 Repeating Manual Workflows

| # | Domain | Steps | Occurrences | Sessions | Tool Pattern (first 8) |
|---|--------|-------|-------------|----------|------------------------|
| 1 | `/mnt` | 15 | 164 | 4 | Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bas |
| 2 | `digitalmodel/src` | 15 | 130 | 3 | Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Rea |
| 3 | `.claude/work-queue` | 15 | 57 | 3 | Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Rea |
| 4 | `.claude/skills` | 15 | 56 | 3 | Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Read → Rea |
| 5 | `vamseeachanta` | 7 | 22 | 3 | Bash → Bash → Bash → Bash → Bash → Bash → Bash |
| 6 | `digitalmodel/tests` | 5 | 19 | 2 | Read → Read → Read → Read → Read |
| 7 | `.claude/work-queue` | 15 | 17 | 2 | Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edi |
| 8 | `/mnt` | 5 | 17 | 2 | Bash → Bash → Bash → Write → Task |
| 9 | `/mnt` | 15 | 16 | 2 | Bash → Bash → Bash → Bash → Write → Bash → Bash → Bash → Bash → Bash → Bash → Ba |
| 10 | `src/digitalmodel` | 8 | 16 | 2 | Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash |
| 11 | `/mnt` | 15 | 14 | 2 | Bash → Bash → Bash → Write → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Ba |
| 12 | `/mnt` | 15 | 14 | 2 | Bash → Bash → Write → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Ba |
| 13 | `scripts/work-queue` | 9 | 13 | 2 | Write → Write → Write → Write → Write → Write → Write → Write → Write |
| 14 | `scripts/skills` | 5 | 13 | 3 | Bash → Bash → Bash → Bash → Bash |
| 15 | `repos/vamseeachanta` | 5 | 13 | 2 | Bash → Bash → Bash → Bash → Bash |
| 16 | `/mnt` | 15 | 12 | 2 | Bash → Write → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Ba |
| 17 | `examples/reporting` | 7 | 12 | 2 | Read → Read → Read → Read → Read → Read → Read |
| 18 | `scripts/cron` | 6 | 12 | 3 | Read → Read → Read → Read → Read → Read |
| 19 | `/mnt` | 15 | 11 | 2 | Write → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Ba |
| 20 | `/tmp` | 10 | 10 | 3 | Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash → Bash |
| 21 | `tests` | 7 | 10 | 2 | Bash → Bash → Bash → Bash → Bash → Bash → Bash |
| 22 | `scripts/cron` | 6 | 10 | 2 | Bash → Bash → Bash → Bash → Bash → Bash |
| 23 | `/mnt` | 12 | 9 | 2 | Write → Bash → Bash → Bash → Write → Bash → Bash → Bash → Bash → Bash → Bash → B |
| 24 | `scripts/work-queue` | 10 | 9 | 2 | Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit |
| 25 | `scripts/session` | 5 | 9 | 2 | Bash → Bash → Bash → Bash → Bash |
| 26 | `specs/wrk` | 9 | 8 | 2 | Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit → Edit |
| 27 | `/mnt` | 9 | 8 | 2 | Bash → Bash → Write → Bash → Write → Bash → Bash → Bash → Bash |
| 28 | `/mnt` | 8 | 8 | 2 | Bash → Write → Bash → Write → Bash → Bash → Bash → Bash |
| 29 | `/mnt` | 7 | 8 | 2 | Write → Bash → Write → Bash → Bash → Bash → Bash |
| 30 | `/tmp` | 5 | 8 | 2 | Read → ToolSearch → StructuredOutput → ToolSearch → Read |

**Key Observations:**

1. **digitalmodel/src** has the most manual workflow repetitions (130 occurrences)
   — bulk Read sequences suggest repeated code exploration without a discovery skill

2. **scripts/work-queue** (.claude/work-queue) shows 57 Read sequences — agents
   repeatedly scan the work queue manually instead of using a dedicated skill

3. **Bash-heavy patterns** (consecutive Bash calls) in /mnt paths indicate
   manual git/build/test cycles that could be automated

---

## 2. Skill Coverage Map

For each top directory/module worked on (from Phase A top-50 files),
is there a matching skill?

### Covered Directories (have matching skills)

| Directory | Frequency | Best Matching Skill | Coverage Depth |
|-----------|-----------|---------------------|----------------|
| `scripts/work-queue` | 2216 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `scripts/work-queue/verify-gate-evidence.py` | 790 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `.claude/skills` | 577 | SKILLS_SUMMARY (workspace-hub) | 882 |
| `scripts/work-queue/generate-html-review.py` | 365 | SKILL (CAD-DEVELOPMENTS) | 230 |
| `.claude/skills/workspace-hub` | 364 | SKILL (workspace-hub) | 882 |
| `.claude/work-queue` | 258 | SKILL (workspace-hub) | 252 |
| `/home` | 245 | SKILL (workspace-hub) | 1082 |
| `/home/vamsee` | 245 | SKILL (workspace-hub) | 1082 |
| `scripts/work-queue/start_stage.py` | 192 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `scripts/work-queue/exit_stage.py` | 187 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `scripts/data` | 174 | SKILL (workspace-hub) | 11 |
| `scripts/work-queue/whats-next.sh` | 159 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `specs/wrk` | 153 | SKILL (workspace-hub) | 2 |
| `scripts/work-queue/stages` | 134 | SKILL (workspace-hub) | 13 |
| `.claude/work-queue/assets` | 127 | SKILL (workspace-hub) | 252 |
| `assetutilities/src` | 125 | SKILL (workspace-hub) | 18 |
| `assetutilities/src/assetutilities` | 125 | SKILL (workspace-hub) | 18 |
| `scripts/work-queue/close-item.sh` | 113 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `.claude/skills/coordination` | 111 | SKILLS_SUMMARY (workspace-hub) | 882 |
| `scripts/review` | 106 | review-contract (workspace-hub) | 223 |
| `.claude/work-queue/pending` | 98 | SKILL (workspace-hub) | 252 |
| `config/scheduled-tasks` | 89 | SKILL (workspace-hub) | 6 |
| `config/scheduled-tasks/schedule-tasks.yaml` | 89 | SKILL (workspace-hub) | 192 |
| `scripts/quality` | 87 | SKILL (workspace-hub) | 3 |
| `scripts/quality/check-all.sh` | 87 | SKILL (workspace-hub) | 3 |
| `scripts/work-queue/archive-item.sh` | 79 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `scripts/work-queue/claim-item.sh` | 77 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `.claude/skills/development` | 76 | SKILLS_SUMMARY (workspace-hub) | 882 |
| `scripts/data/document-index` | 73 | SKILL (workspace-hub) | 11 |
| `.claude/settings.json` | 66 | SKILL (workspace-hub) | 389 |
| `scripts/review/cross-review.sh` | 65 | review-contract (workspace-hub) | 223 |
| `specs/wrk/WRK-658` | 61 | SKILL (workspace-hub) | 2 |
| `scripts/analysis` | 58 | SKILL (workspace-hub) | 16 |
| `scripts/data/doc_intelligence` | 49 | SKILL (workspace-hub) | 11 |
| `scripts/work-queue/verify_checklist.py` | 43 | SKILLS_SUMMARY (workspace-hub) | 12 |
| `scripts/review/submit-to-codex.sh` | 41 | review-contract (workspace-hub) | 286 |
| `scripts/knowledge/update-github-issue.py` | 41 | SKILL (workspace-hub) | 524 |
| `specs/wrk/WRK-1105` | 38 | SKILL (workspace-hub) | 2 |
| `specs/wrk/WRK-1035` | 35 | SKILL (workspace-hub) | 2 |
| `.claude/work-queue/scripts` | 33 | SKILL (workspace-hub) | 252 |
| `.claude/hooks` | 33 | SKILL (CAD-DEVELOPMENTS) | 249 |
| `.claude/hooks/enforce-active-stage.sh` | 33 | SKILL (CAD-DEVELOPMENTS) | 249 |
| `/mnt` | 33 | SKILL (workspace-hub) | 1082 |
| `/mnt/workspace-hub` | 33 | SKILL (workspace-hub) | 1082 |
| `docs/superpowers/plans` | 33 | SKILL (workspace-hub) | 4 |

### GAP: Directories WITHOUT Matching Skills

| Directory | Frequency | Impact |
|-----------|-----------|--------|
| `scripts/cron` | 119 | HIGH |
| `scripts/cron/comprehensive-learning-nightly.sh` | 62 | HIGH |
| `scripts/knowledge` | 41 | MEDIUM |
| `docs/superpowers` | 33 | MEDIUM |
| `scripts/learning` | 32 | MEDIUM |

---

## 3. Skill-to-Work Alignment

### Tier Distribution (from skill-scores.yaml, 547 skills)

| Tier | Count | Invoked in Sessions | Not Invoked |
|------|-------|--------------------:|------------:|
| **Hot** | 120 | 2 | 118 |
| **Warm** | 74 | 1 | 73 |
| **Cold** | 50 | — | — |
| **Dead** | 303 | — | 27 relevant |

**Critical finding**: Only 2/120 hot skills are
directly invoked via `tool:Read` of skill files in session logs. This suggests most
skill usage happens through auto-loading (AGENTS.md references, hooks) rather than
explicit invocation.

### Hot Skills Invoked in Sessions

| Skill | Invocations | Sessions |
|-------|------------|----------|
| cathodic-protection | 2 | 1 |
| comprehensive-learning | 2 | 1 |

### Hot Skills NEVER Invoked (Top 20 — Discoverability Concern)

| Skill | calls_in_period | Path |
|-------|----------------:|------|
| pandas-data-processing | 10 | `data/scientific/pandas-data-processing` |
| github-actions | 7 | `operations/automation/github-actions` |
| gsd-plan-phase | 7 | `gsd-plan-phase` |
| knowledge-base-builder | 7 | `data/documents/knowledge-base-builder` |
| plotly | 7 | `data/visualization/plotly` |
| api-integration | 6 | `data/scientific/api-integration` |
| competitive-analysis | 6 | `business/product/competitive-analysis` |
| data-exploration | 6 | `data/analytics/data-exploration` |
| frontend-design | 6 | `business/content-design/frontend-design` |
| knowledge-management | 6 | `business/customer-support/knowledge-management` |
| polars | 6 | `data/analysis/polars` |
| semantic-search-setup | 6 | `data/documents/semantic-search-setup` |
| streamlit | 6 | `data/analysis/streamlit` |
| tdd-obra | 6 | `development/tdd-obra` |
| webapp-testing | 6 | `development/webapp-testing` |
| yaml-configuration | 6 | `data/scientific/yaml-configuration` |
| account-research | 5 | `business/sales/account-research` |
| audit-support | 5 | `business/finance/audit-support` |
| brand-guidelines | 5 | `business/communication/brand-guidelines` |
| call-prep | 5 | `business/sales/call-prep` |

### Dead Skills Covering Active Domains (Resurrection Candidates)

| Skill | Path |
|-------|------|
| 5-trend-analysis | `_core/bash/usage-tracker/5-trend-analysis` |
| bsee-data-extractor | `data/energy/bsee-data-extractor` |
| code-review | `development/github/code-review` |
| content-quality | `_internal/builders/skill-creator/content-quality` |
| data-analysis | `data/analysis/data-analysis` |
| data-context-extractor | `data/analytics/data-context-extractor` |
| data-fetcher | `data/energy/metocean/data-fetcher` |
| data-management | `data/analysis/data-management` |
| diffraction-analysis | `engineering/marine-offshore/diffraction-analysis` |
| energy-data-visualizer | `data/energy/energy-data-visualizer` |
| environment-config | `engineering/marine-offshore/orcaflex/environment-config` |
| extreme-analysis | `engineering/marine-offshore/orcaflex/extreme-analysis` |
| fatigue-analysis | `engineering/marine-offshore/fatigue-analysis` |
| financial-analysis | `engineering/financial-analysis` |
| gsd-ui-review | `gsd-ui-review` |
| installation-analysis | `engineering/marine-offshore/orcaflex/installation-analysis` |
| json-config-loader | `_core/bash/json-config-loader` |
| jumper-analysis | `engineering/marine-offshore/orcaflex/jumper-analysis` |
| learning-from-past-work | `_core/context-management/learning-from-past-work` |
| legal-sanity-review | `_internal/workflows/legal-sanity-review` |
| modal-analysis | `engineering/marine-offshore/orcaflex/modal-analysis` |
| office-docs | `data/office/office-docs` |
| phase-1-analysis | `_internal/meta/discipline-refactor/phase-1-analysis` |
| qtf-analysis | `engineering/marine-offshore/orcawave/qtf-analysis` |
| quality-checklist | `_internal/builders/skill-creator/quality-checklist` |
| signal-analysis | `engineering/marine-offshore/signal-analysis` |
| sodir-data-extractor | `data/energy/sodir-data-extractor` |

---

## 4. Ranked Skill Gap Candidates

Combined ranking from coverage gaps, workflow patterns, dead skill resurrections,
and discoverability issues. Sorted by priority score.

| # | Source | Suggested Name | Domain | Score | Rationale |
|---|--------|----------------|--------|------:|-----------|
| 1 | workflow_pattern | **digitalmodel-src-workflow** | `digitalmodel/src` | 390 | Repeating 15-step manual workflow in 'digitalmodel/src' across 3 sessions (130 occurrences). Pattern: Read → Read → Read |
| 2 | coverage_gap | **cron-automation** | `scripts/cron` | 119 | Directory 'scripts/cron' has 119 tool calls across sessions but no matching skill. |
| 3 | workflow_pattern | **vamseeachanta-workflow** | `vamseeachanta` | 66 | Repeating 7-step manual workflow in 'vamseeachanta' across 3 sessions (22 occurrences). Pattern: Bash → Bash → Bash → Ba |
| 4 | coverage_gap | **knowledge-automation** | `scripts/knowledge` | 41 | Directory 'scripts/knowledge' has 41 tool calls across sessions but no matching skill. |
| 5 | workflow_pattern | **scripts-skills-workflow** | `scripts/skills` | 39 | Repeating 5-step manual workflow in 'scripts/skills' across 3 sessions (13 occurrences). Pattern: Bash → Bash → Bash → B |
| 6 | workflow_pattern | **digitalmodel-tests-workflow** | `digitalmodel/tests` | 38 | Repeating 5-step manual workflow in 'digitalmodel/tests' across 2 sessions (19 occurrences). Pattern: Read → Read → Read |
| 7 | coverage_gap | **superpowers-automation** | `docs/superpowers` | 33 | Directory 'docs/superpowers' has 33 tool calls across sessions but no matching skill. |
| 8 | coverage_gap | **learning-automation** | `scripts/learning` | 32 | Directory 'scripts/learning' has 32 tool calls across sessions but no matching skill. |
| 9 | workflow_pattern | **src-digitalmodel-workflow** | `src/digitalmodel` | 32 | Repeating 8-step manual workflow in 'src/digitalmodel' across 2 sessions (16 occurrences). Pattern: Bash → Bash → Bash → |
| 10 | workflow_pattern | **tmp-workflow** | `/tmp` | 30 | Repeating 10-step manual workflow in '/tmp' across 3 sessions (10 occurrences). Pattern: Bash → Bash → Bash → Bash → Bas |
| 11 | workflow_pattern | **repos-vamseeachanta-workflow** | `repos/vamseeachanta` | 26 | Repeating 5-step manual workflow in 'repos/vamseeachanta' across 2 sessions (13 occurrences). Pattern: Bash → Bash → Bas |
| 12 | workflow_pattern | **examples-reporting-workflow** | `examples/reporting` | 24 | Repeating 7-step manual workflow in 'examples/reporting' across 2 sessions (12 occurrences). Pattern: Read → Read → Read |
| 13 | workflow_pattern | **tests-workflow** | `tests` | 20 | Repeating 7-step manual workflow in 'tests' across 2 sessions (10 occurrences). Pattern: Bash → Bash → Bash → Bash → Bas |
| 14 | discoverability_gap | **pandas-data-processing-integration** | `data/scientific/pandas-data-processing` | 20 | Hot skill 'pandas-data-processing' (calls_in_period=10) is never directly invoked via Skill/skill_view in session logs.  |
| 15 | workflow_pattern | **scripts-session-workflow** | `scripts/session` | 18 | Repeating 5-step manual workflow in 'scripts/session' across 2 sessions (9 occurrences). Pattern: Bash → Bash → Bash → B |
| 16 | discoverability_gap | **github-actions-integration** | `operations/automation/github-actions` | 14 | Hot skill 'github-actions' (calls_in_period=7) is never directly invoked via Skill/skill_view in session logs. Possible  |
| 17 | discoverability_gap | **gsd-plan-phase-integration** | `gsd-plan-phase` | 14 | Hot skill 'gsd-plan-phase' (calls_in_period=7) is never directly invoked via Skill/skill_view in session logs. Possible  |
| 18 | discoverability_gap | **knowledge-base-builder-integration** | `data/documents/knowledge-base-builder` | 14 | Hot skill 'knowledge-base-builder' (calls_in_period=7) is never directly invoked via Skill/skill_view in session logs. P |
| 19 | discoverability_gap | **plotly-integration** | `data/visualization/plotly` | 14 | Hot skill 'plotly' (calls_in_period=7) is never directly invoked via Skill/skill_view in session logs. Possible discover |
| 20 | discoverability_gap | **competitive-analysis-integration** | `business/product/competitive-analysis` | 12 | Hot skill 'competitive-analysis' (calls_in_period=6) is never directly invoked via Skill/skill_view in session logs. Pos |
| 21 | discoverability_gap | **frontend-design-integration** | `business/content-design/frontend-design` | 12 | Hot skill 'frontend-design' (calls_in_period=6) is never directly invoked via Skill/skill_view in session logs. Possible |
| 22 | discoverability_gap | **knowledge-management-integration** | `business/customer-support/knowledge-management` | 12 | Hot skill 'knowledge-management' (calls_in_period=6) is never directly invoked via Skill/skill_view in session logs. Pos |
| 23 | discoverability_gap | **tdd-obra-integration** | `development/tdd-obra` | 12 | Hot skill 'tdd-obra' (calls_in_period=6) is never directly invoked via Skill/skill_view in session logs. Possible discov |
| 24 | discoverability_gap | **webapp-testing-integration** | `development/webapp-testing` | 12 | Hot skill 'webapp-testing' (calls_in_period=6) is never directly invoked via Skill/skill_view in session logs. Possible  |
| 25 | discoverability_gap | **account-research-integration** | `business/sales/account-research` | 10 | Hot skill 'account-research' (calls_in_period=5) is never directly invoked via Skill/skill_view in session logs. Possibl |
| 26 | discoverability_gap | **audit-support-integration** | `business/finance/audit-support` | 10 | Hot skill 'audit-support' (calls_in_period=5) is never directly invoked via Skill/skill_view in session logs. Possible d |
| 27 | discoverability_gap | **brand-guidelines-integration** | `business/communication/brand-guidelines` | 10 | Hot skill 'brand-guidelines' (calls_in_period=5) is never directly invoked via Skill/skill_view in session logs. Possibl |
| 28 | dead_skill_resurrection | **5-trend-analysis-revival** | `_core/bash/usage-tracker/5-trend-analysis` | 5 | Skill '5-trend-analysis' (tier=dead, path=_core/bash/usage-tracker/5-trend-analysis) covers a domain with active work. C |
| 29 | dead_skill_resurrection | **bsee-data-extractor-revival** | `data/energy/bsee-data-extractor` | 5 | Skill 'bsee-data-extractor' (tier=dead, path=data/energy/bsee-data-extractor) covers a domain with active work. Consider |
| 30 | dead_skill_resurrection | **code-review-revival** | `development/github/code-review` | 5 | Skill 'code-review' (tier=dead, path=development/github/code-review) covers a domain with active work. Consider resurrec |
| 31 | dead_skill_resurrection | **content-quality-revival** | `_internal/builders/skill-creator/content-quality` | 5 | Skill 'content-quality' (tier=dead, path=_internal/builders/skill-creator/content-quality) covers a domain with active w |
| 32 | dead_skill_resurrection | **data-analysis-revival** | `data/analysis/data-analysis` | 5 | Skill 'data-analysis' (tier=dead, path=data/analysis/data-analysis) covers a domain with active work. Consider resurrect |
| 33 | dead_skill_resurrection | **data-context-extractor-revival** | `data/analytics/data-context-extractor` | 5 | Skill 'data-context-extractor' (tier=dead, path=data/analytics/data-context-extractor) covers a domain with active work. |
| 34 | dead_skill_resurrection | **diffraction-analysis-revival** | `engineering/marine-offshore/diffraction-analysis` | 5 | Skill 'diffraction-analysis' (tier=dead, path=engineering/marine-offshore/diffraction-analysis) covers a domain with act |
| 35 | dead_skill_resurrection | **financial-analysis-revival** | `engineering/financial-analysis` | 5 | Skill 'financial-analysis' (tier=dead, path=engineering/financial-analysis) covers a domain with active work. Consider r |
| 36 | dead_skill_resurrection | **gsd-ui-review-revival** | `gsd-ui-review` | 5 | Skill 'gsd-ui-review' (tier=dead, path=gsd-ui-review) covers a domain with active work. Consider resurrecting or merging |
| 37 | dead_skill_resurrection | **learning-from-past-work-revival** | `_core/context-management/learning-from-past-work` | 5 | Skill 'learning-from-past-work' (tier=dead, path=_core/context-management/learning-from-past-work) covers a domain with  |
| 38 | dead_skill_resurrection | **legal-sanity-review-revival** | `_internal/workflows/legal-sanity-review` | 5 | Skill 'legal-sanity-review' (tier=dead, path=_internal/workflows/legal-sanity-review) covers a domain with active work.  |
| 39 | dead_skill_resurrection | **office-docs-revival** | `data/office/office-docs` | 5 | Skill 'office-docs' (tier=dead, path=data/office/office-docs) covers a domain with active work. Consider resurrecting or |
| 40 | dead_skill_resurrection | **phase-1-analysis-revival** | `_internal/meta/discipline-refactor/phase-1-analysis` | 5 | Skill 'phase-1-analysis' (tier=dead, path=_internal/meta/discipline-refactor/phase-1-analysis) covers a domain with acti |

---

## 5. Recommendations

### Immediate Actions (HIGH priority)

1. **Create `digitalmodel-code-explorer` skill** — The most-repeated manual workflow
   (130 occurrences) is bulk-reading digitalmodel source files. A skill that indexes
   the module structure and provides quick discovery would eliminate massive redundancy.

2. **Create `cron-job-management` skill** — scripts/cron has 119 tool calls with
   no matching skill. Agents manually configure, test, and troubleshoot cron jobs.

3. **Create `scripts-knowledge-pipeline` skill** — scripts/knowledge (41 calls)
   and scripts/learning (32 calls) represent knowledge pipeline maintenance without
   skill coverage.

4. **Improve skill discoverability** — 118/120 hot skills are never directly invoked
   via explicit skill reads. Either auto-loading is working perfectly (good) or agents
   don't know these skills exist (bad). Audit needed.

### Medium Priority

5. **Resurrect `diffraction-analysis` skill** — Dead skill covering active OrcaWave work.

6. **Resurrect `extreme-analysis` skill** — Dead skill covering active OrcaFlex domain.

7. **Create `test-runner` skill** — digitalmodel/tests has 19 occurrences of manual
   test exploration. A skill for the common test→debug→fix cycle would help.

8. **Consolidate reporting workflow** — examples/reporting shows 12 occurrences of
   a 7-step manual workflow (Read+Bash sequences).

### Low Priority / Monitoring

9. **Dead skill audit** — 27 dead skills cover active domains. Review each for
   merger into live skills or full resurrection.

10. **Warm skill promotion** — 73 warm skills not invoked; assess if any should
    be promoted to hot or demoted to cold.

---

## Intermediate Data Files

All data saved to `analysis/cross-agent-audit-20260402/phase-b-data/`:

- `repeating_workflows.json`
- `skill_catalog.json`
- `skill_coverage_map.json`
- `skill_alignment.json`
- `gap_candidates.json`