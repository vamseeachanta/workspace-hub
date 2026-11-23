# Plan for #3179: gate scripts mis-resolve REPO_ROOT under git hooks in a worktree

> **Status:** adversarial-reviewed — T3 complete (r1 Claude + r2 Codex + Gemini all folded; design pivoted to git-free structural root; see Review Log)
> **Complexity:** T3 (3 providers reviewed — systemic gate-surface change on the pre-push path)
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3179
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-16-plan-3179-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- **Found** `scripts/testing/run-all-tests.sh:16` — `REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"`, then `source "${REPO_ROOT}/scripts/lib/tier1-repos.sh"` at line 25. This is the reported failure site.
- **Found** the pre-push hook `.git/hooks/pre-push.sh:19` derives its OWN root with bare `REPO_ROOT="$(git rev-parse --show-toplevel)"` (no `-C`, cwd = repo top during push) — immune because cwd is the repo top.
- **Found** the OTHER gate script `scripts/quality/check-all.sh:8` derives root with **pure path arithmetic, no git**: `REPO_ROOT="${QUALITY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"` (under `set -uo pipefail`, no `-e`). This is why `check-all` ran fine while `run-all-tests` failed — a *different* immunity than the hook's, and notably already the safe `cd/pwd` pattern. (r1 finding 2 correction.)
- **Found** the hook invokes the script as `bash "$RUN_TESTS" --repo "$repo"` (pre-push.sh:168), inheriting the hook's environment. Git exports `GIT_DIR` into the hook **only when pushing from a worktree**; from the main checkout `GIT_DIR` is unset and the bug does not occur (matches the #3178 worktree-push symptom). (r1 finding 4.)
- **Found (blast radius)** **34** call sites use `git -C … rev-parse --show-toplevel` across `scripts/` (recount per r1 finding 5). The load-bearing pre-push-path fix is `scripts/testing/run-all-tests.sh:16` (so the correct REPO_ROOT propagates into the sourced `tier1-repos.sh`); `scripts/testing/run-benchmarks.sh:20` is the same gate-surface dir; `scripts/lib/tier1-repos.sh:29` is **defense-in-depth, NOT highest-leverage** — in the failing flow the sourcing script sets `REPO_ROOT` before `source`, so `_tier1_repos_resolve_file` returns at the `$REPO_ROOT/config/...` step and line 29's git fallback is never reached (r1 finding 3). Broader follow-on (CI / pre-commit / maintenance): `scripts/review/*.sh`, `scripts/enforcement/check-*.sh`, `scripts/maintenance/*.sh`, `scripts/session/detect-drift.sh`, `scripts/install/codex-dispatch-prep.sh`.
- **Gap** no shared, tested `repo_root` resolver exists; each script re-implements the same fragile pattern (often with a `2>/dev/null || <fallback>` that does NOT help — see Root Cause).

