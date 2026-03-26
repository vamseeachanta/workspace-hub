# WRK-1244: Evaluate Canonical Skill Ecosystem Quality

## Context

After WRK-639 cleaned out 124 diverged/incoming skills and WRK-1053 scripted the audit
loops, we have 403 canonical skills but **no ecosystem-wide quality baseline**. Three
eval tools exist but have never been run together at scale:
- `eval-skills.py` (18 structural checks) — only 3 eval YAML files exist in `specs/skills/evals/`
- `audit-skill-violations.sh` (4 hard constraints)
- `skill-coverage-audit.sh` (script-wiring gaps)

This WRK runs all three, records results, fixes the worst issues, and establishes a
repeatable eval baseline.

## Plan

### Phase 1: Run existing audit tools (deterministic baseline)

**Files touched:** none (read-only analysis)

1. Run `eval-skills.py` full scan:
   ```bash
   uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py --format json --output specs/audit/skill-eval-2026-03-16.json
   ```
2. Run `audit-skill-violations.sh` → capture YAML output
3. Run `skill-coverage-audit.sh` → capture YAML gaps
4. Collate results into `specs/audit/skill-eval-2026-03-16.yaml` (single source of truth)

### Phase 2: Verify WRK-639 cleanup (no lost content)

1. Check `_diverged/` and `incoming/` dirs — confirm empty (research shows they are)
2. Sample 10 skills from git history that were deleted by WRK-639 (`git log --diff-filter=D`)
3. Diff deleted content vs canonical counterpart — record findings in evidence YAML
4. If valuable content was lost → capture as future-work items

### Phase 3: Fix Phase 9 coverage gaps

**Files touched:** SKILL.md files missing `scripts:` frontmatter or exec patterns

1. Parse `skill-coverage-audit.sh` output for skills with `has_script_ref: false`
2. For each gap: add `scripts:` frontmatter field or document why no script applies
3. Re-run `skill-coverage-audit.sh` to confirm gap count → 0

### Phase 4: Improve bottom quartile

1. From eval-skills.py JSON, sort by issue count (critical > warning > info)
2. Bottom quartile (worst ~100 skills) — categorize issues:
   - Missing frontmatter → fix with `add-missing-frontmatter.sh`
   - Missing required sections → add stubs
   - Broken cross-references → fix or remove
3. Re-run eval-skills.py to confirm improvement
4. Skills that cannot be meaningfully fixed → flag for removal in future-work

### Phase 5: Cleanup stale directories

1. Remove empty `_diverged/` and `incoming/` directories
2. Commit cleanup

## Scripts to Create

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `scripts/skills/ecosystem-eval-report.sh` | Orchestrates all 3 tools, collates into single YAML | none | `specs/audit/skill-eval-<date>.yaml` |

This is the only new script needed — the 25% recurrence rule applies since this should
run weekly alongside Phase 9.

## Test Plan

| What | Type | Expected |
|------|------|----------|
| eval-skills.py runs on 403 skills without crash | happy path | exit 0 or 1; JSON output valid |
| audit-skill-violations.sh produces parseable YAML | happy path | valid YAML with violations list |
| skill-coverage-audit.sh gap count decreases after Phase 3 fixes | regression | gap_count < pre-fix count |
| ecosystem-eval-report.sh produces complete YAML | happy path | all 3 tool outputs present in report |
| Deleted skill diff finds no critical content loss | edge | report documents 0 critical losses |

## Acceptance Criteria Mapping

| AC | Phase |
|----|-------|
| skill-creator eval run on all canonical skills with scores recorded | Phase 1 |
| 18 Phase 9 coverage gaps resolved | Phase 3 |
| Sample of 10 deleted diverged skills diffed | Phase 2 |
| Bottom quartile skills improved or flagged | Phase 4 |
| Eval results saved to specs/audit/ | Phase 1 |

## Critical Files

- `.claude/skills/development/skill-eval/scripts/eval-skills.py` — 18-check evaluator
- `scripts/skills/audit-skill-violations.sh` — 4 hard constraint checks
- `scripts/skills/skill-coverage-audit.sh` — script-wiring gap detector
- `scripts/skills/add-missing-frontmatter.sh` — batch frontmatter fixer
- `specs/skills/evals/*.yaml` — eval definitions (only 3 exist; may need more)
- `specs/audit/` — output directory for results

## Chunk-Sizing Check

- max_repos: 1 (workspace-hub only) ✓
- max_files_changed: will exceed 5 if fixing 100+ skills → **Phase 3+4 fixes are batch**
  - Mitigation: Phase 1-2 are read-only; Phase 3-4 are mechanical fixes (frontmatter, sections)
  - If >5 files need non-trivial content changes, decompose into Feature WRK
- max_plan_words: ~150 ✓
- max_stage10_phases: 5 phases but 1-2 are read-only → effectively 3 execution phases ✓

## Verification

```bash
# After all phases:
uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py --summary-only
bash scripts/skills/audit-skill-violations.sh
bash scripts/skills/skill-coverage-audit.sh
# All three should show improvement over Phase 1 baseline
```
