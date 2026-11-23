# Plan for #3872: fix(review): prevent duplicate Claude reviews across PR events

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-09-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3872
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-23-plan-3872-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.github/workflows/claude-code-review.yml:3–5` — trigger block: `on: pull_request: types: [opened, synchronize, ready_for_review, reopened]`. No `concurrency:` block present in the file.
- Found: `.github/workflows/pages.yml:26–28` — prior art for concurrency in this repo: `concurrency: group: pages` with `cancel-in-progress: true`. Confirms the pattern is in use and accepted.
- Found: `.github/workflows/kanban-reconcile.yml:22–24` — second prior art: `concurrency: group: kanban-reconcile` with `cancel-in-progress: false`. Confirms `cancel-in-progress: true` vs `false` is a deliberate choice per workflow.
- Gap: No test file exists for workflow YAML structure validation; tests will be written as Python tests that parse the YAML and assert the concurrency block structure.

### Standards
Not applicable — this is a CI workflow governance fix, not an engineering calculation.

### LLM Wiki pages consulted
No relevant wiki pages found for GitHub Actions concurrency configuration.

### Documents consulted

- Issue #3872 body — exact evidence: two concurrent workflow run URLs (`35039369534`, `35039372092`) for identical head `38295014ecebf0080d4a60a98a2d5cf1fc09416f`; root cause: "triggers `synchronize` and `ready_for_review` without workflow/job concurrency control."
- Issue #3560 — related: provider sink isolation during review execution. Different concern (in-process artifact isolation during review, not dispatch deduplication). No overlap with this plan's scope.
- Issue #3815 (epic context from issue body) — skill-index and scoped contract initiative that surfaced the duplicate-review observation; confirms this is a repeatable problem, not a one-off.
- `docs/plans/README.md` — no prior plan exists for Claude review workflow concurrency.

### Gaps identified

- GitHub Actions does not expose a built-in "was this run cancelled" test; cancelled runs show status `cancelled` in the UI, which GitHub treats as a non-success for required status checks. No additional change is needed for this safety property — it is inherited from GitHub's required-checks behavior.
- The `multi-ai-review.yml` workflow is `workflow_dispatch`-only and handles no PR events; it is out of scope and will not be modified.

### Evidence (embedded verification)

**Issue status** (verified 2026-09-23 via `gh issue view 3872`):
- `#3872` — OPEN — fix(review): prevent duplicate Claude reviews across PR events

**File existence** (verified 2026-09-23 via `ls`):
- EXISTS: `.github/workflows/claude-code-review.yml`
- EXISTS: `.github/workflows/pages.yml`
- EXISTS: `.github/workflows/kanban-reconcile.yml`
- MISSING (new — this plan creates): `scripts/ci/tests/test_claude_review_workflow.py`

**Line excerpts** (`head -10 .github/workflows/claude-code-review.yml`):
```
1: name: Claude Code Review
2:
3: on:
4:   pull_request:
5:     types: [opened, synchronize, ready_for_review, reopened]
```
No `concurrency:` key present in file — confirmed via `grep concurrency .github/workflows/claude-code-review.yml` returns empty.

**Prior art** (`sed -n 22,30p .github/workflows/kanban-reconcile.yml`):
```
22: concurrency:
23:   group: kanban-reconcile
24:   cancel-in-progress: false
```

**Prior art** (`sed -n 24,30p .github/workflows/pages.yml`):
```
26: concurrency:
27:   group: pages
28:   cancel-in-progress: true
```

**Reproduction proof** (evidence in issue body):
- Two workflow run IDs `35039369534` and `35039372092` both show attempt 1, same head SHA `38295014ecebf0080d4a60a98a2d5cf1fc09416f`.
- Trigger events: `synchronize` (from the push when marking PR ready) and `ready_for_review` (from the draft→ready state transition) fired within milliseconds.
- Failure mode matches issue claim: YES — identical head received two independent review executions at provider expense.

**Gap proof** (no existing CI test for workflow YAML):
- `ls scripts/ci/tests/ 2>&1` → no such directory → confirms no CI test infrastructure exists; test directory will be created.

<!-- Verification: distinct sources: issue #3872 (1), claude-code-review.yml (2), pages.yml (3), kanban-reconcile.yml (4), issue #3560 (5), issue #3815 (6), plans/README.md (7). Count: 7. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-09-23-issue-3872-fix-review-duplicate-dispatch.md |
| Implementation | `.github/workflows/claude-code-review.yml` |
| Tests | `scripts/ci/tests/test_claude_review_workflow.py` |
| Plan review — Claude | scripts/review/results/2026-09-23-plan-3872-claude.md |
| Plan review — Codex | scripts/review/results/2026-09-23-plan-3872-codex.md |
| Plan review — Gemini | scripts/review/results/2026-09-23-plan-3872-gemini.md |

