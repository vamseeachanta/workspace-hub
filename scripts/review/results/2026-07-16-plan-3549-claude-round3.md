I've completed the adversarial verification. Nearly every load-bearing claim in the plan checked out against the actual repository; the one genuine defect is a path-citation mismatch. Here's my structured review.

`★ Insight ─────────────────────────────────────`
- This worktree is a **sparse checkout** (`core.sparseCheckout=true`, `scripts/lib`/`docs/modules`/`docs/ops` not in the cone). A naive `[ -e file ]` existence probe reports tracked-but-unmaterialized files as "MISSING" — which would have produced ~4 false MAJOR findings. The reliable ground-truth check is `git ls-files --error-unmatch`, not the filesystem. This is exactly the "verify generated/state files against origin/main, not the working copy" and "sparse-clone 0-byte trap" lesson in your memory.
- The inherited-baseline reproduction also diverged for the same reason (sourcing `scripts/lib/workstation-lib.sh` errored because it isn't materialized), so the plan's recorded `13 passed` baseline is *not independently reproducible in this review env* — a verification gap on my side, not a plan error.
`─────────────────────────────────────────────────`

## Verdict
MINOR

## Retrieval
- Read the full plan `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` (lines 1–401).
- Read the review prompt `scripts/review/plan-review-prompt.md`.
- Existence-probed all Navigation-map and Changed-Path-map targets on the filesystem, then re-checked as git ground truth with `git ls-files --error-unmatch` (corrected sparse-checkout false negatives).
- `git config core.sparseCheckout` + `git sparse-checkout list` — confirmed sparse cone excludes `scripts/lib`, `docs/modules`, `docs/ops`.
- `git log 24d6c66d…`, `git merge-base --is-ancestor 24d6c66d HEAD`, `git for-each-ref --contains 24d6c66d`, `git for-each-ref` / `git remote -v` — checked commit ancestry and available refs.
- Reproduced the inherited baseline: `uv run pytest tests/workstations/{test_machine_path_resolver,test_registry,test_dev_secondary_ground_truth}.py -q`.
- `git ls-files | grep 3549 … review` — enumerated the actual review-artifact filenames.
- Verified closeout tooling: `scripts/workflow/completeness_score.py` (`def classify`, `def score_code` with `issue_number` kwarg), `scripts/workflow/render_completeness_html.py`.
- `git grep "Exact Runtime Contract"` in the design spec (line 161) — confirmed the normative section the plan delegates to exists.
- Read `ssh-dev-secondary.sh` and `connect-workspace-linux.sh`; grep'd IP literals across `scripts/operations/connection/`; grep'd registry keys in `config/workstations/registry.yaml`.

## Findings

1. **[MINOR — traceability] Review-artifact paths in the frontmatter and Navigation map do not exist.** Line 9 and lines 116–118 cite `scripts/review/results/2026-07-16-plan-3549-{claude,codex,gemini}.md` (no round suffix). `git ls-files` shows the actual tracked artifacts are round-suffixed: `…-claude-round1.md`, `…-claude-round2.md`, `…-codex-round{1,2}.md`, `…-gemini-round{1,2}.md`, plus `…-disagreement-round{1,2}.md`. The un-suffixed paths are untracked and absent. The Navigation map — which the plan calls an authority — points at files that don't exist, and there is no `-round3` artifact yet (this review is r3). Fix: cite the real round-suffixed filenames and add the r3 entries.

2. **[MINOR — unverifiable-in-env, self-mitigated] The "PR #3553 is on main / merged as `24d6c66d`" claim cannot be confirmed here and the implementation gate currently fails.** `git merge-base --is-ancestor 24d6c66d HEAD` → exit 1 (not an ancestor), and `git for-each-ref --contains 24d6c66d` returns nothing — this sparse worktree has *no* `main`/`origin/main` ref, only `chore/3549-registry-connection-design`. The merge commit object exists with message "Merge pull request #3553", consistent with a merge, but I cannot verify it landed on `main` from this environment. Not a blocker: the plan's Implementation Sequence step 1 (line 246) and Acceptance Criterion #1 (line 293) explicitly gate implementation on the `--is-ancestor` check passing on a fresh worktree, so the plan is self-protecting against exactly this. Flagging as an assertion the reviewer could not independently confirm.

3. **[MINOR — verification gap] The recorded inherited baseline is not reproducible in this checkout, so its exact failure-node name is unconfirmed.** Plan lines 84–90 record `1 failed, 13 passed, 1 skipped`, single failure = `test_registry_capabilities_cover_task_requires`. Reproduction here gave `1 failed, 11 passed, 1 skipped, 2 errors`, single *failure* = `test_ws_valid_machines_returns_all_names`, and the plan's cited node degraded to an *error* — all because `scripts/lib/workstation-lib.sh` is tracked but not materialized in this sparse cone. This is an environment artifact, not a plan defect; but it means the "no new failing node beyond the recorded `ecosystem-reconcile` failure" acceptance criterion (lines 326–328) rests on a baseline that should be re-captured on the full implementation checkout before it can be trusted as the comparison node.

## Checks that found nothing wrong (silence-is-failure guard)
The following plan claims were affirmatively verified as correct:
- **Substantive premise is real.** The three "disagreeing target literals" exist and disagree: `connect-workspace-linux.sh`=`10.0.0.1`, `connect-workspace-tailscale.sh`=`10.1.0.1`, `ssh-dev-secondary.sh`=`10.1.0.2` — the endpoint-guard recurrence-protection premise is sound.
- **`ssh-dev-secondary.sh` really does an authentication-probe fallback** (`ssh -o BatchMode=yes … exit` → Tailscale IP), exactly as line 197 describes; `connect-workspace-linux.sh` really hardcodes target/user defaults (line 198).
- **The `dev-secondary` "fixed ID" resolves** — it is a top-level registry key (`config/workstations/registry.yaml:173`), so the retained fixed-ID wrapper delegation is viable.
- **Closeout tooling exists and the cited signature is valid**: `score_code(...)` accepts `issue_number: int | None` (line 344–346 invocation is correct); `classify(...)` and `render_completeness_html.py` exist.
- **The normative design section exists**: `Exact Runtime Contract` at design-spec line 161 (plan line 129).
- **The five-wrapper scope is accurate** (5 SSH wrappers in the connection dir; `sync-tabby-*` and `vnc-ace-linux-2.sh` correctly excluded/deferred to #3550).
- All docs the plan marks "verified existing path" (`docs/modules/cli/WORKSPACE_CLI.md`, `…/SCRIPT_ORGANIZATION.md`, `docs/ops/remote-linux-access.md`, `scripts/lib/workstation-lib.sh`) **are tracked in git** — my initial filesystem "MISSING" flags were sparse-checkout false negatives and are withdrawn.

## Blockers
None. All three findings are MINOR. Finding 1 (wrong review-artifact citations) should be corrected for traceability but does not block implementation; findings 2 and 3 are verification limitations of the sparse review environment that the plan's own gates already guard against. Recommend the author fix the artifact-path citations and re-confirm the inherited baseline on the full implementation checkout at RED time.
