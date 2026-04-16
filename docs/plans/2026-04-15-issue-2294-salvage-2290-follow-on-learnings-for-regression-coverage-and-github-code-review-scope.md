# Plan for #2294: salvage #2290 follow-on learnings for regression coverage and github-code-review scope

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2294
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2294-claude.md | scripts/review/results/2026-04-15-plan-2294-codex.md | scripts/review/results/2026-04-15-plan-2294-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `tests/skills/test_issue_2290_dedup_regression.py` — current canonical regression suite is intentionally narrow (93 lines) and verifies only audit-clearing, stale-dir removal, and canonical-dir existence. It does not validate auxiliary-file preservation, explicit leaf-collision cleanup, or broad deleted-path-reference scans.
- Found: `.claude/skills/development/github/code-review/SKILL.md` — current canonical skill is a concise 175-line review-focused guide centered on PR metadata, diff inspection, verdicting, inline comments, and a preserved generic review checklist.
- Found: `.claude/skills/github/github-pr-workflow/SKILL.md` — already owns the broader PR lifecycle surface (branching, pushing, creating PRs, monitoring CI, merging), which constrains how much PR-operational material should move into `github-code-review`.
- Found: `.claude/skills/github/github-auth/SKILL.md` — already owns GitHub auth setup and token/SSH flows, which means auth-detection/setup content should not be duplicated into `github-code-review`.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — `AGENTS.md` is the canonical entry point and provider adapters (`.claude/`, `.codex/`, `.gemini/`, `.mcp.json`) are durable discovery surfaces, supporting the idea that deleted-path reference scans across those surfaces are legitimate governance checks rather than branch-local noise.

### Standards

