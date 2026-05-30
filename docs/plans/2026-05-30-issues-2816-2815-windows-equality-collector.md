# Plan for #2816 + #2815: Windows-side completion of the #2801 machine-equality matrix

> **Status:** plan-review — **T2 review complete** (Claude r1 + Codex r2, 2026-05-30); design revised per the Adversarial Review Resolution section below. NOT approved — awaiting USER.
> **Complexity:** #2816 = T2 · #2815 = T2 (combined, dependency-ordered)
> **Date:** 2026-05-30
> **Issues:** https://github.com/vamseeachanta/workspace-hub/issues/2816 · https://github.com/vamseeachanta/workspace-hub/issues/2815
> **Client:** N/A
> **Design decisions (user-confirmed 2026-05-30):** #2816 Option 1 (`.ps1` delegates to `.sh`); #2815 Strategy 1 (renderer reads `schedule-tasks.yaml`, constructs the Windows action from task metadata).
> **Dependency:** #2816 (the `.ps1` collector) lands FIRST; #2815 (Task Scheduler single-source + live-validate) schedules it.
> **Review artifacts (to be produced):** scripts/review/results/2026-05-30-plan-2816-2815-{claude,codex}.md

---

## Resource Intelligence Summary

> **All findings verified against `origin/main`.** The default working tree is on `fix/statusline-codex-quota`, ~159 commits behind — the implementer MUST branch off fresh `origin/main` or they will target the obsolete `schema_version: 2` collector and silently lose provenance/solvers.