### Standards
Not applicable (infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (infrastructure).

### Documents consulted
- `.claude/rules/coding-style.md` — "use `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode absolute paths"; the fix must preserve this (no hardcoded `/mnt/local-analysis/...`).
- `.claude/rules/patterns.md` — enforcement gradient (prefer a tested script/helper over prose).
- `SHARED_SOUL.md` must-fire "Promote generalizable review findings" (worktree-incompatibility is a named class) — motivates the shared-helper approach over a one-line patch.
- Prior art: `scripts/lib/tier1-repos.sh`, `scripts/lib/model-registry.sh`, `scripts/lib/uv-env.sh` already establish the `scripts/lib/*.sh` sourced-helper pattern.

---

## Step 1.5 — Reproduce the alleged failure (DONE)

Confirmed deterministically. NB (r1 finding 4): in a *synthetic* test the skew triggers with just `GIT_DIR` exported (no worktree needed) — useful for cheap deterministic tests — but in the **real product flow git only exports `GIT_DIR` into the pre-push hook when pushing from a worktree**, so the user-facing bug is worktree-specific (matches #3178). Synthetic repro:

```
# NORMAL (no hook env): git -C scripts/testing rev-parse --show-toplevel
/tmp/.../repo                          # correct

# HOOK ENV: GIT_DIR set, GIT_WORK_TREE unset (git's behavior for hooks)
git rev-parse --show-toplevel          # cwd=root, no -C  → /tmp/.../repo          (correct: why the hook works)
git -C scripts/testing rev-parse --show-toplevel   → /tmp/.../repo/scripts/testing (WRONG: collapses to -C dir)

# FIX candidate:
env -u GIT_DIR -u GIT_WORK_TREE git -C scripts/testing rev-parse --show-toplevel
                                       → /tmp/.../repo                              (correct)
```

The captured real-world symptom from the #3178 push (worktree `wh-unexempt-wt`):
`run-all-tests.sh: line 25: …/scripts/testing/scripts/lib/tier1-repos.sh: No such file or directory`
→ `[pre-push] FAIL: run-all-tests` for worldenergydata + assethold **despite `mypy: PASS`**.

## Root cause

Git exports `GIT_DIR` (but not `GIT_WORK_TREE`) into hook environments. When `GIT_DIR` is set and `GIT_WORK_TREE` is unset, git uses the **current working directory** as the work-tree top. So `git -C "$SCRIPT_DIR" rev-parse --show-toplevel` first `cd`s into `$SCRIPT_DIR` and then reports `$SCRIPT_DIR` as the toplevel. The bare hook form (`git rev-parse --show-toplevel` with cwd = repo root) is immune.

**Why the existing `|| fallback` guards don't save us:** the skewed call *succeeds* (exit 0) with a wrong-but-nonempty path, so `… 2>/dev/null || echo "$SELF_DIR"` never reaches the fallback. The wrong root propagates silently.

---

## Design

> **REVISED after r2 (Codex + Gemini).** The original design (a git-based `scripts/lib/repo-root.sh` helper using `env -u … || true`) was downgraded: r2 showed it is over-engineered AND that the `|| true` swallow trades a loud `set -e` abort for a *silent empty `REPO_ROOT`* at a caller (`run-all-tests.sh`) that has no fallback before `source "${REPO_ROOT}/…"`. The immune pattern already ships in the sibling gate script `check-all.sh:8` — pure structural arithmetic, **no git at all**, so the `GIT_DIR` skew cannot occur by construction. Aligning to that proven prior art is simpler, lower-risk, and avoids a new tested-helper surface.

### Approach: align the two pre-push-path scripts to `check-all.sh`'s git-free structural root (proven immune)

1. **`scripts/testing/run-all-tests.sh:16`** (load-bearing — resolves #3179 directly) and **`scripts/testing/run-benchmarks.sh:20`** — replace
   `REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"`
   with the exact pattern `check-all.sh` already uses and which passed under the failing hook:
   ```bash
   REPO_ROOT="${QUALITY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
   ```
   (use the script's own override-var name where one exists; otherwise just the `cd …/../.. && pwd` form). `SCRIPT_DIR` is the physical dir the script lives in (inside the worktree); `cd ../.. && pwd` yields the worktree root with **no git invocation**, so GIT_DIR/GIT_WORK_TREE leakage is irrelevant. Confirmed: `check-all.sh` uses this and ran green during the #3178 hook failure.

2. **`scripts/lib/tier1-repos.sh` — leave AS-IS (do NOT add a helper source).** (Codex MAJOR 1) In the failing flow the sourcing script sets `REPO_ROOT` *before* `source`, so `_tier1_repos_resolve_file` returns at the `$REPO_ROOT/config/...` step and line 29's git fallback is never reached. Critically, `tier1-repos.sh` is **copied into test fixtures** (`tests/quality/test_check_all.sh`, `tests/quality/test_tier1_consumer_layouts.sh`) *without* any sibling helper — making it unconditionally `source` a helper would break those fixtures and any standalone consumer. Keep it copy-standalone. (Its own line-29 `-C` form is defense-in-depth only; if hardened later, do it with the git-free subshell idiom in §3, never an unconditional external source.)

3. **No new shared helper in this PR.** A general `resolve_repo_root` for the broader 34-site class is deferred to the follow-on (see §4). If/when built, r2 consensus is: use a **native POSIX subshell** `(unset GIT_DIR GIT_WORK_TREE; git -C "$start" rev-parse --show-toplevel 2>/dev/null)` (Gemini MAJOR 2 — universally portable, no `env -u` feature detection), do **NOT** `|| true`-swallow inside it (Gemini MAJOR 1 / Codex MAJOR 2 — let exit 128 propagate so the caller idiom `REPO_ROOT="$(resolve_repo_root "$SCRIPT_DIR" || echo "$SCRIPT_DIR/../..")"` provides a real fallback AND is `set -e`-safe via the in-substitution `||`), and require an explicit `start` arg (Gemini MINOR 3 — no `${BASH_SOURCE[1]}` magic).

4. **Document the remaining vulnerable call sites** (34 total − 2 fixed here = ~32) as a follow-on conversion wave, with a per-script hook/pre-commit-exposure assessment (Gemini's question: `scripts/enforcement/` + `scripts/review/` are pre-commit/worktree-exposed too). File as a tracked follow-up; do NOT mass-convert blindly here.

### Options considered (ranked, post-r2)
1. **Git-free structural `cd …/../.. && pwd`, matching `check-all.sh` (CHOSEN).** Immune by construction (no git → no GIT_DIR skew), zero new surface, matches proven sibling prior art. Accepts the same "breaks if the script changes directory depth" risk that `check-all.sh` already lives with — covered by an acceptance test.
2. Git-based shared helper with subshell-unset + non-swallowing contract — more general (good for the 34-site class) but heavier, new tested surface, and the caller-contract subtleties (r2) make it riskier for a load-bearing gate. Deferred to the follow-on wave.
3. `env -u … || true` helper (ORIGINAL) — rejected: masks failure into a silent empty root at a fallback-less caller (Codex MAJOR 2, Gemini MAJOR 1).

---

## TDD test list (tests first)

`tests/quality/test_run_all_tests_repo_root.sh` (new — matches the existing `tests/quality/test_tier1_repo_resolver.sh` convention):

**Regression tests (MUST fail on current `main`, proving they capture the #3179 defect):**
1. **test_run_all_tests_sources_tier1_under_hook_env** — invoke `run-all-tests.sh --repo <name>` with `GIT_DIR=<repo>/.git` exported (simulating the pre-push hook), cwd at repo root; assert the `source` of `tier1-repos.sh` succeeds (no "No such file or directory"). Fails on `main` today (the git `-C` form collapses REPO_ROOT to `scripts/testing`); passes after the structural fix.
2. **test_run_all_tests_coverage_path_under_hook_env** — same but invoke `run-all-tests.sh --coverage` (the hook ALSO calls this at `.git/hooks/pre-push.sh:215`, outside the per-repo loop — Codex MAJOR 3). Stub the parser/`uv` so only the bootstrap path is exercised. Fails on `main`, passes after.

**Contract tests (pass after the fix; assert correct resolution, not defect capture — Codex MINOR 4 keeps these separate from the regression set):**
3. **test_repo_root_resolves_at_repo_root** — REPO_ROOT == toplevel when invoked normally.
4. **test_repo_root_correct_under_hook_env_from_subdir** — with `GIT_DIR` exported and cwd in a subdir, REPO_ROOT still == repo root (the structural `cd …/../.. && pwd` is git-free, so this holds by construction).
5. **test_repo_root_in_worktree** — run from inside a real `git worktree`; REPO_ROOT == the *worktree* root, not the main checkout (structural path math returns the physical dir, which is the worktree).

**Existing fixture-copy tests run as acceptance (Codex suggestion — guard against helper-bootstrap-style regressions):** `tests/quality/test_check_all.sh` and `tests/quality/test_tier1_consumer_layouts.sh` must still pass (confirms we did NOT break the copy-standalone contract of `tier1-repos.sh`).

Tests 1 & 2 (regression) MUST FAIL on current `main` before the fix; tests 3–5 (contract) exercise the new behavior and pass only after.

---

## Acceptance criteria
- [ ] `resolve_repo_root` helper added under `scripts/lib/` with the 6 tests above, all green.
- [ ] Tests 3 & 6 demonstrably FAIL on pre-fix `main` (regression captured).
- [ ] `run-all-tests.sh`, `run-benchmarks.sh`, `tier1-repos.sh` use the helper; no `git -C "$SCRIPT_DIR" … --show-toplevel` remains in those three.
- [ ] A clean push from a worktree on this machine no longer FAILs `run-all-tests` for a passing change (verify with a no-op/whitespace test push, or `PRE_PUSH_*` harness env — without `GIT_PRE_PUSH_SKIP`).
- [ ] No hardcoded absolute repo paths introduced (`scripts/enforcement/check-no-abs-paths.sh` passes).
- [ ] `resolve_repo_root` is safe assigned at top-level scope under `set -euo pipefail` in the non-repo case (returns empty, exit 0 — does not abort caller). (r1 finding 1)
- [ ] Follow-on issue filed enumerating the remaining **~31** vulnerable call sites (34 total − 3 fixed here) + a per-script hook-exposure assessment (which run under a hook/pre-commit vs. only CI/interactive). (r1 finding 5)

## Risks & mitigations
- **Load-bearing gate change** → full plan→review→approve→TDD; verify the hook still PASSES legitimately (not just stops false-FAILing) by testing a known-good and a known-bad change.
- **Structural-depth brittleness** — `cd …/../.. && pwd` breaks if `run-all-tests.sh`/`run-benchmarks.sh` ever move directory depth. Mitigation: contract test #4 asserts correct REPO_ROOT; this is the same accepted risk `check-all.sh` already carries (sibling prior art).
- **Copy-standalone contract for `tier1-repos.sh`** — must NOT introduce an unconditional sibling `source` (would break fixture copies). Mitigation: leave the lib as-is; run `test_check_all.sh` + `test_tier1_consumer_layouts.sh` as acceptance.
- **Worktree-cleanup hazard on this machine** (#3153 gap) → implement on a committed branch, expect the branch (not worktree files) to be the durable artifact; commit early.
- **Delivery** still needs `GIT_PRE_PUSH_SKIP` from a real terminal until this very fix lands (chicken-and-egg) — that's expected and audited.

## Out of scope
- The general git-based `resolve_repo_root` helper + mass-converting the remaining ~32 vulnerable call sites (tracked as the follow-on wave; r2-consensus design notes captured in Design §3 for when it's built).
- The separate #3153 worktree-cleanup-guard gap (different root cause; noted in memory).

---

## Review Log

### r1 — Claude (adversarial subagent), 2026-06-16 — REQUEST-CHANGES → folded
- Confirmed the central design bet (worktree resolution via `env -u GIT_DIR`) is **empirically safe** — returns the worktree root, not the main checkout, under a real worktree pre-push hook. No redesign needed.
- MAJOR 1: helper not `set -e`-safe in non-repo path (top-level `REPO_ROOT=$(resolve_repo_root)` aborts on git exit-128) → **folded**: helper ends with `|| true`; new AC + test #5.
- MAJOR 2: `check-all.sh` immunity mis-attributed (it uses `cd/pwd` path math, no git) → **folded** in Resource Intel.
- MAJOR 3: `tier1-repos.sh:29` mis-ranked as "highest leverage" (not reached in failing flow) → **folded**: re-ranked to defense-in-depth; `run-all-tests.sh:16` is load-bearing.
- MINOR 4 (worktree-specific real trigger), 5 (34 sites not ~20; ~31 remaining), 6 (test dir → `tests/quality/`), 7 (portability fallback also needs `|| true`) → all **folded**.

### r2 — Codex + Gemini, 2026-06-16 — both REQUEST-CHANGES/MAJOR → design pivoted (r1≠r2, so folded inline per `feedback_r3_inline_loop_break_pattern`; NOT re-dispatched)
Both independently confirmed the `env -u GIT_DIR` worktree premise holds, but converged against the r1-accepted `|| true` helper:
- **Gemini MAJOR 1 / Codex MAJOR 2** — `|| true` masks genuine failure into a silent empty `REPO_ROOT` at the fallback-less caller `run-all-tests.sh` (empty → `source "/scripts/lib/tier1-repos.sh"`). → **Design pivoted** to git-free structural root (matches `check-all.sh`), which has no failure mode to mask.
- **Gemini MAJOR 2** — `env -u` over-engineered; native subshell `(unset GIT_DIR GIT_WORK_TREE; git …)` is universally portable. → captured for the deferred helper (Design §3); not needed by the chosen git-free fix.
- **Codex MAJOR 1** — making `tier1-repos.sh` source a helper breaks copied-fixture consumers (`test_check_all.sh`, `test_tier1_consumer_layouts.sh`). → **folded**: leave `tier1-repos.sh` copy-standalone; run those fixtures as acceptance.
- **Codex MAJOR 3** — hook also invokes `run-all-tests.sh --coverage` (`pre-push.sh:215`), not covered by the per-repo test. → **folded**: added regression test #2.
- **Codex MINOR 4** — separate "regression-fails-on-main" from "new-contract-passes". → **folded**: TDD list now splits the two groups.
- **Gemini MINOR 3** (no `BASH_SOURCE[1]` magic) & **MINOR 4** (Option-3 rejection was hypocritical) → resolved by the pivot: the chosen design IS structural, so there's no helper-bootstrap or self-contradiction left.
- **Net effect:** scope SHRANK (no new helper, no `tier1-repos.sh` change) and risk dropped (git-free, matches proven sibling pattern). Outcome consistent with the SOUL "simplest correct design" posture; r3 NOT dispatched (inline per protocol).
