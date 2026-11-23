# Exit handoff — Conflict-marker hook ([#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) closed) + SOUL rules ([#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724) plan-review) + 2 follow-ons

Date: 2026-05-16 (evening session)
Repository: `vamseeachanta/workspace-hub`
Predecessor: [`2026-05-16-soul-ecosystem-followup-entry.md`](2026-05-16-soul-ecosystem-followup-entry.md) (this session opened against that entry prompt)

## Scope completed in this session

Three issue chains landed end-to-end through the issue-planning-mode workflow (plan → T3 adversarial review → r3 inline absorb → user-gated approval → TDD impl → close):

### [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) — pre-commit conflict-marker hook (CLOSED)

Full TDD execution in one session. T3 adversarial review (Claude+Codex+Gemini) returned **3× MAJOR** with **29 distinct findings, only 3 overlapping**. r3+r4 inline patches absorbed every blocker. Implementation: 905 lines (4 new shell scripts + manifest + 26 pytest cases + 2 infra modifications + approval marker). 88/88 enforcement suite passes (62 existing + 26 new). Live smoke test confirmed hook blocks marker content with `file:line` citations. Self-hosting: my own implementation commit landed via the live hook.

### [#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724) — 5 SOUL Must-Fire Rules (status:plan-review)

Filed in response to user request to encode this session's review-derived learnings into the SOUL infrastructure. T3 review wave returned Claude MAJOR (7 findings) + Codex MAJOR (8 findings) + Gemini MAJOR (6 findings, **all false-positive sandbox blindness** per `feedback_gemini_sandbox_overlay_blindness`). 15 legit findings absorbed via r3 inline. **Awaits user approval.**

Codex worked on first attempt this round — `env -u CLAUDECODE bash plan-review-fanout.sh ... --providers=...` upfront, no retry needed. Workaround upgraded from "fallback" to "first-class" in this session's memory.

### [#2723](https://github.com/vamseeachanta/workspace-hub/issues/2723) — pre-commit dead-code cleanup (filed, low-priority)

Deferral from #2722 Claude r1 finding #13. Issue-specific small cleanup; not generalizable.

### [#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725) — SOUL auto-load for Claude+Gemini (filed, status:needs-plan)

Architectural gap surfaced by #2724 Claude r1 finding #1: of 5 SOUL runtime artifacts built by `build-soul-runtime.sh`, only 2 (Hermes + Codex) auto-load via symlinks; Claude+Gemini reference the artifacts in CLAUDE.md/GEMINI.md by path but the surface doesn't transitively load them. Today's Must-Fire Rules fire for 2 of 4 intended providers.

### Pipeline structure executed (3 nested chains)

```
Entry: 2026-05-16-soul-ecosystem-followup-entry.md
  ↓
Preflight (5/5 pass: commits on origin, pytest, drift, symlinks, GH state)
  ↓
Tier 1 close-out comment drafts (user-applied actions surfaced)
Tier 2 PR-merge mergeability diagnosed (1 CLEAN, 2 baseline-red-not-PR-broken)
Tier 3 #2722 plan + T3 review + r3+r4 + user-approval + TDD impl + close
  ↓
User asks: does SOUL have what it needs? → 5 SOUL rules drafted
User chooses: file issue first → #2724 chain spun up
  ↓
#2724 plan + T3 review + r3 absorb + status:plan-review (awaiting approval)
  ↓
3 follow-ons surfaced organically:
  - #2723 (filed, deferral from #2722)
  - #2725 (filed, auto-load gap from #2724)
  - SOUL change docs (handoff being written now)
```

## Commits landed (5 total, all `origin/main`)

