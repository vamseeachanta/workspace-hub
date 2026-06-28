# Plan for #3293: seamless(ci): fix two startup-failing docs.yml (worldenergydata, assethold)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3293
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3293-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

Issue class: Harness/Infrastructure (CI) — `cat:harness`, parent epic #3290 (Theme A, CI speed), effort XS, lane claude. Independent of any wiki content (Client: N/A).

### Existing repo code

The implementation target is two GitHub Actions workflow files, both currently failing at startup on every run:

- Found: `/mnt/local-analysis/worldenergydata/.github/workflows/docs.yml` (34 lines) — workflow `name: Build API Docs`, single job `docs`. Defect at **line 20**: `    if: hashFiles('mkdocs.yml') != ''` placed as a **job-level** `if:`.
- Found: `/mnt/local-analysis/assethold/.github/workflows/docs.yml` (34 lines) — byte-for-byte identical structure (only `actions/*` pin versions differ: WED uses checkout@v6 / setup-python@v6 / setup-uv@v7; assethold uses @v4 / @v5 / @v4). Same **line 20** defect.
- Found (re-verified 2026-06-28): both files **already declare `workflow_dispatch:`** in their `on:` block (line 15 in each). This is load-bearing for verification — see Verification Strategy below.
- Found (re-verified 2026-06-28): the `on:` push/pull_request triggers are **path-filtered** to `src/**`, `docs/api/**`, and `mkdocs.yml` (lines 6-9 and 11-14, both repos). A change confined to `.github/workflows/docs.yml` itself matches **none** of these paths.
- Found: both repos DO contain a committed `mkdocs.yml` at HEAD on `main` (`git ls-files --error-unmatch` returned `mkdocs.yml` for each, re-verified 2026-06-28). So the guard's intended purpose — "skip the job when no mkdocs.yml exists on the ref" — is moot for current repo state; the build should actually run.
- Found: both repos define a `docs` dependency group in `pyproject.toml` (mkdocs / mkdocstrings[python] / mkdocs-material) — WED `pyproject.toml:149-151` (and a duplicate at 552-554), assethold `pyproject.toml:95-97` (and 233-235) — so the build step `uv run --group docs mkdocs build --strict` has its toolchain declared.

### Standards

Not applicable — this is a CI/YAML configuration fix, not an engineering-calc issue. No entry in `data/document-index/standards-transfer-ledger.yaml` is relevant.

### LLM Wiki pages consulted

No relevant wiki pages — this is harness/CI, not domain knowledge. (Confirms Client: N/A — no wiki content touched.)

### Documents consulted

- Issue #3293 body (Evidence section) — claims WED docs.yml 14/14 recent runs fail at 0 minutes with the run name surfacing as the raw path `.github/workflows/docs.yml` (the `startup_failure` signature); assethold 19/19 same pattern. Hypothesized cause: "malformed `on:`/`if:` guard (e.g. `if: hashFiles('mkdocs.yml')`...) or invalid YAML that prevents job creation."
- Parent epic #3290 — Theme A (CI speed), groups dashboard-noise CI cleanups.
- GitHub Actions expression semantics — `hashFiles()` requires a checked-out workspace, which only exists once a runner is assigned. A job-level `if:` is evaluated by the workflow loader *before* any runner/workspace exists, so `hashFiles('mkdocs.yml')` cannot be resolved there and the loader rejects the job at load time, producing a `startup_failure` whose UI message is "This run likely failed because of a workflow file issue."

### Gaps identified

- No local `actionlint` is installed on this box (`command -v actionlint` → "not found", re-verified 2026-06-28), so the corrected YAML cannot be statically lint-validated locally during implementation. Validation will rely on (a) a Python YAML parse, and (b) **GitHub's own loader exercised via `workflow_dispatch`** on the fix branch / post-merge — see Verification Strategy. Implementation should still attempt `uvx actionlint` or `pipx run actionlint` if network allows.
- **The fix cannot be verified by an organic trigger.** Because the edit touches only `.github/workflows/docs.yml` (outside the `src/**` / `docs/api/**` / `mkdocs.yml` path filter), neither the fix PR's `pull_request` event nor the post-merge `push` event will start a run. This was a latent defect in the original plan (AC3 + the live-run TDD rows assumed "the next triggering push" would exercise the fix; it will not). The resolution is to drive verification through the already-present `workflow_dispatch` trigger. See MAJOR-1 in the Adversarial Review Summary.
- The eight `wt-*` worktree copies surfaced by grep (`/mnt/local-analysis/wt-ah-pages`, `wt-wed-779`, etc.) are working trees of these same two repos, **not** separate fix targets — the fix lands on each repo's `main` and propagates. Out of scope for this issue.