| Standard | Status | Source |
|---|---|---|
| Mandatory issue-planning workflow | done | `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Skills-governance weekly audit policy | done | `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` |
| Control-plane durable discovery surfaces | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |

### LLM Wiki pages consulted
- No relevant wiki pages; this issue is bounded repo-governance work on tests/skills/docs rather than a domain-knowledge promotion problem.

### Documents consulted
- `docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md` — prior plan explicitly identified missing regression coverage and missing dangling-reference scans as implementation gaps, which directly supports the salvage value of the preserved broader regression checks.
- `docs/plans/README.md` — confirms canonical plan/index workflow and shows #2290 is already represented as a separate completed/planned effort rather than something to reopen here.
- GitHub issue #2294 — current bounded scope, acceptance criteria, and explicit non-goals.
- GitHub issue #2083 — open duplicate-skill reconciliation for `session-corpus-audit`; useful evidence that neighboring consolidation work remains intentionally separate.
- GitHub issue #2019 — open email skill sprawl consolidation; useful evidence that broader skill taxonomy rationalization is intentionally separate from this bounded salvage issue.
- Session recall query `2290 OR github-code-review OR issue-2290-implementation OR skill dedup regression` — returned no directly useful prior salvage-session evidence for this exact follow-on, so the current repo state and preserved branch diff remain the primary evidence sources.

### Gaps identified
- No existing canonical artifact decides which parts of the preserved 197-line regression test are high-signal enough to port and which parts should remain branch-local or be discarded.
- No existing canonical artifact decides whether the 480-line alternate `github-code-review` draft should be partially imported, split into another skill, or rejected.
- No current test or doc explicitly guards against reintroducing deleted-path references across control-plane adapter surfaces after future skill dedup work.

<!-- Verification: distinct sources >= 3. Current count: 10+ (current test, current skill, adjacent GitHub skills, #2290 plan, docs/plans/README.md, CONTROL_PLANE_CONTRACT.md, issues #2294/#2083/#2019, session recall result) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md` |
| Prior issue | `#2290` |
| Preserved branch reference | `issue-2290-implementation` |
| Current regression test | `tests/skills/test_issue_2290_dedup_regression.py` |
| Current canonical skill | `.claude/skills/development/github/code-review/SKILL.md` |
| Adjacent GitHub skill — auth | `.claude/skills/github/github-auth/SKILL.md` |
| Adjacent GitHub skill — PR workflow | `.claude/skills/github/github-pr-workflow/SKILL.md` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2294-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2294-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2294-gemini.md` |
| Docs index update | `docs/plans/README.md` |
| Possible implementation targets | `tests/skills/test_issue_2290_dedup_regression.py`, `.claude/skills/development/github/code-review/SKILL.md` |

---

## Deliverable

A bounded salvage decision, implemented via targeted test and/or skill-doc updates, that captures only the high-signal learnings from the preserved `issue-2290-implementation` branch for #2290 regression coverage and `github-code-review` scope without reopening #2290 or duplicating neighboring GitHub skills.

---

## Pseudocode

```text
salvage_follow_on_learnings():
    retrieve preserved artifacts explicitly via git show from issue-2290-implementation
    if preserved branch or target paths are unavailable:
        stop and record blocker instead of guessing from memory

    diff current regression test against preserved branch version
    classify each preserved assertion as keep, reject, or defer
    keep only assertions that protect durable repo-governance surfaces via an explicit allowlist
    exclude historical docs and the regression test file itself from deleted-path scans to avoid self-referential false positives

    diff current github-code-review skill against preserved branch version
    classify each preserved section as canonical-here, belongs-in-neighbor-skill, or reject
    preserve the concise role of github-code-review as a review skill
    reject auth setup and full PR lifecycle material already owned elsewhere
    if useful content clearly belongs in another skill:
        document it and create a follow-up issue instead of editing neighbor skills here

    implement only the selected minimal changes
    run targeted tests and any relevant skill validation checks
    document which preserved ideas were accepted, rejected, or split out
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md` | canonical plan artifact |
| Update | `docs/plans/README.md` | add plan index row for #2294 |
| Modify | `tests/skills/test_issue_2290_dedup_regression.py` | selectively port stronger regression checks if approved during implementation |
| Modify | `.claude/skills/development/github/code-review/SKILL.md` | selectively import high-signal guidance only if it fits the canonical review-skill boundary |
| Create review artifacts | `scripts/review/results/2026-04-15-plan-2294-claude.md`, `...-codex.md`, `...-gemini.md` | adversarial plan review evidence |
| Future issue candidate only | `#TBD` | if preserved content clearly belongs in `github-pr-workflow` or `github-auth`, create a follow-up instead of editing neighboring skills in this issue |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_regression_scan_uses_explicit_control_plane_allowlist` | Any accepted deleted-path scan is limited to explicit durable surfaces rather than broad unconstrained recursion | allowlisted surfaces + deleted path fragments | only allowlisted files/dirs are scanned |
| `test_regression_scan_ignores_historical_and_test_files` | Deleted-path scan excludes the regression test file itself plus historical planning/review docs that may legitimately mention old paths | repo files including test/plan/review artifacts | no self-referential or historical false positives |
| `test_github_code_review_template_reference_still_present` | Canonical `github-code-review` still preserves the `references/review-output-template.md` link after any update | updated skill text | template reference still present |
| `test_github_code_review_scope_bounded_against_auth_and_pr_workflow` | Canonical `github-code-review` does not absorb auth setup or full PR lifecycle content owned by neighboring skills | updated skill text + known disallowed sections/phrases | no auth-setup or branch/push/create-PR lifecycle takeover |
| `test_auxiliary_skill_assets_preserved_after_2290_dedup` | If selected for salvage, regression suite confirms canonical keepers still retain required moved auxiliary files | current skill tree after implementation | required reference files exist |
| `test_no_residual_collision_for_2290_resolved_leafs` | If selected for salvage, only canonical survivors remain for the three resolved leaf-collision names | current skill tree after implementation | no stale collision dirs remain |
| `test_no_deleted_path_fragments_in_control_plane_surfaces` | If selected for salvage, deleted #2290 paths are absent from the explicit allowlisted control-plane surfaces | deleted path fragments + allowlisted repo files | zero offenders |

---

## Acceptance Criteria

