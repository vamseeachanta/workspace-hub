# Plan for #2272: add repeatable OpenFOAM and Blender smoke verification

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2272
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2272-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/openfoam/run-openfoam-tutorials.sh` — existing headless OpenFOAM tutorial runner; runs cavity + damBreak, writes YAML verdict with per-tutorial pass/fail. This is the execution engine that the OpenFOAM baseline validator (#2269) will wrap.
- Found: `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` — sibling plan for OpenFOAM baseline. Defines `scripts/openfoam/verify-openfoam-baseline.sh` as the operator-facing validator wrapper with YAML verdict output. This plan (#2272) depends on #2269 being implemented first so it can invoke the validator.
- Found: `docs/plans/2026-04-16-issue-2270-blender-headless-baseline-workflow-and-smoke-render-validation.md` — sibling plan for Blender baseline. Defines `scripts/blender/verify-blender-baseline.sh` as the operator-facing validator wrapper. This plan (#2272) depends on #2270 being implemented first so it can invoke the validator.
- Found: `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks OpenFOAM v2312 and Blender headless as baselines on dev-secondary. The smoke verification in this issue must verify these baselines.
- Found: `docs/engineering/portability/MACHINE_ROLES.md` — confirms dev-secondary is the canonical execution host where both tools are installed.
- Found: `config/workstations/registry.yaml` line 50 — confirms both `blender` and `openfoam` in the dev-secondary tool list.
- Found: `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` — validation cases are item 3 in the minimum artifact bundle.
- Gap: no unified smoke verification runner exists that spans both OpenFOAM and Blender.
- Gap: no drift detection mechanism exists for engineering tool baselines.
- Gap: no `tests/portability/` or equivalent cross-tool test directory exists.

### Standards
| Standard | Status | Source |
|---|---|---|
| OpenFOAM v2312 baseline | plan exists (plan-review) | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` |
| Blender headless baseline | plan exists (draft) | `docs/plans/2026-04-16-issue-2270-blender-headless-baseline-workflow-and-smoke-render-validation.md` |
| Engineering delivery minimum bundle | done | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — confirms OpenFOAM capability model including validation against tutorial benchmarks.
- No Blender wiki page found — gap noted in #2270 plan.

### Documents consulted
- GitHub issue #2272 — defines acceptance criteria for repeatable smoke verification across OpenFOAM and Blender.
- GitHub issue #2269 — OpenFOAM baseline (dependency); plan at `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`.
- GitHub issue #2270 — Blender baseline (dependency); plan at `docs/plans/2026-04-16-issue-2270-blender-headless-baseline-workflow-and-smoke-render-validation.md`.
- GitHub issue #1782 — parent epic (zero-loss agent learnings).
- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — canonical baselines for both tools.
- `docs/research/cli-anything-blender-openfoam-eval.md` — landscape of headless automation for both tools.
- `.claude/rules/patterns.md` — enforcement gradient; smoke verification aligns with Level 2 (script).

### Gaps identified
- No unified smoke verification runner spans both OpenFOAM and Blender — each tool has (or will have per #2269/#2270) its own validator, but no aggregator exists.
- No drift detection mechanism exists — re-running verification is possible but not automated or scheduled.
- No cross-tool verification report format exists — each validator produces its own YAML but there is no consolidated machine-readable + human-readable output.
- This issue is blocked until #2269 and #2270 produce the per-tool validators that this issue aggregates.

<!-- Verification: distinct sources >= 3. Current count: 9 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-16-issue-2272-repeatable-openfoam-and-blender-smoke-verification.md` |
| Unified smoke verification runner | `scripts/portability/verify-engineering-baselines.sh` |
| Verification report doc | `docs/engineering/portability/smoke-verification-guide.md` |
| Test harness | `tests/portability/test_smoke_verification.py` |
| Plan review — Claude | `scripts/review/results/2026-04-16-plan-2272-claude-overnight.md` |

---

## Deliverable

A unified smoke verification runner that invokes per-tool baseline validators (OpenFOAM and Blender) from a single entry point, produces a consolidated machine-readable and human-readable report, documents expected outputs and common failure categories, and can be re-run to detect drift from established baselines.

---

## Pseudocode

