# Plan for #3592: Equality matrix — reclassify harness/scheduler/memory rows

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3592
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-22-plan-3592-claude.md | ...-codex.md

---

> **RE-SCOPE (2026-07-22, post-review):** while this plan was in draft, commit `762fa1d8a`
> (issue #3591, same owner, parallel session) landed the **harness** dim reclassification:
> `providers_baseline` is now declared for all 5 active workstations in `harness-config.yaml`,
> the harness row grades as cold conformance (CONFORMS on all 5 boxes, live-verified), and
> `unknown` is fail-closed ("not evidence for ANY baseline"). This plan therefore **drops the
> harness dim from scope** and covers the remaining two mis-voted dims — **scheduler** and
> **memory** — plus the collector `unknown` semantics and Windows `schtasks` probe. The
> implementation will REUSE the cold-conformance machinery #3591 added rather than introduce
> a parallel mechanism.

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/build-equality-matrix.py` — `COLD_DIMS = {"compute", "data_access", "solvers"}` (line 36) grade against DECLARED per-machine baselines via `cold_verdict()` (lines 113–162); `uniform_verdict()` (lines 189–200) majority-votes the rest and filters `None/"unknown"/"n/a"` OUT of votes (line 190). Two precedents already exist for suppressing legitimate per-box variation: `EXPECTED_DIFF_DIMS = {"python_cmd"}` (line 49) and the SHA-aware `skills_verdict()` (lines 203–223).
- Found: `scripts/readiness/build-equality-matrix.py` `SOLVER_ACCEPT` map (lines ~40–47) — declared-baseline acceptance sets with fail-closed semantics (`"absent": {"absent"}`; `unknown` satisfies nothing). This is the exact pattern a providers baseline will reuse.
- Found: `scripts/readiness/build-equality-matrix.py` `extract_value()` (lines 392–416) — `harness` votes on `json(providers)`, `memory` votes on `hermes_home`, `scheduler` votes on `json({has_repo_sync, has_parity_review})`.
- Found: `scripts/readiness/collect-equality.sh` lines 276–281 — `job_count=0; has_sync=false; has_parity=false` defaults, probe gated on `[[ "$OS" != "windows" ]] && have crontab` — Windows and crontab-less boxes emit hardcoded placeholder values indistinguishable from measurements.
- Found: `scripts/readiness/collect-equality.ps1` header — Windows collector is a THIN compute overlay that delegates to `collect-equality.sh` under Git Bash; there is no Windows scheduler probe anywhere (`grep -i sched collect-equality.ps1` → no hits). The scheduler fix is single-sourced in the `.sh`.
- Found: `scripts/readiness/harness-config.yaml` `workstations:` — per-machine `role:`, `compute_floor:`, `required_data_access:`, `solvers_baseline:` already declared per box (e.g., gpu-claw `required_data_access: [digitalmodel]`). The natural home for new `providers_baseline:` / `scheduler_baseline:` / `hermes_home_baseline:` keys.
- Gap: no per-machine baseline exists for provider presence, scheduler expectations, or hermes-home; no `unknown` emission path for the scheduler block; no Windows scheduler probe.

### Standards
Not applicable — harness/infrastructure issue, no engineering standards involved.

### LLM Wiki pages consulted
No relevant wiki pages — this is workspace-hub control-plane tooling, out of wiki scope.

### Documents consulted
- Issue #3592 (this plan's source) — full triage evidence tables, 2026-07-22.
- `.claude/rules/patterns.md` — enforcement gradient; this stays a Level-2 script change with existing pytest coverage.
- Related issue #2801 (matrix design: COLD vs UNIFORM dims), #2815 (ace-win-1 scheduler + gh auth, on-box), #2816 (Windows compute overlay design), #3573 (agy replaces gemini — **OPEN**; its three PRs merged but the issue remains open pending soak), #3580 (gemini uninstall decision — OPEN), #3571 (publish hardening), #3591 (landed the harness-dim reclassification, commit `762fa1d8a` — see RE-SCOPE note).
- Drive-file index: no relevant drive files (search `"equality matrix scheduler provider baseline"` via `scripts/data/drive-index-search/search.py --caller plan-resource-intel` returned 20 keyword-collision hits, all unrelated lab-stability PDFs).

### Gaps identified
- `harness-config.yaml` will need three new per-machine baseline keys (`providers_baseline`, `scheduler_baseline`, `hermes_home_baseline`) — nothing equivalent exists.
- `build-equality-matrix.py` will need the three dims moved out of the uniform vote into declared grading, plus legend/remediation-card text for the new row semantics.
- `collect-equality.sh` will need `unknown` emission when the scheduler probe cannot run, and a `schtasks`-based probe for Windows.
- Evidence inconsistency to resolve at baseline-authoring time: ace-win-2 reports `harness.providers.hermes: present` but `memory.hermes_home: absent` (two different probes disagree about hermes on that box).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-22 via `gh issue view` / issue creation):
- `#3592` — OPEN — equality matrix: reclassify harness/scheduler/memory rows (this plan's issue, filed 2026-07-22)
- `#3580` — OPEN — gemini uninstall (scheduled ~2026-08-01)
- `#2815` — ace-win-1 scheduler/gh-auth on-box fix (tracked, out of this plan's scope)

**File existence** (verified 2026-07-22):
- EXISTS: `scripts/readiness/build-equality-matrix.py`, `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, `scripts/readiness/harness-config.yaml`
- EXISTS: `tests/readiness/test_build_equality_matrix.py`, `tests/readiness/test_collect_equality.py`, `tests/readiness/test_collect_equality_ps1_schema.py`
- MISSING (this plan will NOT create new files except tests-adjacent fixtures if needed — all changes land in existing files)

**Line excerpts** (`sed -n 276,281p scripts/readiness/collect-equality.sh`, 2026-07-22):
```
# ── 8. SCHEDULER (counts/booleans only; never cron lines, C4) ────────────────
job_count=0; has_sync=false; has_parity=false
if [[ "$OS" != "windows" ]] && have crontab; then
  dump=$(crontab -l 2>/dev/null)
  job_count=$(printf '%s\n' "$dump" | grep -cE '^[[:space:]]*[^[:space:]#]')  # non-blank, non-comment
  printf '%s' "$dump" | grep -q 'repository-sync\|repo-sync' && has_sync=true
```

**Reproduction proofs** (per Step 1.5 — the alleged failure is a live mis-grade, not a crash):
```
$ # matrix built from all-5 fresh evidence, commit c6d34c0fa (2026-07-22):
harness   DIVERGES DIVERGES DIVERGES DIVERGES DIVERGES   (all 5 machines)
scheduler DIVERGES DIVERGES DIVERGES DIVERGES DIVERGES   (all 5 machines)
memory    DIVERGES DIVERGES DIVERGES DIVERGES DIVERGES   (all 5 machines)
$ # underlying scheduler values (equality-*.yaml, all fresh 2026-07-19..22):
dev-primary   {has_repo_sync: true,  has_parity_review: true }  job_count: 63  (measured)
dev-secondary {has_repo_sync: true,  has_parity_review: false}  job_count: 26  (measured)
gpu-claw      {has_repo_sync: false, has_parity_review: false}  job_count: 0   (measured — real gap)
ace-win-1     {has_repo_sync: false, has_parity_review: false}  job_count: 0   (PLACEHOLDER — probe skipped on windows)
ace-win-2     {has_repo_sync: false, has_parity_review: false}  job_count: 0   (PLACEHOLDER — probe skipped on windows)
```
- Reproduced at: 2026-07-22 (matrix commit `c6d34c0fa`; evidence yamls in `.claude/state/`)
- Failure mode observed matches issue claim: YES — the `{false,false}` placeholder value wins the scheduler vote 3-to-2 against the two measured Linux values; harness/memory votes penalize per-box provider choices.

<!-- Source count: issue body + build-equality-matrix.py + collect-equality.sh + collect-equality.ps1 + harness-config.yaml + live evidence yamls + drive index = 7 ≥ 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-22-issue-3592-equality-dimension-reclassification.md |
| Config change | scripts/readiness/harness-config.yaml |
| Builder change | scripts/readiness/build-equality-matrix.py |
| Collector change | scripts/readiness/collect-equality.sh |
| Tests | tests/readiness/test_build_equality_matrix.py, tests/readiness/test_collect_equality.py |
| Plan review — Claude | scripts/review/results/2026-07-22-plan-3592-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-22-plan-3592-codex.md |

---

## Deliverable

The `scheduler` and `memory` matrix rows will grade each machine against a declared per-machine baseline in `harness-config.yaml` (CONFORMS / BELOW-BASELINE / MISSING-BASELINE / MISSING-EVIDENCE) via the same cold-conformance machinery #3591 established for the harness row, and the collector will emit `unknown` for any scheduler field it does not actually probe (with a `schtasks` probe added for Windows) — so an all-fleet DIVERGES can no longer be produced by role differences or placeholder data, and the one real gap (gpu-claw's missing cron set) will grade visibly BELOW-BASELINE.

---

## Pseudocode

### 1. Config schema (`harness-config.yaml`, per `workstations.<machine>`)

`providers_baseline` already exists per #3591 (this plan will NOT touch it). NEW keys:

```yaml
hermes_home_baseline: present | absent          # per box
scheduler_baseline:
  repo_sync: required | not-required            # required on execution boxes
  parity_review: required | not-required        # required ONLY on dev-primary (leader)
```

Proposed initial values (owner confirms at approval):

| machine | hermes_home | repo_sync | parity_review |
|---|---|---|---|
| dev-primary | present | required | required |
| dev-secondary | present | required | not-required |
| gpu-claw | absent | required | not-required |
| ace-win-1 | absent → **owner decides** (probes self-contradict on the win boxes) | required (Task Scheduler) | not-required |
| ace-win-2 | absent → **owner decides** | required (Task Scheduler) | not-required |

Note: #3591 declared `hermes: present` in ace-win-2's `providers_baseline` while its
`memory.hermes_home` evidence reads `absent` (and ace-win-1 shows the inverse pairing).
The `hermes_home_baseline` values above must be reconciled with those landed provider
baselines at approval, and the implementation will identify which probe is wrong.

### 2. Builder (`build-equality-matrix.py`)

```
function declared_verdict(dim, report, baseline):     # extends the #3591 cold path
    if baseline missing for this dim → MISSING-BASELINE
    if dim == "memory":
        observed = report.memory.hermes_home  (missing/"unknown" → MISSING-EVIDENCE)
        return CONFORMS iff observed == hermes_home_baseline else BELOW-BASELINE
    if dim == "scheduler":
        if report.scheduler booleans are "unknown" → MISSING-EVIDENCE
        (schema_version < 5 AND os == windows → treat as unknown — migration gate)
        if repo_sync required and has_repo_sync != true  → BELOW-BASELINE
        if parity_review required and has_parity_review != true → BELOW-BASELINE
        return CONFORMS

move "memory" and "scheduler" from the UNIFORM path to this declared path (harness
already moved via #3591); keep DISPLAY_DIMS order unchanged; update the
remediation-card text per dim (BELOW-BASELINE → box-side fix command;
MISSING-EVIDENCE → run-the-collector command), mirroring #3591's harness hints.
```

### 3. Collector (`collect-equality.sh` §8 SCHEDULER)

```
job_count=unknown; has_sync=unknown; has_parity=unknown          # was: 0/false/false
if OS != windows and have crontab:
    probe crontab as today (measured values)
elif OS == windows and have schtasks:
    csv = schtasks /query /fo csv 2>/dev/null                    # counts/booleans only — C4 holds
    job_count = row count (excluding header)
    has_sync  = true iff any TaskName matches repo-sync/repository-sync/equality-report
    has_parity = false                                            # parity review is leader-only; still graded vs baseline
# else: leave all three "unknown" — the builder grades MISSING-EVIDENCE, never a vote/baseline pass
```

YAML emission: quote `unknown` as a string; booleans stay bare. The canonical-hash
commit-on-change payload treats `unknown` like any other value (no volatile-field change).
`schema_version` will bump 4 → 5 with this change (see the migration-gate risk entry:
the builder treats scheduler fields in schema<5 Windows evidence as `unknown`).
Windows `job_count` will include system tasks (schtasks enumerates everything) — it is
display-only (never voted/graded), so noisy counts are acceptable; the graded booleans
match on task NAMES only, consistent with the C4 no-cron-lines allowlist.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/readiness/harness-config.yaml | add `hermes_home_baseline` + `scheduler_baseline` per machine (`providers_baseline` landed via #3591 — untouched) |
| Modify | scripts/readiness/build-equality-matrix.py | move `memory` + `scheduler` from uniform vote to the #3591 declared-grading path; schema<5 Windows migration gate; remediation-card text |
| Modify | scripts/readiness/collect-equality.sh | `unknown` defaults + Windows `schtasks` probe in §8; `schema_version` 4→5 |
| Modify | tests/readiness/test_build_equality_matrix.py | TDD cases for the two declared verdicts + migration gate |
| Modify | tests/readiness/test_collect_equality.py | `unknown` emission + schtasks-parse cases |
| Modify | tests/readiness/test_collect_equality_ps1_schema.py (+ fixture) | ps1 golden fixture asserts `schema_version == 4` today and validates emitted dimensions; must be updated to schema 5 with intentional scheduler `unknown`/probed output (Codex r2 MAJOR-1/MINOR) |
| Update | docs/plans/README.md | index row for this plan |

Out of scope (tracked elsewhere): gpu-claw cron installation (box-side, #3592 checklist); ace-win-1 Task Scheduler repair (#2815); gemini uninstall itself (#3580); provider-capability parity rows `harness:<provider>:<capability>` (separate voting logic via `provider_harness_parity.py`, untouched).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_memory_hermes_home_declared | per-box hermes_home grading | absent vs baseline absent | CONFORMS |
| test_memory_hermes_home_below | hermes_home differs from declared intent | absent vs baseline present | BELOW-BASELINE |
| test_memory_missing_baseline | roster entry without hermes_home_baseline | no key | MISSING-BASELINE |
| test_memory_unknown_missing_evidence | unknown never grades | hermes_home unknown | MISSING-EVIDENCE |
| test_scheduler_required_missing | real gap stays visible | gpu-claw false + required | BELOW-BASELINE |
| test_scheduler_unknown_missing_evidence | placeholder can no longer pass or poison | all three unknown | MISSING-EVIDENCE |
| test_scheduler_leader_parity | parity_review required only on leader | dev-secondary false + not-required | CONFORMS |
| test_no_uniform_vote_for_reclassified_dims | memory + scheduler never enter uniform_verdict | evidence set with mixed values | no DIVERGES/NO-MAJORITY emitted for them |
| test_collect_scheduler_unknown_default | probe unavailable | no crontab, no schtasks | `unknown` ×3 in yaml |
| test_collect_schtasks_parse | Windows probe (fixture csv) | schtasks csv w/ repo-sync task | job_count>0, has_sync true |
| test_builder_schema4_windows_scheduler_unknown | migration gate: stale placeholder evidence cannot mis-grade | schema_version 4, os windows, false/0 | MISSING-EVIDENCE |
| test_builder_schema4_linux_scheduler_measured | Linux legacy evidence keeps measured values | schema_version 4, os linux, true/63 | graded vs baseline (CONFORMS) |
| test_ps1_golden_schema5_scheduler | ps1 golden fixture carries schema 5 + intentional scheduler output | Windows fixture run | schema_version 5; scheduler fields `unknown` or schtasks-probed, never bare false/0 placeholders |

---

## Acceptance Criteria

- [ ] All new tests will pass: `uv run pytest tests/readiness/test_build_equality_matrix.py tests/readiness/test_collect_equality.py tests/readiness/test_collect_equality_ps1_schema.py -v`
- [ ] No regression: full `tests/readiness/` suite will pass (including the updated ps1 golden fixture at schema 5 — Codex r2)
- [ ] Rebuild against the live 2026-07-22 evidence set will produce: dev-primary/dev-secondary `memory`+`scheduler` = CONFORMS (harness already CONFORMS via #3591); gpu-claw `scheduler` = BELOW-BASELINE (real gap surfaced); Windows `scheduler` = MISSING-EVIDENCE until fresh evidence with the schtasks probe lands
- [ ] No all-fleet DIVERGES row will be producible from role differences or placeholder data on the reclassified dims
- [ ] Serialization allowlist (counts/booleans/enums, never cron lines — C4) will still hold; `unknown` is an enum value
- [ ] Review artifacts posted to scripts/review/results/
- [ ] `docs/plans/README.md` index updated

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1 inline) | MINOR | F1 migration hand-wave → fixed via schema_version 4→5 gate; F2 Windows job_count semantics → documented display-only; F3 ace-win-2 hermes probe contradiction → owner decision at approval; F4 render-layer verdict coverage → covered by live-rebuild acceptance criterion |
| Codex (r2 dispatched) | MAJOR → resolved inline (r3) | MAJOR-1: ps1 golden fixture asserts schema_version==4 — test+fixture added to Files to Change / TDD list. MAJOR-2: plan claimed #3573 CLOSED; live state is OPEN — corrected, and the gemini-baseline question is mooted by re-scope (#3591 landed `providers_baseline`; this plan no longer touches provider baselines). MINOR: ps1 emitted-dimensions fixture must prove schema-5 scheduler output is intentional — added as test_ps1_golden_schema5_scheduler |

**Overall result:** PASS (r3 inline patches applied per the r1/r2-divergence loop-break convention; no unresolved MAJOR remains in the plan text)

Revisions made based on review:
- Re-scoped: harness dim removed (landed via #3591 commit `762fa1d8a` in a parallel session); plan now covers memory + scheduler only, reusing #3591's cold-conformance machinery.
- schema_version 4→5 migration gate replaces the "accept one-cycle misgrade" hand-wave (Claude F1).
- `tests/readiness/test_collect_equality_ps1_schema.py` + golden fixture added to scope (Codex MAJOR-1/MINOR).
- #3573 state corrected to OPEN; provider-baseline changes explicitly excluded from scope (Codex MAJOR-2).
- Windows `job_count` documented as display-only/noisy; graded booleans match task names only (Claude F2).

---

## Risks and Open Questions

- **Risk:** builder and `provider_harness_parity.py` share `EXPECTED_DIVERGENCE_REASONS` (drift note #3206/#3209). This plan will not touch the capability rows, but the reviewer should verify the reclassification cannot desync that pairing.
- **Risk (mitigated by design):** existing evidence yamls carry `false/0` placeholders; until every box re-collects with `unknown` semantics, Windows scheduler cells would grade BELOW-BASELINE (false ≠ required-true) instead of MISSING-EVIDENCE. Mitigation: the collector change will bump `schema_version` 4 → 5 (emitted at `collect-equality.sh:425`); the builder will treat scheduler fields in `schema_version < 5` evidence from `os: windows` as `unknown` (→ MISSING-EVIDENCE), so stale placeholder evidence can never mis-grade. Linux `schema_version < 5` evidence keeps its measured values (the Linux probe semantics are unchanged).
- **Risk:** `schtasks /query /fo csv` output is locale-dependent on some Windows SKUs; parse defensively (count rows, case-insensitive name match) and fall back to `unknown` on any parse doubt.
- **Open (owner decision at approval):** win-box hermes intent — evidence self-contradicts (ace-win-2: `providers.hermes: present` / `hermes_home: absent`; ace-win-1 the inverse), and #3591 has now baked `hermes: present` into ace-win-2's `providers_baseline`. The `hermes_home_baseline` values must be set consistently with that, and the implementation will determine which probe is lying.
- **Resolved by re-scope:** the gemini-baseline question (Codex r2) — #3591 landed `providers_baseline` with concrete `gemini` values while #3573/#3580 remain OPEN; this plan does not touch provider baselines. Flipping gemini to `absent` post-#3580 is a one-line follow-on on #3580.
- **Open (minor):** should `has_parity_review` on Windows be probed at all, or is `not-required` + unmeasured acceptable? Plan assumes the latter.

---

## Complexity: T2

**T2** — multi-file harness change (builder + config + collector + two test files), TDD required, no new modules, no cross-repo surface.