- [ ] Implementation uses the preserved `issue-2290-implementation` branch only as a source of candidate learnings, retrieved explicitly via `git show`, not as a wholesale cherry-pick source
- [ ] If the preserved branch or target files are unavailable during implementation, the run stops and records a blocker rather than guessing from memory
- [ ] A deliberate keep/reject/defer decision is made for the stronger preserved #2290 regression assertions
- [ ] Any accepted regression-test improvements are landed as a minimal targeted change in `tests/skills/test_issue_2290_dedup_regression.py`
- [ ] Any deleted-path scan added by this issue uses an explicit allowlist of durable control-plane surfaces and excludes self-referential/historical files that would create false positives
- [ ] A deliberate keep/reject/defer decision is made for the alternate `github-code-review` draft
- [ ] If `github-code-review` is updated, the result remains review-focused, preserves the `references/review-output-template.md` linkage, and does not duplicate `github-auth` or the full PR-lifecycle coverage of `github-pr-workflow`
- [ ] No unrelated preserved-branch drift is imported from `issue-2290-implementation`
- [ ] This issue does not modify `github-auth` or `github-pr-workflow`; if useful preserved content clearly belongs there, a follow-up issue is created instead
- [ ] Targeted validation passes for any changed tests/skills
- [ ] Review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Initial review flagged conditional-only TDD tests, unresolved design decisions, optional neighbor-skill scope-creep path, and self-referential deleted-path scan risk |
| Codex | MAJOR (review package retrieval failure) | Initial non-interactive run could not reliably access the draft plan artifact from committed repo state; useful residual findings were scope-boundary and semantic-preservation concerns, but retrieval adequacy was insufficient |
| Gemini | APPROVE | Initial review approved the bounded direction but flagged branch-availability risk, deleted-path false-positive risk, and the need to remove the optional neighboring-skill update backdoor |

**Overall result:** REVISED — actionable findings incorporated into the draft, but clean re-review is still pending before this plan should move to `status:plan-review`.

Revisions made based on review:
- Made preserved-branch retrieval explicit via `git show` and added a blocker stop if the branch or target file paths are unavailable
- Replaced broad recursive deleted-path scan language with an explicit control-plane allowlist plus self/historical exclusions
- Removed the optional neighboring-skill update path; the plan now requires a follow-up issue instead of editing `github-auth` or `github-pr-workflow` here
- Added unconditional TDD items for allowlist enforcement, self-exclusion, template-reference preservation, and scope-boundary protection
- Tightened acceptance criteria around preserved-template linkage, no neighbor-skill edits, and blocker handling for missing preserved inputs

---

## Risks and Open Questions

- **Risk: overfitted regression scans.** The preserved branch test walks many surfaces; if ported blindly, it could create brittle failures tied to incidental text occurrences rather than meaningful control-plane regressions. Use an explicit allowlist plus self/historical exclusions instead of unconstrained recursion.
- **Risk: skill-scope sprawl.** The preserved 480-line `github-code-review` draft mixes review guidance with auth and PR-lifecycle guidance already owned by neighboring skills, which would make discovery and maintenance worse if merged indiscriminately.
- **Risk: hidden boundary decisions.** Some preserved content may be useful but belong in a different skill or follow-up issue; implementation must separate “good content” from “right canonical home.”
- **Risk: unavailable preserved branch input.** If `issue-2290-implementation` or the target file paths are unavailable at execution time, the issue cannot be completed honestly and must stop with a blocker rather than reconstructing branch content from memory.
- **Open: if the best content from the alternate `github-code-review` draft belongs in another skill, should implementation create the follow-up issue immediately during this issue or merely document the candidate for later triage?**

---

## Scope Boundaries

### In scope (this issue)
- Selective salvage review of the preserved broader #2290 regression checks
- Selective salvage review of the preserved alternate `github-code-review` draft
- Minimal targeted updates to the canonical regression test and/or canonical review skill if justified
- Explicit documentation of keep/reject/defer decisions

### Explicitly out of scope

| Topic | Covered by | Why excluded |
|---|---|---|
| Reopening or redoing #2290 | #2290 | Upstream landing is already authoritative |
| session-corpus-audit dedup | #2083 | Separate duplicate-skill reconciliation issue |
| email skill sprawl consolidation | #2019 | Separate domain-specific consolidation issue |
| full GitHub skill taxonomy redesign | future issue if needed | Too broad for this bounded salvage pass |
| wholesale import of all preserved branch deltas | excluded by issue body | Branch contains unrelated drift |

---

## Complexity: T2

**T2** — bounded multi-file repo-governance work with explicit resource-intelligence requirements, targeted tests/docs changes, and adversarial review before any implementation.