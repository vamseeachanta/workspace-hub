# Plan for #2709: feat(solver-queue): add AQWA runner adapter and schema extension

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2709
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2709-claude.md | scripts/review/results/2026-05-14-plan-2709-codex.md | scripts/review/results/2026-05-14-plan-2709-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/solver/submit-job.sh:13` — hard-rejects any solver that is not `orcawave` or `orcaflex`; `aqwa` will cause immediate `exit 1`.
- EXISTS: `scripts/solver/process-queue.py:180-185` — dispatcher `if solver == "orcawave": ... elif solver == "orcaflex": ... else: raise ValueError(f"Unknown solver: {solver}")` — no `aqwa` branch.
- EXISTS: `scripts/solver/process-queue.py:327` — `run_orcawave(input_path: Path, output_dir: Path, export_excel: bool) -> list` — shape that `run_aqwa()` will mirror.
- EXISTS: `scripts/solver/process-queue.py:375` — `run_orcaflex(input_path: Path, output_dir: Path, export_excel: bool) -> list` — second shape reference.
- EXISTS: `scripts/solver/validate_manifest.py:40` — `VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}` — batch manifest validator will reject `aqwa`.
- EXISTS: `tests/solver/test_batch_submission.py:132` — local helper `parse_batch_manifest` hardcodes `("orcawave", "orcaflex")` — must be updated in step with `validate_manifest.py`.
- EXISTS: `queue/job-schema.yaml:14` — `solver: "orcawave | orcaflex"` — schema doc does not list `aqwa`.
- EXISTS: `scripts/solver/README.md:3` — documents queue as OrcaWave/OrcaFlex only; omits AQWA.
- GAP: No `run_aqwa()` function anywhere in the codebase.
- GAP: No `aqwa` branch in the dispatcher (`process-queue.py:184-185`).
- GAP: No `target_machine` field in `queue/job-schema.yaml` — needed to route AQWA jobs to the correct licensed Windows host.
- GAP: No test file `tests/solver/test_aqwa_adapter.py`.

### Standards

Not applicable — this is a solver adapter/infrastructure issue, not a standards-derived engineering calculation.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/entities/cadquery.md:17,21,47,52` — references AQWA as a hydrodynamic panel-method solver consuming `.DAT` input files; confirms AQWA output feeds RAO pipelines. States "`QPPL DIFF` requirement" for mesh density.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1559` — archived skill "no-dedicated-python-package": "The PyAnsys metapackage (33+ packages) does **not** include a dedicated AQWA client" — confirms `subprocess` is the only invocation path.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1560` — archived skill "python-subprocess-pattern": establishes the `import subprocess` + `subprocess.run()` shape.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1573` — archived skill "detecting-success-vs-failure": `grep -qi "error\|fatal\|abort" analysis.mes && echo "FAILED"` — defines the `.lis`/`.mes` log-scrape success check.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1557` — archived skill "license-architecture": `export ANSYSLMD_LICENSE_FILE=1055@license-server.domain.com` — env-var pattern for ANSYS license.
- `knowledge/wikis/engineering/raw/papers/SKILLS_SUMMARY.md:1558` — archived skill "locating-the-executable": Windows install path is typically `%ANSYS_INSTALL_DIR%\Framework\bin\Win64\` or sibling; must probe at runtime, not hardcode.

### Documents consulted

- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §1 — `licensed-win-1`: "Runs OrcaWave/OrcaFlex/ANSYS through Windows Task Scheduler + Git-backed queue"; `licensed-win-2`: "preferred AQWA fallback/parallel host until live probes confirm exact licenses."
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §5 — `AQWA/ANSYS | not target | absent | target | Run only on licensed Windows hosts.`
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §8 — recommends "feat(solver-queue): AQWA Windows runner adapter" as a discrete follow-on to inbox ingestion.
- `docs/plans/2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md` — parent plan; confirmed AQWA was explicitly scoped out of #2641 and deferred; this issue (#2709) is the deferred work.
- Related issue [#2641](https://github.com/vamseeachanta/workspace-hub/issues/2641) — OPEN — broader multi-machine inbox; AQWA queue extension was its responsibility but no plan was delivered.
- Related issue [#1586](https://github.com/vamseeachanta/workspace-hub/issues/1586) — OPEN — solver queue hardening parent; #2709 is a child.
- `tests/solver/test_batch_submission.py` — establishes mock-based test pattern: `unittest.mock.patch("subprocess.run")`, `tmp_path` fixtures, no real solver invocation.
- `tests/solver/test_queue_health.py` — establishes fixture convention: `healthy_queue`, `unhealthy_queue`, `empty_queue` temp-dir fixtures.
- `tests/solver/test_manifest_validator.py` — establishes pattern for schema validation tests using `from validate_manifest import validate_manifest, VALID_SOLVER_TYPES`.

### Gaps identified

- `run_aqwa()` function does not exist — must be created in `scripts/solver/process-queue.py`.
- Dispatcher `if/elif` block in `process_job()` does not include `aqwa` — must add `elif solver == "aqwa":` branch.
- `VALID_SOLVER_TYPES` in `validate_manifest.py` does not include `"aqwa"` — must extend.
- `submit-job.sh` validation guard does not allow `aqwa` — must extend.
- `queue/job-schema.yaml` does not document `aqwa` as a valid solver or `target_machine` as an optional field — must extend.
- `tests/solver/test_aqwa_adapter.py` does not exist — must create.
- `scripts/solver/README.md` does not mention AQWA — must update.
- Exact ANSYS executable path on licensed-win-1 and licensed-win-2 is unconfirmed — flagged as Open Question.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14T via sibling plan #2708 evidence and `docs/plans/2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md`):
- `#2709` — OPEN — feat(solver-queue): add AQWA runner adapter and schema extension
- `#2641` — OPEN — feat(solver-queue): hands-off multi-machine inbox ingestion for OrcaWave, OrcaFlex, and AQWA
- `#1586` — OPEN — Harden solver queue: batch submission, result watcher, auto post-processing