### Evidence (embedded verification)

**Issue status** (verified 2026-06-28 via `gh issue view 3293`):
- `#3293` — OPEN — "seamless(ci): fix two startup-failing docs.yml (worldenergydata, assethold)"; labels: `enhancement`, `priority:low`, `cat:harness`, `status:needs-plan`, `lane:claude`.

**File existence** (`ls`/`git ls-files` 2026-06-28):
- EXISTS + tracked at HEAD(main): `/mnt/local-analysis/worldenergydata/.github/workflows/docs.yml`
- EXISTS + tracked at HEAD(main): `/mnt/local-analysis/assethold/.github/workflows/docs.yml`
- EXISTS + tracked at HEAD(main): `worldenergydata/mkdocs.yml`, `assethold/mkdocs.yml`
- Both repos currently checked out on `main` (verified 2026-06-28).

**Line excerpt — the defect + the verification lever** (`cat -n .github/workflows/docs.yml`, identical structure in both repos; WED pins shown):
```
 3	on:
 4	  push:
 5	    branches: [main]
 6	    paths:
 7	      - 'src/**'
 8	      - 'docs/api/**'
 9	      - 'mkdocs.yml'
10	  pull_request:
11	    paths:
12	      - 'src/**'
13	      - 'docs/api/**'
14	      - 'mkdocs.yml'
15	  workflow_dispatch:        # <-- already present; the manual verification lever
16	
17	jobs:
18	  docs:
19	    runs-on: ubuntu-latest
20	    if: hashFiles('mkdocs.yml') != ''   # <-- the defect (job-level hashFiles)
...
34	      - name: Build docs
35	        run: uv run --group docs mkdocs build --strict
```

**Reproduction proofs** (verify-against-repo-state, Step 1.5):

I exercised the REAL failing path — the actual CI runs recorded on GitHub — not a local proxy.

```
$ gh run list --repo vamseeachanta/worldenergydata --workflow=docs.yml --limit 6 \
    --json conclusion,name,displayTitle
# every entry:
#   "conclusion":"failure", "name":".github/workflows/docs.yml"   (name == raw path, not "Build API Docs")
# e.g. run 28287572157 (push to main, PR #655 merge) -> failure

$ gh run view 28287572157 --repo vamseeachanta/worldenergydata
X main .github/workflows/docs.yml · 28287572157
Triggered via push about 22 hours ago
X This run likely failed because of a workflow file issue.

$ gh api repos/vamseeachanta/worldenergydata/actions/runs/28287572157 \
    --jq '{conclusion,status,name}'
{"conclusion":"failure","status":"completed","name":".github/workflows/docs.yml"}

$ gh run list --repo vamseeachanta/assethold --workflow=docs.yml --limit 6 ...
# every entry: "conclusion":"failure", "name":".github/workflows/docs.yml"  (same signature)
```

- Reproduced at: 2026-06-28 (GitHub run records for both repos).
- Failure mode observed matches issue claim: **YES** — runs complete in ~0 min with `conclusion=failure`, the run `name` falls back to the raw path `.github/workflows/docs.yml` (GitHub could not load the workflow to read its `name:`), and the run-view banner reads "This run likely failed because of a workflow file issue." This is the textbook `startup_failure` from an invalid expression. The prime-suspect invalid expression is the job-level `if: hashFiles('mkdocs.yml') != ''` (line 20): `hashFiles()` needs a workspace that does not exist at job-load time. **Caveat — diagnosis is not yet locally confirmable** (no actionlint; cannot re-validate corrected YAML locally). The corrected file's load behavior will be confirmed empirically by `workflow_dispatch` (see Verification Strategy); if a dispatch still startup-fails, implementation must fall back to bisecting the remaining `on:`/job expressions before claiming the fix.

