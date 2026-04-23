# Adversarial plan re-review request: workspace-hub issue #2452

## Your role
You are an adversarial reviewer. Assume the plan has defects until proven otherwise.
Do not praise. Do not restate the plan. Focus only on what is wrong, missing, stale, contradictory, or risky.
Return APPROVE only after affirmatively verifying each correctness-critical claim in the supplied context and plan.
When in doubt, return MINOR or MAJOR / REQUEST_CHANGES.
Each finding must cite a specific file path, plan section, line/claim quote, or issue number.
Treat cited sources as assertions to verify, not facts to trust.
If nothing is found, explicitly list what you checked.

## Review objective
This is a fresh re-review after a local cleanup of #2452's draft plan. Decide whether the current plan is now ready to move from draft toward status:plan-review, or whether it still needs revision.

## Live context supplied by orchestrator
Live state checked 2026-04-23:
- #2452 is OPEN with labels priority:medium, cat:infrastructure; no status:plan-review or status:plan-approved.
- No .planning/plan-approved/2452.md marker exists.
- Child issues #2467, #2468, #2469 exist and are OPEN.
- No durable inventory artifact currently exists at worldenergydata/docs/ci/flake8-inventory-2026-04-23*.
- Current review artifacts before this rerun: Claude unavailable/quota text only; Codex REQUEST_CHANGES; Gemini REJECT.
- The workspace-hub root checkout is dirty with unrelated work; review the plan text only and do not assume changes are committed or pushed.

## Specific questions to answer
1. Does the revised plan still truthfully represent #2452 as an umbrella/decomposition issue while preserving the original final outcome: exact worldenergydata Lint job green on main?
2. Are the #2467/#2468/#2469 child issue roles concrete enough, or is ownership/closure still ambiguous?
3. Is the treatment of transient /tmp inventory vs required durable worldenergydata/docs/ci inventory now adequate?
4. Is the nested-repo boundary between workspace-hub planning artifacts and worldenergydata implementation artifacts safe and explicit enough?
5. Is the Verification / TDD Placement section acceptable for an umbrella planning issue, or does it still masquerade as source-level TDD?
6. Are review artifact/status claims internally consistent and conservative?
7. What exact blockers, if any, must be fixed before this plan can be surfaced for user approval or labeled status:plan-review?

## Required output format
Verdict: APPROVE | MINOR | MAJOR | REQUEST_CHANGES | REJECT

Findings:
- [SEVERITY] finding with cited evidence

Checks performed:
- concrete checks you performed or could perform from the supplied material

## Plan under review

```markdown
# Plan for #2452: worldenergydata lint job still fails after #2433 — flake8 debt first-wave remediation

> **Status:** draft — not approval-ready; latest available provider artifacts still block approval
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2452
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2452-claude.md (UNAVAILABLE/quota text only) | scripts/review/results/2026-04-23-plan-2452-codex.md (REQUEST_CHANGES) | scripts/review/results/2026-04-23-plan-2452-gemini.md (REJECT)

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
- Issue #2467 — child issue for the pathological `_cross_database_data.py` outlier; owns the decision/implementation for the single dominant blocker.
- Issue #2468 — child issue for the first execution-safe non-outlier remediation wave (`F401` / `E501` / `E402` clusters).
- Issue #2469 — child issue that explicitly owns the final exact `flake8 src/ ...` green gate and residual fixes after remediation waves land.
- `/tmp/2452-flake8.txt` — transient fresh flake8 inventory captured 2026-04-23 from `uv run --with flake8 flake8 src/worldenergydata --max-line-length=100 --extend-ignore=E203,W503`. This is sufficient as local draft evidence only; a durable checked-in raw/grouped inventory remains required before any implementation-facing approval.

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
- `#2467` — OPEN — pathological `_cross_database_data.py` blocker
- `#2468` — OPEN — first execution-safe non-outlier flake8 cleanup wave
- `#2469` — OPEN — final exact `flake8 src/` green gate owner