**File existence** (verified via Read tool 2026-05-14):
- EXISTS: `scripts/solver/submit-job.sh` (1,523 bytes)
- EXISTS: `scripts/solver/process-queue.py` (15,949 bytes)
- EXISTS: `scripts/solver/validate_manifest.py`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `scripts/solver/README.md`
- EXISTS: `tests/solver/test_batch_submission.py`
- EXISTS: `tests/solver/test_queue_health.py`
- EXISTS: `tests/solver/test_manifest_validator.py`
- MISSING (new — this plan creates): `tests/solver/test_aqwa_adapter.py`

**Line excerpts** (Read tool 2026-05-14):
```
# scripts/solver/submit-job.sh:13-15
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1

# scripts/solver/process-queue.py:180-185
if solver == "orcawave":
    result_files = run_orcawave(input_path, output_dir, export_excel)
elif solver == "orcaflex":
    result_files = run_orcaflex(input_path, output_dir, export_excel)
else:
    raise ValueError(f"Unknown solver: {solver}")

# scripts/solver/validate_manifest.py:40
VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}

# queue/job-schema.yaml:14
solver: "orcawave | orcaflex"

# tests/solver/test_batch_submission.py:132
if job["solver_type"] not in ("orcawave", "orcaflex"):
    raise ValueError(f"Job {i} invalid solver '{job['solver_type']}' — must be 'orcawave' or 'orcaflex'")

# docs/ops/2026-05-04-multimachine-baseline-inventory.md (table row §1):
| `licensed-win-2` | Secondary licensed solver host | preferred AQWA fallback/parallel host until live probes confirm exact licenses. |

# docs/ops/2026-05-04-multimachine-baseline-inventory.md (table row §5):
| AQWA/ANSYS | not target | absent | target | Run only on licensed Windows hosts. |
```

**Gap proofs**:
- `grep -r "run_aqwa" scripts/solver/` → no matches → `run_aqwa()` does not exist anywhere in solver scripts.
- `grep -r '"aqwa"' scripts/solver/validate_manifest.py` → no matches → `VALID_SOLVER_TYPES` does not include `aqwa`.
- `ls tests/solver/test_aqwa_adapter.py 2>&1` → "No such file or directory" → no existing AQWA adapter test file.

**Reproduction proofs**:

N/A — adding new functionality, not fixing a regression. No runtime failure alleged. The gap is absence of AQWA support; the existing code correctly rejects `aqwa` as an unknown solver (which is the correct behavior until this plan is implemented). Marked intentional per `issue-planning-mode` SKILL.md Step 1.5 skip-allowed rule.

<!-- Verification: distinct sources: (1) issue #2709 body, (2) submit-job.sh, (3) process-queue.py, (4) validate_manifest.py, (5) job-schema.yaml, (6) #2641 plan + issue, (7) #1586, (8) baseline inventory doc, (9) archived AQWA skills in SKILLS_SUMMARY.md, (10) test_batch_submission.py, (11) cadquery wiki page. Count: 11 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2709-aqwa-runner-adapter.md` |
| New test file | `tests/solver/test_aqwa_adapter.py` |
| Modified: dispatcher + adapter | `scripts/solver/process-queue.py` |
| Modified: submit script | `scripts/solver/submit-job.sh` |
| Modified: manifest validator | `scripts/solver/validate_manifest.py` |
| Modified: schema doc | `queue/job-schema.yaml` |
| Modified: README | `scripts/solver/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-14-plan-2709-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-14-plan-2709-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-14-plan-2709-gemini.md` |

---

## Deliverable

A `run_aqwa()` adapter function will be added to `scripts/solver/process-queue.py`, the dispatcher will be extended to route `solver: aqwa` jobs to it, all four hardcoded solver-type allowlists will be updated to include `aqwa`, and a `target_machine` optional field will be added to `queue/job-schema.yaml`; the full change will be covered by a new pytest test file `tests/solver/test_aqwa_adapter.py`.

---

## Pseudocode