**Distinct sources consulted:** issue body (1) + WED docs.yml file (2) + assethold docs.yml file (3) + GitHub run records via `gh run`/`gh api` (4) + both repos' mkdocs.yml + pyproject.toml (5). Count ≥ 3. ✔

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3293-docs-yml-startup-fix.md |
| Fix target 1 | `/mnt/local-analysis/worldenergydata/.github/workflows/docs.yml` |
| Fix target 2 | `/mnt/local-analysis/assethold/.github/workflows/docs.yml` |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3293-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3293-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3293-gemini.md |

---

## Deliverable

Both repos' `Build API Docs` workflow (`.github/workflows/docs.yml`) will load successfully and its `docs` job will EXECUTE — instead of producing a 0-minute `startup_failure` — by removing the invalid job-level `if: hashFiles('mkdocs.yml') != ''` expression (line 20). The deliverable is **the startup_failure cleared / the job running**, NOT a green `mkdocs build --strict`; the strict-build content (which has never passed on either repo) is explicitly out of scope and tracked separately (see Verification Strategy Scope boundary). Because the fix touches a file outside the workflow's path filter, **confirmation is obtained by a manual `workflow_dispatch` run, not by an organic push** (see Verification Strategy and Acceptance Criteria).

---

## Cross-cutting wave decisions — applicability to #3293