**File existence** (`ls` / direct inspection, 2026-04-23):
- EXISTS: `worldenergydata/.github/workflows/ci.yml`
- EXISTS: `worldenergydata/src/worldenergydata/marine_safety/_cross_database_data.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/bsee_analysis.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/financial/report_generator.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/analysis/well_api12.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/data/_legacy/production_unclean_code.py`
- EXISTS: `worldenergydata/src/worldenergydata/bsee/paleowells/cli.py`
- EXISTS: `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md`

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
| Fresh inventory input | `/tmp/2452-flake8.txt` (transient local draft evidence; not durable enough for approval by itself) |
| Required durable inventory report | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` (not present yet; must be produced in the nested `worldenergydata` repo by the child execution plan before source cleanup) |
| Child issue — pathological blocker | GitHub issue #2467 |
| Child issue — safe-rule first wave | GitHub issue #2468 |
| Child issue — final green-gate owner | GitHub issue #2469 |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2452-claude.md` — unavailable/quota text only, not a substantive approval artifact |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2452-codex.md` — REQUEST_CHANGES |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2452-gemini.md` — REJECT |

---

## Deliverable

A phased execution contract for issue #2452 that preserves the original issue outcome — restoring the exact `Lint` job to green on `worldenergydata` main — while sequencing delivery across three explicit child issues: #2467 (pathological outlier), #2468 (first safe-rule remediation wave), and #2469 (final exact `flake8 src/` green gate / residual fixes / closure proof). Issue #2452 stays open until that final green gate is satisfied.

---

## Pseudocode

```text
step 1: capture and normalize fresh flake8 inventory from the exact CI command
step 2: group findings by rule family and module area in a checked-in report
step 3: identify whether a single pathological outlier dominates the job failure
step 4: split that outlier into child issue #2467 with explicit handling options
step 5: split the first execution-safe non-outlier wave into child issue #2468
step 6: create child issue #2469 as the explicit owner of the end-to-end `flake8 src/` green gate after remediation waves land
step 7: keep #2452 open as the umbrella until #2467, #2468, and #2469 are complete and the exact lint job is green
step 8: only move direct source edits into the child issue(s), not the umbrella plan
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create in child plan/worktree | `worldenergydata/docs/ci/flake8-inventory-2026-04-23.md` | checked-in grouped lint inventory and decomposition evidence; must live in the nested `worldenergydata` repo, not the dirty workspace-hub root |
| Link existing | GitHub issue #2467 | already created child issue for the pathological `_cross_database_data.py` blocker |
| Link existing | GitHub issue #2468 | already created child issue for the first execution-safe non-outlier remediation wave |
| Link existing | GitHub issue #2469 | already created child issue for the final exact `flake8 src/` green gate and closure proof |
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
| verify_final_green_gate_has_explicit_owner | one child issue explicitly owns the exact CI lint-green outcome | child issue specs / comments | #2469 named as owner of exact `flake8 src/` green gate and closure proof |

---

## Acceptance Criteria

- [ ] Canonical plan artifact exists under `docs/plans/` and README index is updated
- [ ] A checked-in grouped flake8 inventory exists for the current `worldenergydata` main state before any source-remediation child issue is approved
- [ ] The single pathological `_cross_database_data.py` blocker is split into its own child issue (#2467)
- [ ] The first execution-safe non-outlier remediation slice is split into its own child issue (#2468)
- [ ] The exact end-to-end `flake8 src/` green gate is assigned to child issue #2469
- [ ] #2452 explicitly remains the umbrella/decomposition issue until #2467, #2468, and #2469 are complete
- [ ] Review artifacts are posted under `scripts/review/results/` and latest substantive reviews no longer return REQUEST_CHANGES/REJECT/MAJOR

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | local artifact currently contains only `You've hit your limit · resets 2pm (America/Chicago)`; it is not a substantive review |
| Codex | REQUEST_CHANGES | latest artifact says the draft is not approval-ready, cites stale child-issue/create language, transient `/tmp` evidence, and weak TDD placement |
| Gemini | REJECT | latest artifact rejects the prior partial-wave framing and says the plan cannot claim green CI while deferring residual flake8 debt unless the final green-gate owner/closure contract is explicit |

**Overall result:** NOT APPROVAL-READY — latest available substantive artifacts are Codex REQUEST_CHANGES and Gemini REJECT. The current text has been tightened to remove stale child-creation language and transient-evidence overclaiming, but it still requires a fresh substantive adversarial re-review before `status:plan-review`.

Revisions made based on review:
- split the pathological blocker into child issue #2467
- split the first execution-safe non-outlier wave into child issue #2468
- created child issue #2469 as the explicit owner of the final exact `flake8 src/` green gate
- rewrote the deliverable and acceptance criteria so #2452 stays open until #2467, #2468, and #2469 complete and the exact lint job is green

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

```
