# Plan for #2452: worldenergydata lint job still fails after #2433 — flake8 debt first-wave remediation

> **Status:** plan-approved — user approved via GitHub label transition; implementation may proceed under approved-plan gates
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2452
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2452-claude.md (UNAVAILABLE/quota text only) | scripts/review/results/2026-04-23-plan-2452-codex.md (r4 MINOR) | scripts/review/results/2026-04-23-plan-2452-gemini.md (r4 APPROVE)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `worldenergydata/.github/workflows/ci.yml` — the `lint` job runs three gates in order: `black --check --diff src/ tests/`, `isort --check-only --diff src/ tests/`, and `flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv`. Historical run `24757842396` failed at flake8 after Black/isort passed, which is why #2452 was split as flake8-debt work; however, live local checks on 2026-04-23 now show Black/isort are also red on current `worldenergydata` main. Therefore #2469 must verify the full `Lint` job sequence, not only flake8.
- Found: `worldenergydata/src/worldenergydata/marine_safety/_cross_database_data.py` — a single file now accounts for 4,060 lint findings, dominated by `E231`, making it the largest blocker by far.
- Found: broad residual flake8 debt remains across multiple `src/worldenergydata/**` module areas including `bsee/analysis`, `bsee/reports`, `marine_safety/importers`, `metocean`, `sodir`, `texas_rrc`, `vessel_fleet`, and both `modules/well_production_dashboard` and top-level `well_production_dashboard`.
- Gap: there is no checked-in flake8 inventory snapshot, no grouped debt report, and no bounded remediation wave in `worldenergydata` for the current lint-red state.

### Standards
Not applicable — this is CI / lint infrastructure work, not an engineering-standard implementation issue.

### LLM Wiki pages consulted
No relevant wiki pages — this is repository hygiene and CI debt rather than domain knowledge work.

### Documents consulted
- Issue #2452 body — defines scope as `src/worldenergydata/**` flake8 debt only, names representative rule families (`F401`, `E501`, `E722`, `F841`, `F402`, `E402`, `F541`), and explicitly says runtime test failures belong elsewhere.
- Issue #2433 comments — prove the collection-unblock fix landed and record that the broad CI goal later re-broke because of post-#2433 drift. The latest local gate check confirms Black/isort are currently red in addition to the flake8 debt; #2452 remains the flake8-debt decomposition umbrella, while #2469 owns final full `Lint` job proof.
- Issue #2424 — open parent ecosystem CI-health meta issue.
- Issue #2451 — closed sibling follow-up for runtime test failures, confirming that runtime-test scope is already split away from #2452.
- Issue #2467 — child issue for the pathological `_cross_database_data.py` outlier; owns the decision/implementation for the single dominant blocker.
- Issue #2468 — child issue for the first execution-safe non-outlier remediation wave (`F401` / `E501` / `E402` clusters).
- Issue #2469 — child issue that explicitly owns the final exact `flake8 src/ ...` green gate and residual fixes after remediation waves land.
- `/tmp/2452-flake8.txt` — transient fresh flake8 inventory captured 2026-04-23 from `uv run --with flake8 flake8 src/worldenergydata --max-line-length=100 --extend-ignore=E203,W503`. This is sufficient as local draft evidence only; a durable checked-in raw/grouped inventory remains required before any implementation-facing approval.

### Gaps identified
- No canonical plan artifact existed for #2452 before this file.
- The lint debt is too large for a single undifferentiated T2/T3 implementation wave: fresh inventory shows thousands of `E231` violations in one generated/legacy-style file plus hundreds of `E501`/`F401` across the rest of `src/worldenergydata/**`.
- The current decomposition is now explicit and child issue bodies have been aligned after r2: #2467 cannot satisfy the work by weakening the lint gate, #2468 owns the durable inventory artifact before source edits, and #2469 must prove the full `Lint` job is green on `main`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2452` — OPEN — `follow-up(ci): worldenergydata lint job still fails after #2433 collection fix — flake8 debt in src/worldenergydata/**`
- `#2433` — OPEN — `chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333)`
- `#2424` — OPEN — `chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI`
- `#2451` — CLOSED — `follow-up(ci): worldenergydata test job still fails after #2433 collection fix — benchmark fixture + legacy NPV API regressions`
- `#2467` — OPEN — pathological `_cross_database_data.py` blocker
- `#2468` — OPEN — first execution-safe non-outlier flake8 cleanup wave
- `#2469` — OPEN — final exact `flake8 src/` green gate owner

**File existence** (`ls` / direct inspection, 2026-04-23; local/uncommitted unless otherwise stated):
- EXISTS: `worldenergydata/.github/workflows/ci.yml`
- EXISTS: `worldenergydata/src/worldenergydata/marine_safety/_cross_database_data.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/bsee_analysis.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/financial/report_generator.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/well_api12.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/data/_legacy/production_unclean_code.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/paleowells/cli.py`
- EXISTS LOCALLY: `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md` (not yet pushed to `workspace-hub` `main`)
- EXISTS LOCALLY: `docs/plans/README.md` row for #2452 (not yet pushed to `workspace-hub` `main`)

