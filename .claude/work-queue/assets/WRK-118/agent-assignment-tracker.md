# Agent Assignment Tracker

> Tracks AI agent assignments, work types, and quality ratings to optimize budget utilization.

## Model Tier Strategy

| Model | Cost Ratio | Assignment Rule | Best For |
|-------|-----------|-----------------|----------|
| **Haiku** | 1x | Route A, clear-scope scripts, config edits | Shell scripts, YAML, simple tests, audits |
| **Sonnet** | 5x | Route B, well-scoped code, data pipelines | Code + tests, medium analysis, CI/CD |
| **Opus** | 15x | Route C, architecture, multi-repo engineering | Complex porting, engineering analysis, multi-repo |

## Execution Log

### Batch 1 (2026-02-13) — COMPLETE

| WRK | Title | Model | Work Type | Quality (1-5) | Status | Notes |
|-----|-------|-------|-----------|---------------|--------|-------|
| 134 | Future-work brainstorming hook | Haiku | Shell scripting | **3** | done | suggest-future-work.sh (380 lines) + archive-item.sh edit. Fixed bugs in script. Side effect: ran tests against real data, created orphan WRK-134.md at root (cleaned up). |
| 086 | Rewrite CI workflows | Sonnet | GitHub Actions YAML | **4** | done | Deleted 3 obsolete workflows, rewrote 2. 83% code reduction (1,734→248 lines). YAML validated. Created verbose quick-reference card (unnecessary). |
| 054 | Test coverage config fix | Sonnet | pytest config | **4** | done | Root cause: .coveragerc measured `src/` not `src/worldenergydata/`. Fixed .coveragerc, pytest.ini, pyproject.toml. True coverage: 1.97% (full scope) → 8.73% (unit tests only). |
| 109 | Audit hooks & skills | Sonnet | Research/inventory | **5** | done | Comprehensive audit: 446 skills, 13 hook scripts, 405 commands, 3 repos. Found 2 broken post-commit hooks (hardcoded paths), 16MB state accumulation. Zero side effects. |
| 083 | Multi-format export validation | Sonnet | Integration testing | **3** | done | 9/10 tests pass (PDF skip). Created test_multi_format_export.py + validation report. Side effects: created EXPORT_FORMATS.md (violates CLAUDE.md, removed) + verbose docs. |
| 124 | Session cleanup | Manual | Triage/archive | n/a | done | Archived manually pre-batch. |

**Batch 1 Summary**: 5 agents completed, avg quality 3.8/5.0. One 5-star (research/audit), two 4-star (CI + config), two 3-star (shell scripting + integration). Haiku adequate for shell scripting but needs tighter guard rails to prevent test side effects.

### Batch 2 (2026-02-13) — COMPLETE

| WRK | Title | Model | Work Type | Quality (1-5) | Status | Notes |
|-----|-------|-------|-----------|---------------|--------|-------|
| 138 | Fitness-for-service module | Sonnet | Engineering Python | **4** | done | Phase 0 audit correct scope. Fixed B31G import bug, found legal refs ("Client Asset"), 17 tests. Module needs rename before full impl. |
| 056 | aceengineer-admin test coverage | Haiku | Test writing | **5** | done | Best Haiku result: 87%→94% coverage, 69 new tests, 356 total passing. cli.py 100%. Zero side effects. |
| 053 | assethold test coverage | Haiku | Test writing | **4** | done | 26%→45% coverage, 60 new tests, engine.py 0→100%. Created COVERAGE_BASELINE.md (cleaned up), otherwise solid. |
| 103 | Heavy construction vessel schema | Sonnet | Data schema + loader | **5** | done | 10 seed vessels, 60 tests, loader + schema + data catalog update. Self-committed in submodule. Clean execution. |
| 078 | Energy data case study | Sonnet | Technical writing | **4** | done | Case study HTML + data script + nav updates. Legal scan passed. Minor artifact: coverage/ dir (cleaned up). |
| ~~136~~ | ~~Operator fleet scraping~~ | - | - | - | dropped | File does not exist in pending/ |

**Batch 2 Summary**: 5 agents completed, avg quality 4.4/5.0 (up from 3.8 in Batch 1). Two 5-star (test writing + data schema), three 4-star (engineering code + test writing + technical writing). Haiku performed significantly better with refined prompts — one 5-star result. No-doc constraint mostly effective (1 of 5 created unnecessary doc vs 3 of 5 in Batch 1).

