# Plan for #2709: feat(solver-queue): add AQWA runner adapter and schema extension

> **Status:** draft (revised after r1 Codex review — 7 blockers addressed)
> **Complexity:** T2
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2709
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2709-claude.md | scripts/review/results/2026-05-14-plan-2709-codex.md | scripts/review/results/2026-05-14-plan-2709-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/solver/submit-job.sh:13` — hard-rejects any solver that is not `orcawave` or `orcaflex`; `aqwa` will cause immediate `exit 1`.
- EXISTS: `scripts/solver/submit-batch.sh:92` — **inline Python parser** inside `parse_manifest()` will reject any `solver_type` outside `{'orcawave', 'orcaflex'}` **before** `submit-job.sh` is invoked. This is production code, not just a test helper. (Surfaced by r1 Codex review, finding #1.)
- EXISTS: `scripts/solver/process-queue.py:180-185` — dispatcher `if solver == "orcawave": ... elif solver == "orcaflex": ... else: raise ValueError(f"Unknown solver: {solver}")` — no `aqwa` branch.
- EXISTS: `scripts/solver/process-queue.py:151-154` — `process_job()` reads only `solver`, `input_file`, `export_excel`, `description` from the job YAML — no `target_machine` consumption. (Surfaced by r1 Codex review, finding #3.)
- EXISTS: `scripts/solver/process-queue.py:162` — `input_path = REPO_ROOT / input_file` is at the repo root; `output_dir = COMPLETED_DIR / job_name` is a separate directory. AQWA cannot read `<stem>.dat` from `output_dir` because the input lives elsewhere. (Surfaced by r1 Codex review, finding #4.)
- EXISTS: `scripts/solver/process-queue.py:327` — `run_orcawave(input_path: Path, output_dir: Path, export_excel: bool) -> list` — shape that `run_aqwa()` will mirror.
- EXISTS: `scripts/solver/process-queue.py:375` — `run_orcaflex(input_path: Path, output_dir: Path, export_excel: bool) -> list` — second shape reference.
- EXISTS: `scripts/solver/validate_manifest.py:40` — `VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}` — batch manifest validator will reject `aqwa`.
- EXISTS: `scripts/solver/validate_manifest.py:67-82` — `JobEntry` Pydantic model with fields `name`, `solver_type`, `model_file`, `description`. No `target_machine` field, no validator. (Surfaced by r1 Codex review, finding #2.)
- EXISTS: `tests/solver/test_batch_submission.py:132` — local helper `parse_batch_manifest` hardcodes `("orcawave", "orcaflex")` — must be updated in step with `validate_manifest.py`.
- EXISTS: `queue/job-schema.yaml:14` — `solver: "orcawave | orcaflex"` — schema doc does not list `aqwa`.
- EXISTS: `scripts/solver/README.md:3` — documents queue as OrcaWave/OrcaFlex only; omits AQWA.
- EXISTS: `scripts/enforcement/check-no-abs-paths.sh:101` — detection regex `(/home/|/mnt/|/Users/|/opt/|[A-Z]:[\\/])` matches Windows `C:\` and `C:/` paths; baseline file at `config/quality/no-abs-paths-baseline.txt` contains zero `C:` entries, so any new Windows hardcoded path will fail the gate. Line-level exemption marker is trailing `# abs-path-allowed`. (Verified by Read tool 2026-05-15.)
- GAP: No `run_aqwa()` function anywhere in the codebase.
- GAP: No `aqwa` branch in the dispatcher (`process-queue.py:184-185`).
- GAP: No `target_machine` field in `queue/job-schema.yaml`, no `JobEntry.target_machine` in `validate_manifest.py`, and no `process_job()` skip/claim logic.
- GAP: No test file `tests/solver/test_aqwa_adapter.py`.

### Standards