The owner-confirmed cross-cutting decisions (D1–D6, 2026-06-28) govern the workflow-registry / deckhand / governance wave (#3282, #3283, #3284, #3291, #3295, #3296). Their applicability to this issue is recorded here so reviewers see they were considered, not missed:

- **D1 (schema_version / request_schema / `result:` descriptor / `invocation:` / capability_smoke.py)** — N/A. #3293 touches no registry schema, no `capability_smoke.py`, no invocation descriptor. Owned by #3295/#3282.
- **D2 (CI caching: keep `cache:'pip'` on the 5 plain-pip dm workflows; ADD caching only to assetutilities `tests.yml`, assethold, and the 4 dm setup-uv files; no package-manager swap)** — **adjacent but NOT bundled here.** D2 is owned by **#3291**. The assethold `docs.yml` in this issue does use `astral-sh/setup-uv` with caching disabled, so it is a candidate for D2's "add caching where missing" — but adding `enable-cache:` here would violate this plan's AC ("each diff is the single-line workflow edit only") and conflate a startup-failure fix with a performance change. **Decision: keep #3293 scoped to the startup fix; defer any caching addition on these two `docs.yml` files to #3291** under D2. A cross-reference note will be left on #3291.
- **D3 (envelope/golden determinism ownership)** — N/A. No determinism surface in #3293. Owned by #3282/#3283.
- **D4 (discovery: `workflow_id`, per-row `input`, license-gating)** — N/A. Owned by #3284.
- **D5 (governance evaluator: deterministic `issue_class`, fail-closed)** — N/A. Owned by #3296.
- **D6 (sequencing: #3283 deferred to Wave 2)** — N/A to #3293's content; noted for wave ordering only.

No prior "open question" in this plan maps onto D1–D6; the decisions are baked in only as the scope boundary above.

---

## Verification Strategy (why `workflow_dispatch`, not "the next push")

The original plan assumed the fix would be confirmed by observing "the next triggering run." That is **impossible** for this change: the edit is confined to `.github/workflows/docs.yml`, which matches none of the `on.push.paths` / `on.pull_request.paths` entries (`src/**`, `docs/api/**`, `mkdocs.yml`). Therefore:

1. The **fix PR** will show **no** `Build API Docs` check (no `pull_request` event fires for it).
2. **Merging** the fix to `main` will start **no** `Build API Docs` run (no matching `push` path).

Verification therefore uses the **`workflow_dispatch`** trigger that both files already declare (line 15):

- **Preferred (pre-merge) path:** push the fix to a branch and run `gh workflow run docs.yml --repo <owner>/<repo> --ref <fix-branch>`, then poll `gh run list --workflow=docs.yml` for the dispatched run's conclusion. This exercises the *corrected* workflow without merging. Caveat: GitHub only makes a `workflow_dispatch` workflow dispatchable once the trigger is registered from the **default branch**; the current default-branch copy declares `workflow_dispatch:` but startup-fails, so trigger registration may be unreliable. If `gh workflow run` reports the workflow is not dispatchable on the branch, fall back to:
- **Fallback (post-merge) path:** after the PR is merged to `main` (merge performed by the **operator** — the agent cannot self-merge its own PR, per `feedback_agent_can_verify_but_not_self_merge_pr`), run `gh workflow run docs.yml --repo <owner>/<repo> --ref main` and observe the dispatched run.

Either way the success signal is the same and it is **narrow**: the dispatched run must **reach a real job conclusion** — i.e. it is NOT a `startup_failure` and NOT a 0-minute workflow-parse failure, and its `name` resolves to `Build API Docs` rather than the raw path `.github/workflows/docs.yml`. That is the entire scope of this issue: prove the workflow file LOADS and ITS JOB EXECUTES.

**What the success signal is NOT:** it is *not* a green `mkdocs build --strict`. After the startup_failure clears, the `Build docs` step actually runs and `mkdocs build --strict` may still **fail on pre-existing documentation warnings** (broken links, missing nav entries, etc.) — that produces a *normal, log-visible, non-zero-minute* `failure` with `name == "Build API Docs"`, which is materially different from the `startup_failure` this issue targets. **This issue does NOT fix the strict-build content** (recommendation: NO — track separately; see Scope boundary below). Therefore the pass condition keys on *the run reaching a job conclusion*, not on that conclusion being `success`.

This single dispatch mechanism also empirically confirms the **diagnosis** (that removing line 20 actually clears the startup failure): a dispatched run that resolves its `name` to `Build API Docs` and spends real runner minutes proves the workflow loaded, regardless of whether the strict build then passes or fails on content.

**Scope boundary (strict-build content — explicitly out of scope):** if the dispatched run clears startup_failure but the `mkdocs build --strict` step then fails on pre-existing doc warnings, that is a *separate* concern. It is **not** fixed by this issue and **not** a reason to mark #3293 unmet. If observed, file/annotate a follow-on issue (under epic #3290) to harden the strict build (fix the doc warnings or relax `--strict`); do not expand #3293's single-line scope to chase it. AC3 below is satisfiable by clearing the startup_failure alone.

---

## Pseudocode

Trivial (T1) — see Files to Change. The change is a one-line deletion per file.

**Chosen fix (Primary — decision settled, no longer an open question):** delete the job-level `if:` (line 20) in both files. Rationale: `mkdocs.yml` is committed and tracked in both repos, AND the `on.*.paths` filter already includes `mkdocs.yml`, so the guard is doubly redundant — it can never legitimately skip the job for current repo state, yet it is the exact cause of the startup failure. After removal the workflow LOADS and the `docs` job EXECUTES on a (path-matching) trigger or a manual dispatch — which is the entire goal of this issue. **Note:** the issue's success condition is that the job *runs* (no startup_failure), NOT that `mkdocs build --strict` is green. `mkdocs build --strict` has never been observed to pass on either repo and may still fail on pre-existing doc warnings once the step actually executes; that is a separate, out-of-scope concern (see Scope boundary in Verification Strategy and the Risks section) and does not change the chosen fix.

Resulting `jobs:` block (WED pins; assethold identical structure with its own pins):
```
jobs:
  docs:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6
      ...
```

**Rejected alternative (documented fallback only):** replace the job-level `if:` with a post-checkout step-level guard:
```
      - uses: actions/checkout@v6
      - name: Detect mkdocs config
        id: cfg
        run: |
          if [ -f mkdocs.yml ]; then echo "present=true" >> "$GITHUB_OUTPUT"; else echo "present=false" >> "$GITHUB_OUTPUT"; fi
      - name: Build docs
        if: steps.cfg.outputs.present == 'true'
        run: uv run --group docs mkdocs build --strict
```
This keeps a valid expression (`steps.*` context exists at step time) and yields a green run with a skipped build step when no config is present. **Not chosen** because mkdocs.yml is committed and path-filtered in both repos, so the "graceful skip when mkdocs.yml absent" behavior is dead code for the current and foreseeable repo state; the Primary fix is the smaller, lower-risk diff for XS scope. (Re-open this choice only if the owner wants the skip-on-absent behavior preserved as future-proofing.)

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `/mnt/local-analysis/worldenergydata/.github/workflows/docs.yml` | remove invalid job-level `if: hashFiles('mkdocs.yml') != ''` (line 20) causing startup_failure |
| Modify | `/mnt/local-analysis/assethold/.github/workflows/docs.yml` | same one-line deletion (identical defect) |
| Update | docs/plans/README.md | add this plan to the plans index (if the index enumerates plans) |

No source, test, caching, or other CI files change (caching deferred to #3291 per D2 above). Each repo's edit is committed on a branch in that repo (not on `main` directly) and PR'd per repo.

---

## TDD Test List

This is a CI-config fix; "tests" are validation/observation steps rather than unit tests.

| Check | What it verifies | Command | Expected result |
|---|---|---|---|
| YAML parse | corrected file is still valid YAML | `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" .github/workflows/docs.yml` (per repo) | no exception |
| Workflow lint (best-effort) | no remaining invalid expression / schema error | `uvx actionlint .github/workflows/docs.yml` (or `pipx run actionlint`); skip if no network/binary | exit 0, no "hashFiles not allowed" / context error |
| Guard removed | the offending line is gone | `grep -n "hashFiles" .github/workflows/docs.yml` | no match |
| Dispatch loads — WED | corrected workflow no longer startup-fails — the run reaches a real JOB conclusion (this is the empirical diagnosis+fix confirmation) | `gh workflow run docs.yml --repo vamseeachanta/worldenergydata --ref <fix-branch-or-main>` then `gh run list --repo vamseeachanta/worldenergydata --workflow=docs.yml --limit 1 --json conclusion,name,event` then `gh run view <id> --json jobs,startedAt,updatedAt` | `event` == `workflow_dispatch`; `name` == "Build API Docs" (NOT the raw path); the run is **not** a `startup_failure` and **not** a 0-minute parse failure — at least one `job` exists with a real `conclusion` and non-zero elapsed time. **`conclusion` may be `success` OR `failure`** — a `failure` here is acceptable ONLY if it is the `Build docs` step failing on pre-existing `mkdocs --strict` warnings (job ran, non-zero minutes), NOT a 0-minute load failure. (Strict-build content is out of scope — see Verification Strategy Scope boundary.) |
| Dispatch loads — assethold | same, second repo | `gh workflow run docs.yml --repo vamseeachanta/assethold --ref <fix-branch-or-main>` then `gh run list --repo vamseeachanta/assethold --workflow=docs.yml --limit 1 --json conclusion,name,event` then `gh run view <id> --json jobs,startedAt,updatedAt` | `event` == `workflow_dispatch`; `name` == "Build API Docs" (NOT the raw path); run reaches a real `job` conclusion with non-zero elapsed time (not `startup_failure`). `conclusion` `success` OR a `Build docs`-step `failure` both PASS this check; only a 0-minute load failure FAILS it. |

Note: the previous plan's "next push" live-run rows are intentionally removed — see Verification Strategy. An organic push/PR will not start this workflow for a `docs.yml`-only change. The pass key is **"a job executed"** (startup_failure cleared), not **"the strict build is green."**

---

## Acceptance Criteria

- [ ] `grep hashFiles .github/workflows/docs.yml` returns no match in either repo (job-level guard deleted).
- [ ] Both files parse as valid YAML; `actionlint` (if runnable) reports no errors.
- [ ] A **`workflow_dispatch`** run of `Build API Docs` in **each** repo (triggered on the fix branch, or post-merge on `main`) **reaches a real job conclusion** — it is **NOT** a `startup_failure` and **NOT** a 0-minute workflow-parse failure (the run spends real runner minutes and has at least one job with a concrete `conclusion`), and the run `name` resolves to `Build API Docs` rather than `.github/workflows/docs.yml`. This is the issue's success signal: the workflow LOADS and its job EXECUTES. **A `conclusion` of `success` is sufficient but NOT required** — if `mkdocs build --strict` then fails on pre-existing doc warnings, that produces a normal job-level `failure` (non-zero minutes, `name == "Build API Docs"`) which **still satisfies this criterion**, because the startup_failure — the only thing #3293 fixes — has been cleared. (Organic push/PR will not trigger this workflow for a `docs.yml`-only change — verification is by manual dispatch.)
- [ ] **Strict-build content is explicitly out of scope for #3293.** If the dispatched run's `Build docs` step fails on pre-existing `mkdocs --strict` warnings, #3293 is still met (startup_failure cleared); a follow-on issue under epic #3290 is filed/annotated for the strict-build content, and #3293 is **not** held open for it.
- [ ] No NEW 0-minute `startup_failure` `docs.yml` run is introduced in either repo's Actions tab; the dispatched verification run reaches a real job conclusion (a strict-build content `failure` is permitted and tracked separately, per the row above).
- [ ] One PR per repo (worldenergydata, assethold); each diff is the single-line workflow deletion only (no caching change — deferred to #3291).
- [ ] Final merge of each PR is performed by the **operator** (agent cannot self-merge its own PR); post-merge dispatch confirmation is recorded on #3293.
- [ ] Review artifacts posted to scripts/review/results/.

---

## Adversarial Review Summary

| Round | Provider | Verdict | Key findings |
|---|---|---|---|
| R1 | Claude (inline) | **MAJOR** | 3 findings (MAJOR-1/2/3 below) — addressed in the prior revision |
| R2 | Claude / Codex / Gemini | **MAJOR** (now addressed) | 1 finding (MAJOR-4 below): AC3's `conclusion in {success, skipped}` was unsatisfiable under the chosen "delete the `if:`" fix — `skipped` is impossible (no job-level gate remains) and `success` demands a green `mkdocs build --strict`, which has never passed and is explicitly out of scope. Addressed in this revision. |
| R3 | Claude / Codex / Gemini | PENDING | (this re-review) |

**Overall result:** PENDING (Round-3 re-review not yet run; plan remains `draft`). Round-2 returned a MAJOR (MAJOR-4) which is addressed in this revision.

**Round-1 MAJOR findings and their resolutions (baked into this revision):**

- **MAJOR-1 — Self-verification impossible via organic triggers.** The original AC3 and the two "live run" TDD rows asserted the fix would be confirmed by "the next triggering push." But the edit is confined to `.github/workflows/docs.yml`, which matches none of the `on.*.paths` entries (`src/**`, `docs/api/**`, `mkdocs.yml`, re-verified 2026-06-28), so neither the PR's `pull_request` event nor the post-merge `push` event starts a run. **Resolution:** switched verification to the already-present `workflow_dispatch` trigger (line 15) — see Verification Strategy; rewrote AC3 and the TDD live-run rows to dispatch + observe; added the operator-merge constraint (agent cannot self-merge).
- **MAJOR-2 — Diagnosis asserted but not locally confirmable.** No actionlint is installed and the corrected YAML could not be locally lint-validated; the plan asserted line 20 as THE cause without a confirmation path. **Resolution:** the `workflow_dispatch` verification now empirically confirms the corrected file loads; added an explicit fallback ("if a dispatch still startup-fails, bisect the remaining `on:`/job expressions before claiming the fix") so the diagnosis is provable rather than assumed.
- **MAJOR-3 — Primary-vs-alternative left unresolved as an open question.** An approvable plan must commit to one approach. **Resolution:** Primary (delete the `if:`) is now the settled decision, justified by mkdocs.yml being both committed and path-filtered (the guard is redundant); the step-level guard is retained only as a documented, rejected fallback. Removed from Open Questions.

**Round-2 MAJOR finding and its resolution (baked into this revision):**

- **MAJOR-4 — Success signal was unsatisfiable under the chosen fix (`success`/`skipped`).** The prior revision's AC3 + TDD dispatch rows required the dispatched run's `conclusion` to be in `{success, skipped}`. But under the settled "delete the job-level `if:`" fix, **`skipped` is impossible** (there is no longer any job-level gate that could skip the `docs` job), so the only passing outcome was a fully green `mkdocs build --strict`. That strict build **has never succeeded on either repo** and is explicitly listed as out-of-scope in the Risk section — so a fix that correctly clears the `startup_failure` but then hits a pre-existing `--strict` doc-warning failure would meet the issue's real goal yet read as AC3-UNMET. The success signal conflated "the job executes" (the issue's goal) with "the strict build is green" (a separate concern). **Resolution:** re-defined the success signal to **"the dispatched run reaches a real job conclusion — NOT `startup_failure`, NOT a 0-minute parse failure — with `name == "Build API Docs"` and non-zero elapsed runner time."** AC3 now passes on `conclusion == success` OR a `Build docs`-step `failure` (job ran), and FAILS only on a 0-minute load failure. Added an explicit **Scope boundary** stating #3293 does **NOT** fix the strict-build content (recommendation: NO — track a follow-on under epic #3290). Updated: Deliverable, Verification Strategy (success-signal + Scope boundary paragraphs), Pseudocode rationale, both TDD dispatch rows, AC3 + the new strict-build-out-of-scope AC, and the first Risk entry.

Revisions made based on review:
- (R1) Rewrote Deliverable, Verification Strategy (new section), TDD live-run rows, and Acceptance Criteria around `workflow_dispatch` instead of organic-push observation (MAJOR-1).
- (R1) Added the empirical fix-confirmation + fallback-bisection path (MAJOR-2).
- (R1) Settled the Primary-fix decision and moved it out of Open Questions (MAJOR-3).
- (R1) Added the "Cross-cutting wave decisions — applicability" section recording D1–D6 disposition (D2 caching explicitly deferred to #3291).
- (R1) Added the operator-merge / agent-cannot-self-merge constraint to Verification Strategy and AC.
- (R2) Re-defined the success signal from `conclusion in {success, skipped}` to "run reaches a real job conclusion (not `startup_failure`/0-minute parse failure)"; added the strict-build Scope boundary marking #3293 as NOT fixing strict-build content; propagated through Deliverable, Verification Strategy, Pseudocode, TDD dispatch rows, AC3 (+ new AC), and Risks (MAJOR-4).

---

## Risks and Open Questions

- **Risk (low) — strict build may fail on pre-existing doc warnings, and that is acceptable / out of scope.** Removing the guard means the job always runs on a path-matching trigger or dispatch; if `mkdocs build --strict` emits warnings (broken links, missing nav, etc.), `--strict` makes the `Build docs` step fail. **`mkdocs build --strict` has never been observed to pass on either repo**, so this is the *expected* outcome, not an edge case. This is a normal, log-visible, non-zero-minute build failure with `name == "Build API Docs"` — categorically different from the 0-minute `startup_failure` #3293 targets. **It does NOT mean the fix failed and does NOT block AC3:** the success signal for #3293 is "the workflow loads and its job executes," which a content `failure` still demonstrates. The strict-build content is tracked as a **separate** follow-on under epic #3290 (recommendation: NO, #3293 does not fix it). Do not expand #3293's single-line scope to make `--strict` green. The `workflow_dispatch` verification run's purpose is to confirm the run reaches a job conclusion (startup_failure cleared), NOT to assert the strict build passes.
- **Risk (low):** The two repos pin different `actions/*` versions; the fix deletes only line 20 and leaves pins untouched, so no version coupling is introduced.
- **Risk (low):** `workflow_dispatch` dispatchability depends on the default branch having a loadable workflow with the trigger; the current broken default-branch copy may not have registered it reliably. Mitigation: the fallback post-merge dispatch path (operator merges first, then dispatch on `main`) always works because the merged file is valid.
- **Open (deferred to #3291, not this issue):** whether to add `enable-cache:` to the `setup-uv` step in these two `docs.yml` files (D2). Out of scope for the startup fix; cross-referenced on #3291.
- **Open (latent, owner option only):** preserve the "graceful skip when mkdocs.yml absent" behavior via a step-level guard instead of outright deletion. Not chosen (dead code for current repo state); re-open only on explicit owner request.

---

## Complexity: T1

**T1** — a one-line deletion in each of two near-identical workflow files removing a single invalid expression; no new modules, no source/unit tests. The only nuance is that verification must go through `workflow_dispatch` (not an organic push) and the post-merge dispatch is operator-gated — observation, not implementation.
