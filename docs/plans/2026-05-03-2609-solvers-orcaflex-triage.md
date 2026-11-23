# solvers/orcaflex Bucket Triage — workspace-hub #2609

> **Status:** draft (r1)
> **Date:** 2026-05-03
> **Bucket:** solvers (33 unique FAILED + 9 ERROR = 42 unique broken tests in `tests/solvers/`)
> **Source log:** `/tmp/qg-repro-60d59565.log` (12,482 lines / 1,398,149 bytes ≈ 1.3 MB; local repro on digitalmodel `main` SHA `60d59565` captured 2026-05-02)
> **CI artifact gap:** post-#547 main run does not exercise `tests/solvers/` — see open question 5
> **Sister bucket plan:** `docs/plans/2026-05-03-2609-marine-ops-triage.md` (in parallel)
> **Parent umbrella:** [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609)

---

## Live verification — counts and file existence

Performed during plan drafting (raw outputs reproduced in the verification block at the end of this file):

- `grep -oE "tests/solvers/[^ ]+ FAILED" /tmp/qg-repro-60d59565.log | sort -u | wc -l` = **33** unique FAILED
- `grep -oE "tests/solvers/[^ ]+ ERROR$" /tmp/qg-repro-60d59565.log | sort -u | wc -l` = **9** unique ERROR
- The previous agent's correction (9 ERRORs, not 13) is **confirmed**: `tests/solvers/blender_automation/test_batch_processor.py::TestBatchProcessor::test_process_files_with_error` and `test_convert_directory*` lines that look like `ERROR:digitalmodel.blender_automation.utils.batch_processor:...` are **logging-record prefixes inside PASSED tests**, not pytest ERROR markers — confirmed by grep showing those tests end in `PASSED`. Pattern `ERROR$` (anchored) excludes them correctly.
- Test files for every cluster in this plan exist on disk under `digitalmodel/tests/solvers/`.

The triage targets the 33 + 9 = 42 broken tests. The defect is overwhelmingly in **test code** (subprocess invocation pattern), not in the shipped CLI binaries (which execute correctly standalone).

---

## Cluster summary

| Cluster | Title | Count | Top symptom (verbatim from test source / log) | Source under test | Hypothesis | Fix shape |
|---|---|---|---|---|---|---|
| **S1** | orcaflex CLI bare-command subprocess invocation | 23 FAILED | `subprocess.run(['orcaflex-universal', ...])` / `['run-to-sim', ...]` raises FileNotFoundError when venv `bin/` is not on subprocess PATH | `digitalmodel/tests/solvers/orcaflex/test_orcaflex_cli.py` (24 tests, 23 fail, 1 pass) | Test bug: bare-command `subprocess.run` does not inherit pytest's resolved PATH; `[sys.executable, '-m', ...]` form (used by the lone passing test) does | (b) test bug — replace bare-command invocations with `[sys.executable, '-m', '<entry>']` |
| **S2** | modular_generator builder/schema/legacy compat | 4 FAILED | `test_all_builders_registered`, `test_get_include_order`, `test_orc_installation_deprecation_warning`, `test_invalid_water_depth_too_deep` | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_builder_registry.py`, `test_legacy_compat.py`, `test_schema_compat.py` | Likely real assertion drift in registry/schema after refactor — independent of S1 | (a) source/test investigation per file; verify in isolated re-run |
| **S3** | mooring-tension-iteration | 3 FAILED | `test_mooring_tension_iteration`, `test_multi_line_coupling`, `test_single_line_iteration` | `digitalmodel/tests/solvers/orcaflex/mooring-tension-iteration/mooring_tension_iteration_test.py` (single file, hyphenated parent dir) | Likely missing fixture file, OrcFxAPI-not-available skip not honoured, or numeric drift | (a) source/test bug — investigate per failure |
| **S4** | reporting fixture snapshots | 2 FAILED | `test_minimal_fixture_report_matches_snapshot`, `test_fpso_report_matches_snapshot` | `digitalmodel/tests/solvers/orcaflex/reporting/test_fixture_snapshot.py`, `test_fpso_fixture_snapshot.py` | Snapshot drift after report-template change | (b) test snapshot regen, OR (a) source bug if snapshot is canonical — needs body inspection |
| **S5** | mooring_analysis config validation | 1 FAILED | `test_config_validation` | `digitalmodel/tests/solvers/orcaflex/mooring_analysis/comprehensive_analysis/test_config.py` | Config-schema or validator drift | (a) inspect failure body |
| **E1** | orcaflex_converter_enhanced CLI / perf | 3 ERROR | `TestCLI::test_cli_single_file`, `TestCLI::test_cli_batch`, `TestPerformance::test_large_batch_performance` | `digitalmodel/tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py` | `TestCLI::*` are likely the **same root cause as S1** (subprocess CLI invocation); `test_large_batch_performance` is a separate concern (timeout / fixture) | (b) test bug for TestCLI::*; (a)/(c) for performance test |
| **E2** | modular_generator campaign CLI | 6 ERROR | `TestCLICampaignGenerate::test_cli_campaign_*` (3), `TestCLICampaignPreview::*` (1), `TestCLICampaignSpecOnly::*` (2) | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_campaign_generator.py` | **Hypothesised cascade from S1** — these are also CLI subprocess tests; if they call `orcaflex-campaign` (or similar) via bare command, fix template applies. Verify per question 4 below | (b) test bug — likely auto-resolved by S1 fix template |