### Existing repo code (origin/main)
- `scripts/readiness/collect-equality.sh` — the canonical collector the `.ps1` must mirror: `schema_version: 3`, top-level `provenance:` block (`checkout_sha`, `dirty`, `behind_main`, `ahead_main`, `origin_ref_age_h`), 9 dims incl. `solvers`. The Windows `case` (~line 57) emits `cores` only; RAM/disk/gpu = `unknown`. **This is the contract.**
- `scripts/readiness/build-equality-matrix.py` — consumes provenance via `is_stale()` (fail-closed: missing provenance ⇒ stale; `behind_main`/`ahead_main` ≠ 0 ⇒ stale; `origin_ref_age_h` out of `[0,12]` window ⇒ stale). `coerce_to_mib()` normalizes `ram_total_mib`. The `.ps1` output must satisfy both.
- `scripts/readiness/lib/probe-solvers.sh` — shared solver-detection helpers; already Windows-aware. Emits `{licensed,present,absent,unknown}`; never emits `licensed` yet (Windows license probe is a documented #2849 follow-up).
- `scripts/readiness/harness-config.yaml` — `licensed-win-1/2` baselines carry `compute_floor: {cores_min: 8}` with `ram_gib_min` **deliberately removed** ("returns when the .ps1 compute companion lands"). This is #2816's restoration target.
- `scripts/windows/setup-scheduler-tasks.ps1` — hardcodes ~5 tasks; **no YAML read, no EqualityReport.** #2815's modification target.
- `config/scheduled-tasks/schedule-tasks.yaml` — `equality-report` is ONE `cron`-scheduler entry (`30 4 * * 1`, Mon) whose `machines:` already lists `licensed-win-1/2`, but whose `command` is Linux-shaped (`bash collect-equality.sh && uv run python build-equality-matrix.py`). Separate `win-repository-sync`/`win-session-state-commit` use `scheduler: windows-task-scheduler`.
- `scripts/cron/setup-cron.sh` — exits 0 for `contribute-minimal` (Windows) WITHOUT installing; prints "set up Task Scheduler manually." So **today nothing renders the equality task onto Windows** — exactly the #2815 gap.
- `scripts/cron/validate-schedule.py` — `VALID_SCHEDULERS = {cron, windows-task-scheduler}`; cron-format validated only when `scheduler == "cron"`.
- `tests/readiness/test_build_equality_matrix.py::test_wiring_single_source_schedule` — asserts `equality-report` stays weekly-Monday, names all 4 active machines, references both scripts. Does NOT cover the Windows renderer → #2815 adds that.

### Standards / LLM Wiki
Not applicable — harness/infrastructure.

### Evidence (verified 2026-05-30)
- Issue statuses: `#2816` OPEN, `#2815` OPEN, `#2851` CLOSED (PR #2869 MERGED — provenance/freshness live on main).
- `git rev-list --count HEAD..origin/main` on the default tree = **159** (stale — plan targets origin/main).
- `origin/main:scripts/readiness/collect-equality.sh` = `schema_version: 3` with `provenance:`; the stale tree's copy = `schema_version: 2`, no provenance.
- `grep EqualityReport scripts/windows/setup-scheduler-tasks.ps1` → no match (no equality task scheduled on Windows today).
- MISSING (this plan creates): `scripts/readiness/collect-equality.ps1`.
<!-- sources: #2816, #2815, collect-equality.sh, build-equality-matrix.py, harness-config.yaml, schedule-tasks.yaml, setup-scheduler-tasks.ps1, context.md = 8 ≥ 3 -->

### Reproduction (Step 1.5)
Structural, not a runtime crash (additive feature): the Windows `case` in `collect-equality.sh` emits `cores` only → the matrix grades licensed-win-* compute `MISSING-EVIDENCE`; and no scheduler renders the equality task onto Windows (`setup-cron.sh` exits 0 for Windows). Verified by reading both files on origin/main.

---

## Deliverable
A `scripts/readiness/collect-equality.ps1` that emits a schema-compatible `schema_version: 3` `equality-licensed-win-{1,2}.yaml` (provenance + solvers + accurate CIM compute), restored `ram_gib_min` floors in `harness-config.yaml`, and a `setup-scheduler-tasks.ps1` that renders the EqualityReport task **from `schedule-tasks.yaml`** so licensed-win-1/2 produce real, fresh, gradeable reports weekly.

---

## PART A — #2816: `collect-equality.ps1` (lands first)

### Design (Option 1 — thin compute overlay, delegate to `.sh`)
The `.ps1` computes ONLY the Windows-hard fields via CIM, exports them as `EQ_*` env vars, then invokes `bash scripts/readiness/collect-equality.sh`. The `.sh` Windows `case` is modified to honor those overrides when set (fallback to today's `unknown`). **Schema, provenance, solvers, behavior probes, and canonical-hash idempotency stay single-sourced in the `.sh`** — the `.ps1` is ~40 lines and provenance/idempotency come for free (git reads work in Git Bash). This avoids the schema-drift trap of a standalone reimplementation.

CIM compute (the `.ps1`'s real job):
```
$cs = Get-CimInstance Win32_ComputerSystem ; $os = Get-CimInstance Win32_OperatingSystem
EQ_CORES          = $cs.NumberOfLogicalProcessors
EQ_RAM_TOTAL_MIB  = [math]::Floor($cs.TotalPhysicalMemory / 1MB)      # bytes -> MiB
EQ_RAM_AVAIL_MIB  = [math]::Floor($os.FreePhysicalMemory / 1KB)       # FreePhysicalMemory is KB
EQ_DISK_AVAIL_GB  = [math]::Floor((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='<WS drive>'").FreeSpace / 1GB)
EQ_GPU_MODEL      = (Get-CimInstance Win32_VideoController | Select -First 1).Name  # or "none"
```
Emit bare integers (no units/commas) so `coerce_to_mib()` accepts them; `ram_total_mib` in MiB (matrix compares `ram_gib_min * 1024`). **Disk drive letter derived from the resolved `D:\workspace-hub` path, not hardcoded `D:`.**

**RAM floor restoration:** once the `.ps1` yields a trustworthy `ram_total_mib`, add `ram_gib_min` to `licensed-win-1/2` `compute_floor` — at an **owner-confirmed value captured from one real run** (do NOT guess: too-high = permanent BELOW-BASELINE, too-low = no signal). Sequence: land `.ps1` → owner runs once → set floor with confirmed number.

### Files to Change (#2816)
| Action | Path | Reason |
|---|---|---|
| Create | `scripts/readiness/collect-equality.ps1` | CIM compute + `EQ_*` env export + delegate to `.sh` |
| Modify | `scripts/readiness/collect-equality.sh` | Windows `case` honors `EQ_*` overrides (fallback `unknown`) |
| Modify | `scripts/readiness/harness-config.yaml` | restore `ram_gib_min` to licensed-win-1/2 (owner-confirmed) |
| Create | `tests/readiness/test_collect_equality_ps1_schema.py` | schema-contract + fixture-parity tests |
| Create | `tests/readiness/fixtures/equality-licensed-win-1.sample.yaml` | golden sample for matrix-grading test |
| Update | `docs/plans/README.md` | index row |

### TDD Test List (#2816) — PowerShell can't run on Linux CI, so test the *contract*
| Test | Verifies |
|---|---|
| `test_ps1_sample_output_parses_schema_v3` | committed `.ps1` fixture parses to v3 with `provenance` + all 9 dims |
| `test_ps1_sample_grades_conforms_compute` | fixture (cores≥8, ram≥floor) → `cold_verdict` CONFORMS |
| `test_ps1_sample_not_stale` | fixture provenance (dirty:false, behind:0, ahead:0, age in-window) → `is_stale()==False` |
| `test_ps1_ram_total_mib_is_mib_integer` | `ram_total_mib` bare integer, `coerce_to_mib` accepts, ≥ `ram_gib_min*1024` |
| `test_ps1_field_parity_with_sh_stdout` | `.ps1` fixture key-tree == `collect-equality.sh --stdout` key-tree (minus OS values) |
| `test_harness_config_winram_floor_present` | licensed-win-1/2 now carry `ram_gib_min` |
| `test_sh_honors_eq_env_overrides` | running `.sh` with `EQ_CORES=…` etc. emits those values (proves the override seam) |
| `test_ps1_static_analysis` (skip-if-no-pwsh) | `.ps1` passes `Invoke-ScriptAnalyzer` — runs only where PowerShell exists |

### Acceptance Criteria (#2816)
- [ ] `collect-equality.ps1 -Stdout` on licensed-win-1 emits `schema_version: 3` with real `cores`/`ram_total_mib`/`ram_avail_mib`/`disk_avail_gb`/`gpu_model` (owner-pasted in the issue).
- [ ] Output carries the full `provenance` block with `behind_main: 0`, `dirty: false` on clean main (not graded STALE-CHECKOUT).
- [ ] Matrix grades licensed-win-1 compute `CONFORMS` against the restored `ram_gib_min` (not MISSING-EVIDENCE).
- [ ] `ram_gib_min` restored at an owner-confirmed value.
- [ ] `uv run pytest tests/readiness/` green (no regression).

---

## PART B — #2815: Task Scheduler single-source + live-validate (lands after A)

### Design (Strategy 1 — renderer reads YAML, constructs the Windows action from task metadata)
Teach `setup-scheduler-tasks.ps1` to parse `schedule-tasks.yaml` (via `python -c`, since Windows has `python` not `uv`), select tasks where the current machine ∈ `machines:`, translate the cron `schedule` → `New-ScheduledTaskTrigger`, and **construct the action from task metadata** (the known collect + build scripts) rather than string-rewriting the Linux `command` (which would mishandle PATH prefixes, `$(date)` log redirects, `>>`). The action invokes a small atomic wrapper `equality-report.ps1` (CIM collector via the `.ps1` → matrix build via `python`), run through Git Bash so `$(date)` redirects still work. This eliminates the hardcoded duplicate for the equality task (the single-source goal) and mirrors how `setup-cron.sh` already translates the same YAML for Linux. The `equality-report` YAML entry stays the single source — `uv run python` is treated as Linux-authoritative; Windows derives `python`.

### Live-validation (owner-driven — cannot run from Linux)
1. `setup-scheduler-tasks.ps1 -WhatIf` → confirms it would register `\Claude\EqualityReport` at the YAML cadence (Mon 04:30).
2. Register, then `Start-ScheduledTask` to force an immediate run.
3. Verify `.claude/state/equality-licensed-win-1.yaml`: `schema_version: 3`, provenance `behind_main: 0`/`dirty: false`, real compute, commit-on-change fired.
4. `python scripts/readiness/build-equality-matrix.py` → licensed-win-1 column shows CONFORMS compute (not STALE-CHECKOUT / MISSING-EVIDENCE).
5. Paste evidence in #2815 / #2229.

### Files to Change (#2815)
| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/windows/setup-scheduler-tasks.ps1` | read `schedule-tasks.yaml`; render EqualityReport from it |
| Create | `scripts/windows/equality-report.ps1` | atomic Task Scheduler wrapper: `.ps1` collector → matrix build |
| Create | `tests/readiness/test_windows_scheduler_single_source.py` | static assertions (Linux-runnable): PS1 references YAML, renders EqualityReport, uses `python` not `uv` |
| Modify | `tests/readiness/test_build_equality_matrix.py` | extend wiring test to assert the Windows render path exists |
| Update | `docs/ops/` scheduled-tasks doc | document the Windows single-source render |

### TDD Test List (#2815)
| Test | Verifies |
|---|---|
| `test_ps1_reads_schedule_yaml` | PS1 references `schedule-tasks.yaml` (no hardcoded equality literal) |
| `test_ps1_no_hardcoded_equality_schedule` | `30 4 * * 1` / "04:30" not hardcoded in the PS1 |
| `test_windows_command_uses_python_not_uv` | Windows-rendered path uses `python`, never `uv run` |
| `test_wrapper_invokes_both_scripts` | `equality-report.ps1` calls `collect-equality.ps1` AND `build-equality-matrix.py` |
| `test_validate_schedule_still_passes` | `validate-schedule.py` exits 0 after changes |
| Owner-run (not CI) | `-WhatIf` register + forced run + matrix CONFORMS |

### Acceptance Criteria (#2815)
- [ ] `setup-scheduler-tasks.ps1` renders EqualityReport from `schedule-tasks.yaml` — no hardcoded duplicate.
- [ ] `-WhatIf` shows `\Claude\EqualityReport` at the YAML cadence.
- [ ] licensed-win-1 produces a real, provenance-fresh `equality-licensed-win-1.yaml` via the scheduled task.
- [ ] Windows action uses `python` (never `uv run`); both OSes invoke the same scripts from the same YAML entry.
- [ ] `validate-schedule.py` + `test_wiring_single_source_schedule` still pass.

---

## Risks and Open Questions
- **Dominant risk — cannot live-test from Linux.** The `.ps1`, CIM, Task Scheduler registration, and end-to-end run are owner-driven on licensed-win-1/2. Linux CI proves only the schema/parity *contract* via fixtures + the matrix builder. Mitigation: golden fixtures + contract tests + an explicit owner runbook; gate `Invoke-ScriptAnalyzer` to PowerShell-present machines.
- **Risk — provenance freshness on Windows (most likely "ran but graded nothing").** If the scheduled run hits a `D:\workspace-hub` behind `origin/main` or with a stale `origin/main` ref (`origin_ref_age_h` out of window), `is_stale()` marks every cell STALE-CHECKOUT. Mitigation: ensure the Windows RepoSync task (23:30) fetches before Mon-04:30 EqualityReport, OR add a `git fetch` step; verify `origin_ref_age_h` in the owner run.
- **Risk — CIM unit errors.** `FreePhysicalMemory` is KB, `TotalPhysicalMemory` is bytes — wrong magnitude → BELOW-BASELINE or absurd CONFORMS. Covered by `test_ps1_ram_total_mib_is_mib_integer` + owner sanity-check.
- **Expected, not a regression — `solvers` BELOW-BASELINE.** The probe emits at most `present`, never `licensed`, until a Windows license probe lands (#2849 follow-up), while licensed-win-* `solvers_baseline` demands `licensed`. So solver cells show BELOW-BASELINE even after this plan. Stated explicitly so reviewers don't read it as a defect.
- **Open (USER) — RAM floor value.** Recommend: land `.ps1`, capture one real run, set `ram_gib_min` to the owner-confirmed spec. Do not guess.
- **Open (USER) — Windows tier-1 layout.** Brief/`context.md` suggest repos are NESTED under `D:\workspace-hub\` (unlike Linux siblings). The `data_access` probe handles both, so this only affects whether `required_data_access` resolves CONFORMS. Confirm the layout.

## Adversarial Review Resolution (Codex r2 — 2026-05-30)
Codex returned MAJOR; both load-bearing claims were verified locally against `origin/main`. These **amend the Design / Files / Acceptance above**; artifact: `scripts/review/results/2026-05-30-plan-2816-2815-codex.md`.

| # | Finding | Verified | Resolution |
|---|---|---|---|
| W1 | **The report is never committed/pushed.** `collect-equality.sh` ends at `printf … > "$OUT"; exit` — "commit-on-change" = idempotent file *rewrite*, NOT git push. A Windows report stays local; the central matrix never sees it. | ✅ `collect-equality.sh` tail = `printf > OUT`, no `git commit/push` | **`equality-report.ps1` MUST commit + push `.claude/state/equality-*.yaml` after a successful collect+build** (or explicitly delegate to a verified `win-session-state-commit` step). New AC + a test asserting the wrapper invokes the commit/push step. (Same gap exists for Linux but is covered by repo-sync; Windows must not assume it.) |
| W2 | **PyYAML / `uv` env contract.** The `equality-report` task declares `requires: [bash, python3, uv]`; the matrix imports `yaml`. Windows has system `python` but no `uv` and possibly no PyYAML → `ModuleNotFoundError: yaml`. | ✅ `schedule-tasks.yaml` `equality-report.requires: [bash, python3, uv]`; `build-equality-matrix.py:22 import yaml` | **Explicit Windows Python environment contract (new AC):** the renderer/wrapper resolves a Python that has PyYAML — preference order: `uv run python` IF uv is present on the box, else system `python` with PyYAML confirmed installed (documented in the owner runbook + a preflight check that fails fast with a clear message). For the small YAML read in the renderer, prefer a stdlib-only extraction to avoid the dependency entirely. |
| W3 | **Freshness mitigation was advisory, not an acceptance item.** A stale `origin/main` ref → every Windows cell STALE-CHECKOUT, yet the plan only *suggested* "ensure RepoSync / OR git fetch." | ✅ collector never fetches; `is_stale()` fail-closes | **Required:** `equality-report.ps1` runs a **freshness preflight** — `git fetch` (or verify FETCH_HEAD age + `behind_main==0`) BEFORE collecting; if it can't establish freshness, it **fails fast without writing a report** (no silent STALE-CHECKOUT). New AC + owner-run check of `origin_ref_age_h`/`behind_main`. |
| W4 | **`ram_gib_min` restoration is unimplementable as written** — listed as a #2816 file change + acceptance, but the value is deferred to "owner runs once." | ✅ `harness-config.yaml` has no Windows RAM floor | **Split into a two-step gate:** #2816 lands the `.ps1` + captures one real `-Stdout` run; the `ram_gib_min` floor is set in a **follow-up commit** (within #2816) once the owner confirms the value, OR the owner supplies it before approval. Removed from the hard pre-floor acceptance; added as a gated post-evidence step. |
| W5 (MINOR) | **EQ_* override seam needs numeric allowlisting**, not happy-path only — a null/failed CIM query or malformed `EQ_*` could emit `0`/empty/garbled YAML instead of `unknown`. | — | The `.sh` seam validates each `EQ_*` is a non-negative integer (counts/MiB/GiB) and **falls back to `unknown`** otherwise. New tests: empty, non-numeric, newline, negative, unit-suffixed values. |
| W6 (MINOR) | **Scheduler tests are static string checks** — they don't cover cron(Mon-weekly)→TaskScheduler-trigger translation; the current PS1 only supports daily `-At` triggers, so a renderer could register a daily/wrong-day task and still pass. | ✅ `setup-scheduler-tasks.ps1` daily `-At` only | Add a **parser-level contract test** asserting the generated trigger metadata is weekly-Monday at the YAML time (not daily), exercising the cron→trigger translation, not just string presence. |

**Amended Acceptance (supersedes conflicting items):** the wrapper commits+pushes state after success (W1); a Windows Python-with-PyYAML contract + fail-fast preflight (W2); a freshness preflight that fails fast rather than emit a STALE report (W3); `ram_gib_min` set in a gated follow-up after captured evidence (W4); EQ_* integer-validation with `unknown` fallback (W5); a weekly-Monday trigger contract test (W6).

## Complexity
#2816 = **T2** (new `.ps1` + `.sh` seam + config + Python contract tests; owner-driven live verify). #2815 = **T2** (PS1 renderer + wrapper + YAML/test wiring; owner-driven live-validation). Combined review T2 (Claude + Codex — complete).

*Not approved. Future-tense throughout. Awaiting USER approval to move `status:plan-review` → `status:plan-approved`.*