Not applicable — this is a solver adapter/infrastructure issue, not a standards-derived engineering calculation.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/entities/cadquery.md:17,21,47,52` — references AQWA as a hydrodynamic panel-method solver consuming `.DAT` input files; confirms AQWA output feeds RAO pipelines. States "`QPPL DIFF` requirement" for mesh density.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1559` — archived skill "no-dedicated-python-package": "The PyAnsys metapackage (33+ packages) does **not** include a dedicated AQWA client" — confirms `subprocess` is the only invocation path.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1560` — archived skill "python-subprocess-pattern": establishes the `import subprocess` + `subprocess.run()` shape.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1573` — archived skill "detecting-success-vs-failure": `grep -qi "error\|fatal\|abort" analysis.mes && echo "FAILED"` — defines the `.lis`/`.mes` log-scrape success check.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1557` — archived skill "license-architecture": `export ANSYSLMD_LICENSE_FILE=1055@license-server.domain.com` — env-var pattern for ANSYS license.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1558` — archived skill "locating-the-executable": Windows install path is typically `%ANSYS_INSTALL_DIR%\Framework\bin\Win64\` **or sibling**; must probe at runtime, not hardcode. The revised pseudocode probe set explicitly includes `Framework/bin/Win64/ansys*l.exe` per this source (r1 Codex finding #5).

### Documents consulted

- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §1 — `licensed-win-1`: "Runs OrcaWave/OrcaFlex/ANSYS through Windows Task Scheduler + Git-backed queue"; `licensed-win-2`: "preferred AQWA fallback/parallel host until live probes confirm exact licenses."
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §5 — `AQWA/ANSYS | not target | absent | target | Run only on licensed Windows hosts.`
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §8 — recommends "feat(solver-queue): AQWA Windows runner adapter" as a discrete follow-on to inbox ingestion, explicitly noting "live Windows Task Scheduler + ANSYS/AQWA command proof" as part of the deliverable.
- `docs/plans/2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md` — parent plan; confirmed AQWA was explicitly scoped out of #2641 and deferred; this issue (#2709) is the deferred work.
- `docs/plans/2026-05-14-issue-2708-orcawave-windows-smoke-validation.md` — sibling plan establishes the live-on-host smoke-validation acceptance pattern this plan will mirror.
- Related issue [#2641](https://github.com/vamseeachanta/workspace-hub/issues/2641) — OPEN — broader multi-machine inbox; AQWA queue extension was its responsibility but no plan was delivered.
- Related issue [#1586](https://github.com/vamseeachanta/workspace-hub/issues/1586) — OPEN — solver queue hardening parent; #2709 is a child.
- `tests/solver/test_batch_submission.py` — establishes mock-based test pattern: `unittest.mock.patch("subprocess.run")`, `tmp_path` fixtures, no real solver invocation.
- `tests/solver/test_queue_health.py` — establishes fixture convention: `healthy_queue`, `unhealthy_queue`, `empty_queue` temp-dir fixtures.
- `tests/solver/test_manifest_validator.py` — establishes pattern for schema validation tests using `from validate_manifest import validate_manifest, VALID_SOLVER_TYPES`.

### Gaps identified

- `run_aqwa()` function does not exist — must be created in `scripts/solver/process-queue.py`.
- Dispatcher `if/elif` block in `process_job()` does not include `aqwa` — must add `elif solver == "aqwa":` branch.
- `process_job()` does not read or honor `target_machine` — must add an opt-in skip branch (see Files to Change).
- `VALID_SOLVER_TYPES` in `validate_manifest.py` does not include `"aqwa"` — must extend.
- `JobEntry` schema in `validate_manifest.py` has no `target_machine` field and no validator — must extend.
- `submit-job.sh` validation guard does not allow `aqwa` — must extend.
- `submit-batch.sh` inline parser (`parse_manifest()` heredoc, line 92) does not allow `aqwa` — must extend (r1 finding #1).
- `queue/job-schema.yaml` does not document `aqwa` as a valid solver or `target_machine` as an optional field — must extend.
- `tests/solver/test_aqwa_adapter.py` does not exist — must create.
- `scripts/solver/README.md` does not mention AQWA — must update.
- Exact ANSYS executable path on licensed-win-1 and licensed-win-2 is unconfirmed — flagged as Open Question; live smoke validation will resolve.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14T via sibling plan #2708 evidence and `docs/plans/2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md`):
- `#2709` — OPEN — feat(solver-queue): add AQWA runner adapter and schema extension
- `#2641` — OPEN — feat(solver-queue): hands-off multi-machine inbox ingestion for OrcaWave, OrcaFlex, and AQWA
- `#1586` — OPEN — Harden solver queue: batch submission, result watcher, auto post-processing