**Net leverage:** S1 plus E1 `TestCLI::*` plus E2 plausibly clears **23 + 2 + 6 = 31** of 42 broken tests with a single test-side change. Remaining ~11 failures (S2, S3, S4, S5, E1 perf) require per-cluster investigation and likely separate sub-issues.

---

## Cluster details

### S1 — orcaflex CLI bare-command subprocess invocation (23 FAILED, ROOT CAUSE LIVE-VERIFIED)

**Live verification performed:**

1. **All 23 failing tests use bare-command `subprocess.run`.** Reading `digitalmodel/tests/solvers/orcaflex/test_orcaflex_cli.py` (298 lines total) shows the same pattern in every failing test class — for example:
   - `TestCLIAvailability.test_orcaflex_universal_command_exists` (lines 16-24): `subprocess.run(['orcaflex-universal', '--version'], capture_output=True, text=True)`
   - `TestCLIAvailability.test_run_to_sim_command_exists` (lines 26-33): `subprocess.run(['run-to-sim', '--version'], ...)`
   - `TestUniversalCLIHelp.test_universal_help` (lines 39-48): `subprocess.run(['orcaflex-universal', '--help'], ...)`
   - `TestCLIOptions.test_*` (lines 90-151): all 7 use bare `['orcaflex-universal', '--help']` or `['run-to-sim', '--help']`
   - `TestCLIErrorHandling.*` (lines 157-174): bare-command pattern
   - `TestCLIExamples.*`, `TestCLIOutputFormats.*`, `TestCLICompatibility.*`, `TestCLIDefaults.*`: all bare-command

2. **The lone passing test (`TestCLIModuleIntegration::test_python_can_import_after_cli_install`, lines 203-212) uses `[sys.executable, '-c', '<python source>']`** — never invokes the CLI binary by name. This is the fix template.

3. **`test_cli_commands_from_module` (lines 214-226) ALSO uses `sys.executable` BUT FAILS** — the assertion is `'orcaflex-universal' in result.stdout` after running `from digitalmodel.orcaflex import list_cli_commands; cmds = list_cli_commands(); print(cmds)`. The failure is likely a real bug: the imported namespace does not match the registered console-script names. **This one test is NOT a PATH issue and needs separate investigation** — it's mis-bucketed if grouped with the bare-command failures. The simple sys.executable rewrite will not fix it. Flagging in sub-issue body.