| # | Commit | What landed |
|---|---|---|
| 1 | [`0e62057d6`](https://github.com/vamseeachanta/workspace-hub/commit/0e62057d6) | #2722 plan draft (382 lines) + README index row |
| 2 | [`122a9bf1f`](https://github.com/vamseeachanta/workspace-hub/commit/122a9bf1f) | #2722 r3+r4 absorb (plan → 793 lines) + 3 review artifacts + disagreement.md |
| 3 | [`340af0021`](https://github.com/vamseeachanta/workspace-hub/commit/340af0021) | #2722 implementation (905 lines: 4 scripts + manifest + tests + 2 infra mods + approval marker) → **CLOSES #2722** |
| 4 | [`cae347193`](https://github.com/vamseeachanta/workspace-hub/commit/cae347193) | #2724 plan draft + README index row |
| 5 | [`1ca99ff5c`](https://github.com/vamseeachanta/workspace-hub/commit/1ca99ff5c) | #2724 r3 absorb + 3 review artifacts + disagreement.md |

Net: ~1,500 lines added across docs/plans, scripts/review/results, scripts/enforcement, scripts/agents, scripts/memory, tests/enforcement, .planning/plan-approved.

## Repo states at session end

- **`workspace-hub` HEAD**: `1ca99ff5c` on `origin/main` (auto-sync confirmed; preflight verified all 5 session commits present).
- **Working tree**: ~25 modified/untracked files, all auto-sync state / kanban / quota / memory snapshots — **none touched by this session's commits** (pathspec form preserved isolation per `feedback_retry_loop_sweep_contamination`).
- **Tests**: `uv run python -m pytest tests/enforcement/` → **88 passed** (62 pre-existing + 26 new from #2722).
- **Drift check**: `scripts/enforcement/check-soul-runtime-drift.sh` → all 5 runtime artifacts in sync with sources.
- **Conflict-marker hook**: wired into `.git/hooks/pre-commit` of workspace-hub itself (before line 49 `exit 0`); live verified.
- **Cross-repo installer reach (probed live)**: of 7 tier-1 repos in manifest, only 3 are checked out on this machine (workspace-hub self, digitalmodel, llm-wiki). The other 4 (assetutilities, worldenergydata, assethold, aceengineer-website) live on other machines; installer correctly skips them with notice.

## Issues touched

- **[#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722)** — **CLOSED** via commit `340af0021` `Closes #2722` trailer. Closeout summary at [issuecomment-4468402596](https://github.com/vamseeachanta/workspace-hub/issues/2722#issuecomment-4468402596).
- **[#2723](https://github.com/vamseeachanta/workspace-hub/issues/2723)** — OPEN, priority:low, `cat:harness`. Pre-commit dead-code cleanup deferral.
- **[#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724)** — OPEN, `status:plan-review`. Plan absorbed full T3 review; awaits user approval.
- **[#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725)** — OPEN, `status:needs-plan`. SOUL auto-load architectural gap.

Carry-forward from this morning's session (still pending user action):
- **[#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719)** — OPEN, `status:plan-approved`. Close-out comment drafted; awaits `gh issue close 2719`.
- **[#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411)** — OPEN. Close-out comment drafted; awaits `gh issue close 2411`.
- **3 sibling PRs** ([worldenergydata#415](https://github.com/vamseeachanta/worldenergydata/pull/415), [aceengineer-website#15](https://github.com/vamseeachanta/aceengineer-website/pull/15), [assethold#51](https://github.com/vamseeachanta/assethold/pull/51)) — OPEN, mergeability diagnosed:
  - aceengineer-website#15: CLEAN (mergeable + all checks pass)
  - worldenergydata#415: BLOCKED on PR-unrelated baseline-red CI (`feedback_ci_baseline_red_not_pr_broken`); admin-via-ruleset toggle
  - assethold#51: UNSTABLE on PR-unrelated baseline-red CI; admin-via-ruleset toggle

## What this session unblocks

1. **Conflict-marker hook is now live on `ace-linux-1` workspace-hub.** Any commit that stages anchored `<<<<<<<` + `>>>>>>>` content at column 0 (outside path-restricted forensic-allowlist sentinels) is blocked at commit time. Smoke test verified.
2. **Hook bootstraps onto sibling repos when each machine runs `bootstrap-machine.sh §2.6`** (added in commit `340af0021`). Per-machine coverage; not all 7 tier-1 repos reachable from a single machine.
3. **Drift check and installer reach are observable**: `scripts/enforcement/check-pre-commit-hook-drift.sh` reports per-sibling state; current ace-linux-1 state shows 2 unprotected siblings (digitalmodel, llm-wiki) until installer runs.
4. **Codex `env -u CLAUDECODE` workaround is documented + memory-promoted** for future review dispatches. The first-class fallback alongside `script -qc`.
5. **#2724 plan is review-ready**: if user approves, implementation is mechanical (single file edit + rebuild + 30 grep verifications + commit), estimated 15-20 min.

## Reviewer artifacts (for audit)

### #2722
- Plan body: [`docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md`](../plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md) (793 lines, r3+r4 final)
- Review wave: `scripts/review/results/2026-05-16-plan-2722-{claude,codex,gemini,disagreement}.md`
- Closeout comment: [issuecomment-4468402596](https://github.com/vamseeachanta/workspace-hub/issues/2722#issuecomment-4468402596)

### #2724
- Plan body: [`docs/plans/2026-05-16-issue-2724-soul-must-fire-rules-from-2722-review.md`](../plans/2026-05-16-issue-2724-soul-must-fire-rules-from-2722-review.md) (r3-absorbed)
- Review wave: `scripts/review/results/2026-05-16-plan-2724-{claude,codex,gemini,disagreement}.md`
- Plan summary comment: [issuecomment-4468460776](https://github.com/vamseeachanta/workspace-hub/issues/2724#issuecomment-4468460776)

## New memory artifacts this session

- `feedback_codex_cli_0_124_upstream_regression.md` — **UPDATED** with `env -u CLAUDECODE` workaround (validated 2026-05-16 evening: codex returned MAJOR + 8 findings on first attempt via env-unset). The two workarounds (`script -qc` for non-TTY contexts; `env -u CLAUDECODE` for Claude-Code-Bash-invoked contexts) address different sub-paths of the same TTY-detection bug class.

## No external-action status

- No external messages sent (Gmail, GitHub PRs to other repos, etc.).
- No mutation of shared infrastructure (CI/CD, secrets, deploys).
- All 4 GH issue comments (#2722 closeout, #2722 close-via-trailer, #2724 plan summary, plus #2723+#2725 issue creations) were user-authorized via session direction.
- 2 subagent dispatches (both `plan-review-fanout.sh` invocations for #2722 and #2724); completed cleanly.

## Outstanding from prior session (Tier 1+2 user-applied actions, still pending)

These were drafted earlier in THIS session but require user-side action:

```bash
# Tier 1 close-outs (issue close requires user gate per never-self-approve discipline)
gh issue close 2719 --repo vamseeachanta/workspace-hub --comment "<see drafted text in this session>"
gh issue close 2411 --repo vamseeachanta/workspace-hub --comment "<see drafted text in this session>"

# Tier 2 sibling-repo PR merges
gh pr merge 15 --repo vamseeachanta/aceengineer-website --squash --auto   # CLEAN — direct merge
# 415 and 51 are baseline-red (PR-unrelated); admin-via-ruleset toggle pattern
```

## Next-step candidates for follow-on session

1. **Approve or revise #2724** (`status:plan-review` → `status:plan-approved` + marker, or post revision-request comment) — implementation is mechanical post-approval.
2. **Plan #2725** (SOUL auto-load for Claude+Gemini) — architectural; T2 likely; would unlock all 14+5 Must-Fire Rules for the 2 underserved providers retroactively.
3. **Run cross-repo installer on this machine** to propagate the #2722 hook to digitalmodel + llm-wiki (drift check currently reports both as unprotected). User-applied: `bash scripts/agents/install-pre-commit-hook-cross-repo.sh`.
4. **Cross-machine bootstrap dry-run on ace-linux-2** — empirically validates the §2.6 bootstrap-machine integration for #2722 (and the #2719 §2.5 SOUL symlinks). User-driven per `feedback_cross_machine_execution`.
5. **Plan #2723** (pre-commit dead-code cleanup) — low-priority; small T1.
6. **Tier 4 deferred from morning session**: per-repo adapter-parity rollout (5 sibling repos PARTIAL per #2411 inventory).

## Empirical lessons re-validated this session

- **Cross-provider review payoff**: 29 distinct findings on #2722, only 3 overlap. Single-provider would have missed ~90%. Each provider has unique coverage (Codex: threat-model + infrastructure gaps; Claude: empirical fact-checking + portability; Gemini: worktree + filename-handling edge cases + sandboxed-overlay self-discounting failure-mode).
- **`env -u CLAUDECODE` works first-attempt** for codex review from Claude-Code-Bash context; promoted to first-class workaround alongside `script -qc`.
- **r3 inline patches break the loop** when r1/r2 surface different defects (#2722 and #2724 both followed this pattern; no r3-dispatch needed).
- **Plan-approval gate is load-bearing** but user-direct-instruction overrides: today the marker for #2722 was created mid-session under explicit user instruction (`approved #2722`, `continue`); the gate accepted on commit and let implementation proceed.
- **`feedback_gemini_sandbox_overlay_blindness` is reproducible**: Gemini's r2 on #2724 returned 6 MAJOR findings all of the form "file does not exist at HEAD" for files that demonstrably exist. Recorded as transparent provenance, not absorbed.