```
function run_aqwa(input_path, output_dir, export_excel):
    validate input_path suffix in (".dat", ".aqwa")
        raise ValueError with clear message if not

    locate ANSYS executable:
        check env var ANSYS_INSTALL_DIR (set by ANSYS installer on Windows)
        construct candidate: Path(ANSYS_INSTALL_DIR) / "ansys" / "bin" / "winx64" / "ansys<ver>l.exe"
        fallback: glob(C:\Program Files\ANSYS Inc\**\ansys*l.exe, recursive)
        if no candidate found: raise RuntimeError("AQWA executable not found — set ANSYS_INSTALL_DIR")

    build command: [str(aqwa_exe), str(input_path.stem)]
        # AQWA batch: pass the job-name (stem without extension); AQWA reads <stem>.dat,
        # writes <stem>.lis, <stem>.res, <stem>.tab, <stem>.plt into cwd

    run subprocess in output_dir as cwd:
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True, timeout=3600)

    check returncode:
        if result.returncode != 0:
            raise RuntimeError(f"AQWA exited {result.returncode}: {result.stderr[:500]}")

    check listing file for error markers:
        lis_path = output_dir / (input_path.stem + ".lis")
        if lis_path.exists():
            content = lis_path.read_text(errors="replace").lower()
            if any(kw in content for kw in ("error", "fatal", "abort")):
                raise RuntimeError(f"AQWA listing contains error markers — see {lis_path.name}")

    collect output files:
        output_files = []
        for suffix in (".lis", ".res", ".tab", ".plt"):
            candidate = output_dir / (input_path.stem + suffix)
            if candidate.exists():
                output_files.append(candidate.name)

    return output_files

function _locate_aqwa_exe():
    # extracted helper for testability
    install_dir = os.environ.get("ANSYS_INSTALL_DIR", "")
    if install_dir:
        for pattern in ["ansys/bin/winx64/ansys*l.exe", "ansys*/bin/winx64/ansys*l.exe"]:
            matches = list(Path(install_dir).glob(pattern))
            if matches:
                return max(matches)   # latest version by name sort
    # last-resort Windows default path probe
    default_roots = [Path("C:/Program Files/ANSYS Inc"), Path("C:/ANSYS Inc")]
    for root in default_roots:
        if root.exists():
            matches = list(root.glob("**/ansys*l.exe"))
            if matches:
                return max(matches)
    return None
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/solver/process-queue.py` | Add `run_aqwa()` + `_locate_aqwa_exe()` functions; extend dispatcher `if/elif` block at line 183 with `elif solver == "aqwa":` branch |
| Modify | `scripts/solver/submit-job.sh` | Extend validation guard at line 13 to allow `aqwa` in addition to `orcawave` and `orcaflex` |
| Modify | `scripts/solver/validate_manifest.py` | Add `"aqwa"` to `VALID_SOLVER_TYPES` set at line 40 |
| Modify | `queue/job-schema.yaml` | Add `aqwa` to the `solver` enum string; add `target_machine` as optional field with values `licensed-win-1 \| licensed-win-2` |
| Modify | `scripts/solver/README.md` | Add AQWA to the solver list in the Architecture section; add `target_machine` field to the Job YAML Format section |
| Create | `tests/solver/test_aqwa_adapter.py` | Full pytest test suite for `run_aqwa()`, `_locate_aqwa_exe()`, schema extension, and submit-job guard |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_run_aqwa_subprocess_called_with_correct_args` | subprocess is called with AQWA exe + stem arg, cwd=output_dir | mock ANSYS_INSTALL_DIR env, mock exe path, mock subprocess.run → returncode=0 | output_files list contains `.lis` stem |
| `test_run_aqwa_invalid_input_suffix_raises` | non-.dat input is rejected before subprocess call | input_path with `.owd` suffix | `ValueError` with message mentioning expected suffix |
| `test_run_aqwa_nonzero_returncode_raises` | subprocess failure is surfaced as RuntimeError | mock subprocess.run → returncode=1, stderr="license error" | `RuntimeError` containing "AQWA exited 1" |
| `test_run_aqwa_lis_error_marker_raises` | `.lis` log containing "ERROR" triggers RuntimeError even when returncode=0 | returncode=0, `.lis` file with "** ERROR" line | `RuntimeError` containing "error markers" |
| `test_run_aqwa_collects_all_output_files` | all four output files (.lis, .res, .tab, .plt) when present are returned | mock subprocess.run → returncode=0, create all four files in tmp output_dir | list of four filenames in any order |
| `test_run_aqwa_partial_output_files_ok` | partial output (only .lis, .res) does not raise | only .lis and .res created | list of two filenames, no exception |
| `test_run_aqwa_missing_exe_raises` | missing ANSYS install with no env var raises RuntimeError | no ANSYS_INSTALL_DIR, no default path | `RuntimeError` containing "not found — set ANSYS_INSTALL_DIR" |
| `test_locate_aqwa_exe_uses_env_var` | `_locate_aqwa_exe()` returns path from ANSYS_INSTALL_DIR env | mock ANSYS_INSTALL_DIR pointing to tmp dir with fake exe | Path object matching the fake exe |
| `test_locate_aqwa_exe_returns_none_if_missing` | `_locate_aqwa_exe()` returns None when nothing found | no env var, no default paths | `None` |
| `test_validate_manifest_accepts_aqwa_solver_type` | `validate_manifest.py` no longer rejects `aqwa` | manifest with `solver_type: aqwa` | `ValidationResult.valid == True` |
| `test_validate_manifest_still_rejects_unknown_solver` | non-`{orcawave,orcaflex,aqwa}` still raises | manifest with `solver_type: abaqus` | `ValueError` or `ValidationResult.valid == False` |
| `test_submit_job_sh_accepts_aqwa` | `submit-job.sh` no longer exits 1 for `aqwa` | dry invocation: `bash submit-job.sh aqwa /nonexistent/model.dat` (will fail at file-check step, NOT at solver-check step) | exit 1 with "input file not found", NOT "solver must be" |
| `test_process_job_dispatches_aqwa` | `process_job()` routes `solver=aqwa` to `run_aqwa()`, not `raise ValueError` | mock job YAML with `solver: aqwa`, mock `run_aqwa` | `run_aqwa` called once; `run_orcawave` and `run_orcaflex` not called |
| `test_job_schema_target_machine_optional` | `target_machine` field is optional in schema; omitting it does not raise | manifest without `target_machine` | validation passes |
| `test_job_schema_target_machine_invalid_value_warns` | unrecognised `target_machine` value produces a warning (not error) | manifest with `target_machine: gali-linux-compute-1` | `ValidationResult.warnings` non-empty |

---

## Acceptance Criteria

- [ ] All new tests will pass: `uv run pytest tests/solver/test_aqwa_adapter.py -v`
- [ ] Manifest validator will accept `aqwa`: `uv run pytest tests/solver/test_manifest_validator.py -v`
- [ ] Batch submission tests will pass with updated allowlist: `uv run pytest tests/solver/test_batch_submission.py -v`
- [ ] No regression in full solver suite: `uv run pytest tests/solver/ -v`
- [ ] `bash scripts/solver/submit-job.sh aqwa nonexistent.dat` will exit 1 with "input file not found" (not "solver must be"), confirming the solver-guard was updated
- [ ] `grep "aqwa" queue/job-schema.yaml` will match at least two lines (solver enum + target_machine section)
- [ ] `scripts/solver/README.md` will mention AQWA in both the Architecture and the Job YAML Format sections
- [ ] No hardcoded absolute paths introduced (enforced by `scripts/enforcement/check-no-abs-paths.sh`)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review:
- (none yet — review has not run)

---

## Risks and Open Questions

- **Open (blocking for implementation): Which licensed Windows host holds the AQWA license?** `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §1 states licensed-win-2 is the "preferred AQWA fallback/parallel host until live probes confirm exact licenses." licensed-win-1 lists "OrcaWave/OrcaFlex/ANSYS" broadly. Exact ANSYS/AQWA install and license-server address on each host are unconfirmed. Implementation will require the user to verify and supply `ANSYS_INSTALL_DIR` and `ANSYSLMD_LICENSE_FILE` before a live AQWA job can be processed.
- **Open: ANSYS AQWA command-line invocation shape.** Archived skill `python-subprocess-pattern` (SKILLS_SUMMARY:1560) confirms subprocess is the only path. The exact executable name and argument format varies by ANSYS version (e.g., `ansys241l.exe` for v24.1 vs `ansys251l.exe` for v25.1) and install location. Plan's `_locate_aqwa_exe()` uses glob + env-var probe as the safest cross-version approach. This must be validated on-host before the first live job.
- **Open: Primary vs secondary output artifacts.** AQWA produces `.lis` (text listing/log — always), `.res` (binary results), `.tab` (tabular output), `.plt` (plot data). Plan treats all four as collected if present, with `.lis` as the success-indicator file. The RAO pipeline downstream (digitalmodel AQWA module) consumes `.lis` and `.res`. If `.plt` and `.tab` are not needed for the immediate pipeline, they can be deprioritised or excluded from `output_files` in a follow-up.
- **Risk: `export_excel` parameter is accepted but not implemented for AQWA.** OrcaWave and OrcaFlex have xlsx exporters; AQWA does not (no Python API, no built-in XLSX emitter). `run_aqwa()` will accept `export_excel` for interface parity but will log a warning and skip if `True`. A follow-up issue should wire `export_excel=True` to a post-processing step that parses `.tab` into an xlsx.
- **Risk: 60-minute subprocess timeout may be insufficient for large AQWA models.** Diffraction analyses with fine-mesh hulls can exceed 2h. Plan sets a 3600s timeout as a starting point with a comment to make it configurable via an optional `timeout_seconds` job field.
- **Risk: `test_batch_submission.py:132` local helper `parse_batch_manifest` hardcodes `("orcawave", "orcaflex")`.** This helper is defined inside the test file (not imported from `validate_manifest.py`) and must be updated separately. If missed, the batch submission test for `aqwa` will fail even after the validator is updated.
- **Risk: ANSYS license server environment variable must be set in the Windows Task Scheduler task's environment.** If `ANSYSLMD_LICENSE_FILE` is not set in the scheduled task context, AQWA will silently use the wrong license server or fail. The `setup-scheduler.ps1` will need to be updated to include the env-var if/when AQWA is deployed on a licensed Windows host. This is out of scope for this plan but should be noted in the README update.

---

## Complexity: T2

**T2** — new adapter function with subprocess invocation and error handling, schema extension across four files, new test file, one existing test file updated. No new repo-level infrastructure required; follows the established `run_orcawave` / `run_orcaflex` pattern.