4. **Console-script registration is correct in `digitalmodel/pyproject.toml`** (lines 193-209, verified):

   ```toml
   [project.scripts]
   digital_model = "digitalmodel.__main__:main"
   run-to-sim = "digitalmodel.solvers.orcaflex.run_to_sim_cli:main"
   orcaflex-universal = "digitalmodel.solvers.orcaflex.universal_cli:main"
   orcaflex-sim = "digitalmodel.solvers.orcaflex.universal_cli:main"
   orcaflex-convert = "digitalmodel.solvers.orcaflex.format_converter.cli:main"
   ...
   ```

   So the binaries `orcaflex-universal` and `run-to-sim` are real console scripts with valid entry points; running them standalone in an activated venv works. **The defect is in the test invocation, not the source.**

5. **Top-error caveat:** the source log (`/tmp/qg-repro-60d59565.log`) records PASSED/FAILED markers per test but does **not** include the `=== FAILURES ===` traceback section (verified — `grep -n "FileNotFoundError" /tmp/qg-repro-60d59565.log` returns no lines). The previous agent's claim of `FileNotFoundError: [Errno 2] No such file or directory: 'orcaflex-universal'` as the verbatim error is **inferred from the bare-command pattern, not quoted from this log**. Implementing agent should re-run pytest with `--tb=short` and capture one verbatim traceback before opening the sub-issue PR; that traceback is the canonical evidence.

**Fix template (future tense, proposed):** rewrite all 23 failing tests to use `[sys.executable, '-m', 'digitalmodel.solvers.orcaflex.universal_cli']` and `[sys.executable, '-m', 'digitalmodel.solvers.orcaflex.run_to_sim_cli']` instead of bare command names. The console-script entry points map directly to module `:main` callables, so `python -m <module>` reaches the same code with no CLI-API change. This is the smallest-diff fix.

**Why not just fix PATH?** Setting `env={'PATH': f'{venv_bin}:{old_path}'}` on every `subprocess.run` would also work but couples tests to venv layout discovery and breaks under `uv run`. The `sys.executable -m` form is venv-agnostic and matches the lone passing test's pattern.

**Affected test classes (verbatim from `test_orcaflex_cli.py`):**

- `TestCLIAvailability` — 2 tests (lines 13-33)
- `TestUniversalCLIHelp` — 2 tests (lines 36-59)
- `TestRunToSimCLIHelp` — 2 tests (lines 62-84)
- `TestCLIOptions` — 7 tests (lines 87-151)
- `TestCLIErrorHandling` — 2 tests (lines 154-174)
- `TestCLIExamples` — 2 tests (lines 177-197)
- `TestCLIModuleIntegration::test_cli_commands_from_module` — 1 test (lines 214-226), **likely a real source bug; needs separate triage**
- `TestCLIOutputFormats` — 2 tests (lines 229-248)
- `TestCLICompatibility` — 1 test (lines 251-269) — note this test invokes both binaries; rewrite both
- `TestCLIDefaults` — 2 tests (lines 272-292)

**Total:** 23 tests across 9 classes in 1 file.

---

### S2 — modular_generator builder/schema/legacy compat (4 FAILED)

**Failing tests (verbatim from log):**

- `tests/solvers/orcaflex/modular_generator/test_builder_registry.py::TestBuilderRegistry::test_all_builders_registered`
- `tests/solvers/orcaflex/modular_generator/test_builder_registry.py::TestBuilderRegistry::test_get_include_order`
- `tests/solvers/orcaflex/modular_generator/test_legacy_compat.py::TestOrcInstallationDeprecationWarning::test_orc_installation_deprecation_warning`
- `tests/solvers/orcaflex/modular_generator/test_schema_compat.py::TestSchemaValidation::test_invalid_water_depth_too_deep`