**File existence** (verified via Read tool 2026-05-14 and 2026-05-15):
- EXISTS: `scripts/solver/submit-job.sh` (1,523 bytes)
- EXISTS: `scripts/solver/submit-batch.sh` (verified 2026-05-15 — 153 lines, inline parser at line 92)
- EXISTS: `scripts/solver/process-queue.py` (15,949 bytes)
- EXISTS: `scripts/solver/validate_manifest.py`
- EXISTS: `scripts/enforcement/check-no-abs-paths.sh` (verified 2026-05-15)
- EXISTS: `config/quality/no-abs-paths-baseline.txt` (zero `C:` entries)
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `scripts/solver/README.md`
- EXISTS: `tests/solver/test_batch_submission.py`
- EXISTS: `tests/solver/test_queue_health.py`
- EXISTS: `tests/solver/test_manifest_validator.py`
- MISSING (new — this plan creates): `tests/solver/test_aqwa_adapter.py`

**Line excerpts** (Read tool 2026-05-14 and 2026-05-15):
```
# scripts/solver/submit-job.sh:13-15
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1

# scripts/solver/submit-batch.sh:92-97  (inside parse_manifest() heredoc)
    if job['solver_type'] not in {'orcawave', 'orcaflex'}:
        print(
            f"ERROR: Job {index} invalid solver_type '{job['solver_type']}'",
            file=sys.stderr,
        )
        sys.exit(1)

# scripts/solver/process-queue.py:151-154
solver = job.get("solver", "").lower()
input_file = job.get("input_file", "")
export_excel = job.get("export_excel", False)
description = job.get("description", "")

# scripts/solver/process-queue.py:162  (input_path is at repo root)
input_path = REPO_ROOT / input_file

# scripts/solver/process-queue.py:169  (output_dir is a separate location)
output_dir = COMPLETED_DIR / job_name

# scripts/solver/process-queue.py:180-185
if solver == "orcawave":
    result_files = run_orcawave(input_path, output_dir, export_excel)
elif solver == "orcaflex":
    result_files = run_orcaflex(input_path, output_dir, export_excel)
else:
    raise ValueError(f"Unknown solver: {solver}")

# scripts/solver/validate_manifest.py:40
VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}

# scripts/enforcement/check-no-abs-paths.sh:101
PATTERN='(/home/|/mnt/|/Users/|/opt/|[A-Z]:[\\/])'

# queue/job-schema.yaml:14
solver: "orcawave | orcaflex"

# tests/solver/test_batch_submission.py:132
if job["solver_type"] not in ("orcawave", "orcaflex"):
    raise ValueError(f"Job {i} invalid solver '{job['solver_type']}' — must be 'orcawave' or 'orcaflex'")
```

**Gap proofs**:
- `grep -r "run_aqwa" scripts/solver/` → no matches → `run_aqwa()` does not exist anywhere in solver scripts.
- `grep -r '"aqwa"' scripts/solver/validate_manifest.py` → no matches → `VALID_SOLVER_TYPES` does not include `aqwa`.
- `grep -r 'target_machine' scripts/solver/` → no matches → no consumption path.
- `grep -c "C:" config/quality/no-abs-paths-baseline.txt` → 0 → Windows absolute paths are NOT baselined-exempt (verified 2026-05-15).
- `ls tests/solver/test_aqwa_adapter.py 2>&1` → "No such file or directory" → no existing AQWA adapter test file.

**Reproduction proofs**:

N/A — adding new functionality, not fixing a regression. No runtime failure alleged. The gap is absence of AQWA support; the existing code correctly rejects `aqwa` as an unknown solver (which is the correct behavior until this plan is implemented). Marked intentional per `issue-planning-mode` SKILL.md Step 1.5 skip-allowed rule.

<!-- Verification: distinct sources: (1) issue #2709 body, (2) submit-job.sh, (3) submit-batch.sh, (4) process-queue.py, (5) validate_manifest.py, (6) job-schema.yaml, (7) #2641 plan + issue, (8) #1586, (9) baseline inventory doc, (10) archived AQWA skills in SKILLS_SUMMARY.md, (11) test_batch_submission.py, (12) cadquery wiki page, (13) check-no-abs-paths.sh + baseline file, (14) sibling plan #2708. Count: 14 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2709-aqwa-runner-adapter.md` |
| New test file | `tests/solver/test_aqwa_adapter.py` |
| Modified: dispatcher + adapter + target_machine claim | `scripts/solver/process-queue.py` |
| Modified: submit script | `scripts/solver/submit-job.sh` |
| Modified: batch submit script (inline parser) | `scripts/solver/submit-batch.sh` |
| Modified: manifest validator | `scripts/solver/validate_manifest.py` |
| Modified: schema doc | `queue/job-schema.yaml` |
| Modified: README | `scripts/solver/README.md` |
| New: live-smoke validation report | `docs/reports/<date>-aqwa-smoke-validation.md` (written during implementation execution on the AQWA-licensed Windows host) |
| Plan review — Claude | `scripts/review/results/2026-05-14-plan-2709-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-14-plan-2709-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-14-plan-2709-gemini.md` |