### Batch 3 (planned — complex items)

| WRK | Title | Model | Work Type | Depends On |
|-----|-------|-------|-----------|------------|
| 051 | digitalmodel test coverage | Opus | Test infrastructure | - |
| 052 | assetutilities test coverage | Opus | Test infrastructure | - |
| 072 | Technical safety (ENIGMA port) | Opus | ML/NLP porting | Legal scan |
| 110 | Hull library expansion | Opus | Engineering data | - |
| 074 | Marine safety importers | Sonnet | Data validation | External access |

## Quality Rating Scale

| Score | Meaning | Action |
|-------|---------|--------|
| 5 | Perfect — no corrections needed | Use same model for similar tasks |
| 4 | Good — minor edits needed | Model appropriate, refine prompt |
| 3 | Acceptable — moderate rework | Consider upgrading model tier |
| 2 | Poor — significant rework | Upgrade model tier or restructure task |
| 1 | Failed — had to redo from scratch | Wrong model or task too complex for agent |

## Work Type Performance Matrix

| Work Type | Haiku | Sonnet | Opus | Recommended |
|-----------|-------|--------|------|-------------|
| Shell scripting | 3 (WRK-134) | - | - | Sonnet (Haiku needs guardrails) |
| GitHub Actions | - | 4 (WRK-086) | - | Sonnet |
| pytest config | - | 4 (WRK-054) | - | Sonnet |
| Research/audit | - | 5 (WRK-109) | - | Sonnet |
| Integration testing | - | 3 (WRK-083) | - | Sonnet (refine prompts) |
| Engineering code | - | 4 (WRK-138) | - | Sonnet (good at scoping, finds bugs) |
| Test writing | 5 (WRK-056), 4 (WRK-053) | - | - | **Haiku** (excellent ROI, avg 4.5) |
| Data schema + loader | - | 5 (WRK-103) | - | Sonnet |
| Technical writing | - | 4 (WRK-078) | - | Sonnet |
| Complex porting | - | - | - | TBD |

> Updated after each batch review. Ratings populate the matrix to guide future assignments.

## Budget Optimization Rules (derived from Batches 1+2)

1. **Sonnet is the workhorse**: 7 of 10 tasks ran on Sonnet with avg 4.1 quality. Use as default for Route B items.
2. **Haiku excels at test writing**: WRK-056 scored 5/5, WRK-053 scored 4/5 — avg 4.5 for test writing at 1/5th Sonnet cost. **Best ROI discovery**: assign all test coverage tasks to Haiku.
3. **Research/audit tasks get best ROI on Sonnet**: WRK-109 scored 5/5 — comprehensive, zero side effects, actionable findings. Research is high-value/low-risk.
4. **No-doc constraint is effective but imperfect**: Batch 2 reduced doc side effects from 60% (3/5) to 20% (1/5). Keep the constraint; accept occasional cleanup.
5. **Config investigation is well-suited to agents**: WRK-054 correctly diagnosed root cause and fixed 3 config files. Agent investigation often faster than manual debugging.
6. **Engineering code benefits from Phase 0 scoping**: WRK-138 correctly identified module needs rename before full impl. Complex engineering tasks benefit from audit-first approach.
7. **Data schema tasks are Sonnet sweet spot**: WRK-103 scored 5/5 — schema + loader + seed data + tests + self-committed. Perfect agent task.
8. **Refined prompts improve Haiku significantly**: Batch 1 Haiku avg 3.0, Batch 2 Haiku avg 4.5 (after prompt refinements). Explicit constraints work.
9. **Always specify no-create-doc constraint**: Prompt should include "do not create documentation files unless the task specifically requires it."
10. **Batch 2 avg 4.4 vs Batch 1 avg 3.8**: Prompt refinement between batches yields measurable quality improvement.

## Batch 1 Deliverables Inventory

### Files Created
- `.claude/work-queue/scripts/suggest-future-work.sh` (380 lines, WRK-134)
- `worldenergydata/tests/modules/bsee/reports/test_multi_format_export.py` (WRK-083)
- `worldenergydata/docs/wrk-083-export-validation-report.md` (WRK-083)

