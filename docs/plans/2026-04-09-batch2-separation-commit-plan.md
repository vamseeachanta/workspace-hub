# Batch 2 Separation / Commit Plan — 2026-04-09

Scope: safely separate and commit the mixed working-tree changes produced by Claude Batch 2 for issues #2057, #2054, and #2058.

Repo roots:
- workspace-hub: `/mnt/local-analysis/workspace-hub`
- digitalmodel: `/mnt/local-analysis/workspace-hub/digitalmodel`
- worldenergydata: `/mnt/local-analysis/workspace-hub/worldenergydata`

## 1. Verified current state

### #2057 — workspace-hub
Verified complete pieces:
- `tests/skills/test_session_start_routine_smoke.py`
- `tests/skills/test_session_corpus_audit_smoke.py`
- `tests/skills/test_comprehensive_learning_smoke.py`
- `tests/skills/test_cross_review_policy_smoke.py`
- `docs/governance/SESSION-GOVERNANCE.md` updated with Phase 3e section
- verification passed: `uv run pytest tests/skills/test_*_smoke.py -v` → 9 passed

Verified missing piece:
- The 5 broken `session-start-routine` links in `.claude/skills/...` are STILL UNFIXED.
- So #2057 is partial, not truly close-ready.

### #2054 — digitalmodel
Verified present:
- `src/digitalmodel/field_development/economics.py`
- `tests/field_development/test_economics.py`
- verification passed: `PYTHONPATH=src uv run python -m pytest tests/field_development/test_economics.py -v` → 74 passed