**Line excerpts** (`sed -n` on `worldenergydata/.github/workflows/ci.yml`):
```yaml
92      - name: Run Black
93        run: uv run black --check --diff src/ tests/
95      - name: Run isort
96        run: uv run isort --check-only --diff src/ tests/
98      - name: Run flake8
99        run: |
100          uv run flake8 src/ \
101            --max-line-length=100 \
102            --extend-ignore=E203,W503 \
103            --exclude=__pycache__,*.egg-info,.git,.venv
```

**Live local formatting gate check** (2026-04-23 from `worldenergydata` repo root):
- `uv run black --check --diff src/ tests/` -> exit 1; current main has formatting drift in `src/worldenergydata/cost/**` and `tests/unit/cost/**`.
- `uv run isort --check-only --diff src/ tests/` -> exit 1; current main has import-order drift in `src/worldenergydata/cost/data_collection/disclosure_ingest_contract.py`, `tests/test_query_api.py`, and cost unit tests.
- Implication: final closure for #2452/#2469 requires the full `Lint` job to be green on `main`; the flake8 child decomposition alone is necessary but not sufficient if Black/isort drift remains.

**Gap proofs / inventory summary** (`/tmp/2452-flake8.txt`, parsed 2026-04-23):
- Top rule families:
  - `E231`: 3857
  - `E501`: 421
  - `F401`: 280
  - `F841`: 44
  - `E402`: 36
  - `E722`: 26
  - `F541`: 21
- Top offending area:
  - `src/worldenergydata/marine_safety/_cross_database_data.py`: 4060 findings
- Representative files outside the giant blocker:
  - `src/worldenergydata/bsee/analysis/bsee_analysis.py`
  - `src/worldenergydata/bsee/analysis/financial/report_generator.py`
  - `src/worldenergydata/bsee/analysis/well_api12.py`
  - `src/worldenergydata/bsee/data/_legacy/production_unclean_code.py`
  - `src/worldenergydata/bsee/paleowells/cli.py`

<!-- Verification source count: issue body + #2433 comments + #2424 + #2451 + ci.yml + fresh flake8 inventory = 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md` (local/uncommitted draft until deliberately staged from the dirty root or moved to a clean branch) |
| worldenergydata lint workflow | `worldenergydata/.github/workflows/ci.yml` |
| Fresh inventory input | `/tmp/2452-flake8.txt` (transient local draft evidence; not durable enough for approval by itself) |
| Required durable inventory report | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` (not present yet; child issue #2468 must produce it in the nested `worldenergydata` repo before source cleanup) |
| Child issue — pathological blocker | GitHub issue #2467 |
| Child issue — safe-rule first wave | GitHub issue #2468 |
| Child issue — final green-gate owner | GitHub issue #2469 |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2452-claude.md` — unavailable/quota text only, not a substantive approval artifact |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2452-codex.md` — r4 MINOR |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2452-gemini.md` — r4 APPROVE |

---

## Deliverable

A phased execution contract for issue #2452 that preserves the original issue outcome — restoring the exact `Lint` job to green on `worldenergydata` main — while sequencing delivery across three explicit child issues: #2467 (pathological outlier), #2468 (first safe-rule remediation wave and durable inventory), and #2469 (full Black/isort/flake8 `Lint` job green gate / residual fixes / closure proof). Issue #2452 stays open until that final green gate is satisfied.

---

## Pseudocode

```text
step 1: keep #2452 as a workspace-hub umbrella/decomposition issue; do not perform direct worldenergydata source edits here
step 2: link existing child issue #2467 for the pathological `_cross_database_data.py` blocker, with the invariant that #2467 must not weaken the current lint gate to satisfy the parent
step 3: link existing child issue #2468 for the first safe-rule non-outlier wave and make #2468 the owner of creating `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` before source edits
step 4: link existing child issue #2469 as the owner of final exact-command and GitHub Actions full-`Lint` proof on `worldenergydata` main, including Black/isort/flake8 gates
step 5: keep #2452 open until #2467, #2468, and #2469 are complete and the full `Lint` job is green on main
step 6: only move implementation details into child issue plans/worktrees, not this umbrella plan
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create in #2468 child plan/worktree | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` | checked-in grouped lint inventory and decomposition evidence; must live in the nested `worldenergydata` repo, not the dirty workspace-hub root, and must be created before #2468 source edits |
| Link existing | GitHub issue #2467 | already created child issue for the pathological `_cross_database_data.py` blocker |
| Link existing | GitHub issue #2468 | already created child issue for the first execution-safe non-outlier remediation wave |
| Link existing | GitHub issue #2469 | already created child issue for final exact `flake8 src/` plus full GitHub Actions `Lint` green proof on `worldenergydata` main; closure must account for current Black/isort drift too |
| Update | `docs/plans/README.md` | add this plan to index |