### Files Modified
- `.claude/work-queue/scripts/archive-item.sh` (WRK-134: --no-suggest flag, suggest integration)
- `.github/workflows/baseline-check.yml` (WRK-086: Python rewrite)
- `.github/workflows/multi-ai-review.yml` (WRK-086: cross-review integration)
- `worldenergydata/.coveragerc` (WRK-054: source path fix)
- `worldenergydata/pytest.ini` (WRK-054: cov path fix, timeout removal)
- `worldenergydata/pyproject.toml` (WRK-054: coverage source fix)

### Files Deleted
- `.github/workflows/baseline-audit.yml` (WRK-086: redundant)
- `.github/workflows/refactor-analysis.yml` (WRK-086: one-off)
- `.github/workflows/phase1-consolidation.yml` (WRK-086: completed task)

### Cleaned Up (by orchestrator)
- `WRK-134.md` at workspace root (orphan from Haiku agent test)
- `worldenergydata/EXPORT_FORMATS.md` (unnecessary doc file from WRK-083 agent)

### Key Findings (from WRK-109 audit)
- 2 broken git post-commit hooks in worldenergydata + digitalmodel (hardcoded `/mnt/github/` path)
- 16MB state accumulation in `.claude/state/` without cleanup
- 446 total skills across 3 repos (301 active in workspace-hub)

## Batch 2 Deliverables Inventory

### Submodule Commits
- `aceengineer-admin` → `c4ce9d3` (WRK-056: 69 new tests, 87%→94% coverage)
- `assethold` → `a57fe65` (WRK-053: 60 new tests, 26%→45% coverage)
- `aceengineer-website` → `ad6741f` (WRK-078: BSEE field economics case study)
- `digitalmodel` → `412a2393c` (WRK-138: FFS Phase 0 audit, 17 tests, B31G fix)
- `worldenergydata` → `2810475` (WRK-103: vessel schema + 10 seed vessels + 60 tests)

### Files Created (by agents)
- `aceengineer-admin/aceengineer_admin/tests/test_cli.py` expanded (56→458 lines, WRK-056)
- `aceengineer-admin/tests/knowledge/test_knowledge_config.py` (307 lines, WRK-056)
- `aceengineer-admin/aceengineer_admin/tests/common/test_config_extended.py` (247 lines, WRK-056)
- `assethold/tests/unit/test_engine.py` (420 lines, WRK-053)
- `assethold/tests/unit/test_common_data.py` (483 lines, WRK-053)
- `aceengineer-website/src/case-studies/bsee-field-economics.html` (499 lines, WRK-078)
- `aceengineer-website/scripts/generate_field_economics_data.py` (WRK-078)
- `digitalmodel/.../tests/test_api579_calculations_standalone.py` (262 lines, WRK-138)
- `worldenergydata/.../vessel_fleet/loaders/construction_vessel_loader.py` (371 lines, WRK-103)
- `worldenergydata/data/modules/vessel_fleet/curated/` (seed data, WRK-103)

### Cleaned Up (by orchestrator)
- `assethold/COVERAGE_BASELINE.md` (unnecessary doc from WRK-053 Haiku agent)
- `aceengineer-website/coverage/` (spurious artifact from WRK-078 agent)

## Cumulative Statistics (Batches 1+2)

| Metric | Batch 1 | Batch 2 | Total |
|--------|---------|---------|-------|
| Agents executed | 5 | 5 | 10 |
| Avg quality | 3.8 | 4.4 | 4.1 |
| Side effects cleaned | 2 | 2 | 4 |
| Perfect scores (5/5) | 1 | 2 | 3 |
| Submodule commits | 1 | 5 | 6 |
| New test files | 1 | 7 | 8 |

## Not AI-Executable Items (66 pending, 16 excluded)

| Reason | Count | Items |
|--------|-------|-------|
| Licensed software (OrcaFlex/AQWA) | 16 | WRK-031,032,036,039,043,044,045,046,047,064,075,099,106,126,128,131 |
| Physical/admin action | 5 | WRK-005,008,050,111,133 |
| Blocked by dependencies | 5 | WRK-018,019,079,085,137 |
| Needs external data access | 5 | WRK-074,103,105,136,137 |
