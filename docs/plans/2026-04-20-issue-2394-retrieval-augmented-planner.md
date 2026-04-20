# Plan for #2394: Retrieval-augmented planner step in issue-planning-mode

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2394
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2394-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` — mandates Resource Intelligence step, enforces retrieval contract #2208, but has no automated retrieval tool.
- Found: `docs/plans/_template-issue-plan.md` — template contains evidence contract comment but no auto-populated section.
- Found: `scripts/conformance/` (if present) — where the new check lives.
- Gap: no automated retrieval at plan-draft time.

### Standards
Not applicable.

### LLM Wiki pages consulted
- Not applicable (tooling issue).

### Documents consulted
- `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md` — retrieval contract this extends with tooling.
- `docs/plans/README.md` — template + index authority.
- Operating model §4 (L3+L2 → L5 flow — retrieval IS this flow; tool operationalizes it).
- Related issue #2206 (conformance checks) — this adds a new check class under that umbrella.
- Related issue #2393 (embeddings index — parallel) — this tool depends on it.
- Memory `feedback_adversarial_review_stance.md` — reviewers frequently flag "retrieval inadequate"; this tool closes that failure mode.
- `scripts/review/results/` (sample 5 artifacts) — confirmed retrieval-inadequacy is the recurring finding.

### Gaps identified
- No CLI/tool for planner-side retrieval.
- No conformance check that plan files under `status:plan-review` contain the retrieval block.
- No template update showing the new block placement.

**Distinct sources consulted: 9** — exceeds ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2394-retrieval-augmented-planner.md` |
| Implementation | `scripts/knowledge/retrieve_plan_candidates.py` |
| Conformance check | `scripts/conformance/planner_retrieval_check.py` |
| Skill update | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Template update | `docs/plans/_template-issue-plan.md` |
| Tests | `tests/knowledge/test_retrieve_plan_candidates.py`, `tests/conformance/test_planner_retrieval_check.py` |
| Pre-push hook wiring | `.git/hooks/pre-push` (via `scripts/enforcement/install-hooks.sh`) |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2394-claude.md` |

---

## Deliverable

A CLI `retrieve_plan_candidates.py --issue NNN` that emits a markdown block listing top-K embedding-index candidates, plus a conformance check enforcing that every plan file carries this block with each candidate explicitly ACCEPTED/REJECTED.

---

## Pseudocode

```
function retrieve(issue_number):
    issue = gh_view(issue_number)  # title + body
    query = issue.title + " " + issue.body[:500]
    results = query_embeddings(query, top_k=10, layer="both")
    emit markdown block:
        ## Retrieval Candidates (auto-generated YYYY-MM-DD)
        | doc_key | layer | path | similarity | status |
        ...  [status is blank by default — plan author fills with ACCEPTED / REJECTED: <reason>]

function conformance_check(plan_file):
    parse plan markdown
    if no "## Retrieval Candidates" section → FAIL (with fix suggestion)
    for each row in candidates table:
        if status cell is blank → FAIL
        if status starts "REJECTED" without reason → FAIL
    return PASS
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/retrieve_plan_candidates.py` | CLI |
| Create | `scripts/conformance/planner_retrieval_check.py` | Conformance check |
| Create | `tests/knowledge/test_retrieve_plan_candidates.py` | CLI tests |
| Create | `tests/conformance/test_planner_retrieval_check.py` | Check tests |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Step 2 now references CLI as required |
| Modify | `docs/plans/_template-issue-plan.md` | Add "## Retrieval Candidates" section |
| Modify | `scripts/enforcement/install-hooks.sh` | Wire pre-push check for `docs/plans/` |
| Update | `docs/plans/README.md` | Add this plan |

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_retrieve_returns_markdown_block | CLI emits well-formed markdown table | issue #2205 (known) | table with 10 rows, blank status column |
| test_retrieve_empty_corpus | Empty index → friendly error, exit ≠0 | empty index | stderr + non-zero |
| test_retrieve_issue_not_found | Invalid issue num → clear error | --issue 99999999 | stderr + non-zero |
| test_check_passes_on_filled_block | All statuses filled | fixture plan with completed block | PASS |
| test_check_fails_missing_block | No block at all | fixture plan w/o block | FAIL with section-name hint |
| test_check_fails_blank_status | Empty status cell | fixture with 1 blank row | FAIL citing row |
| test_check_fails_rejected_no_reason | `REJECTED` without colon-reason | fixture | FAIL |
| test_check_skip_flag_logged | `--skip-retrieval` requires and logs reason | fixture + --skip + reason | PASS + audit log entry |
| test_skill_documents_required_step | Skill file text mentions the CLI | skill file | grep succeeds |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] CLI runs on 3 real open issues producing sensible output (manual check during review)
- [ ] Conformance check integrated into pre-push hook; blocks commits of plan files missing the block
- [ ] Skill SKILL.md updated and lints clean
- [ ] Template updated with example filled-in block
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self) | MINOR | See findings below |
| Codex | PENDING | Optional before approval |
| Gemini | PENDING | Optional |

Revisions made inline:
- **A:** Added `test_check_skip_flag_logged` — escape hatch must be auditable, not silent.
- **B:** Added template-update file (was implicit in AC, promoted to explicit row).
- **C:** Added manual-check AC (3 real issues); pure unit tests insufficient to validate query relevance.

---

## Risks and Open Questions

- **Risk:** Hard-depends on #2393 (embeddings index). Mitigation: issue chained in body; implementation waits.
- **Risk:** Pre-push hook friction in high-velocity sessions. Mitigation: `--skip-retrieval` flag with logged justification.
- **Open:** Should the block be written directly into the plan file by the CLI (side-effect) or stdout-only (author pastes)? Plan: stdout-only; no surprise file writes.

---

## Complexity: T2

Multi-file but bounded; depends on #2393; conformance check is modest.
