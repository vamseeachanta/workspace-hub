# Plan for #2452: worldenergydata lint job still fails after #2433 — flake8 debt first-wave remediation

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2452
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2452-claude.md | scripts/review/results/2026-04-23-plan-2452-codex.md | scripts/review/results/2026-04-23-plan-2452-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `worldenergydata/.github/workflows/ci.yml` — the `lint` job runs three gates in order: `black --check --diff src/ tests/`, `isort --check-only --diff src/ tests/`, and `flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv`. This confirms #2452 is specifically about `flake8 src/` debt after black/isort were already restored.
- Found: `worldenergydata/src/worldenergydata/marine_safety/_cross_database_data.py` — a single file now accounts for 4,060 lint findings, dominated by `E231`, making it the largest blocker by far.
- Found: broad residual flake8 debt remains across multiple `src/worldenergydata/**` module areas including `bsee/analysis`, `bsee/reports`, `marine_safety/importers`, `metocean`, `sodir`, `texas_rrc`, `vessel_fleet`, and both `modules/well_production_dashboard` and top-level `well_production_dashboard`.
- Gap: there is no checked-in flake8 inventory snapshot, no grouped debt report, and no bounded remediation wave in `worldenergydata` for the current lint-red state.

### Standards
Not applicable — this is CI / lint infrastructure work, not an engineering-standard implementation issue.

### LLM Wiki pages consulted
No relevant wiki pages — this is repository hygiene and CI debt rather than domain knowledge work.

### Documents consulted
- Issue #2452 body — defines scope as `src/worldenergydata/**` flake8 debt only, names representative rule families (`F401`, `E501`, `E722`, `F841`, `F402`, `E402`, `F541`), and explicitly says runtime test failures belong elsewhere.
- Issue #2433 comments — prove the collection-unblock fix landed and that the broad CI goal re-broke later because of post-#2433 drift, not because #2433 itself regressed.
- Issue #2424 — open parent ecosystem CI-health meta issue.
- Issue #2451 — closed sibling follow-up for runtime test failures, confirming that runtime-test scope is already split away from #2452.
- `/tmp/2452-flake8.txt` — fresh flake8 inventory captured 2026-04-23 from `uv run --with flake8 flake8 src/worldenergydata --max-line-length=100 --extend-ignore=E203,W503`.

### Gaps identified
- No canonical plan artifact existed for #2452 before this file.
- The lint debt is too large for a single undifferentiated T2/T3 implementation wave: fresh inventory shows thousands of `E231` violations in one generated/legacy-style file plus hundreds of `E501`/`F401` across the rest of `src/worldenergydata/**`.
- The issue body asks for both inventory extraction/grouping and remediation, but there is no current decomposition between “pathological single-file blocker” and “broad multi-module rule-family cleanup”.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2452` — OPEN — `follow-up(ci): worldenergydata lint job still fails after #2433 collection fix — flake8 debt in src/worldenergydata/**`
- `#2433` — OPEN — `chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333)`
- `#2424` — OPEN — `chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI`
- `#2451` — CLOSED — `follow-up(ci): worldenergydata test job still fails after #2433 collection fix — benchmark fixture + legacy NPV API regressions`

**File existence** (`ls` / direct inspection, 2026-04-23):
- EXISTS: `worldenergydata/.github/workflows/ci.yml`
- EXISTS: `worldenergydata/src/worldenergydata/marine_safety/_cross_database_data.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/bsee_analysis.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/financial/report_generator.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/well_api12.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/data/_legacy/production_unclean_code.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/paleowells/cli.py`
- MISSING (new — this plan creates): `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md`

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
| This plan | `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md` |
| worldenergydata lint workflow | `worldenergydata/.github/workflows/ci.yml` |
| Fresh inventory input | `/tmp/2452-flake8.txt` |
| First-wave grouped inventory report | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` |
| Child issue — pathological blocker | GitHub issue #2467 |
| Child issue — safe-rule first wave | GitHub issue #2468 |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2452-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2452-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2452-gemini.md` |

---

## Deliverable

A decomposition-ready flake8 remediation packet for `worldenergydata` that turns #2452 from an unbounded lint-debt umbrella into: (a) a checked-in grouped inventory report, (b) an explicit child issue for the pathological `_cross_database_data.py` blocker (#2467), and (c) an explicit child issue for the first execution-safe remediation wave on non-outlier `F401`/`E501`/`E402` clusters (#2468).

