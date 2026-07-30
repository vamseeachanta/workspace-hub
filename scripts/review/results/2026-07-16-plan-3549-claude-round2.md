I've verified the plan's load-bearing claims. Most hold up: PR #3553 and the runbook are genuinely on `origin/main`, the design spec's normative section exists, the SSH helpers and tests exist, and the `completeness_score`/`render_completeness_html` APIs match the closeout AC exactly. But I found concrete defects in the closeout gate and internal consistency. Here is the review.

`★ Insight ─────────────────────────────────────`
- The sharpest class of plan defect here isn't wrong code — it's a **closeout acceptance criterion that reads as enforced but structurally no-ops**. GitHub Action `if:` gates keyed on an opt-in label silently *skip* (report neutral/success) rather than *fail* when the label is absent, so "the Action succeeds" can be vacuously true while gating nothing.
- Plans drafted across a merge boundary (pre- vs post-#3553) accumulate **tense contradictions** — one section says a dependency "remains pending," another says it's "now on main." Both can't be current.
`─────────────────────────────────────────────────`

## Verdict
MAJOR

## Retrieval

- Read the full plan `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` (lines 1–400) in the worktree.
- `git merge-base --is-ancestor 24d6c66… HEAD` in the worktree → **NO** (HEAD `b9df21e55` does not contain PR #3553); `… origin/main` → **YES** (origin/main at `42eca007a`).
- `ls` verified existence of: `resolver.py`, design spec, `scripts/lib/workstation-lib.sh`, `config/tabby/{config.yaml,QUICK_REFERENCE.md,INTERNET_ACCESS_SUMMARY.md}`, all 5 SSH wrappers + `vnc-ace-linux-2.sh` + `sync-tabby-*` under `scripts/operations/connection/`, `docs/modules/cli/{WORKSPACE_CLI.md,SCRIPT_ORGANIZATION.md}`, `install-hooks.sh`, `completeness_score.py`, `render_completeness_html.py`, `registry.yaml`, and the 3 inherited workstation test files.
- `git cat-file -e origin/main:docs/ops/remote-linux-access.md` → EXISTS on origin/main; MISSING in the current worktree.
- `gh issue view` for #3547/#3548/#3549/#3550/#3552/#3435 and `gh pr view 3553` — confirmed states/labels; PR #3553 MERGED at `24d6c66…` 2026-07-16T11:18:51Z.
- Read `completeness_score.py` lines 83–160 (`classify`, `score_code(..., issue_number=…)`) and `render_completeness_html.py` lines 55–80 (`json.load(sys.stdin)`, argv[1]=issue, argv[2]=title) — both match plan AC lines 344–347.
- `grep` design spec for Gitleaks pin → lines 295–306 pin v8.30.1 with checksum verification.
- Read `.github/workflows/completeness-gate.yml` line 25 (`if: contains(github.event.issue.labels.*.name, 'gate:completeness')`); confirmed #3549 carries **no** `gate:completeness` label.

## Findings

1. **The closeout completeness ACs (lines 344–350) cannot fire for this issue as labeled — a false gate.** `completeness-gate.yml:25` gates the server Action on `contains(…labels…, 'gate:completeness')`. Issue #3549 does **not** carry `gate:completeness` (verified via `gh issue view`; the sibling #3548 does). The plan has no implementation-sequence step and no changed-path entry that adds the label. As written, AC line 349 ("the server completeness Action succeeds") is satisfied vacuously — the job's `if:` is false, so it is **skipped**, gating nothing, while reading as "passed." Either add an explicit step to apply `gate:completeness` (making the gate real) or mark the completeness ACs N/A for this opt-in-only issue. This is exactly the "enforced-but-actually-skipped" false-green class the adversarial review exists to catch.

2. **Internal tense contradiction about PR #3553 status.** Line 32 (Standards) states "the canonical runbook remains pending through PR #3553," but line 62 (Gaps) states "PR #3553 is now on `main`," and lines 44–47 cite the runbook `docs/ops/remote-linux-access.md` as an *establishing* source. Verified: #3553 is MERGED and the runbook exists on origin/main — so "remains pending" (line 32) is stale/false. The plan simultaneously treats the runbook as pending (line 32), as an authoritative existing source (line 44), and as a Conditional post-rebase edit target (line 210). Reconcile line 32 to reflect the merged state.

3. **The plan document's own working base does not yet contain #3553; the RI reads as if it does.** Worktree HEAD `b9df21e55` is not a descendant of `24d6c66…` (verified) and the runbook is absent from the worktree. Implementation step 1 and AC #292 do mandate the rebase, and the Conditional row (line 210) is explicitly gated on "After rebasing onto merged PR #3553" — so the plan is *recoverable* — but the RI/Evidence sections assert integration ("PR #3553 is now on `main`") without stating that the plan's own branch has not been rebased. If the implementer trusts the RI and skips the rebase, the runbook Conditional row (line 210) operates on a nonexistent file. Add an explicit precondition that the runbook edits are unreachable until the rebase lands.

4. **Gitleaks v8.30.1 release existence is unverified (no network on this runner).** Design spec line 306 and AC #336 pin `v8.30.1` against `https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1`. The checksum-verify procedure fails closed if the artifact is absent (self-protecting), but a nonexistent/renamed release would dead-end the closeout scan. Confirm the release + `gitleaks_8.30.1_checksums.txt` are actually published before relying on this at closeout.

5. **New CLI lives under `scripts/`, outside the `src/` package tree the completeness snapshot measures — coverage-substrate gap.** The most security-sensitive new surface, `scripts/operations/connection/connect-workstation.py` (line 194, the "shell-free OpenSSH launch boundary"), is not a `src/workspace_hub/*` package member. `classify()` (verified: `completeness_score.py:83`) still returns "code" via `connection.py`, and `score_code`'s `changed_code_coverage` is a caller-supplied float — so the implementer *can* include the CLI, but nothing in the plan guarantees the CLI's coverage is counted. Add an explicit AC that changed-code coverage includes the CLI file, or the completeness score can pass at threshold while the launcher itself is untested-by-measure.

6. **Navigation-map artifact filenames hardcode `2026-07-16` but the renderer is date-of-run.** `render_completeness_html.py:69` writes `{date.today()}-{issue}-completeness.html`; navigation map lines 105/115 hardcode the `2026-07-16` date. If implementation lands on a later date, the emitted completeness/plan HTML filenames drift from the map. The map is declared non-authoritative for changes (lines 184–185), so this is cosmetic — but the "compare sorted changed paths with the canonical map" step (line 285, AC line 332) should compare against the *canonical implementation map*, not the dated navigation map, to avoid a spurious mismatch.

## Blockers

- **Finding 1** — the completeness-gate ACs must be corrected before implementation: either add an explicit step to apply the `gate:completeness` label to #3549 (so the server Action actually fires and AC #349 is meaningful), or explicitly scope the completeness ACs out as non-applicable for this opt-in-only issue. Shipping an AC that reads as an enforced gate while structurally no-opping is a false-green defect.
- **Finding 2** — resolve the stale "runbook remains pending through PR #3553" claim (line 32) against the verified merged state; the contradiction with line 62 must be fixed so reviewers/implementers aren't working from a self-contradicting dependency status.

Findings 3–6 are MINOR (advisory / verify-before-closeout) and do not independently block, but Finding 3 should be folded into the rebase precondition so the runbook Conditional row isn't attempted pre-rebase.
