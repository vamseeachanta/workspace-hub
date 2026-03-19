# WRK-1330: Archive Synthesis Plan

## Decisions (User-approved 2026-03-19)

| # | Question | Decision |
|---|----------|----------|
| 1 | Backfill scope | All 409 archived WRKs |
| 2 | Output format | New `docs/archive-synthesis-report.yaml` + roadmap delta |
| 3 | GitHub Issues for follow-ons | Auto-create from synthesis script |
| 4 | Future archive flow | Always create issue for each future-work item |
| 5 | Existing 38 open issues | Review in bulk groups, then decide |
| 6 | HTMLs vs GitHub Issues | **Replace HTMLs with GitHub Issue body updates** |
| 7 | Issue body template | Approved — see issue #39 for live example |

## GitHub Issue Body Template (Approved)

Section order (all collapsible):
1. **Status line** (always visible) — status, priority, category, repo, complexity, machine
2. **Implementation Summary** — what was done (files, commits)
3. **Final Plan** — approved plan with decisions
4. **Acceptance Criteria** — checkboxes
5. **TDD Results** — test evidence
6. **Evidence and Cost** — tokens, cross-review, legal, future work
7. **Stage Progress** — 20-stage checklist (audit detail)

Live example: https://github.com/vamseeachanta/workspace-hub/issues/39

## Architecture

### Phase 1: One-time synthesis script

**Script**: `scripts/knowledge/synthesize-archive.py`

**Inputs** (per archived WRK):
- `archive/YYYY-MM/WRK-NNN.md` — frontmatter (category, title, tags, repository)
- `assets/WRK-NNN/evidence/stage-evidence.yaml` — journey (stage progression, comments)
- `assets/WRK-NNN/evidence/future-work.yaml` — unaddressed follow-ons
- `assets/WRK-NNN/evidence/resource-intelligence.yaml` — gaps and patterns
- `assets/WRK-NNN/evidence/cost-summary.yaml` — AI cost attribution

**Processing**:
1. Parse all 409 archived WRKs
2. Backfill missing `knowledge-base/wrk-completions.jsonl` entries (currently only 21)
3. Group by category → subcategory → repository
4. Per group, extract:
   - Completed capability summary (what was built)
   - Unaddressed follow-ons (future-work items not yet captured as pending WRKs)
   - Stage journey patterns (capture-to-plan delta, scope changes, rejection reasons)
   - Cost profile (total tokens, model mix)
5. Cross-WRK analysis:
   - Category heat map: which categories have most unfinished follow-ons
   - Repeat spawners: WRKs with 3+ follow-ons (capability gaps, not task backlogs)
   - Cost vs compound value: categories with high follow-on density per dollar

**Outputs**:
- `docs/archive-synthesis-report.yaml` — structured report grouped by category
- `knowledge-base/wrk-completions.jsonl` — backfilled to all 409
- `knowledge-base/index.jsonl` — rebuilt
- GitHub Issues created for each unaddressed high-signal follow-on
- Delta patch for `roadmap-2026-h1.md` (new themes, updated metrics)

### Phase 2: GitHub Issue body updater

**Script**: `scripts/knowledge/update-github-issue.py`
- Generates issue body from WRK frontmatter + evidence files using approved template
- Wire into `start_stage.py` / `exit_stage.py` (replace HTML gen calls)
- At archive: write full final state to issue body, then close issue

### Phase 3: Cleanup

- Delete `generate-html-review.py` (1,200 lines)
- Delete 12 HTML sub-skills
- Delete 828 legacy + 224 active HTML files
- Patch `archive-item.sh` for GitHub Issue creation on future-work items

### Phase 4: Bulk review of 38 existing open issues

**Script**: `scripts/knowledge/review-open-issues.py`
- Fetch all open issues via `gh issue list`
- Group by label/category
- Present bulk groups for user decision (keep/close/merge/reprioritize)

## Execution Sequence

1. Write `scripts/knowledge/update-github-issue.py` with TDD (template renderer)
2. Write `scripts/knowledge/synthesize-archive.py` with TDD
3. Run backfill — populate `wrk-completions.jsonl` for all 409
4. Run synthesis — generate `archive-synthesis-report.yaml`
5. Auto-create GitHub Issues for unaddressed follow-ons
6. Update `roadmap-2026-h1.md` with new themes
7. Wire `update-github-issue.py` into `start_stage.py` / `exit_stage.py`
8. Delete `generate-html-review.py` + HTML sub-skills + HTML files
9. Patch `archive-item.sh` for ongoing Issue creation
10. Write `scripts/knowledge/review-open-issues.py`
11. Run bulk review of 38 existing open issues with user

## Acceptance Criteria

- [ ] AC1: All 409 archived WRKs have knowledge-base entries
- [ ] AC2: `archive-synthesis-report.yaml` exists, grouped by category
- [ ] AC3: Unaddressed future-work items surfaced as GitHub Issues
- [ ] AC4: `roadmap-2026-h1.md` updated with archive-derived themes
- [ ] AC5: `archive-item.sh` creates GitHub Issues for future-work at archive time
- [ ] AC6: `generate-html-review.py` + HTML sub-skills deleted
- [ ] AC7: `update-github-issue.py` wired into stage lifecycle
- [ ] AC8: 38 existing open issues reviewed in bulk groups