```text
# --- verify-engineering-baselines.sh (unified runner) ---

parse arguments:
    --tool <openfoam|blender|all>  (default: all)
    --report-dir <path>            (default: logs/engineering/smoke-verification/)
    --json                         (emit JSON summary to stdout)
    --help

create report directory if missing

results = []

if tool == "all" or tool == "openfoam":
    openfoam_verdict_path = <report-dir>/openfoam-verdict.yaml
    invoke scripts/openfoam/verify-openfoam-baseline.sh --verdict $openfoam_verdict_path
    capture exit code
    parse openfoam verdict YAML
    append to results:
        tool: openfoam
        verdict_file: $openfoam_verdict_path
        status: PASS|FAIL
        version: <from verdict>
        error_summary: <if failed>

if tool == "all" or tool == "blender":
    blender_verdict_path = <report-dir>/blender-verdict.yaml
    invoke scripts/blender/verify-blender-baseline.sh --verdict $blender_verdict_path
    capture exit code
    parse blender verdict YAML
    append to results:
        tool: blender
        verdict_file: $blender_verdict_path
        status: PASS|FAIL
        version: <from verdict>
        error_summary: <if failed>

generate consolidated report:
    machine-readable (YAML):
        path: <report-dir>/consolidated-verdict.yaml
        schema:
            generated_at: <timestamp>
            machine: <hostname>
            overall_verdict: PASS|FAIL (FAIL if any tool fails)
            tools:
                - name: openfoam
                  status: PASS|FAIL|SKIPPED
                  version: <detected>
                  verdict_file: <path>
                  error_summary: <if failed>
                - name: blender
                  status: PASS|FAIL|SKIPPED
                  version: <detected>
                  verdict_file: <path>
                  error_summary: <if failed>
    human-readable (terminal):
        print summary table:
            Tool      | Status | Version  | Verdict File
            openfoam  | PASS   | v2312    | <path>
            blender   | PASS   | 4.x      | <path>
        print overall verdict line
        if any failures: print failure details with line references

    if --json flag: also emit JSON summary to stdout

exit code:
    0 if overall_verdict == PASS
    1 if any tool FAIL
    2 if runner itself fails (missing validator script, parse error)

# --- Drift detection ---

drift detection is achieved by re-running the verification:
    compare current consolidated-verdict.yaml against a known-good reference
    if version field changes: flag as drift
    if status changes from PASS to FAIL: flag as regression
    document this re-run workflow in the guide

# --- Test harness ---

tests use fixture verdicts (YAML files) to test:
    - consolidated report generation from per-tool verdicts
    - failure propagation (one tool fails -> overall fails)
    - partial runs (--tool openfoam only)
    - drift detection logic
    - human-readable and machine-readable output correctness
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/portability/verify-engineering-baselines.sh` | unified smoke verification runner |
| Create | `docs/engineering/portability/smoke-verification-guide.md` | documents expected outputs, pass/fail criteria, common failures, drift detection |
| Create | `tests/portability/test_smoke_verification.py` | test harness for consolidated verification |
| Create | `tests/portability/fixtures/openfoam-pass-verdict.yaml` | fixture for OpenFOAM PASS scenario |
| Create | `tests/portability/fixtures/blender-pass-verdict.yaml` | fixture for Blender PASS scenario |
| Create | `tests/portability/fixtures/openfoam-fail-verdict.yaml` | fixture for OpenFOAM FAIL scenario |
| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | cross-reference smoke verification guide |
| Update | `docs/README.md` | add discoverability link to smoke verification guide |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_consolidated_report_schema_valid` | consolidated verdict YAML has required fields | fixture verdicts from both tools | YAML with generated_at, machine, overall_verdict, tools list |
| `test_overall_verdict_pass_when_all_tools_pass` | overall = PASS when both tools pass | two PASS fixture verdicts | overall_verdict = PASS, exit 0 |
| `test_overall_verdict_fail_when_any_tool_fails` | overall = FAIL when one tool fails | one PASS + one FAIL fixture | overall_verdict = FAIL, exit 1 |
| `test_partial_run_openfoam_only` | `--tool openfoam` skips Blender | `--tool openfoam` flag | blender status = SKIPPED, openfoam evaluated |
| `test_partial_run_blender_only` | `--tool blender` skips OpenFOAM | `--tool blender` flag | openfoam status = SKIPPED, blender evaluated |
| `test_human_readable_output_contains_table` | terminal output includes summary table | standard run | stdout contains tool names, statuses, versions in tabular format |
| `test_json_flag_emits_parseable_json` | `--json` produces valid JSON summary | `--json` flag | stdout is valid JSON matching consolidated schema |
| `test_missing_validator_exits_with_code_2` | runner exits 2 if per-tool validator script is missing | nonexistent validator path | exit code 2 + error message naming missing script |
| `test_drift_detection_flags_version_change` | version mismatch from reference is flagged | current verdict with different version than reference | drift warning in report |
| `test_report_dir_created_if_missing` | runner creates report directory when it does not exist | nonexistent report-dir path | directory created, verdict files written inside |

---

## Acceptance Criteria

- [ ] `scripts/portability/verify-engineering-baselines.sh` exists and invokes per-tool validators from a single entry point.
- [ ] One OpenFOAM smoke verification path exists and is documented in the guide.
- [ ] One Blender smoke verification path exists and is documented in the guide.
- [ ] Verification output is machine-readable (YAML consolidated verdict) and human-readable (terminal summary table).
- [ ] `docs/engineering/portability/smoke-verification-guide.md` explains expected outputs, pass/fail criteria, common failure categories, and drift detection workflow.
- [ ] Verification can be re-run to detect drift (documented workflow for comparing against known-good reference).
- [ ] `tests/portability/test_smoke_verification.py` exists with fixture-based tests covering report generation, failure propagation, partial runs, and drift detection.
- [ ] The unified runner exits 0 on full pass, 1 on any tool failure, and 2 on runner-level errors.
- [ ] The guide is linked from `docs/README.md`.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | overnight draft review |
| Codex | pending | not yet reviewed |
| Gemini | pending | not yet reviewed |

**Overall result:** pending

Revisions made based on review:
- (none yet — initial draft)

---

## Requirement traceability

| Issue #2272 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
|---|---|---|---|
| one OpenFOAM smoke verification path exists and documented | `scripts/portability/verify-engineering-baselines.sh`, `docs/engineering/portability/smoke-verification-guide.md` | `test_partial_run_openfoam_only`, `test_consolidated_report_schema_valid` | OpenFOAM path invoked and documented |
| one Blender smoke verification path exists and documented | same as above | `test_partial_run_blender_only`, `test_consolidated_report_schema_valid` | Blender path invoked and documented |
| verification output is machine-readable and human-readable | consolidated YAML + terminal table + optional JSON | `test_consolidated_report_schema_valid`, `test_human_readable_output_contains_table`, `test_json_flag_emits_parseable_json` | both output formats produced |
| docs explain expected outputs, pass/fail, common failure categories | `docs/engineering/portability/smoke-verification-guide.md` | `test_consolidated_report_schema_valid` | guide covers all sections |
| verification can be re-run to detect drift | drift detection workflow in guide + comparison logic | `test_drift_detection_flags_version_change` | drift detection documented and testable |

---

## Risks and Open Questions

- **BLOCKER:** This issue depends on #2269 (OpenFOAM baseline) and #2270 (Blender baseline) completing first. The per-tool validator scripts (`verify-openfoam-baseline.sh` and `verify-blender-baseline.sh`) must exist before this unified runner can invoke them. Implementation cannot begin until both are done.
- **Risk:** If #2269 or #2270 are delayed, this issue's timeline shifts proportionally. The plan can be approved in advance but implementation is gated.
- **Risk:** The YAML verdict schemas from #2269 and #2270 may diverge; the unified runner must handle schema differences gracefully or establish a common verdict schema contract.
- **Open:** Should the drift detection be scheduled (cron) or on-demand only? Current plan keeps it on-demand; scheduled execution could be a follow-up issue.
- **Open:** Should additional tools (CalculiX, Gmsh, Capytaine) be included in the unified runner? Current scope is OpenFOAM + Blender per issue #2272 acceptance criteria. Other tools can be added incrementally.
- **Open:** Should the consolidated report be committed to git or remain as operational output under `logs/`? Current plan treats it as operational (logs), matching the pattern from #2269.

---

## Dependency Graph

```
#1782 (parent epic)
  ├── #2269 (OpenFOAM baseline) ──┐
  ├── #2270 (Blender baseline) ───┼── #2272 (this: unified smoke verification)
  └── #2271 (skill propagation)   │       (blocked until #2269 and #2270 complete)
                                   └──────
```

---

## Complexity: T2

**T2** — new unified runner + documentation + test harness, but primarily orchestrating existing per-tool validators rather than creating new solver-level logic. Bounded by the two-tool scope (OpenFOAM + Blender).