### #2058 — digitalmodel + worldenergydata
Verified present:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`
- `digitalmodel/tests/field_development/test_architecture_patterns.py`
- `worldenergydata/subseaiq/analytics/normalize.py`
- verification passed: `PYTHONPATH=src uv run python -m pytest tests/field_development/test_benchmarks.py tests/field_development/test_architecture_patterns.py -v` → 77 passed

## 2. Mixed working tree inventory

### workspace-hub working tree (relevant to Batch 2)
Keep for #2057:
- `docs/governance/SESSION-GOVERNANCE.md`
- `tests/skills/test_session_start_routine_smoke.py`
- `tests/skills/test_session_corpus_audit_smoke.py`
- `tests/skills/test_comprehensive_learning_smoke.py`
- `tests/skills/test_cross_review_policy_smoke.py`

Required-but-still-missing #2057 changes:
- `.claude/skills/_internal/meta/repo-cleanup/SKILL.md`
- `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md`
- `.claude/skills/_internal/meta/module-based-refactor/SKILL.md`
- `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md`
- `.claude/skills/_internal/builders/skill-creator/SKILL.md`

Ignore for Batch 2 commit planning:
- all current unrelated workspace-hub modifications under `.claude/state/`, `scripts/analysis/`, `docs/reports/claude-session-ecosystem-audit-*`, `tests/analysis/`, etc.

### digitalmodel working tree
Relevant to #2054:
- `src/digitalmodel/field_development/economics.py`
- `tests/field_development/test_economics.py`

Relevant to #2058:
- `src/digitalmodel/field_development/benchmarks.py`
- `src/digitalmodel/field_development/architecture_patterns.py`
- `tests/field_development/test_benchmarks.py`
- `tests/field_development/test_architecture_patterns.py`

Unrelated / do not bundle with #2054 or #2058:
- `src/digitalmodel/drilling_riser/__init__.py`
- `src/digitalmodel/drilling_riser/adapter.py`
- `tests/drilling_riser/conftest.py`
- `tests/drilling_riser/test_adapter_integration.py`
- `tests/naval_architecture/test_vessel_fleet_adapter.py`

### worldenergydata working tree
Relevant to #2058:
- `subseaiq/analytics/normalize.py`

## 3. Safe separation strategy

### Recommended commit order
1. Finish/fix #2057 in workspace-hub, then commit only #2057 files there.
2. Commit #2054 in digitalmodel.
3. Commit #2058 in digitalmodel.
4. Commit #2058 companion change in worldenergydata.
5. Update submodule pointers in workspace-hub only after nested repo commits are complete.

Rationale:
- #2057 lives entirely in workspace-hub and is independent.
- #2054 and #2058 both touch digitalmodel but have zero file overlap.
- #2058 also needs a worldenergydata commit, so it should be treated as a cross-repo issue with two commits plus later submodule pointer updates.

## 4. Exact file boundaries by issue

### #2057 commit boundary (workspace-hub only)
Stage ONLY:
- `docs/governance/SESSION-GOVERNANCE.md`
- `tests/skills/test_session_start_routine_smoke.py`
- `tests/skills/test_session_corpus_audit_smoke.py`
- `tests/skills/test_comprehensive_learning_smoke.py`
- `tests/skills/test_cross_review_policy_smoke.py`
- plus the 5 skill-link fixes once added

Do NOT stage:
- `.claude/state/**`
- `scripts/analysis/claude_session_ecosystem_audit.py`
- `tests/analysis/test_claude_session_ecosystem_audit.py`
- unrelated docs/plans/reports files

Suggested commit message after fixing the missing links:
- `chore(governance): fix skill links and add smoke tests (#2057)`

### #2054 commit boundary (digitalmodel only)
Stage ONLY:
- `src/digitalmodel/field_development/economics.py`
- `tests/field_development/test_economics.py`

Do NOT stage:
- any `drilling_riser/*`
- `tests/naval_architecture/test_vessel_fleet_adapter.py`
- `field_development/benchmarks.py`
- `field_development/architecture_patterns.py`
- `test_benchmarks.py`
- `test_architecture_patterns.py`

Suggested commit message:
- `feat(field-dev): add Arps decline curves to economics cashflow model (#2054)`

### #2058 commit boundary (digitalmodel)
Stage ONLY:
- `src/digitalmodel/field_development/benchmarks.py`
- `src/digitalmodel/field_development/architecture_patterns.py`
- `tests/field_development/test_benchmarks.py`
- `tests/field_development/test_architecture_patterns.py`

Do NOT stage:
- `field_development/economics.py`
- `tests/field_development/test_economics.py`
- any drilling_riser/naval_architecture files

Suggested commit message:
- `feat(field-dev): add subsea architecture pattern analytics (#2058)`

### #2058 companion commit boundary (worldenergydata)
Stage ONLY:
- `subseaiq/analytics/normalize.py`

Suggested commit message:
- `feat(subseaiq): add flowline and layout normalization fields for architecture analytics (#2058)`

## 5. Exact commands to use later

### #2057 (workspace-hub)
```bash
cd /mnt/local-analysis/workspace-hub
# first patch the 5 broken links, then:
uv run pytest tests/skills/test_*_smoke.py -v

git add \
  docs/governance/SESSION-GOVERNANCE.md \
  tests/skills/test_session_start_routine_smoke.py \
  tests/skills/test_session_corpus_audit_smoke.py \
  tests/skills/test_comprehensive_learning_smoke.py \
  tests/skills/test_cross_review_policy_smoke.py \
  .claude/skills/_internal/meta/repo-cleanup/SKILL.md \
  .claude/skills/_internal/meta/hidden-folder-audit/SKILL.md \
  .claude/skills/_internal/meta/module-based-refactor/SKILL.md \
  .claude/skills/operations/devtools/ai-tool-assessment/SKILL.md \
  .claude/skills/_internal/builders/skill-creator/SKILL.md

git commit -m "chore(governance): fix skill links and add smoke tests (#2057)"
```

### #2054 (digitalmodel)
```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src uv run python -m pytest tests/field_development/test_economics.py -v

git add \
  src/digitalmodel/field_development/economics.py \
  tests/field_development/test_economics.py

git commit -m "feat(field-dev): add Arps decline curves to economics cashflow model (#2054)"
```

### #2058 (digitalmodel)
```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src uv run python -m pytest tests/field_development/test_benchmarks.py tests/field_development/test_architecture_patterns.py -v

git add \
  src/digitalmodel/field_development/benchmarks.py \
  src/digitalmodel/field_development/architecture_patterns.py \
  tests/field_development/test_benchmarks.py \
  tests/field_development/test_architecture_patterns.py

git commit -m "feat(field-dev): add subsea architecture pattern analytics (#2058)"
```

### #2058 (worldenergydata)
```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH='src:../assetutilities/src' uv run python -m pytest --noconftest

git add subseaiq/analytics/normalize.py

git commit -m "feat(subseaiq): add flowline and layout normalization fields for architecture analytics (#2058)"
```

### Update submodule pointers in workspace-hub after nested commits
```bash
cd /mnt/local-analysis/workspace-hub
git add digitalmodel worldenergydata
git commit -m "chore(submodules): update digitalmodel and worldenergydata for batch 2 field-dev work"
```

## 6. Risk flags

1. #2057 is NOT actually ready to close yet.
   - The five required link fixes are still missing.
   - Commiting only tests/docs would leave the issue partially done.

2. digitalmodel currently contains unrelated uncommitted work.
   - Do not use `git add .`
   - Do not stage by directory.
   - Stage exact files only.

3. #2058 spans two repos.
   - A single workspace-hub commit is insufficient.
   - You need one digitalmodel commit, one worldenergydata commit, then a workspace-hub submodule-pointer commit.

## 7. Recommended next execution sequence

1. Fix the 5 missing #2057 links in workspace-hub.
2. Commit #2057 in workspace-hub.
3. Commit #2054 in digitalmodel.
4. Commit #2058 in digitalmodel.
5. Commit #2058 in worldenergydata.
6. Update workspace-hub submodule pointers.
7. Post issue comments / closeout notes.

## 8. Bottom line

The safest separation boundary is clear:
- #2057 = workspace-hub only, but incomplete until 5 links are fixed
- #2054 = 2 files in digitalmodel
- #2058 = 4 files in digitalmodel + 1 file in worldenergydata

Do not commit anything with broad globs. Stage exact files only.
