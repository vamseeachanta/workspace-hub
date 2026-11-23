# WRK-5100: Purge Lifecycle HTML Refs & Fix GitHub-Issue Workflow Gaps

## Context

The work-queue lifecycle migrated from local `WRK-NNN-lifecycle.html` files to GitHub issues
(WRK-5104, WRK-5107). Stage 1 was already cleaned up (commit 3780f948), but stages 2-20
micro-skills, YAML contracts, templates, and scripts still reference the dead HTML artifact.
Two live sessions (WRK-5104 #1252, WRK-5106 #1254) exposed 4 workflow discrepancies.

## Plan

### Phase 1: Purge lifecycle HTML from stage micro-skills (Section A)

Edit 18 files: `.claude/skills/workspace-hub/stages/stage-{02..20}-*.md`

Per file:
- Replace `Entry: WRK-NNN-lifecycle.html#sN-sM` → `Entry: GitHub issue + evidence/*.yaml`
- Remove checklist items: "Update lifecycle HTML Stage N section"
- **Stage 11** special case: rewrite entire checklist from HTML generation → evidence audit + `update-github-issue.py --update` verification

### Phase 2: Update stage YAML contracts (Section B)

Edit 8 files: `scripts/work-queue/stages/stage-{04,05,06,07,10,12,13,17}-*.yaml`
- Remove `WRK-NNN-lifecycle.html` from `exit_artifacts` and `entry_reads`
- Replace with evidence YAML file refs or GitHub issue ref where appropriate

### Phase 3: Fix archive template (Section C)

File: `scripts/work-queue/templates/archive-tooling-template.yaml`
- Replace `html_verification_ref` field → `github_issue_ref`
- Match what `gate_checks_archive.py` now validates (WRK-5107)

### Phase 4: Fix validate-queue-state.sh (Section D)

File: `scripts/work-queue/validate-queue-state.sh` lines 152-163
- Replace `html_verification_ref` check → `github_issue_ref` check

### Phase 5: Update ecosystem terminology (Section E)

File: `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md` lines 109, 136
- Update `Lifecycle HTML` references to reflect GitHub issue as review surface
- Keep as historical note if needed, mark as deprecated

### Phase 6: Fix _extract_sections fallback (already done)

File: `scripts/knowledge/update-github-issue.py`
- `_extract_sections` now falls back to all `##` headings when Mission/What/Why not present
- **Already committed during this session** — just needs inclusion in final commit

### Phase 7: Discrepancy items (Section F) — capture as future work

These are **code changes to `exit_stage.py` and approval detection** — larger scope:
1. Stage summaries in completion comments → enhance `_post_stage_comment()` in `exit_stage.py`
2. Approval UX too verbose → fix in approval detection logic
3. Execute group human gate → evaluate if stage 10.5 checkpoint needed
4. Agent attribution → prefix bot comments with `🤖 [agent]`

**Recommendation:** Capture F.1-F.4 as WRK-5109 (separate item) to keep WRK-5100 focused on the HTML purge + template/script fixes.

## Files to modify

| Phase | File | Change |
|-------|------|--------|
| 1 | `stages/stage-02-resource-intelligence.md` | Remove HTML refs |
| 1 | `stages/stage-03-triage.md` | Remove HTML refs |
| 1 | `stages/stage-04-plan-draft.md` | Remove HTML exit artifact |
| 1 | `stages/stage-05-user-review-plan-draft.md` | Replace HTML entry + checklist |
| 1 | `stages/stage-06-cross-review.md` | Replace HTML entry + checklist |
| 1 | `stages/stage-07-user-review-plan-final.md` | Replace HTML entry + checklist |
| 1 | `stages/stage-08-claim-activation.md` | Remove HTML checklist |
| 1 | `stages/stage-09-routing.md` | Remove HTML checklist |
| 1 | `stages/stage-10-work-execution.md` | Replace HTML entry |
| 1 | `stages/stage-11-artifact-generation.md` | Full rewrite |
| 1 | `stages/stage-12-tdd-eval.md` | Replace HTML entry |
| 1 | `stages/stage-13-agent-cross-review.md` | Replace HTML entry + checklist |
| 1 | `stages/stage-14-verify-gate-evidence.md` | Remove HTML checklist |
| 1 | `stages/stage-15-future-work.md` | Remove HTML checklist |
| 1 | `stages/stage-16-resource-intelligence-update.md` | Remove HTML checklist |
| 1 | `stages/stage-17-user-review-implementation.md` | Replace HTML entry + checklist |
| 1 | `stages/stage-18-reclaim.md` | Remove HTML checklist |
| 1 | `stages/stage-20-archive.md` | Remove HTML checklist |
| 2 | `scripts/work-queue/stages/stage-04-*.yaml` | Remove HTML from exit_artifacts |
| 2 | `scripts/work-queue/stages/stage-05-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-06-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-07-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-10-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-12-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-13-*.yaml` | Remove HTML from entry_reads |
| 2 | `scripts/work-queue/stages/stage-17-*.yaml` | Remove HTML from entry_reads |
| 3 | `scripts/work-queue/templates/archive-tooling-template.yaml` | html_verification_ref → github_issue_ref |
| 4 | `scripts/work-queue/validate-queue-state.sh` | html_verification_ref → github_issue_ref |
| 5 | `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md` | Update Lifecycle HTML entries |
| 6 | `scripts/knowledge/update-github-issue.py` | Already done |

## Acceptance Criteria

1. `grep -r 'lifecycle\.html' .claude/skills/workspace-hub/stages/` returns 0 matches
2. `grep -r 'lifecycle\.html' scripts/work-queue/stages/` returns 0 matches
3. `grep 'html_verification_ref' scripts/work-queue/templates/archive-tooling-template.yaml` returns 0 matches
4. `grep 'html_verification_ref' scripts/work-queue/validate-queue-state.sh` returns 0 matches
5. `uv run --no-project python scripts/knowledge/update-github-issue.py WRK-5100 --update --dry-run` renders scope sections in body
6. Stage 11 micro-skill describes evidence audit, not HTML generation
7. Ecosystem terminology no longer lists Lifecycle HTML as active canonical concept

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| grep lifecycle.html across stages/ | happy | 0 matches |
| grep html_verification_ref across templates + scripts | happy | 0 matches |
| update-github-issue.py --update --dry-run for a WRK with ## sections | happy | Sections rendered in body |
| validate-queue-state.sh on an archived WRK with github_issue_ref | happy | No false warnings |
| verify_checklist.py WRK-5100 --summary after all evidence written | happy | All stages PASS |
| Stage 11 micro-skill parse — no reference to generate-html-review.py | edge | Clean |

## Confirmation

confirmed_by: vamseeachanta
confirmed_at: 2026-03-21T22:00:00Z
decision: passed

## Verification

```bash
# AC verification
grep -r 'lifecycle\.html' .claude/skills/workspace-hub/stages/ && echo FAIL || echo PASS
grep -r 'lifecycle\.html' scripts/work-queue/stages/ && echo FAIL || echo PASS
grep 'html_verification_ref' scripts/work-queue/templates/archive-tooling-template.yaml && echo FAIL || echo PASS
grep 'html_verification_ref' scripts/work-queue/validate-queue-state.sh && echo FAIL || echo PASS
uv run --no-project python scripts/knowledge/update-github-issue.py WRK-5100 --update --dry-run | grep -c '###' # should be ≥2
```
