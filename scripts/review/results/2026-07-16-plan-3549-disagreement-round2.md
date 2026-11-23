# Disagreement report — plan #3549 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-round1 | MAJOR |
| claude | MAJOR |
| codex-round1 | MAJOR |
| codex | MAJOR |
| disagreement-round1 | | Provider | Verdict | |
| gemini-round1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-round1

(no findings unique to this provider)

### claude

- **The closeout completeness ACs (lines 344–350) cannot fire for this issue as labeled — a false gate.** `completeness-gate.yml:25` gates the server Action on `contains(…labels…, 'gate:completeness')`. Issue #3549 does **not** carry `gate:completeness` (verified via `gh issue view`; the sibling #3548 does). The plan has no implementation-sequence step and no changed-path entry that adds the label. As written, AC line 349 ("the server completeness Action succeeds") is satisfied vacuously — the job's `if:` is false, so it is **skipped**, gating nothing, while reading as "passed." Either add an explicit step to apply `gate:completeness` (making the gate real) or mark the completeness ACs N/A for this opt-in-only issue. This is exactly the "enforced-but-actually-skipped" false-green class the adversarial review exists to catch.
- **Internal tense contradiction about PR #3553 status.** Line 32 (Standards) states "the canonical runbook remains pending through PR #3553," but line 62 (Gaps) states "PR #3553 is now on `main`," and lines 44–47 cite the runbook `docs/ops/remote-linux-access.md` as an *establishing* source. Verified: #3553 is MERGED and the runbook exists on origin/main — so "remains pending" (line 32) is stale/false. The plan simultaneously treats the runbook as pending (line 32), as an authoritative existing source (line 44), and as a Conditional post-rebase edit target (line 210). Reconcile line 32 to reflect the merged state.
- **The plan document's own working base does not yet contain #3553; the RI reads as if it does.** Worktree HEAD `b9df21e55` is not a descendant of `24d6c66…` (verified) and the runbook is absent from the worktree. Implementation step 1 and AC #292 do mandate the rebase, and the Conditional row (line 210) is explicitly gated on "After rebasing onto merged PR #3553" — so the plan is *recoverable* — but the RI/Evidence sections assert integration ("PR #3553 is now on `main`") without stating that the plan's own branch has not been rebased. If the implementer trusts the RI and skips the rebase, the runbook Conditional row (line 210) operates on a nonexistent file. Add an explicit precondition that the runbook edits are unreachable until the rebase lands.
- **Gitleaks v8.30.1 release existence is unverified (no network on this runner).** Design spec line 306 and AC #336 pin `v8.30.1` against `https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1`. The checksum-verify procedure fails closed if the artifact is absent (self-protecting), but a nonexistent/renamed release would dead-end the closeout scan. Confirm the release + `gitleaks_8.30.1_checksums.txt` are actually published before relying on this at closeout.
- **New CLI lives under `scripts/`, outside the `src/` package tree the completeness snapshot measures — coverage-substrate gap.** The most security-sensitive new surface, `scripts/operations/connection/connect-workstation.py` (line 194, the "shell-free OpenSSH launch boundary"), is not a `src/workspace_hub/*` package member. `classify()` (verified: `completeness_score.py:83`) still returns "code" via `connection.py`, and `score_code`'s `changed_code_coverage` is a caller-supplied float — so the implementer *can* include the CLI, but nothing in the plan guarantees the CLI's coverage is counted. Add an explicit AC that changed-code coverage includes the CLI file, or the completeness score can pass at threshold while the launcher itself is untested-by-measure.
- **Navigation-map artifact filenames hardcode `2026-07-16` but the renderer is date-of-run.** `render_completeness_html.py:69` writes `{date.today()}-{issue}-completeness.html`; navigation map lines 105/115 hardcode the `2026-07-16` date. If implementation lands on a later date, the emitted completeness/plan HTML filenames drift from the map. The map is declared non-authoritative for changes (lines 184–185), so this is cosmetic — but the "compare sorted changed paths with the canonical map" step (line 285, AC line 332) should compare against the *canonical implementation map*, not the dated navigation map, to avoid a spurious mismatch.

### codex-round1

(no findings unique to this provider)

### codex

- Plan AC lines 341-350 require completeness scoring, `status:completeness-verified`, and “the server completeness Action succeeds,” but `.github/workflows/completeness-gate.yml` lines 23-25 only runs when the closed issue has `gate:completeness`. Live #3549 labels do not include `gate:completeness`. The plan has no step to apply that label, so the server gate can skip while the AC reads as enforced.
- Plan line 31 says “the canonical runbook remains pending through PR #3553,” but lines 60-61 say “PR #3553 is now on `main`,” and live `gh pr view 3553` verifies it is merged. This is an internal stale-state contradiction in a dependency gate.
- Plan lines 44-47 cite `docs/ops/remote-linux-access.md` as a consulted authority, but the reviewed worktree HEAD `b9df21e55...` is not a descendant of `24d6c66...`, and `docs/ops/remote-linux-access.md` is absent from that worktree. The file exists on `origin/main`, so the plan must explicitly require rebasing before treating that source as locally verified.
- Plan header line 9 and artifact map lines 116-118 cite `scripts/review/results/2026-07-16-plan-3549-codex.md`, but that file is 0 bytes. The substantive Codex artifact appears to be `scripts/review/results/2026-07-16-plan-3549-codex-round1.md`. The plan’s review-artifact pointers are not reliable evidence as written.

### disagreement-round1

- A finding is 'unique to X' if its text appears in X's artifact but not
- verbatim in any other provider's artifact.
- ### claude
- ### codex
- ### gemini

### gemini-round1

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

