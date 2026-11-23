# Next-Session Prompt — Doc-Intel Continuation (2026-04-20 → 21, session 3)

> Paste this into a fresh Claude Code session at `/mnt/local-analysis/workspace-hub` to continue the doc-intel work. Supersedes `.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md`.

---

## One-paragraph context

Session 3 landed Action 1 from session-2's list — the #2405 cross-review sandbox attestation scaffold — end-to-end: v3-final plan implemented with TDD (30 passing tests), dispatcher integration into `submit-to-codex.sh` and `submit-to-gemini.sh`, contract updates in `scripts/review/prompts/plan-review.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md`, and live Codex validation proving the infrastructure works. Then executed Path B (governance cleanup across 7 drifted issues) and Path A (1-call Codex validation against #2392's preserved plan). Codex returned MAJOR with zero Class-B "unverified claims" findings and three attestation-surfaced plan-vs-reality contradiction findings — a new class of precise defect detection that was unreachable before this session.

## Where to start reading

- **This handoff:** `.planning/handoffs/2026-04-20-doc-intel-session-3-handoff.md`
- **Session-2 handoff:** `.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md`
- **#2405 plan (now `Status: implemented`):** `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md`
- **Validation artifact:** `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md`
- **Operating model (authority):** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`

## Commits landed on `origin/main`

```
c85657584 — docs(review): validation artifact proving #2405 attestation works end-to-end
965ced541 — feat(review): #2405 cross-review sandbox pre-verification attestation
```

## Issue state changes

| Issue | Session-3 change | Current state |
|---|---|---|
| **#2405** | Reopened → implementation committed → closed (auto-closed via `Closes #2405` trailer) → reopened → summary attached → closed; validation added in follow-up | **CLOSED implemented + validated** |
| **#2400** | `plan-review`+`plan-approved` labels removed (missing-plan drift) | OPEN, no status label |
| **#2401** | Same as #2400 | OPEN, no status label |
| **#2402** | `plan-approved` removed, `plan-review` retained (premature approval) | OPEN `plan-review` |
| **#2417** | `plan-approved` rolled back to `plan-review` (fresh MAJOR×3 outranks stale approval) | OPEN `plan-review` |
| **#2392** | Stale `plan-review` removed from CLOSED issue; Codex-found revision requirements attached | CLOSED, plan preserved, needs revision before re-file |
| **#2394** | Stale `plan-review` removed from CLOSED issue | CLOSED, plan preserved, needs revision before re-file |
| **#2395** | Stale `plan-review` removed from CLOSED issue | CLOSED, plan preserved, needs revision before re-file |
| **#2408** | Untouched (held for next-session investigation) | OPEN `plan-approved` — governance-drift candidate |

## Critical insights from session 3

1. **Attestation enables plan-vs-reality contradiction detection** (new memory `feedback_attestation_enables_contradiction_detection.md`). Adversarial Codex on #2392 produced 6 findings, zero Class-B. Three of those findings were unreachable before attestation because Codex previously lacked ground truth. This is the real ROI of #2405 — not just silencing Class-B noise.