---

## Deliverable

`.github/workflows/claude-code-review.yml` will include a `concurrency:` block scoped to the pull-request number, with `cancel-in-progress: true`, so that at most one Claude review run will be active per PR at any time; a newer head will cancel prior-head work; different PRs will remain fully independent; cancelled runs will not satisfy required check requirements; a Python test will assert the concurrency block is present and structurally correct.

---

## Pseudocode

```yaml
# Addition to .github/workflows/claude-code-review.yml
# Placed after the `on:` block, before `jobs:`:

concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

The group expression `claude-review-<PR-number>` ensures:
- Each PR gets its own concurrency slot.
- A new run for the same PR cancels any in-progress run.
- Runs for different PRs are in different groups and do not interfere.

`cancel-in-progress: true` ensures the older, superseded run is cancelled — not queued — so no stale review from an older head can complete and be confused with a current-head review.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.github/workflows/claude-code-review.yml` | Add `concurrency:` block with PR-scoped group and `cancel-in-progress: true` |
| Create | `scripts/ci/tests/test_claude_review_workflow.py` | TDD: assert concurrency block is present, group expression contains PR number reference, `cancel-in-progress` is `true` |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_concurrency_block_present` | workflow YAML has a top-level `concurrency:` key | parsed `claude-code-review.yml` | `'concurrency' in workflow_data` is True |
| `test_concurrency_group_scoped_to_pr_number` | group expression references `pull_request.number` | `workflow_data['concurrency']['group']` | string contains `pull_request.number` |
| `test_cancel_in_progress_is_true` | superseded runs are cancelled, not queued | `workflow_data['concurrency']['cancel-in-progress']` | value is `True` |
| `test_trigger_includes_synchronize_and_ready_for_review` | both triggering event types remain present (coverage must not be removed) | `workflow_data['on']['pull_request']['types']` | contains both `synchronize` and `ready_for_review` |
| `test_concurrency_group_is_pr_scoped_not_global` | group expression includes PR number, not a repo-global constant | `workflow_data['concurrency']['group']` | does NOT equal a bare string with no `${{` expression |

---

## Acceptance Criteria

- [ ] `concurrency:` block with `group: claude-review-${{ github.event.pull_request.number }}` and `cancel-in-progress: true` is present in `.github/workflows/claude-code-review.yml`.
- [ ] All four original trigger types (`opened`, `synchronize`, `ready_for_review`, `reopened`) remain present — coverage must not be removed.
- [ ] All new tests pass: `uv run pytest scripts/ci/tests/test_claude_review_workflow.py -v`
- [ ] Concurrent `synchronize` + `ready_for_review` events for the same PR will result in at most one completed Claude review run (manual verification: observe only one run in Actions tab after next PR publish; or confirm via issue #3872 comment after merge).
- [ ] Reviews of different PRs (different PR numbers) run independently and do not cancel each other.
- [ ] A cancelled run does not satisfy required status checks in the branch protection settings.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** `cancel-in-progress: true` will cancel a Claude review mid-run if a new push arrives while review is executing. For long-running reviews, this means a push during review restarts the review from scratch. This is the correct behavior (review must target the current head), but it may increase total review cost on PRs with rapid successive pushes.
- **Risk:** If the required status check is named after the job (`claude-review`), a cancelled run will leave the check in `cancelled` state, which does not satisfy a required-checks rule. This is the desired fail-closed behavior per issue acceptance criteria. Verify the required check name matches the job name `claude-review` after merge.
- **Open:** Should `cancel-in-progress` be `false` for the first run (opened event) to avoid any race on brand-new PRs? Current plan uses `true` uniformly — flag for user during approval if queue-rather-than-cancel semantics are preferred for the initial open event.
- **Open:** Issue #3872 body notes "This issue does not authorize cancelling existing runs." The plan's `cancel-in-progress: true` will cancel future in-flight runs when superseded; it does not retroactively cancel historical runs. Verify this interpretation matches user intent.

---

## Complexity: T1

**T1** — single YAML file modified (three lines added); root cause and fix fully specified in issue body and prior art; test file is the only new artifact; no cross-repo changes.