---

## Deliverable

A `run_aqwa()` adapter function will be added to `scripts/solver/process-queue.py`, the dispatcher will be extended to route `solver: aqwa` jobs to it, all hardcoded solver-type allowlists (in `submit-job.sh`, `submit-batch.sh` inline parser, `validate_manifest.py`, and `test_batch_submission.py`'s local helper) will be updated to include `aqwa`, a `target_machine` optional field will be added to `queue/job-schema.yaml` **and made functional** in `validate_manifest.py` (warning on unknown values) and in `process-queue.py`'s `process_job()` (skip when set to a host other than the current `socket.gethostname()`); the full change will be covered by a new pytest test file `tests/solver/test_aqwa_adapter.py` and validated end-to-end by a live AQWA smoke run on the AQWA-licensed Windows host whose result will be captured in `docs/reports/<date>-aqwa-smoke-validation.md`.

---

## Pseudocode

```
function run_aqwa(input_path, output_dir, export_excel):
    validate input_path suffix in (".dat", ".aqwa")
        raise ValueError with clear message if not

    locate ANSYS executable:
        # ANSYS_INSTALL_DIR is REQUIRED — no Windows-default fallback (per r1 Codex
        # finding #7; check-no-abs-paths.sh regex `[A-Z]:[\\/]` rejects hardcoded
        # `C:/Program Files/ANSYS Inc/...`).
        install_dir = os.environ.get("ANSYS_INSTALL_DIR")
        if not install_dir:
            raise RuntimeError(
                "AQWA executable not found — set ANSYS_INSTALL_DIR to the ANSYS "
                "installation root (e.g., the directory containing 'v241', 'v251', "
                "or 'Framework/bin/Win64'). See scripts/solver/README.md "
                "AQWA-host-setup section."
            )
        aqwa_exe = _locate_aqwa_exe(Path(install_dir))
        if aqwa_exe is None:
            raise RuntimeError(
                f"AQWA executable not found under ANSYS_INSTALL_DIR={install_dir}. "
                f"Probed: ansys/bin/winx64/ansys*l.exe, ansys*/bin/winx64/ansys*l.exe, "
                f"Framework/bin/Win64/ansys*l.exe, **/aqwa*.exe."
            )

    # AQWA reads <stem>.dat from cwd, writes <stem>.lis, <stem>.res, etc. into cwd.
    # input_path lives at REPO_ROOT/<input_file>; output_dir is COMPLETED_DIR/<job_name>.
    # Copy the input into output_dir BEFORE invoking AQWA (per r1 Codex finding #4).
    staged_input = output_dir / input_path.name
    shutil.copy2(input_path, staged_input)

    build command: [str(aqwa_exe), str(staged_input.stem)]

    run subprocess in output_dir as cwd:
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True, timeout=3600)

    check returncode:
        if result.returncode != 0:
            raise RuntimeError(f"AQWA exited {result.returncode}: {result.stderr[:500]}")

    check listing file for error markers:
        lis_path = output_dir / (staged_input.stem + ".lis")
        if lis_path.exists():
            content = lis_path.read_text(errors="replace").lower()
            if any(kw in content for kw in ("error", "fatal", "abort")):
                raise RuntimeError(f"AQWA listing contains error markers — see {lis_path.name}")

    collect output files:
        output_files = []
        for suffix in (".lis", ".res", ".tab", ".plt"):
            candidate = output_dir / (staged_input.stem + suffix)
            if candidate.exists():
                output_files.append(candidate.name)

    if export_excel:
        log.warning("AQWA: export_excel=True accepted for interface parity but skipped; "
                    "see #2709 risks for follow-up xlsx wiring.")

    return output_files

function _locate_aqwa_exe(install_dir):
    # extracted helper for testability; install_dir is REQUIRED (Path object)
    # Probe ordering follows SKILLS_SUMMARY.md:1558 (Framework/bin/Win64 listed first
    # per the cited source; legacy ansys*/bin/winx64 included as fallback).
    probe_patterns = [
        "Framework/bin/Win64/ansys*l.exe",
        "ansys/bin/winx64/ansys*l.exe",
        "ansys*/bin/winx64/ansys*l.exe",
        "v*/aqwa/bin/winx64/aqwa*.exe",
    ]
    for pattern in probe_patterns:
        matches = list(install_dir.glob(pattern))
        if matches:
            return max(matches)   # latest version by name sort
    return None

# Dispatcher and target_machine claim logic in process_job():
function process_job(job_path):
    ... existing parse ...
    target_machine = job.get("target_machine", "")
    if target_machine:
        import socket
        current_host = socket.gethostname().lower()
        if target_machine.lower() != current_host:
            log.info(f"Skipping {job_name}: target_machine={target_machine}, "
                     f"this host={current_host}")
            return None   # caller treats None as "not claimed" — not moved to failed
    ... existing dispatcher, extended with elif solver == "aqwa": run_aqwa(...) ...
```

**Note on `_locate_aqwa_exe`**: it intentionally contains **zero hardcoded Windows paths**. The probe is rooted at `ANSYS_INSTALL_DIR` (provided by the Windows host's environment, set during ANSYS install or by `setup-scheduler.ps1`). This satisfies `scripts/enforcement/check-no-abs-paths.sh` without needing `# abs-path-allowed` exemptions (r1 finding #7).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/solver/process-queue.py` | (a) Add `run_aqwa()` + `_locate_aqwa_exe()` functions. (b) Extend dispatcher `if/elif` block at line 183 with `elif solver == "aqwa":` branch. (c) Add `target_machine` claim check at the top of `process_job()` (after parse, before solver validation) that returns `None` and logs when the YAML's `target_machine` does not match `socket.gethostname()`. (d) Update the main-loop `for job_file in job_files` counter to treat a `None` return as "skipped" (not success, not failure). |
| Modify | `scripts/solver/submit-job.sh` | Extend validation guard at line 13 to allow `aqwa` in addition to `orcawave` and `orcaflex` |
| Modify | `scripts/solver/submit-batch.sh` | Update the inline Python parser in `parse_manifest()` at line 92 — change the allowlist set from `{'orcawave', 'orcaflex'}` to `{'orcawave', 'orcaflex', 'aqwa'}`. Without this, AQWA batch manifests fail before `submit-job.sh` is reached (r1 finding #1). |
| Modify | `scripts/solver/validate_manifest.py` | (a) Add `"aqwa"` to `VALID_SOLVER_TYPES` set at line 40. (b) Add `target_machine: Optional[str] = None` to `JobEntry` (line 67-72) with a `@field_validator("target_machine")` that **warns** (does not raise) for values outside `{"licensed-win-1", "licensed-win-2"}` — uses the result.warnings channel via the same pattern as schema_version. (c) If pydantic unavailable, mirror the warning in the manual-validation else-branch. (r1 finding #2.) |
| Modify | `queue/job-schema.yaml` | Add `aqwa` to the `solver` enum string; add `target_machine` as optional field with values `licensed-win-1 \| licensed-win-2` and a comment documenting it as a "claim" mechanism processed by `process_job()` |
| Modify | `scripts/solver/README.md` | Add AQWA to the solver list in the Architecture section; add `target_machine` field to the Job YAML Format section; add an "AQWA-host-setup" subsection documenting `ANSYS_INSTALL_DIR` and `ANSYSLMD_LICENSE_FILE` env-var requirements |
| Modify | `tests/solver/test_batch_submission.py` | Update local helper `parse_batch_manifest` at line 132 to include `aqwa` in its allowlist tuple |
| Create | `tests/solver/test_aqwa_adapter.py` | Full pytest test suite for `run_aqwa()`, `_locate_aqwa_exe()`, schema extension, submit-job guard, submit-batch inline parser, and target_machine routing |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_run_aqwa_subprocess_called_with_correct_args` | subprocess is called with AQWA exe + stem arg, cwd=output_dir | mock ANSYS_INSTALL_DIR env, mock exe path, mock subprocess.run → returncode=0 | output_files list contains `.lis` stem |
| `test_run_aqwa_stages_input_into_output_dir` | input file is copied into output_dir before subprocess invocation | input_path at tmp_repo/input.dat, output_dir at tmp_completed/job1, mock subprocess.run → returncode=0 | `output_dir / "input.dat"` exists after run_aqwa returns; subprocess cwd == output_dir |
| `test_run_aqwa_invalid_input_suffix_raises` | non-.dat input is rejected before subprocess call | input_path with `.owd` suffix | `ValueError` with message mentioning expected suffix |
| `test_run_aqwa_nonzero_returncode_raises` | subprocess failure is surfaced as RuntimeError | mock subprocess.run → returncode=1, stderr="license error" | `RuntimeError` containing "AQWA exited 1" |
| `test_run_aqwa_lis_error_marker_raises` | `.lis` log containing "ERROR" triggers RuntimeError even when returncode=0 | returncode=0, `.lis` file with "** ERROR" line | `RuntimeError` containing "error markers" |
| `test_run_aqwa_collects_all_output_files` | all four output files (.lis, .res, .tab, .plt) when present are returned | mock subprocess.run → returncode=0, create all four files in tmp output_dir | list of four filenames in any order |
| `test_run_aqwa_partial_output_files_ok` | partial output (only .lis, .res) does not raise | only .lis and .res created | list of two filenames, no exception |
| `test_run_aqwa_missing_env_var_raises` | missing ANSYS_INSTALL_DIR raises RuntimeError with clear message | env var unset | `RuntimeError` containing "set ANSYS_INSTALL_DIR" |
| `test_run_aqwa_env_set_but_no_exe_raises` | ANSYS_INSTALL_DIR set but no executable found raises with probed-patterns hint | env var set to empty tmp dir | `RuntimeError` listing the probed glob patterns |
| `test_locate_aqwa_exe_finds_framework_bin_win64` | `_locate_aqwa_exe()` finds exe under Framework/bin/Win64 (cited source) | tmp dir with `Framework/bin/Win64/ansys251l.exe` | Path object matching the fake exe |
| `test_locate_aqwa_exe_finds_legacy_winx64` | `_locate_aqwa_exe()` finds exe under ansys/bin/winx64 (legacy) | tmp dir with `ansys/bin/winx64/ansys241l.exe` | Path object matching the fake exe |
| `test_locate_aqwa_exe_returns_none_if_missing` | `_locate_aqwa_exe()` returns None when nothing found | tmp dir with no matching exe | `None` |
| `test_validate_manifest_accepts_aqwa_solver_type` | `validate_manifest.py` no longer rejects `aqwa` | manifest with `solver_type: aqwa` | `ValidationResult.valid == True` |
| `test_validate_manifest_still_rejects_unknown_solver` | non-`{orcawave,orcaflex,aqwa}` still raises | manifest with `solver_type: abaqus` | `ValueError` or `ValidationResult.valid == False` |
| `test_submit_job_sh_accepts_aqwa` | `submit-job.sh` no longer exits 1 for `aqwa` | dry invocation: `bash submit-job.sh aqwa /nonexistent/model.dat` (will fail at file-check step, NOT at solver-check step) | exit 1 with "input file not found", NOT "solver must be" |
| `test_submit_batch_sh_inline_parser_accepts_aqwa` | `submit-batch.sh` heredoc parser no longer exits 1 for `aqwa` | minimal manifest with one `solver_type: aqwa` job, `--dry-run` | exit 0; stdout shows "[DRY RUN] Would call: submit-job.sh aqwa" |
| `test_process_job_dispatches_aqwa` | `process_job()` routes `solver=aqwa` to `run_aqwa()`, not `raise ValueError` | mock job YAML with `solver: aqwa`, mock `run_aqwa` | `run_aqwa` called once; `run_orcawave` and `run_orcaflex` not called |
| `test_job_schema_target_machine_optional` | `target_machine` field is optional in schema; omitting it does not raise | manifest without `target_machine` | validation passes |
| `test_job_schema_target_machine_invalid_value_warns` | unrecognised `target_machine` value produces a warning (not error) | manifest with `target_machine: gali-linux-compute-1` | `ValidationResult.valid == True`, `ValidationResult.warnings` non-empty and mentions `target_machine` |
| `test_process_job_skips_when_target_machine_mismatch` | `process_job()` returns None and does not invoke a solver when `target_machine` ≠ `socket.gethostname()` | mock job YAML with `target_machine: licensed-win-2`, mock `socket.gethostname` → `licensed-win-1` | `run_aqwa` not called; return value is None; job_path not moved |
| `test_process_job_claims_when_target_machine_matches` | `process_job()` proceeds when `target_machine` == `socket.gethostname()` | mock job YAML with `target_machine: licensed-win-1`, mock `socket.gethostname` → `licensed-win-1` | `run_aqwa` called once |

---

## Acceptance Criteria

- [ ] All new tests will pass: `uv run pytest tests/solver/test_aqwa_adapter.py -v`
- [ ] Manifest validator will accept `aqwa` and surface a warning (not error) for unknown `target_machine`: `uv run pytest tests/solver/test_manifest_validator.py -v`
- [ ] Batch submission tests will pass with updated allowlist in both Python helper and shell inline parser: `uv run pytest tests/solver/test_batch_submission.py -v`
- [ ] No regression in full solver suite: `uv run pytest tests/solver/ -v`
- [ ] `bash scripts/solver/submit-job.sh aqwa nonexistent.dat` will exit 1 with "input file not found" (not "solver must be"), confirming the solver-guard was updated
- [ ] `bash scripts/solver/submit-batch.sh tests/fixtures/aqwa-batch.yaml --dry-run` will exit 0 with `[DRY RUN] Would call: submit-job.sh aqwa ...`, confirming the inline parser was updated
- [ ] `grep "aqwa" queue/job-schema.yaml` will match at least two lines (solver enum + target_machine documentation)
- [ ] `scripts/solver/README.md` will mention AQWA in the Architecture section, the Job YAML Format section, and an AQWA-host-setup section
- [ ] `scripts/enforcement/check-no-abs-paths.sh scripts/solver/process-queue.py` will exit 0 with no new violations (no `C:\...` hardcoded paths introduced)
- [ ] **Live on-host AQWA smoke run**: a real AQWA invocation on the AQWA-licensed Windows host (licensed-win-1 or licensed-win-2 per inventory §1) will process a representative `.dat` input through the full queue path (`submit-job.sh aqwa` → pending/ → `process-queue.py` → completed/ with `.lis` file containing zero error markers), with the run result captured in `docs/reports/<YYYY-MM-DD>-aqwa-smoke-validation.md` following the pattern established by #2708's smoke-validation deliverable. This criterion is **not satisfiable by mocked tests** — closure of #2709 requires the report.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | MAJOR | 7 blockers — addressed in this revision (see Revisions made) |
| Codex (r2) | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** MAJOR — revised. r2 pending.

### Revisions made based on r1 review

1. **r1 finding #1 (submit-batch.sh missing)** — Added `scripts/solver/submit-batch.sh` to Files to Change, with the specific edit to the inline `parse_manifest()` heredoc allowlist set at line 92. New TDD entry `test_submit_batch_sh_inline_parser_accepts_aqwa`. Added to acceptance criteria.
2. **r1 finding #2 (target_machine schema not implementable)** — Added explicit `JobEntry.target_machine: Optional[str] = None` field and `@field_validator("target_machine")` warning mechanism to `validate_manifest.py` in Files to Change, with parallel update to the pydantic-fallback manual branch. Test `test_job_schema_target_machine_invalid_value_warns` is now backed by code.
3. **r1 finding #3 (target_machine cannot route)** — Added explicit `process_job()` claim/skip branch in `scripts/solver/process-queue.py` (Files to Change row updated with sub-bullets a–d). Two new TDD tests: `test_process_job_skips_when_target_machine_mismatch` and `test_process_job_claims_when_target_machine_matches`. Routing is now real, not schema-only.
4. **r1 finding #4 (pseudocode can't read input)** — Revised pseudocode to copy `input_path` into `output_dir` via `shutil.copy2` **before** `subprocess.run`, then pass `staged_input.stem` as the AQWA job-name arg. New TDD test `test_run_aqwa_stages_input_into_output_dir` verifies the staging step.
5. **r1 finding #5 (executable probe contradicts cited source)** — Reconciled probe order. `Framework/bin/Win64/ansys*l.exe` is now the **first** glob pattern in `_locate_aqwa_exe()`, matching SKILLS_SUMMARY.md:1558. Legacy `ansys/bin/winx64` retained as fallback. New TDD test `test_locate_aqwa_exe_finds_framework_bin_win64`.
6. **r1 finding #6 (no live-AQWA acceptance)** — Added live-on-host AQWA smoke-run acceptance criterion mirroring #2708's pattern, with explicit `docs/reports/<date>-aqwa-smoke-validation.md` deliverable. Criterion is explicitly flagged "not satisfiable by mocked tests."
7. **r1 finding #7 (hardcoded Windows paths)** — Verified that `scripts/enforcement/check-no-abs-paths.sh` line 101 regex `[A-Z]:[\\/]` will match `C:\` and `C:/`, and that `config/quality/no-abs-paths-baseline.txt` contains zero `C:` entries. Removed `Path("C:/Program Files/ANSYS Inc")` and `Path("C:/ANSYS Inc")` from pseudocode. `ANSYS_INSTALL_DIR` is now strictly required; clear error message points operator to README setup section. Added `scripts/enforcement/check-no-abs-paths.sh` invocation to acceptance criteria.

---

## Risks and Open Questions

- **Open (blocking for implementation): Which licensed Windows host holds the AQWA license?** `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §1 states licensed-win-2 is the "preferred AQWA fallback/parallel host until live probes confirm exact licenses." licensed-win-1 lists "OrcaWave/OrcaFlex/ANSYS" broadly. Exact ANSYS/AQWA install and license-server address on each host are unconfirmed. Implementation will require the user to verify and supply `ANSYS_INSTALL_DIR` and `ANSYSLMD_LICENSE_FILE` before the live smoke-validation acceptance criterion can be met.
- **Open: ANSYS AQWA command-line invocation shape.** Archived skill `python-subprocess-pattern` (SKILLS_SUMMARY:1560) confirms subprocess is the only path. The exact executable name and argument format varies by ANSYS version (e.g., `ansys241l.exe` for v24.1 vs `ansys251l.exe` for v25.1) and install location. Plan's `_locate_aqwa_exe()` uses glob + env-var probe as the safest cross-version approach. The live smoke-validation criterion will resolve this open question by recording the actual invocation that worked.
- **Open: Primary vs secondary output artifacts.** AQWA produces `.lis` (text listing/log — always), `.res` (binary results), `.tab` (tabular output), `.plt` (plot data). Plan treats all four as collected if present, with `.lis` as the success-indicator file. The RAO pipeline downstream (digitalmodel AQWA module) consumes `.lis` and `.res`. If `.plt` and `.tab` are not needed for the immediate pipeline, they can be deprioritised or excluded from `output_files` in a follow-up.
- **Risk: `export_excel` parameter is accepted but not implemented for AQWA.** OrcaWave and OrcaFlex have xlsx exporters; AQWA does not (no Python API, no built-in XLSX emitter). `run_aqwa()` will accept `export_excel` for interface parity but will log a warning and skip if `True`. A follow-up issue should wire `export_excel=True` to a post-processing step that parses `.tab` into an xlsx.
- **Risk: 60-minute subprocess timeout may be insufficient for large AQWA models.** Diffraction analyses with fine-mesh hulls can exceed 2h. Plan sets a 3600s timeout as a starting point with a comment to make it configurable via an optional `timeout_seconds` job field.
- **Risk: `target_machine` host-matching uses `socket.gethostname()`.** This relies on each Windows host being named exactly `licensed-win-1` or `licensed-win-2`. If the actual hostnames differ (Windows hostname conventions vary), the claim branch will skip everything. The README update will document the requirement; live smoke validation will surface any mismatch.
- **Risk: `test_batch_submission.py:132` local helper `parse_batch_manifest` hardcodes `("orcawave", "orcaflex")`.** This helper is defined inside the test file (not imported from `validate_manifest.py`) and is now an explicit Files-to-Change row, but if a future contributor adds a new solver they will need to remember three sites (validator, batch shell inline parser, test helper) — consider extracting to a shared module in a follow-up.
- **Risk: ANSYS license server environment variable must be set in the Windows Task Scheduler task's environment.** If `ANSYSLMD_LICENSE_FILE` is not set in the scheduled task context, AQWA will silently use the wrong license server or fail. The `setup-scheduler.ps1` will need to be updated to include the env-var if/when AQWA is deployed on a licensed Windows host. The README's AQWA-host-setup section will document this; live smoke validation will detect a misconfiguration.

---

## Complexity: T2

**T2** — new adapter function with subprocess invocation and error handling, schema extension across five files (one new test file, four production files including the previously-missed `submit-batch.sh`), one existing test file updated, plus a functional `target_machine` claim branch in the queue processor and a live-on-host smoke-validation deliverable. No new repo-level infrastructure required; follows the established `run_orcawave` / `run_orcaflex` pattern and #2708's live-validation pattern. The r1 review surfaced no scope expansion that would push this into T3 — all seven fixes are concrete code edits within the existing solver-queue module boundary.
