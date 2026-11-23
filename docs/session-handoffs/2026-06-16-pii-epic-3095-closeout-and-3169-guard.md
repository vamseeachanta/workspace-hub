# Session handoff — PII epic #3095 closeout + #3169 guard follow-up

**Date:** 2026-06-16 · **Host:** ace-linux-2 · **PII-free by construction** (codenames/issue-numbers only; client names live only in private `aceengineer-strategy`).

## Scope
Finish the public-repo client-PII epic [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095) (last 14 functional dev-ops scripts + closeout), then implement the prevention follow-up [#3169](https://github.com/vamseeachanta/workspace-hub/issues/3169) it surfaced.

## Outcome — both fully closed
- **Epic #3095 CLOSED** — sub-issues #3096/#3097/#3098/#3099 all closed. Final guard on `main`: **0 client identifiers across 21,356 tracked files** (`scripts/legal/check-client-pii.py --all`).
- **#3169 CLOSED** — guard now also scans commit messages + PR title/body (closed via the #2798 completeness gate: evidence 90% ≥ 80, owner-verified).

## Merged this session (all on `main`)
| PR | What |
|---|---|
| [#3164](https://github.com/vamseeachanta/workspace-hub/pull/3164) | 5 closeout-sweep residuals + `config/.*.local` gitignore glob |
| [#3165](https://github.com/vamseeachanta/workspace-hub/pull/3165) | bash dev-ops repo-list externalization (coordination/git + automation) |
| [#3166](https://github.com/vamseeachanta/workspace-hub/pull/3166) | python automation + `src/ace/router.py` route externalization |
| [#3167](https://github.com/vamseeachanta/workspace-hub/pull/3167) | Windows `.bat` repo-list externalization |
| [#3168](https://github.com/vamseeachanta/workspace-hub/pull/3168) | counts-only artifact `analysis/3095-epic-closeout.md` |
| [#3173](https://github.com/vamseeachanta/workspace-hub/pull/3173) | #3169 guard: commit-message + PR-metadata scanning (text mode, commit-msg hook, CI step) |
| [#3175](https://github.com/vamseeachanta/workspace-hub/pull/3175) | #3169 completeness artifact |

## Externalization model (CTA-B)
The 14 dev-ops scripts hardcoded client repo names in lists/maps/routing they commit/push/`cd`/route into. Fix = change **only list-acquisition** (source from gitignored per-host `config/.*.local`), leaving commit/push/route logic byte-identical → verifiable without running the destructive code. Real lists are gitignored; committed `config/*.local.example` templates document each format; canonical copies + a provisioning README are in private `aceengineer-strategy/pii-remediation/3098-provisioning/`.

## Prevention (now covering every public surface)
`check-client-pii.py` (engine-shared with the redactor; never prints the match) scans **tracked files** (pre-commit `--staged` + CI diff), **commit messages** (auto-wired `commit-msg` hook + CI per-commit, fails-closed), and **PR title/body** (CI, env-passed). Strict in CI via the `LEGAL_CLIENT_MAP` secret; degrade-open locally. Docs: `.claude/docs/client-pii-prevention.md`.

## Repo states at exit
- **`workspace-hub`:** all session work merged to `main`. **NOTE:** at exit the shared clone is checked out on **another session's** branch `chore/harness-tools-agy-update` (PR [#3177](https://github.com/vamseeachanta/workspace-hub/pull/3177)) — **not this session's work; left undisturbed.** This session's handoff branch was cut from `origin/main` and the clone restored to the chore branch afterward.
- **`aceengineer-strategy`:** clean, pushed (`9e91f16`) — holds the codename maps (incl. the redactor-map boundary fix) + the `3098-provisioning/` provision files.

## External actions taken (all operator-authorized)
- Merged PRs #3164–#3168, #3173, #3175 (you merged; never self-merged public `main`).
- Set/re-set the `LEGAL_CLIENT_MAP` CI secret (latest = with the redactor-map boundary fix).
- ssh ace-linux-1 (explicitly authorized): provisioned the 6 `config/.*.local` files + refreshed the codename map + added the gitignore glob to `.git/info/exclude`; did **not** touch its in-flight `plan/3062-retirement-replan` branch.
- Closed #3095/#3096/#3098/#3169 with summary comments; filed #3169; dispatched plan- + code-stage cross-reviews.
- No other outward actions.

## Accepted residual (out of scope)
Git-history scrub is **HEAD-only** (accepted). Two `main` commit messages from the #3098 closeout carry 3 short codename-source tokens (file content is clean; rewriting protected `main` is more destructive than the residue). The #3169 guard now **prevents** this recurring for new PRs.

## Next steps (operator-side, non-urgent)
- **Windows smoke-test** the 4 `scripts/windows/*.bat` on ace-win-1 — could not run `cmd.exe` from Linux; verified via guard + standard batch idioms + parse/path simulation only.
- The redactor-map boundary fix is live in the CI secret + both dev hosts + canonical map; no further action needed.
