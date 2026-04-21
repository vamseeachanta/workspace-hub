# Review: #2424 — pilot scoping (adversarial)

## Verdict: **MAJOR**

The CI-state claims in the issue body are largely reproducible, but the **Claude-CLI framing comment that promotes #2424 to pilot #2 has enforcement, classification, and coupling defects that must be addressed before kickoff.** The issue as a tracker is acceptable; the issue as a "Claude-CLI pilot" is under-specified in load-bearing ways.

---

## What I actually verified (checklist)

- ✓ Issue body claim "`worldenergydata` ❌ FAILURE (Nightly + Full Test Suite)" — confirmed: `gh run list --repo vamseeachanta/worldenergydata --branch main --limit 10` shows `Nightly` failing 2026-04-17 → 2026-04-21 (4 consecutive nights).
- ✓ Issue body claim "`digitalmodel` ❌ FAILURE 2026-04-17" — confirmed: latest main-branch run is `Quality Gates` failure on commit `chore(gitignore): exclude .claude/worktrees/`, but NOTE: `Build API Docs` is GREEN on the same commits. The "red main" label is workflow-specific, not repo-wide. Issue body elides that distinction.
- ✓ Issue body claim "`assethold` ❌ FAILURE 2026-04-17" — confirmed: both `python-tests.yml` and `docs.yml` red across 2026-04-17/18 commits.
- ✓ Issue body claim "`achantas-data` red since 2025-10-05" — confirmed: only 2 runs total visible, both failing, oldest 2025-10-04. So "6+ months red" is technically accurate but misleading — **the repo has had ~zero CI runs since Oct 2025, not 180 continuous failures.** Dormant ≠ broken-and-being-rerun.
- ✓ Issue body claim "`aceengineer-admin` — No CI configured" — confirmed: `gh run list` returns `[]`.
- ✓ Issue body claim "`assetutilities` ✅ SUCCESS" — confirmed: last 5 main runs all `success`.
- ✓ Issue body claim "`workspace-hub` ❌ FAILURE" — confirmed: `Baseline Testing` workflow failing on main on 2026-04-21 commits (`solver dashboard`, `docs(handoffs)`, `fix(email-routing)`).
- ✓ `gh auth status` returned token scopes `'gist', 'project', 'read:org', 'repo', 'workflow'` — sufficient for all 7 repos (all are under `vamseeachanta/`, covered by `repo` scope); **no silent-skip risk from missing scopes** for these specific repos.
- ✓ Checked for existing CI-fix PRs: digitalmodel/assethold/achantas-data have **no open CI-related PRs**. worldenergydata has the 5 Dependabot PRs already cited. workspace-hub has one unrelated feat PR (#2354). No duplication-risk blocker found, but see Finding 6.
- ✓ Checked `scripts/readiness/`, `scripts/cron/`, `scripts/review/`: no existing cross-repo CI-log ingestion infrastructure. Grep for `gh run view --log-failed` in `scripts/` returned **zero files**. Grep for `needs-human-review` in `.claude/` returned **zero files**.

---

## Findings

### 1. MAJOR — "Draft-only, never merged" is prompt-discipline, not enforcement
The framing comment states: *"Output must be draft-only. PRs opened as drafts with `needs-human-review`; never merged by the agent."* Verified: **zero files in `.claude/` or `scripts/` reference `needs-human-review`**, and no label by that name appears to be provisioned. There is no pre-push hook, no branch-protection rule cited, no CODEOWNERS enforcement, and no stop-hook that asserts `isDraft=true` on a PR the runner creates. The existing `feedback_never_offer_to_self_label_plan_approved.md` is a prose norm, not a script. If a future model mis-reads the prompt and calls `gh pr ready` or `gh pr merge`, nothing stops it. **The umbrella (#2425) explicitly cites "user-in-loop at approval is load-bearing" as a hard constraint — the pilot must have a technical gate, not just a prose gate.**

### 2. MAJOR — Context-window / log-size strategy is completely undefined
Framing says *"fetch last-N failing workflow logs via `gh run list` + `gh run view --log-failed`"*. Quick check on `assethold` 2026-04-17 `python-tests.yml` failure: these logs are commonly 5–50 MB compressed. `claude -p` with default `sonnet`/`opus` input caps will reject or truncate. The framing proposes **no** truncation rule (last-N lines? grep-filter for `FAIL|ERROR|Traceback`? per-job slicing?). Without this, the pilot will either silently pass empty classifications or fail at first log pull. This is THE single biggest gap.

### 3. MAJOR — Classification across heterogeneous CI shapes will produce low-signal output
- `worldenergydata` is failing on `Nightly` (scheduled, not PR-triggered — different failure class).
- `digitalmodel` has `Quality Gates` red but `Build API Docs` green on identical commits — a partial-failure, not a "red repo".
- `assethold` has BOTH `python-tests.yml` AND `docs.yml` failing (possibly same root cause, possibly two unrelated bugs).
- `achantas-data` hasn't RUN since Oct 2025 — its "failure" is dormant state, not an active regression.

"Classify root cause" as a single prompt across these 4 radically different failure modes will produce a confidently-phrased taxonomy that **papers over the fact that the correct treatment differs per-repo** (nightly-env fix vs quality-gate tolerance vs dormant workflow retirement). The umbrella's framing *"multi-repo iteration where Claude-CLI beats manual triage"* is weaker than advertised — these 5 repos may actually need 5 bespoke human triage sessions, with Claude-CLI adding negative value by homogenizing the lens.

### 4. MINOR — Issue body "6 of 7 red" is technically true but the count hides dormancy
`aceengineer-admin` has no CI at all and `achantas-data` has been CI-inactive for 6 months. So the "red main" population is really **4 active-and-red** (workspace-hub, worldenergydata, digitalmodel, assethold) out of **5 active repos**. The punchier "6 of 7" number will drive pilot scope decisions; the true operating figure is 4. Recommend the pilot PLAN explicitly carve out the 2 dormant repos as out-of-scope — they need policy decisions ("retire CI?"), not log-classification.

### 5. MINOR — Framing says "pairs well with #2399/#2408 release-readiness" but this is opportunistic
The framing comment claims: *"Pairs well with #2399/#2408 release-readiness contract — if CI classifier outputs become part of the smoke battery, red CI across 6 repos becomes observable rather than episodic."* But the umbrella (#2425) lists #2408/#2399 as a **bench candidate** requiring "dual-role harness design" and explicitly NOT in the first wave. Coupling pilot #2 to a not-yet-scoped harness is hand-waving. Cut the claim or demote it to "future integration point."

### 6. MINOR — Parallel-work risk on workspace-hub itself
`workspace-hub`'s `Baseline Testing` is currently failing on 2026-04-21 commits authored in the SAME session that filed #2424. If pilot #2 runs against workspace-hub, the agent will be attempting to diagnose CI failures caused by its own active author. That's not a blocker but it's a feedback-loop hazard worth naming in the plan: either exclude workspace-hub from pilot scope OR freeze workspace-hub commits during the pilot window. The issue body does not acknowledge this.

### 7. MINOR — No proposed "stop condition" / success metric for the pilot
The framing does not state what makes the pilot a **success** vs. a **learn-and-abandon**. E.g., "≥3 of 4 classifications match human post-hoc judgment" or "draft PRs for ≥2 of 4 repos have diffs a human accepts without rework." Without that, the pilot is open-ended research and will consume effort indefinitely. Umbrella (#2425) also fails to specify this for any of its 4 pilots — #2424 is the first that will have real ROI risk, so this gap matters here most.

### 8. MINOR — "Per-repo tree context" glossed over for repos not cloned locally
Framing says *"Pass log + repo-tree context to `claude -p`"*. `/mnt/local-analysis/workspace-hub/` contains `workspace-hub`, but `worldenergydata`/`digitalmodel`/`assethold`/`achantas-data` aren't all guaranteed cloned on every machine running the pilot (see `reference network_machines.md` cross-machine conventions). The pilot plan must specify: clone-on-demand? read-only via GitHub Contents API? First-run bootstrap? Unstated = broken on machine #2.

---

## Required changes before pilot kickoff

1. **Enforcement gate for draft-only**: add a pre-push hook OR a wrapper script that asserts any PR the pilot creates has `isDraft=true` and the `needs-human-review` label, and refuses to exit 0 otherwise. Prose-only is insufficient given the `feedback_never_offer_to_self_label_plan_approved` constraint.
2. **Log-size strategy spec**: plan must define max bytes passed to `claude -p`, the truncation rule (tail-N, grep-window, job-split), and the fallback when log exceeds budget. Include a fixture-based test with a real 10MB+ log.
3. **Per-repo taxonomy, not global**: rewrite the pilot shape so `achantas-data` and `aceengineer-admin` are OUT of log-classification scope (route them to a separate "CI policy decision" issue). Narrow pilot to the 4 active-red repos.
4. **Drop or scope the #2399/#2408 coupling claim** in the framing comment — it's premature.
5. **Workspace-hub self-reference policy**: explicitly decide in-scope vs. out-of-scope; if in-scope, freeze commits during pilot window.
6. **Stop condition**: plan must include a success metric (e.g., human-acceptance rate of classifications on a 4-repo test set) and a time budget after which the pilot is declared learn-and-abandon.
7. **Per-repo clone/fetch strategy**: plan must specify how logs and repo-tree context are obtained for non-checked-out repos.

---

## What I did NOT check (honesty declaration)

- Did **not** read the actual failing log contents for any of the 4 active-red repos — so I cannot assert whether the failures are "classifier-tractable" or "obviously-human-only". Treat Finding 3 as a hypothesis, not a proof.
- Did **not** verify `claude -p` actual context-window limits at current model version — just flagged that logs are typically too large without an explicit strategy.
- Did **not** test whether `gh auth` with the current `'repo'` scope can access `gh run view --log-failed` on every named repo (token scope is necessary but not always sufficient — fine-grained PAT/org SSO can still block).
- Did **not** check whether the `needs-human-review` GitHub label already exists on any of the 7 repos. If it doesn't, the pilot must provision it first.
- Did **not** inspect the digitalmodel `Quality Gates` workflow YAML — so "Quality Gates red, Build API Docs green on same commit" is reported from `gh run list` only; the actual diagnosis may show these are coupled in ways I didn't investigate.
- Did **not** audit whether pushing branches + opening PRs on 4 external repos from a batch agent is allowed by the workspace's existing CODEOWNERS / branch-protection rules. This could block the pilot mid-run.
