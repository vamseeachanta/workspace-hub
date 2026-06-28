# Plan for #3292: seamless(ci): digitalmodel touched-domain-only on push + clear baseline red

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3292
> **Client:** N/A
> **Project:** (n/a)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3292-claude.md | ...-codex.md | ...-gemini.md

---

## Scope note (read first — Round-2 honest descope)

Issue #3292 lists **two** deliverables and **two** acceptance bullets:

1. **Route `push` like PR** (touched-domain-only); gate the full sweep to nightly-cron / `workflow_dispatch`. → **THIS PLAN delivers this.**
2. **Triage + clear the chronic baseline red** (coordinate #700/#949/#706) and **quarantine** license-gated/solver legs (coordinate #705/#714). → **THIS PLAN does NOT deliver this.** It is a multi-issue test-repair + quarantine effort owned by those issues.

This plan therefore proposes to **re-scope #3292 to deliverable #1 only (routing)** and route deliverable #2 / Acceptance bullet #2 ("default-branch gate reaches green or legs are explicitly quarantined") to the baseline-triage track (#700/#949/#706) and the solver-quarantine track (#705/#714). The Round-1 plan dishonestly claimed Acceptance bullet #2 was "satisfied by those issues + the nightly sweep"; it is not — pointing at other open issues is not delivery. **The user must decide** (open question below) whether to (a) re-title/re-scope #3292 to routing-only and close it on this PR, or (b) keep #3292 open until the baseline track lands. This plan's own Acceptance Criteria cover **only** the routing change it actually ships.

## Sibling / wave coordination (cross-cutting decisions, settled 2026-06-28)

- **Caching is out of scope (D2 / #3291).** `quality-gates-by-domain.yml` uses `astral-sh/setup-uv@v5` with **no cache** today (lines 30-31, 71-72, 99-100). Adding caching is owned by **#3291**, and D2 scopes #3291's caching additions to `assetutilities tests.yml`, `assethold`, and the **four** dm `setup-uv` workflows (`aqwa`/`diffraction`/`mooring-analysis`/`structural-analysis`) — `quality-gates-by-domain.yml` is **not** in that set, and there is **no pip→uv swap**. This plan touches the `detect-domains` routing only and **must not** add `cache:` keys or change any package manager.
- **Golden-harness determinism is Wave 2 (D6 / #3283).** Out of scope here; this plan ships in the current wave.
- **No schema / discovery / governance surfaces touched** (D1/#3295, D4/#3284, D5/#3296 are unrelated sibling issues). No `result:`/`invocation:` registry work, no `workflow_id` work, no evaluator work in this plan.

---

## Resource Intelligence Summary

Implementation target lives in the **digitalmodel** sibling repo
(`/mnt/local-analysis/digitalmodel`); this plan file and the README index row live in
**workspace-hub**. No wiki content is touched (`Client: N/A`).

### Existing repo code

- Found: `digitalmodel/.github/workflows/quality-gates-by-domain.yml` (167 lines) — the `detect-domains`
  job branches on `github.event_name`: only `pull_request` runs `--mode touched`
  (PR base/head SHAs, lines 40-46); **every other event (`push`, `schedule`, `workflow_dispatch`) falls into
  the `else` arm and runs `--mode full`** (lines 47-52). So a `push` to `main`/`develop` runs the
  full ~21-domain matrix, exactly the behavior the issue calls out. The detect step env (lines 35-38) sets
  only `PR_BASE_SHA`/`PR_HEAD_SHA`; there are no push before/after SHAs wired in yet.
- Found: `digitalmodel/scripts/ci/detect_touched_domains.py` (299 lines) — the detector already supports
  `--mode touched --base <sha> --head <sha>` (argparse lines 256-268; `touched_domains()`
  lines 218-245). `--mode full` returns **all** parsed domains (`main()` lines 275-284:
  `domains if args.mode == "full"`). The detector reads the changed-file set via
  `git diff --name-only base head` (`git_changed_files()` lines 99-106) with `check=True`.
- **Verified (correction of Round-1 framing):** `main()` (lines 271-294) **already wraps the whole
  body in a broad `except Exception` that prints to stderr and `return 2`** (lines 285-287). So an
  unreachable base today already yields **exit 2** — but via the *catch-all*, not a dedicated handler.
  Consequence for design: the new fail-safe must catch `subprocess.CalledProcessError` from
  `git_changed_files()` **specifically and inside** the existing try, deciding full-vs-reraise **before**
  the catch-all sees it. The Round-1 pseudocode (a free-standing try around `git_changed_files`) was
  directionally right but did not account for the existing outer try/except; the revised pseudocode below
  slots into the real structure.
- Found: `digitalmodel/tests/DOMAINS.md` — real domain rows (full mode = ~21 legs; confirmed by the
  grep below). Confirms "full mode = many legs".
- Found: `digitalmodel/tests/scripts/test_detect_touched_domains.py` — **18** detector tests; the
  touched-mode pattern (`init_repo` → commit base → commit head → `run_detector --mode touched
  --base --head`) at lines 107-133 is the template for the new push-fallback tests. **Verified: there is
  NO existing test that asserts exit-2 on an unreachable/zero base SHA**, and **no test asserts the
  *opposite* of the new behavior** — so the "contradicted-test" defect class does **not** apply to this
  change (nothing to invert). `test_quality_gate_workflows_parse` (lines 574-579) only asserts the two
  quality-gate workflows parse as YAML; the new structural routing test is additive, not a contradiction.
- Found: `digitalmodel/.claude/quality-gates.yaml` — per-domain gate commands; the workflow reads
  `gates[tests-<domain>].command` per matrix leg (workflow lines 105-126). No change needed here.
- Gap: the workflow has no `push`-specific routing branch and the detector has no fail-safe for an
  unreachable base SHA (new-branch zero SHA `0000…0000`, or force-push pruned history).

### Standards

Not applicable — CI/harness infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — pure CI routing change, no wiki content touched.

### Documents consulted

- Issue body #3292 (verified, below) — directs: route push like PR (touched-domain-only); gate full
  sweep to nightly/dispatch; baseline-red triage coordinated via #700/#949/#706, solver legs via
  #705/#714.
- Parent epic workspace-hub #3290 — "Seamless ecosystem development — fast green CI…"; this is its
  Theme-A (CI speed) child. `lane:claude`, `cat:harness`.
- digitalmodel #700 (OPEN) "CI baseline: Quality Gates and broad domain shards fail on main",
  #949 (OPEN) "ci: root-cause of 9-domain quality-gates baseline failure", #706 (OPEN) "split domain
  baseline diagnostics from touched-domain PR routing" — the baseline-red triage track. **This plan
  does NOT fix the underlying test failures** (that is #700/#949/#706 scope) and does NOT claim
  Acceptance bullet #2; it changes routing so push stops re-running known-red unrelated legs.
- digitalmodel #705 (OrcaFlex-solver baseline), #714 (OrcaWave licensed-host benchmark) — solver/
  license-gated legs; quarantine of these out of the blocking path is **issue deliverable #2 scope**,
  out of scope here, referenced as the quarantine track.

### Gaps identified

- No `push`-event routing branch in the workflow detect step — must be added.
- No fail-safe in the detector for an unreachable base SHA — must be added (zero SHA / force-push).
- No test covering the unreachable-base path — must be added.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `workspace-hub#3292` — OPEN — "seamless(ci): digitalmodel touched-domain-only on push + clear baseline red" (labels: enhancement, priority:medium, cat:harness, status:needs-plan, lane:claude)
- `workspace-hub#3290` — OPEN — parent EPIC "Seamless ecosystem development…" (lane:claude, cat:harness)
- `digitalmodel#700` — OPEN — "CI baseline: Quality Gates and broad domain shards fail on main"
- `digitalmodel#949` — OPEN — "ci: root-cause of 9-domain quality-gates baseline failure"
- `digitalmodel#706` — OPEN — "CI: split domain baseline diagnostics from touched-domain PR routing"
- `digitalmodel#705` — OPEN — "CI: repair tests-orcaflex-solver baseline failures…"
- `digitalmodel#714` — OPEN — "OrcaWave: investigate L01 180-case API benchmark timeout… (licensed host)"

**File existence** (verified 2026-06-28):
- EXISTS: `digitalmodel/.github/workflows/quality-gates-by-domain.yml` (167 lines)
- EXISTS: `digitalmodel/scripts/ci/detect_touched_domains.py` (299 lines)
- EXISTS: `digitalmodel/tests/scripts/test_detect_touched_domains.py` (18 test fns)
- EXISTS: `digitalmodel/tests/DOMAINS.md`
- EXISTS: `digitalmodel/.claude/quality-gates.yaml`

**Line excerpts** — `quality-gates-by-domain.yml:40-52` (the push→full defect):
```
          if [ "$EVENT_NAME" = "pull_request" ]; then
            matrix=$(uv run --no-sources python scripts/ci/detect_touched_domains.py \
              --mode touched \
              --base "$PR_BASE_SHA" \
              --head "$PR_HEAD_SHA" \
              --domains-file tests/DOMAINS.md \
              --output-format json-matrix)
          else
            matrix=$(uv run --no-sources python scripts/ci/detect_touched_domains.py \
              --mode full \
              --domains-file tests/DOMAINS.md \
              --output-format json-matrix)
          fi
```

**Detector `main()` already returns exit 2 on any exception** — `detect_touched_domains.py:271-294`:
```
def main(argv=None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        domains = parse_domains(args.domains_file)
        selected = (
            domains
            if args.mode == "full"
            else touched_domains(git_changed_files(args.base, args.head), domains, args.base, args.head)
        )
    except Exception as exc:
        print(f"detect_touched_domains.py: {exc}", file=sys.stderr)
        return 2
    ...
```
(So today's unreachable-base behavior is already exit 2 via the catch-all; the fix must intercept the
`CalledProcessError` *before* this handler.)

**Reproduction proofs** (Step 1.5 — CI-yaml/routing issue; the behavioral claim is "push runs full =
every domain", verified directly from config + run history):

1. Routing defect confirmed in source: the `else` arm above runs `--mode full` for `push`,
   `schedule`, and `workflow_dispatch`.

2. Full mode emits the whole matrix — `detect_touched_domains.py:275-284` returns `domains`
   unconditionally in full mode, and `tests/DOMAINS.md` has 21 domain rows:
   ```
   $ cd /mnt/local-analysis/digitalmodel
   $ grep -oP '^\| \K[a-z-]+(?= \|)' tests/DOMAINS.md | grep -v '^---' | wc -l
   21
   ```

3. Run history confirms the symptom — every `push` run on `main` fails while PR runs sometimes
   pass:
   ```
   $ gh run list --repo vamseeachanta/digitalmodel --workflow quality-gates-by-domain.yml --limit 12
   failure  schedule      main
   failure  push          main
   success  pull_request  feat/ffs-field-dashboard
   failure  push          main
   ...
   ```
   PRs that touch a green domain pass; the push of the same merge re-runs all 21 legs and inherits
   the baseline-red domains → fails. This is the noise the issue targets.

- Reproduced at: 2026-06-28
- Failure mode observed matches issue claim: YES — push routes to full (~21 legs) and inherits
  baseline-red unrelated legs.

**Source count:** issue body (1) + workflow yaml (2) + detector script (3) + DOMAINS.md (4) +
detector test file (5) + run history (6) + related issues #700/#949/#706/#705/#714/#3290 (7). ≥3 ✓

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3292-dm-touched-domain-ci.md (workspace-hub) |
| Workflow (modify) | `digitalmodel/.github/workflows/quality-gates-by-domain.yml` |
| Detector (modify) | `digitalmodel/scripts/ci/detect_touched_domains.py` |
| Detector tests (modify) | `digitalmodel/tests/scripts/test_detect_touched_domains.py` |
| Plan index row | docs/plans/README.md (workspace-hub) |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3292-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3292-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3292-gemini.md |

---

## Deliverable

A `push`-event routing branch in `quality-gates-by-domain.yml` that will run the touched-domain matrix
(scoped to `github.event.before..github.event.after`) with a fail-safe-to-full fallback, plus an
`--on-missing-base {error,full}` option in `detect_touched_domains.py`, so that `push` to
`main`/`develop` will run only the legs for changed domains while the full ~21-domain sweep will run on
`schedule` (nightly) and `workflow_dispatch` (and on push **only** as a fail-safe when the base SHA is
unreachable). **This is issue deliverable #1 only.** Baseline-red triage / quarantine (issue deliverable
#2, Acceptance bullet #2) is **explicitly out of scope** and routed to #700/#949/#706 + #705/#714.

---

## Pseudocode

Detector — add a dedicated `CalledProcessError` fail-safe **inside** the existing `main()` try, so an
unreachable base does not crash the push gate, while preserving today's catch-all exit-2 for the default:

```
# parse_args(): add
#   --on-missing-base {"error","full"}  default "error"   (preserves today's behavior)

def main(argv=None) -> int:
    args = parse_args(...)
    try:
        domains = parse_domains(args.domains_file)
        if args.mode == "full":
            selected = domains
        else:
            try:
                changed = git_changed_files(args.base, args.head)   # git diff --name-only base head
            except subprocess.CalledProcessError:                   # base unreachable: zero-SHA new
                if args.on_missing_base == "full":                  #   branch, force-push pruned base
                    selected = domains                              # fail SAFE → run everything
                else:
                    raise                                           # default → outer except → exit 2
            else:
                selected = touched_domains(changed, domains, args.base, args.head)
    except Exception as exc:
        print(f"detect_touched_domains.py: {exc}", file=sys.stderr)
        return 2
    ... emit matrix ... return 0
```

Notes:
- `--on-missing-base error` (default) re-raises into the existing catch-all → **identical** stderr +
  exit 2 to today. Zero behavior change for PR/schedule/dispatch callers, which never pass the flag.
- Only `subprocess.CalledProcessError` is treated as "missing base"; other exceptions (bad DOMAINS.md,
  etc.) still hit the catch-all and exit 2 — we do **not** broaden the fail-safe to swallow real bugs.

Workflow — replace the 2-arm `if pull_request / else full` with explicit 3-way routing:

```
EVENT = github.event_name
if EVENT == "pull_request":
    detect --mode touched --base $PR_BASE_SHA --head $PR_HEAD_SHA
elif EVENT == "push":
    # github.event.before is 0000…0000 on new-branch create; --on-missing-base full handles it,
    # and git diff against a zero/unreachable SHA raises CalledProcessError → fail-safe to full sweep.
    detect --mode touched --base $PUSH_BEFORE_SHA --head $PUSH_AFTER_SHA --on-missing-base full
else:                                   # schedule (nightly cron) + workflow_dispatch
    detect --mode full
```

Env additions for the detect step (alongside the existing `PR_BASE_SHA`/`PR_HEAD_SHA` at lines 35-38):
`PUSH_BEFORE_SHA: ${{ github.event.before }}`, `PUSH_AFTER_SHA: ${{ github.event.after }}`.
`fetch-depth: 0` is already set (line 23) so non-pruned push history is available for the diff.
**No `cache:` key or package-manager change is added** (caching is #3291 scope per D2).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/.github/workflows/quality-gates-by-domain.yml` | add `push` → `--mode touched` branch with before/after SHAs + `--on-missing-base full`; keep `--mode full` only for schedule/dispatch. No caching/package-manager change (that is #3291). |
| Modify | `digitalmodel/scripts/ci/detect_touched_domains.py` | add `--on-missing-base {error,full}` (default error); catch `CalledProcessError` from `git_changed_files` inside `main()` and fail-safe to full matrix when `full` |
| Modify | `digitalmodel/tests/scripts/test_detect_touched_domains.py` | add tests for unreachable-base default-error and fallback-full paths + flag-inert happy-path + structural workflow-routing assertion |
| Update | docs/plans/README.md (workspace-hub) | add index row for this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_touched_mode_unreachable_base_errors_by_default | current behavior preserved: bogus base, no flag → hard error (catch-all path) | `--mode touched --base <bogus-sha> --head <head>` | returncode 2, stderr mentions failure |
| test_touched_mode_unreachable_base_falls_back_to_full | push fail-safe: bogus/zero base + flag → full matrix, exit 0 | `--mode touched --base <bogus-sha> --head <head> --on-missing-base full` | returncode 0, all domains emitted |
| test_zero_sha_base_falls_back_to_full | new-branch zero-SHA path specifically | `--base 0000000000000000000000000000000000000000 --head <head> --on-missing-base full` | returncode 0, all domains emitted |
| test_on_missing_base_full_does_not_alter_happy_path | flag is inert when base is reachable | valid base/head touching one domain + `--on-missing-base full` | returncode 0, single touched domain only |
| test_push_like_pr_scopes_single_domain | a single-domain push diff routes to one leg (regression mirror of PR path) | valid base/head touching `tests/citations/` | returncode 0, `citations` only |
| test_workflow_routes_push_to_touched_mode | guard: workflow yaml maps `push` to `--mode touched` + `--on-missing-base full`; full reachable only from schedule/dispatch | parse `quality-gates-by-domain.yml` text | structural assertion passes (push branch present with the flag; `--mode full` not reachable from the push arm) |

All new detector subprocess tests reuse the existing `init_repo`/`commit_all`/`run_detector` harness
(lines 24-63). The `test_touched_mode_unreachable_base_*` tests obtain a "bogus base" by committing a
real `head` then passing a 40-char SHA that does not exist in the repo (git `diff` exits non-zero →
`CalledProcessError`).

---

## Acceptance Criteria

**Routing change (issue deliverable #1 — what THIS plan ships, all pre-merge verifiable):**

- [ ] New detector tests pass: `cd digitalmodel && uv run --no-sources python -m pytest tests/scripts/test_detect_touched_domains.py -q`.
- [ ] No detector regression: existing 18 tests still pass (default `--on-missing-base error` keeps exit-2 stderr behavior identical).
- [ ] A docs-only or single-domain diff selects only the relevant domain leg(s), not all ~21 — **verified locally** by running `detect_touched_domains.py --mode touched` over representative crafted base/head commits (the new `test_push_like_pr_scopes_single_domain` is the executable form of this AC). No reliance on a post-merge CI run for this gate.
- [ ] The `quality-gates-by-domain.yml` `push` arm maps to `--mode touched … --on-missing-base full`, and `--mode full` is reachable **only** from the `schedule`/`workflow_dispatch` (else) arm — asserted structurally by `test_workflow_routes_push_to_touched_mode`.
- [ ] New-branch / force-push (`github.event.before == 0000…0000` or pruned) fails **SAFE** to the full sweep, never silently skips all legs — asserted by `test_zero_sha_base_falls_back_to_full` / `test_touched_mode_unreachable_base_falls_back_to_full`.
- [ ] **No caching or package-manager change** is introduced in this PR (D2/#3291 boundary): `git diff` shows no added `cache:` key and no `pip`/`uv` swap in the workflow.
- [ ] Review artifacts posted to scripts/review/results/.

**Post-merge observation (NOT an agent pre-merge gate — documented, not self-verifiable):**

- The push event only fires on `main`/`develop`, so the end-to-end push routing **cannot be exercised on a feature branch before merge.** After merge, the first real `push` run on `main` should show only touched-domain legs (or harness-only on a docs change). This is recorded as a follow-up observation for the merging human, **not** claimed as satisfied by this plan.

**Explicitly descoped (issue deliverable #2 / Acceptance bullet #2):**

- This plan does **not** turn the default-branch gate green and does **not** quarantine license-gated/solver legs. Baseline-red triage is owned by #700/#949/#706 and solver quarantine by #705/#714. **Recommended issue action (user decision):** re-scope #3292 to routing-only and close it on this PR, OR keep #3292 open until the baseline track lands. See Open Questions.

---

## Adversarial Review Summary

| Round | Provider | Verdict | Key findings |
|---|---|---|---|
| R1 | Claude (inline) | **MAJOR** | 3 findings (below) |
| R2 | Claude | PENDING | (this re-review) |
| R2 | Codex | PENDING | |
| R2 | Gemini | PENDING | |

**Overall result:** PENDING

**Round-1 findings (MAJOR) and resolution in this revision:**

1. **AC2 claimed-satisfied-by-other-issues (scope dishonesty).** Round-1 AC asserted issue Acceptance
   bullet #2 (green/quarantined default-branch gate) was "satisfied by #700/#949/#706 + the nightly
   sweep." Pointing at other open issues is not delivery. → **Resolved:** added a top-of-plan Scope note
   that honestly **descopes** deliverable #2 / Acceptance bullet #2 from this issue; the plan's own ACs
   now cover only the routing change; recommended a user decision to re-scope or keep #3292 open.
2. **Self-verify-impossible AC.** Round-1 AC relied on "first real push run after merge", which the
   push-only-on-main/develop trigger makes impossible to verify pre-merge. → **Resolved:** the routing
   ACs are now all pre-merge verifiable (detector unit tests + structural YAML assertion + local detector
   runs); the post-merge run is reclassified as a non-gating observation for the merging human.
3. **Pseudocode mis-modeled the detector + caching-boundary omission.** Round-1 pseudocode wrapped
   `git_changed_files` in a free-standing try without accounting for the existing broad
   `except Exception → return 2` in `main()` (lines 285-287), and the plan was silent on the #3291
   caching boundary. → **Resolved:** pseudocode now slots a dedicated `CalledProcessError` handler
   **inside** the real `main()` try, re-raising on default so today's exit-2 path is byte-identical; added
   an explicit "no caching / no package-manager change (D2/#3291)" constraint to Deliverable, Files,
   and ACs.

**Defect classes checked and found NOT applicable (verified against real code):**

- *"Contradicted test" (invert-a-test) class:* verified all 18 tests in
  `test_detect_touched_domains.py`; none assert exit-2-on-unreachable-base or any behavior the new
  `--on-missing-base full` would contradict. The new tests are purely additive; nothing to invert.

Revisions made based on review:
- See the three numbered resolutions above (Scope note, AC honesty split, pseudocode/structure +
  caching-boundary), plus settled Open Questions below.

---

## Risks and Open Questions

- **Risk (zero-SHA on branch create):** the first push that creates a branch sends
  `github.event.before = 0000000000000000000000000000000000000000`; `git diff` against it raises
  `CalledProcessError`. Mitigated by `--on-missing-base full` → fail-safe full sweep. Tested
  (`test_zero_sha_base_falls_back_to_full`).
- **Risk (force-push pruned base):** `before` SHA may no longer be reachable even with
  `fetch-depth: 0` if it was rewritten. Same fail-safe applies; never silently skip.
- **Risk (fail-safe runs full on push):** the fail-safe means a zero/pruned base push runs the full
  ~21-leg sweep on push — opposite of the speed goal, but the SAFE choice (never skip). For `main`/
  `develop`, branch-create is a one-time event; normal pushes have a reachable `before`. Accepted.
- **Risk (scope confusion — this does NOT fix baseline red):** push will still go red if a *touched*
  domain is itself baseline-broken. That is correct signal and is the remit of #700/#949/#706. The
  win is that pushes stop re-running ~21 legs to inherit unrelated red. The Scope note + descoped ACs
  make this boundary explicit so a reviewer does not expect a green main from this change alone.
- **Risk (merge-commit diff range):** for a merge to `main`, `before`=prior tip, `after`=merge
  commit; `git diff before after` covers the merged delta. Squash/rebase merges produce a single new
  commit on `main` whose diff vs prior tip is the squashed change — also correct.
- **Risk (workflow-yaml test brittleness):** `test_workflow_routes_push_to_touched_mode` parses bash
  inside yaml; kept as a structural string/AST assertion (push branch exists with the flag; `--mode
  full` not reachable from the push arm) rather than executing the bash, to avoid false negatives on
  formatting changes.

**Settled (were Round-1 open questions; now decided):**

- **Schedule + workflow_dispatch stay full; no dispatch toggle.** Decided to keep both `schedule` and
  `workflow_dispatch` on `--mode full` (matches issue text "gate the full-domain sweep to nightly-cron /
  `workflow_dispatch`"). A `workflow_dispatch` input to choose touched-vs-full is **not** added here
  (scope discipline); it can be a follow-on if ad-hoc debugging demand appears.
- **Implementation lands in digitalmodel; workspace-hub #3292 closed by reference.** No workspace-hub
  source change — only this plan + the README index row. The PR/commit lands in `digitalmodel`.

**Open (genuine — needs user decision):**

- **Re-scope vs keep-open for #3292.** The issue bundles routing (deliverable #1, shipped here) with
  baseline-triage + solver-quarantine (deliverable #2, owned by #700/#949/#706/#705/#714). Choose:
  (a) re-title/re-scope #3292 to "route push touched-domain-only" and close it on this PR, with a new
  or existing tracking issue carrying Acceptance bullet #2; or (b) keep #3292 open after this PR until
  the baseline track lands. This plan implements (a)'s deliverable regardless; the user picks the
  bookkeeping.

---

## Complexity: T2

**T2** — multi-file change (one workflow yaml + one detector script + its test file) across a sibling
repo, TDD required, no new module but a behavior-changing CI routing fix with edge-case fallbacks.
Not T1 (more than a trivial single-file edit; needs tests for the unreachable-base path). Not T3 (no
cross-provider systemic change; the detector already supports touched mode — this wires push to it).
Cross-review depth: 2 providers at plan stage (Claude + one dispatched), per the T2 scale.
