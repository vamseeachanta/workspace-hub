# Disagreement report — plan #3549 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **[MINOR — traceability] Review-artifact paths in the frontmatter and Navigation map do not exist.** Line 9 and lines 116–118 cite `scripts/review/results/2026-07-16-plan-3549-{claude,codex,gemini}.md` (no round suffix). `git ls-files` shows the actual tracked artifacts are round-suffixed: `…-claude-round1.md`, `…-claude-round2.md`, `…-codex-round{1,2}.md`, `…-gemini-round{1,2}.md`, plus `…-disagreement-round{1,2}.md`. The un-suffixed paths are untracked and absent. The Navigation map — which the plan calls an authority — points at files that don't exist, and there is no `-round3` artifact yet (this review is r3). Fix: cite the real round-suffixed filenames and add the r3 entries.
- **[MINOR — unverifiable-in-env, self-mitigated] The "PR #3553 is on main / merged as `24d6c66d`" claim cannot be confirmed here and the implementation gate currently fails.** `git merge-base --is-ancestor 24d6c66d HEAD` → exit 1 (not an ancestor), and `git for-each-ref --contains 24d6c66d` returns nothing — this sparse worktree has *no* `main`/`origin/main` ref, only `chore/3549-registry-connection-design`. The merge commit object exists with message "Merge pull request #3553", consistent with a merge, but I cannot verify it landed on `main` from this environment. Not a blocker: the plan's Implementation Sequence step 1 (line 246) and Acceptance Criterion #1 (line 293) explicitly gate implementation on the `--is-ancestor` check passing on a fresh worktree, so the plan is self-protecting against exactly this. Flagging as an assertion the reviewer could not independently confirm.
- **[MINOR — verification gap] The recorded inherited baseline is not reproducible in this checkout, so its exact failure-node name is unconfirmed.** Plan lines 84–90 record `1 failed, 13 passed, 1 skipped`, single failure = `test_registry_capabilities_cover_task_requires`. Reproduction here gave `1 failed, 11 passed, 1 skipped, 2 errors`, single *failure* = `test_ws_valid_machines_returns_all_names`, and the plan's cited node degraded to an *error* — all because `scripts/lib/workstation-lib.sh` is tracked but not materialized in this sparse cone. This is an environment artifact, not a plan defect; but it means the "no new failing node beyond the recorded `ecosystem-reconcile` failure" acceptance criterion (lines 326–328) rests on a baseline that should be re-captured on the full implementation checkout before it can be trusted as the comparison node.

### codex

- The strict-schema contract does not reject duplicate YAML mapping keys. Plan lines 143–159 and design lines 205–213 require complete validation before hashing, but the test matrix at plan lines 227–230 covers unknown keys and wrong types—not duplicate keys. `src/workspace_hub/workstations/resolver.py:38-50` uses `yaml.safe_load`, which empirically parsed duplicate `ssh` and duplicate overlay `address` fields by silently retaining the final value. This permits ambiguous security policy and attestation content to enter the supposedly strict snapshot. Both registry and overlay loaders need duplicate-key rejection tests and a rejecting loader.
- Fallback freshness semantics are under-specified. The design defines `max_age_seconds`, `verified_at`, and `expires_at` at `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md:165-195`, while plan lines 255–260 test only generic “freshness” and the TDD table at line 230 names only “stale.” Nothing requires rejection of future-dated verification, `expires_at <= verified_at`, or an expiry interval exceeding policy `max_age_seconds`. A loader can therefore satisfy the listed stale test while allowing an attestation to remain valid longer than registry policy permits.
- The governed-surface inventory is empirically incomplete. Plan lines 20 and 78 claim five helpers plus Tabby and `governed_existing_files=6`; lines 217–221 defer only `vnc-ace-linux-2.sh`. The tracked tree also contains `scripts/operations/connection/.fuse_hidden0002aeb10000414f` and `.fuse_hidden0002aeb100013f84`, both byte-identical VNC/SSH helper copies containing a fixed operator/host target. They also exist in merged commit `24d6c66d`. Plan lines 138 and 235 require every target-bearing surface to be classified, but the plan neither names, deletes, nor explicitly defers these unstable artifact paths.
- The linked-worktree acceptance criterion conflicts with the declared scope. Plan lines 281–283 and 320–321 claim `install-hooks.sh` will work in normal and linked worktrees, while risk lines 388–391 say #3549 will change only the endpoint-guard insertion path and defer broader installer hardening to #3435. Yet `scripts/enforcement/install-hooks.sh:32`, `:47`, `:73`, and `:248` still construct `${REPO_ROOT}/.git/hooks/...`; in a linked worktree `.git` is a file, and the first `cp` at line 38 exits under `set -e`. Resolving only the new guard’s insertion path cannot make the installer pass a real linked-worktree test. The plan must either authorize conversion of every hook destination in this installer or narrow the acceptance claim and defer linked-worktree support.
- The review-artifact pointers do not resolve. Plan lines 9 and 116–118 name `2026-07-16-plan-3549-{claude,codex,gemini}.md`, but all three files are absent; only `*-round1.md` and `*-round2.md` exist. Plan line 359 additionally claims the canonical Gemini stub was retained, which is false in the reviewed tree. Current review evidence must be written to revision-stamped, non-empty paths and the plan pointers updated before the review gate is represented as complete.
- Plan line 317 specifies bare `python scripts/enforcement/check-connection-helper-endpoints.py --staged`, contradicting the repository command contract requiring `uv run` for Python. This also assumes a `python` executable exists independently of the plan’s uv-managed runtime. Use the reviewed runtime form consistently or explicitly justify a directly executable stdlib hook entry point.

### gemini

- (none)

