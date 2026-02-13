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

### Batch 2 (planned)

| WRK | Title | Model | Work Type | Depends On |
|-----|-------|-------|-----------|------------|
| 138 | Fitness-for-service module | Sonnet | Engineering Python | - |
| 056 | aceengineer-admin test coverage | Haiku | Test writing | - |
| 053 | assethold test coverage | Haiku | Test writing | - |
| 136 | Operator fleet scraping | Sonnet | Web scraping | - |
| 103 | Heavy construction vessel data | Sonnet | Data schema + curation | - |
| 078 | Energy data case study | Sonnet | Technical writing | - |

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
| Engineering code | - | - | - | TBD |
| Test writing | - | - | - | TBD |
| Data curation | - | - | - | TBD |
| Technical writing | - | - | - | TBD |
| Complex porting | - | - | - | TBD |

> Updated after each batch review. Ratings populate the matrix to guide future assignments.

## Budget Optimization Rules (derived from Batch 1)

1. **Sonnet is the workhorse**: 4 of 5 tasks ran on Sonnet with avg 4.0 quality. Use as default for Route B items.
2. **Haiku for shell scripting needs guardrails**: Quality 3 — script worked but agent ran tests against real state (created orphan files). Add explicit "DO NOT test against real data" in prompts.
3. **Research/audit tasks get best ROI on Sonnet**: WRK-109 scored 5/5 — comprehensive, zero side effects, actionable findings. Research is high-value/low-risk.
4. **Integration testing prompts need refinement**: WRK-083 scored 3/5 — agent created unnecessary documentation files (EXPORT_FORMATS.md, verbose report) violating CLAUDE.md rules. Add "no new doc files" constraint.
5. **Config investigation is well-suited to agents**: WRK-054 correctly diagnosed root cause and fixed 3 config files. Agent investigation often faster than manual debugging.
6. **Always specify no-create-doc constraint**: Both WRK-083 (EXPORT_FORMATS.md) and WRK-086 (quick-reference card) proactively created documentation files. Prompt should include explicit "do not create documentation files unless the task specifically requires it."

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

## Not AI-Executable Items (66 pending, 16 excluded)

| Reason | Count | Items |
|--------|-------|-------|
| Licensed software (OrcaFlex/AQWA) | 16 | WRK-031,032,036,039,043,044,045,046,047,064,075,099,106,126,128,131 |
| Physical/admin action | 5 | WRK-005,008,050,111,133 |
| Blocked by dependencies | 5 | WRK-018,019,079,085,137 |
| Needs external data access | 5 | WRK-074,103,105,136,137 |