2. **Two plan-pseudocode defects caught during TDD** (documented in #2405 plan's "Post-implementation deviations" section):
   - `grep -oE '#[0-9]{3,5}'` without `\b` mis-extracts `#9999999` as `#99999`. Fixed with word-boundary.
   - `"$PAYLOAD_SHA_"` parses as undefined `PAYLOAD_SHA_` under `set -u`. Fixed with `${PAYLOAD_SHA}_`.
   Both regression-locked by tests. Future plans reviewed against these regressions.

3. **Test-harness pattern: prepend-to-PATH fake `gh`/`codex`/`gemini` beats real CLI calls.** Pure stubs avoid rate limits, quota, network flakiness; tests deterministic. Pattern is in `tests/review/test_attest_plan_claims.py::_make_fake_gh` etc. — reusable for future CLI-integration tests.

4. **Pre-implementation validation beats post-hoc reasoning.** 87 seconds of one Codex call proved #2405 works; would have taken hours to reach the same confidence by reasoning from code. Prefer one cheap live test before committing to a heavy dispatch wave.

5. **Auto-close-on-push via `Closes #NNNN` trailer is real.** When a commit with `Closes #NNNN` lands on main (possibly via auto-sync), GitHub auto-closes the issue. Existing memory `feedback_gh_issue_close_silent_comment_drop.md` predicted the follow-on problem: `gh issue close --comment` silently drops the comment on already-closed issues. Recovery: reopen → comment → close.

## Recommended first actions for session 4 — priority order

### Action 1: Path C (re-file #2392 with revised plan) — highest leverage

**Why first:** infrastructure proven; #2392 plan has 6 Codex-surfaced defects already sharply scoped; unblocks the doc-intel coverage-gap detector.

**How:**
1. Read `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md` — 6 defects listed.
2. Revise `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` to v2 addressing all 6:
   - Replace 4 missing registry YAMLs with real inputs or make them optional with tested absence behavior
   - Remove `Status: plan-review` header or mark retrospective
   - Remove or restore the missing adversarial-review-artifact references
   - Specify `md5`→`sha256` identity crosswalk or emit `identity-unresolved`
   - Align AC "≥1 gap YAML per domain on first run" with pseudocode reality
   - Define `L3-eligibility heuristic` concretely
3. Reopen #2392 with revised plan → run fresh adversarial review wave (Codex + Gemini) → iterate until APPROVE.

### Action 2: #2408 investigation — promote iter-4 artifacts or abandon

**Why:** only governance item left from session-2's drift list.

**How:**
1. `ls -la .planning/quick/review-2408-*` — see session-2's observation of iter-5 errored.
2. Read iter-4 `.planning/quick/review-2408-{codex,gemini}-r4.out` — do they contain useful Class A findings?
3. Decide:
   - **Promote:** `cp .planning/quick/review-2408-codex-r4.out scripts/review/results/2026-04-20-v4-plan-2408-codex.md`; same for gemini. Revise plan addressing findings. Then Fresh-MAJOR rollback may no longer apply.
   - **Abandon:** post governance comment explaining unpromoted iters were superseded by a different approach; remove stale `plan-approved` label; close or re-scope.

### Action 3: Repeat Path C for #2394 and #2395

Same shape as Action 1 but apply the attestation-dispatched adversarial review to each preserved plan first, then revise, then re-file. Each pass consumes ~1 Codex call (~90s) + revision work.

### Action 4: #2403 measurement phase

**Status:** still blocked on provisioning at least one of `OPENAI_API_KEY`, `VOYAGE_API_KEY`, or local `ollama`.

**How:** once any is available, the scaffold is ready — `uv run python scripts/knowledge/run_embeddings_spike.py` should run end-to-end.

### Action 5 (low priority): orphan-file cleanup

`git status` shows untracked `This` (981 bytes) and `Compatibility` (0 bytes) plus phantom `**...**` entries. All are artifacts of a prior heredoc mishap — `cat This` shows output from `file` command being mis-invoked with a markdown sentence as argv. Safe to `git clean -f -- This Compatibility` after confirming they're unrelated to any live work. Doesn't block anything; cosmetic.

## Adversarial review prompt — reusable template

Embedded in `scripts/review/submit-to-codex.sh` and `submit-to-gemini.sh` via `scripts/review/prompts/plan-review.md`. The new Evidence Authority section tells reviewers:
> If this prompt contains a `## Attested Evidence` block, prefer attested evidence over plan text. Do NOT return "unverified claims" findings for facts already covered by the attestation.

For one-off live dispatches (like session 3's Path A validation), a minimal adversarial prompt works:
```bash
PROMPT='You are an adversarial reviewer. Assume the plan has defects until proven otherwise. Do not praise or restate. Focus on what is wrong, missing, or risky. Return APPROVE only after affirmatively verifying each correctness-critical claim. Each finding must cite a specific plan section or quoted claim. An empty review is a failure.

If this prompt contains a "## Attested Evidence" block, treat plan-asserted facts (issue states, file existence, commit SHAs) as claims verified by that block. Do NOT return "unverified claims" findings for facts already covered by the attestation. Attested evidence outranks plan text.

Review this plan file per the adversarial contract above.'
```

## Known gotchas (cumulative, sessions 1+2+3)

Session-1 and -2 gotchas still apply. New from session 3:

15. **Attestation script allowlist is strict (`^docs/plans/[^/]+\.md$`), dispatcher check is looser (unanchored `docs/plans/[^/]+\.md$`).** Dispatchers normalize CONTENT_FILE to relative-to-REPO_ROOT before calling attestation; if REPO_ROOT is unset or file lives outside, attestation silently skips (fail-soft). No user-visible break, but review will lack attestation in those corner cases.

16. **`SOURCE_DATE_EPOCH` is an attestation affordance for tests.** Production users who want reproducible SHAs on unchanged plan state can set it; normally unset → current UTC.

17. **`Closes #NNNN` trailer auto-closes on push.** Memory `feedback_gh_issue_close_silent_comment_drop.md` covers the downstream comment-drop recovery (reopen → comment → close). Be aware if you intend to keep an issue open after commit.

18. **Label-edit side-effect: removing both `plan-review` and `plan-approved` leaves an issue with zero status labels.** This is correct per the missing-plan-drift remediation but looks "lost" in dashboards. Governance comments attached to each cleaned issue explain the state.

## Commits this session (chronological — on `main`)

```
965ced541 — feat(review): #2405 cross-review sandbox pre-verification attestation
c85657584 — docs(review): validation artifact proving #2405 attestation works end-to-end
```

Plus 14 GitHub API operations (7 label edits + 7 governance comments, all traceable via issue comment history).

## Memory relevance (cumulative)

Load at session start if not already auto-loaded (new in session 3 marked ⭐):

- `feedback_adversarial_review_stance.md`
- `feedback_cross_provider_review_payoff.md`
- `feedback_codex_needs_pushed_artifact.md`
- `feedback_codex_sandbox_write_blocked.md`
- `feedback_codex_sandbox_no_execution.md`
- `feedback_merge_race_silent_revert.md`
- `feedback_multi_agent_commit_serialization.md`
- `feedback_retry_loop_reset_hazard.md`
- `feedback_plan_past_tense_artifact_claims.md`
- `feedback_mock_vs_live_invocation_divergence.md`
- `feedback_gh_issue_close_silent_comment_drop.md`
- ⭐ `feedback_attestation_enables_contradiction_detection.md` — new this session
- ⭐ `feedback_never_offer_to_self_label_plan_approved.md` — new this session
- `project_doc_intel_operating_model.md`
- `project_hermes_codex_quota.md`

## First-message template for next session

```
Continuing doc-intel work from 2026-04-20 session 3. Context in
.planning/handoffs/2026-04-20-doc-intel-session-3-handoff.md.

First task: [pick one — Action 1 (#2392 revision + re-file),
Action 2 (#2408 investigation), Action 3 (#2394/#2395 revision),
Action 4 (#2403 measurement if provisioned), Action 5 (orphan-file
cleanup)].

If unclear, default to Action 1 (#2392 revision+re-file) — the
validation artifact at scripts/review/results/2026-04-20-validation
-2405-via-plan-2392-codex.md has already mapped the 6 defects that
need addressing; revision is the most scoped and has the clearest
path to APPROVE.

Before touching anything, verify state:
  gh issue view 2392 --json state,comments --jq '.state,"last comment: "+(.comments[-1].body[:200])'
  uv run pytest tests/review/test_attest_plan_claims.py --no-header -q
  git log --oneline -3
  ls .planning/quick/review-2408-*r*.out 2>&1 | head
```

## Session exit condition

All session-3 artifacts durable on `origin/main`. One issue definitively changed state:
- #2405 CLOSED (was reopened-then-closed) — fully implemented + tests + live validation

Working tree has parallel-session drift (unrelated) plus pre-existing orphan files (`This`, `Compatibility`). No uncommitted critical work from this session.

Session 4 starts clean.