---

## Verification / TDD Placement List

Because #2452 is now the umbrella/decomposition issue, executable source-level TDD belongs in child issues #2467/#2468/#2469. This parent plan still requires concrete verification checks for its planning artifacts and for the durable lint inventory that child work must create before source edits.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_exact_ci_flake8_command_reproduces_inventory | local command matches CI lint surface | `uv run flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv` | non-zero before any remediation; raw output captured into a durable report path, not only `/tmp` |
| test_inventory_groups_top_rule_families | grouped report names top codes and module areas | fresh flake8 output | markdown report with grouped counts, with raw command provenance quoted |
| test_pathological_outlier_is_explicitly_classified | `_cross_database_data.py` is called out as a separate blocker rather than buried in a flat list | fresh inventory | explicit outlier section |
| test_child_issue_split_is_recorded | umbrella plan records the decomposition into #2467, #2468, and #2469 | plan + issue links | all child issues referenced with distinct purpose |
| verify_final_green_gate_has_explicit_owner | one child issue explicitly owns the exact CI lint-green outcome | child issue specs / comments | #2469 named as owner of full `Lint` job closure proof: Black, isort, and exact `flake8 src/` on main |

---

## Acceptance Criteria

- [ ] Canonical plan artifact exists under `docs/plans/` and README index is updated
- [ ] A checked-in grouped flake8 inventory exists for the current `worldenergydata` main state and is owned by #2468 before source-remediation edits begin
- [ ] The single pathological `_cross_database_data.py` blocker is owned by #2467 without weakening the current lint gate as a parent-satisfying outcome
- [ ] The first execution-safe non-outlier remediation slice and durable inventory generation are owned by #2468
- [ ] The exact end-to-end `flake8 src/` command and full GitHub Actions `Lint` job green proof on `worldenergydata` main are owned by #2469, including current Black/isort drift resolution or verification
- [ ] #2452 explicitly remains the umbrella/decomposition issue until #2467, #2468, and #2469 are complete and the main-branch `Lint` job is green
- [x] Review artifacts are posted under `scripts/review/results/`; latest substantive reviews are Codex r4 MINOR and Gemini r4 APPROVE

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | local artifact currently contains only `You've hit your limit · resets 2pm (America/Chicago)`; it is not a substantive review |
| Codex | r4 MINOR | r4 found one non-blocking cleanup item: live #2452 issue body still had stale Black/isort-green wording; this was resolved by a superseding status comment before plan-review labeling |
| Gemini | r4 APPROVE | r4 found no remaining findings and judged the plan structurally sound and ready for user approval |

**Overall result:** PLAN APPROVED — latest substantive r4 artifacts are Codex MINOR and Gemini APPROVE. Codex's only remaining finding was stale live #2452 body wording; that was handled by a superseding GitHub comment before `status:plan-review`, and the user subsequently approved the plan via the `status:plan-approved` label. Implementation may proceed under approved-plan gates.

Revisions made based on review:
- split the pathological blocker into child issue #2467
- split the first execution-safe non-outlier wave into child issue #2468
- created child issue #2469 as the explicit owner of the final exact `flake8 src/` green gate
- rewrote the deliverable and acceptance criteria so #2452 stays open until #2467, #2468, and #2469 complete and the exact lint job is green
- r2 cleanup: changed pseudocode from "create/split" to "link existing", assigned durable inventory to #2468, tightened #2467/#2469 closure invariants to current-lint-gate and main-branch proof
- r3 cleanup: disclosed current Black/isort RED state, made #2469 own full `Lint` job proof on main, synchronized review-artifact statuses, and marked plan/review artifacts as local/uncommitted until deliberately landed
- r4 review: Codex returned MINOR and Gemini APPROVE; the only cleanup was stale live #2452 body wording, handled by superseding GitHub comment before plan-review labeling

---

## Risks and Open Questions

- **Risk:** `_cross_database_data.py` may be generated, vendored, or intentionally non-normalized, making direct cleanup the wrong first move. This is now split to child issue #2467.
- **Risk:** because `worldenergydata` is a nested repo, implementation must occur in the nested repo/worktree, not from the workspace-hub root.
- **Risk:** the safe-rule child wave may still expose additional rule families after the first clusters are cleaned, so #2468 should carry an explicit residual-debt accounting section.
- **Risk:** even after #2467 and #2468 land, #2469 may still need a narrow residual-fix pass before the exact CI lint job turns green on main.
- **Open:** none for umbrella approval — the decomposition decision and final green-gate ownership are now explicit. Remaining execution decisions belong to child issues #2467, #2468, and #2469.

---

## Complexity: T3

**T3** — the issue currently mixes inventory extraction, debt classification, and multi-module remediation across a nested repository. The fresh inventory shows one pathological single-file blocker plus broad residual debt across many module families, so safe execution requires decomposition and explicit sequencing rather than a single flat patch wave.