---

## Pseudocode

```text
step 1: capture and normalize fresh flake8 inventory from the exact CI command
step 2: group findings by rule family and module area in a checked-in report
step 3: identify whether a single pathological outlier dominates the job failure
step 4: if yes, split that outlier into its own child issue with explicit handling options
step 5: select an execution-safe non-outlier first wave and create a separate child issue for it
step 6: keep #2452 as the umbrella/decomposition tracker until child waves are approved and executed
step 7: only move implementation into the child issue(s), not the umbrella plan
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` | checked-in grouped lint inventory and decomposition evidence |
| Create | GitHub issue #2467 | split the pathological `_cross_database_data.py` blocker into a separately reviewable child issue |
| Create | GitHub issue #2468 | split the first execution-safe non-outlier remediation wave into a separately reviewable child issue |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_exact_ci_flake8_command_reproduces_inventory | local command matches CI lint surface | `uv run flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv` | non-zero before any remediation; reproducible inventory captured |
| test_inventory_groups_top_rule_families | grouped report names top codes and module areas | fresh flake8 output | markdown report with grouped counts |
| test_pathological_outlier_is_explicitly_classified | `_cross_database_data.py` is called out as a separate blocker rather than buried in a flat list | fresh inventory | explicit outlier section |
| test_child_issue_split_is_recorded | umbrella plan records the decomposition into #2467 and #2468 | plan + issue links | both child issues referenced with distinct purpose |
| verify_child_issue_acceptance_owns_green_gate | full lint-green requirement is moved to the execution child issue rather than left ambiguous in the umbrella | child issue specs / comments | exact green-gate owner is explicit |

---

## Acceptance Criteria

- [ ] Canonical plan artifact exists under `docs/plans/` and README index is updated
- [ ] A checked-in grouped flake8 inventory exists for the current `worldenergydata` main state
- [ ] The single pathological `_cross_database_data.py` blocker is split into its own child issue (#2467)
- [ ] The first execution-safe non-outlier remediation slice is split into its own child issue (#2468)
- [ ] #2452 explicitly remains the umbrella/decomposition issue until child waves are approved and executed
- [ ] The exact full-lint green requirement is owned by a child execution issue rather than left ambiguous in this umbrella plan
- [ ] Review artifacts are posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | REQUEST_CHANGES | draft still retreats from the issue’s original green-lint goal, mixes nested-repo vs workspace-hub artifacts, and lacked explicit child-issue ownership / green-gate mapping |
| Codex | MAJOR | revised umbrella still rewrites #2452 into decomposition-only work while no child issue actually owns full `flake8 src/` green; residual rule-family coverage and verification ownership remain incomplete |
| Gemini | UNAVAILABLE | CLI returned repeated 429 `MODEL_CAPACITY_EXHAUSTED` responses and agent-loading errors; no substantive review artifact produced |

**Overall result:** FAIL — re-draft required before `status:plan-review`

Revisions made based on review:
- split the pathological blocker into child issue #2467
- split the first execution-safe non-outlier wave into child issue #2468
- rewrote the plan from a flat implementation wave to an umbrella/decomposition packet
- remaining blocker: the umbrella/child structure still does not provide a clean owner for the end-to-end `flake8 src/` green requirement

---

## Risks and Open Questions

- **Risk:** `_cross_database_data.py` may be generated, vendored, or intentionally non-normalized, making direct cleanup the wrong first move. This is now split to child issue #2467.
- **Risk:** because `worldenergydata` is a nested repo, implementation must occur in the nested repo/worktree, not from the workspace-hub root.
- **Risk:** the safe-rule child wave may still expose additional rule families after the first clusters are cleaned, so #2468 should carry an explicit residual-debt accounting section.
- **Open:** none for umbrella approval — the decomposition decision is now explicit. Remaining execution decisions belong to child issues #2467 and #2468.

---

## Complexity: T3

**T3** — the issue currently mixes inventory extraction, debt classification, and multi-module remediation across a nested repository. The fresh inventory shows one pathological single-file blocker plus broad residual debt across many module families, so safe execution requires decomposition and explicit sequencing rather than a single flat patch wave.