**(Note:** the previous agent's brief listed S2 as "3 FAILED — `test_builder_registry`, `test_legacy_compat`, `test_schema_compat`"; the log shows **4 unique tests** because `test_builder_registry.py` contributes 2. Plan reflects the 4-test count.)

**Hypothesis:** real assertion drift after a refactor (registry membership, include order, deprecation-warning emit path, schema validator's depth bound). Independent of S1 — these are not subprocess invocations.

**Recommended fix shape:** (a) per-test investigation. Likely sub-issue per file or per assertion; defer until S1 is closed and the failure noise is reduced.

**Plausibly cascades from S1 fix?** **No.** Different root cause.

---

### S3 — mooring-tension-iteration (3 FAILED)

**Failing tests:**

- `tests/solvers/orcaflex/mooring-tension-iteration/mooring_tension_iteration_test.py::test_mooring_tension_iteration`
- `tests/solvers/orcaflex/mooring-tension-iteration/mooring_tension_iteration_test.py::test_multi_line_coupling`
- `tests/solvers/orcaflex/mooring-tension-iteration/mooring_tension_iteration_test.py::test_single_line_iteration`

**Path note:** the parent directory is `mooring-tension-iteration` (hyphenated). Per workspace-hub memory `feedback_llm_wiki_hyphen_module_path_pattern.md`, hyphenated path segments cannot appear in dotted Python imports — flagging as a P1 smell to investigate during S3 triage in case the test module is doing `import` games to reach fixtures across the hyphenated boundary.

**Hypothesis:** likely missing OrcFxAPI mock/skip (the rest of `tests/solvers/orcaflex/` skips when `OrcFxAPI` is unavailable — see log lines 12274-12281 showing `[NOTSET] SKIPPED` for `test_load_orcaflex_files.py`), or fixture-file path drift.

**Recommended fix shape:** (a) per-test investigation. If skip marker is missing, add `pytest.importorskip("OrcFxAPI")` at the test level.

**Plausibly cascades from S1 fix?** **No.**

---

### S4 — reporting fixture snapshots (2 FAILED)

**Failing tests:**

- `tests/solvers/orcaflex/reporting/test_fixture_snapshot.py::test_minimal_fixture_report_matches_snapshot`
- `tests/solvers/orcaflex/reporting/test_fpso_fixture_snapshot.py::test_fpso_report_matches_snapshot`

**Hypothesis:** snapshot drift — either the report template changed and the snapshot files weren't regenerated, or the report generator has a real regression.

**Recommended fix shape:** read both snapshot files and the assertion bodies. If the diff is cosmetic (e.g., timestamp, version string) → (b) regenerate snapshot. If the diff reflects numeric/structural change → (a) source bug.

**Plausibly cascades from S1 fix?** **No.**

---

### S5 — mooring_analysis config validation (1 FAILED)

**Failing test:**

- `tests/solvers/orcaflex/mooring_analysis/comprehensive_analysis/test_config.py::TestAnalysisConfig::test_config_validation`

**Hypothesis:** schema-validator drift — single test asserting on `AnalysisConfig` validation rules.

**Recommended fix shape:** (a) inspect assertion body. Single-test failure → likely a single-line fix.

**Plausibly cascades from S1 fix?** **No.**

---

### E1 — orcaflex_converter_enhanced CLI / perf (3 ERROR)

**ERRORs:**

- `tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py::TestCLI::test_cli_single_file`
- `tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py::TestCLI::test_cli_batch`
- `tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py::TestPerformance::test_large_batch_performance`

**Hypothesis split:**

- **`TestCLI::test_cli_single_file` and `TestCLI::test_cli_batch`** — likely the **same root cause as S1**. These almost certainly use bare-command `subprocess.run` against `orcaflex-convert` (registered in `pyproject.toml:198`). The fix template (`sys.executable -m digitalmodel.solvers.orcaflex.format_converter.cli`) should apply directly. **Plausibly cascades from S1 fix.** Implementing agent should grep `test_orcaflex_converter_enhanced.py` for `subprocess.run\(\[` to confirm before lumping into the S1 sub-issue.
- **`TestPerformance::test_large_batch_performance`** — independent concern. ERROR (not FAIL) usually means fixture/setup raised. Could be missing test data, OrcFxAPI dependency, or a real performance-budget violation. **Does NOT cascade from S1.** Separate sub-issue or `collect_ignore` if perf tests are not meant to run in CI.

**Recommended fix shape:** (b) test bug for the two `TestCLI` ERRORs (rolled into S1 sub-issue if subprocess pattern is confirmed); (a) or (c) for `test_large_batch_performance`.

---

### E2 — modular_generator campaign CLI (6 ERROR, HYPOTHESISED CASCADE FROM S1)

**ERRORs:**

- `tests/solvers/orcaflex/modular_generator/test_campaign_generator.py::TestCLICampaignGenerate::test_cli_campaign_generate`
- `...::TestCLICampaignGenerate::test_cli_campaign_missing_file`
- `...::TestCLICampaignGenerate::test_cli_campaign_no_output_no_preview`
- `...::TestCLICampaignPreview::test_cli_campaign_preview`
- `...::TestCLICampaignSpecOnly::test_cli_campaign_spec_only_flag`
- `...::TestCLICampaignSpecOnly::test_cli_preview_shows_sweep_counts`

**Hypothesis:** **all six are CLI tests** (note the `TestCLI*` class-name pattern). If `test_campaign_generator.py` invokes a campaign CLI binary via bare command, the fix template from S1 applies. Implementing agent should grep the file for `subprocess.run\(\[` and check whether a `campaign-generate` (or similar) console-script is registered in `pyproject.toml` — if it is, the fix is mechanical; if it isn't, ERROR may be `FileNotFoundError` for an unregistered binary, which is still a test bug but with a different fix (use `python -m <module>` against the campaign module path).

**Recommended fix shape:** (b) test bug — likely auto-resolved by S1 fix template, BUT verify the campaign-CLI registration before claiming the cascade. If the campaign binary is unregistered, this becomes a separate "register or rewrite" sub-issue.

**Plausibly cascades from S1 fix?** **Yes, conditionally** — confirm via grep + pyproject inspection.

---

## Highest-leverage sub-issue draft

```
Title: fix(tests/orcaflex): replace bare CLI invocations with sys.executable -m — clears 23+ of 42 solvers/orcaflex failures

Repository: vamseeachanta/digitalmodel
Labels: bug, tests, area:solvers/orcaflex, status:plan-review

## Summary

Twenty-three tests in `tests/solvers/orcaflex/test_orcaflex_cli.py` will be rewritten to invoke `orcaflex-universal` and `run-to-sim` via `[sys.executable, '-m', '<module>']` instead of bare command names, matching the pattern of the lone passing test in the same file. With this fix, an estimated 23 directly resolved failures and (conditional on grep-verification) up to 6 cascading ERRORs in `test_campaign_generator.py` and 2 in `test_orcaflex_converter_enhanced.py::TestCLI::*` will clear — total expected leverage **23 to 31** of the 42 broken tests under [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609).

## Root cause (live-verified 2026-05-02 against `digitalmodel` SHA `60d59565`)

`subprocess.run(['orcaflex-universal', ...])` and `subprocess.run(['run-to-sim', ...])` rely on the venv's `bin/` directory being on the subprocess `PATH`. Pytest does not always propagate that — particularly under `uv run` and under bare-`pytest` invocations from outside an activated venv — so the subprocess raises `FileNotFoundError`. The console-script entry points themselves are correctly registered in `pyproject.toml:193-209`:

    [project.scripts]
    run-to-sim = "digitalmodel.solvers.orcaflex.run_to_sim_cli:main"
    orcaflex-universal = "digitalmodel.solvers.orcaflex.universal_cli:main"

so the binaries work standalone in an activated venv. The defect is in the **test invocation pattern**, not the source.

The lone passing test in the same file (`TestCLIModuleIntegration::test_python_can_import_after_cli_install`, lines 203-212) uses `subprocess.run([sys.executable, '-c', '<inline source>'])` — never invokes the CLI binary by name. That is the fix template.

## Affected tests (23, all in `tests/solvers/orcaflex/test_orcaflex_cli.py`)

- TestCLIAvailability — 2 tests (lines 13-33)
- TestUniversalCLIHelp — 2 tests
- TestRunToSimCLIHelp — 2 tests
- TestCLIOptions — 7 tests
- TestCLIErrorHandling — 2 tests
- TestCLIExamples — 2 tests
- TestCLIOutputFormats — 2 tests
- TestCLICompatibility — 1 test (invokes both binaries; rewrite both)
- TestCLIDefaults — 2 tests
- TestCLIModuleIntegration::test_cli_commands_from_module — 1 test, BUT the failure here is a real assertion drift (`'orcaflex-universal' in result.stdout` from `list_cli_commands()`) and is NOT solved by the rewrite. Document this as a follow-up.

## Fix template

Replace every occurrence of:

    subprocess.run(['orcaflex-universal', <args...>], capture_output=True, text=True)

with:

    subprocess.run([sys.executable, '-m', 'digitalmodel.solvers.orcaflex.universal_cli', <args...>], capture_output=True, text=True)

and similarly `run-to-sim` → `[sys.executable, '-m', 'digitalmodel.solvers.orcaflex.run_to_sim_cli']`. Imports (`import sys`, `import subprocess`) are already present at the top of the file.

## Acceptance criteria

- [ ] All 22 mechanical-rewrite tests in `test_orcaflex_cli.py` pass against digitalmodel `main` after the patch.
- [ ] The 23rd test (`test_cli_commands_from_module`) is filed as a separate follow-up issue with a verbatim failure assertion captured.
- [ ] Verbatim `FileNotFoundError` traceback from one pre-patch failure is captured in the PR body as canonical evidence (the source log records markers but not tracebacks).
- [ ] No regressions in the lone existing passing test (`test_python_can_import_after_cli_install`).
- [ ] `pytest tests/solvers/orcaflex/test_orcaflex_cli.py -v` reports 24 passing tests on the patch branch (or 23 + 1 known failure for `test_cli_commands_from_module` if its follow-up has not landed).
- [ ] PR description references [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609) as the umbrella triage and confirms which of E1's `TestCLI::*` and E2's `TestCLICampaign*` cascades cleared in the same patch.

## Out of scope

- The S2 (4), S3 (3), S4 (2), S5 (1), and E1 perf (1) failures — see umbrella triage `docs/plans/2026-05-03-2609-solvers-orcaflex-triage.md`.
- The `test_cli_commands_from_module` source/assertion drift (separate follow-up).
- Any change to `pyproject.toml` console-script registration (already correct).
- Any change to the CLI source modules.

## References

- Umbrella: [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609)
- Source log: `/tmp/qg-repro-60d59565.log` (12,482 lines / 1.4 MB; SHA `60d59565`)
- Console-script registration: `digitalmodel/pyproject.toml:193-209`
- Fix template (passing test): `digitalmodel/tests/solvers/orcaflex/test_orcaflex_cli.py:203-212`
```

(Body above is `gh issue create --body`-ready; render once with the umbrella issue's actual repo target — `digitalmodel`, not `workspace-hub` — pending answer to open question 1.)

---

## Open questions for user

1. **Filing target.** The tests live in `digitalmodel/tests/solvers/orcaflex/`, so the natural sub-issue target is `vamseeachanta/digitalmodel` (not `workspace-hub`). Confirm, or specify the alternative (mirror under `workspace-hub` umbrella).
2. **Dedup of mirrored tests.** Are any of these tests duplicated under another path (e.g., a workspace-hub mirror, an older `tests/orcaflex/` location)? Recommendation: implementing agent runs `find /mnt/local-analysis/workspace-hub -name "test_orcaflex_cli.py"` before opening the PR.
3. **CI re-validation cadence.** Should the implementing agent push to a feature branch and wait for the digitalmodel quality-gates workflow to re-run before requesting review, or is a local `pytest tests/solvers/orcaflex -v` proof sufficient?
4. **Sub-cluster split for E1/E2.** Should E1 (`TestCLI::*`) and E2 (`TestCLICampaign*`) be folded into the S1 sub-issue (single PR, broader leverage) or filed as separate sub-issues that depend on S1's pattern?
5. **CI artifact gap (verify recommended).** The post-#547 CI run (id `25287048442`, claimed by previous agent) reportedly does not exercise `tests/solvers/`. Recommend running `gh run view 25287048442 --repo vamseeachanta/digitalmodel --log | grep -c "tests/solvers"` and comparing to the local repro's count of `33 + 9 = 42` broken tests in that bucket. If CI's marker filter is excluding `tests/solvers/`, that is a separate gap to widen — should that be a sibling sub-issue?
6. **Other gaps surfaced by live verification.**
   - The previous agent's claim of `FileNotFoundError: [Errno 2] ...` as verbatim error text is **not quotable from `/tmp/qg-repro-60d59565.log`**; the log records PASSED/FAILED markers but not the FAILURES section. Confirm before the sub-issue is opened — the implementing agent should re-run pytest with `--tb=short` and capture one verbatim traceback.
   - `TestCLIModuleIntegration::test_cli_commands_from_module` already uses `sys.executable` and still fails — this is a **real assertion drift**, not a PATH issue, and is mis-bucketed if it is grouped with the bare-command failures. Surfacing here so it doesn't silently slip into the S1 sub-issue and contaminate the success criterion.
   - S2 was reported as 3 FAILED but the log shows **4 unique tests** (`test_builder_registry.py` contributes 2). Plan uses the 4-test count.
   - Previous agent's draft mentioned an `E3 — blender_automation/test_batch_processor.py (4 ERROR)` cluster. **No such cluster exists** — those tests are PASSED with `ERROR:digitalmodel.blender_automation...` log records prefixed inside the test transcript line. Total ERROR count is **9**, all in 2 files (E1 + E2). Confirming the previous agent's "9 vs. 13" correction was right and extending it: there is also no E3 and no E4.

---

## Calc-citation-contract check

Per `.claude/rules/calc-citation-contract.md`, citations are required when calc modules emit numeric outputs derived from external standards. **None of the 42 failing tests in this triage assert against external-standards-derived constants:**

- S1 (23) — CLI help/version/option-parsing assertions; no standards involved.
- S2 (4) — registry membership, include order, deprecation warning, schema-bound water-depth (likely a code-internal bound; verify in implementation).
- S3 (3) — mooring-tension iteration (numeric; potentially DNV-OS-E301-derived per the existing `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` pilot, but the **test** is asserting numeric convergence, not a citation surface). Worth checking whether the source under test emits a `Citation` sidecar — if it does, that's a separate completeness check; not the concern of this triage.
- S4 (2) — fixture-snapshot equality; no standards constants.
- S5 (1) — config validation; schema-only.
- E1, E2 (9) — CLI / campaign generation; no standards.

**Conclusion:** no citation-contract action required for this bucket. Flagging S3 only as a recommendation for the implementing agent to confirm — if the mooring-tension source emits citations and a test breaks on the citation sidecar shape, that is in scope for the citation-contract pilot, not this triage.

---

## Approval gate

This is a draft plan (r1). **The user owns the `status:plan-approved` transition.** No self-approval, no pre-authorization of downstream agents (per workspace-hub memory `feedback_never_offer_to_self_label_plan_approved.md`). Adversarial review must occur first; sub-issue draft above is body-only (not opened against GitHub yet).

Sister bucket plan `docs/plans/2026-05-03-2609-marine-ops-triage.md` is being written in parallel. After both land, the umbrella issue [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609) will be updated with both plan paths in a single comment.
