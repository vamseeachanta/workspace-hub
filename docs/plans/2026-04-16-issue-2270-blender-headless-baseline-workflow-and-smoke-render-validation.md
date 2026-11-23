# Plan for #2270: standardize headless Blender baseline workflow and smoke render validation

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2270
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2270-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/research/cli-anything-blender-openfoam-eval.md` — comprehensive evaluation of Blender headless automation approaches, confirms `blender -b --python ...` as canonical headless path, documents CLI-Anything Blender harness installation at `/mnt/local-analysis/cli-anything-env`, and recommends raw headless scripting over MCP for the baseline use case.
- Found: `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks Blender as headless baseline via `blender -b --python ...` on dev-secondary (`ace-linux-2`), issue #26 is the reference. This is the contract this plan must satisfy.
- Found: `docs/engineering/portability/MACHINE_ROLES.md` — confirms dev-secondary is the canonical engineering execution host with Blender installed; headless post-processing and visualization are expected to originate there.
- Found: `config/workstations/registry.yaml` line 50 — confirms `blender` in the dev-secondary tool list alongside openfoam, freecad, gmsh, paraview, calculix, meshio, capytaine.
- Found: `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` — defines the minimum reusable artifact bundle; Blender Python scripts are explicitly listed as applicable solver configuration templates.
- Found: `scripts/pipelines/stubs/stub_openfoam.py` — confirms the stub pattern exists for OpenFOAM; no equivalent Blender stub exists, indicating no prior pipeline integration for Blender.
- Gap: no repo-tracked Blender headless baseline workflow doc exists under `docs/engineering/portability/`.
- Gap: no `scripts/blender/` directory exists; no headless Blender scripts exist anywhere in the repo.
- Gap: no smoke render validation script or example scene path exists in the repo.
- Gap: no `tests/blender/` directory exists for Blender-related test coverage.

### Standards
| Standard | Status | Source |
|---|---|---|
| Blender headless baseline (via `blender -b --python`) | declared but not documented | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
| Engineering artifact portability / machine-role policy | done | `docs/engineering/portability/MACHINE_ROLES.md` |
| External design-code implementation | not applicable | issue is tool/workflow standardization |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — engineering wiki exists for OpenFOAM but no equivalent Blender wiki page was found, confirming a gap in Blender domain knowledge documentation.

### Documents consulted
- GitHub issue #2270 — defines acceptance criteria for Blender headless baseline workflow and smoke render validation.
- GitHub issue #26 — historical Blender configs issue; referenced by PORTABILITY_CONTRACT.md as the Blender baseline reference.
- GitHub issue #1782 — parent epic (zero-loss agent learnings) that drives portability work.
- GitHub issue #1475 — CLI-Anything evaluation (`docs/research/cli-anything-blender-openfoam-eval.md`) documenting Blender headless automation landscape.
- `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` — sibling plan for OpenFOAM baseline; this plan mirrors the structure and delivery pattern established there (baseline doc + validator wrapper + smoke manifest + test harness).
- `docs/document-intelligence/data-intelligence-map.md` — entry points for engineering registries confirmed.

### Gaps identified
- No Blender headless scripts exist in the repo (`scripts/blender/` does not exist).
- No smoke render example or reproducible scene exists under `examples/blender/`.
- No baseline workflow doc exists for Blender under `docs/engineering/portability/`.
- No test harness exists for Blender validation (`tests/blender/` does not exist).
- No Blender version pin is documented anywhere (only "headless via `blender -b --python ...`" in PORTABILITY_CONTRACT.md).
- CLI-Anything Blender CLI is installed but is convenience tooling, not the canonical baseline path.

<!-- Verification: distinct sources >= 3. Current count: 8 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-16-issue-2270-blender-headless-baseline-workflow-and-smoke-render-validation.md` |
| Canonical baseline workflow doc | `docs/engineering/portability/blender-headless-baseline-workflow.md` |
| Baseline validator wrapper | `scripts/blender/verify-blender-baseline.sh` |
| Minimal headless render script | `scripts/blender/smoke-render.py` |
| Smoke example manifest | `examples/blender/cube-render/README.md` |
| Test harness | `tests/blender/test_verify_blender_baseline.py` |
| Engineering delivery contract | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` |
| Plan review — Claude | `scripts/review/results/2026-04-16-plan-2270-claude-overnight.md` |

---

## Deliverable

A repo-tracked Blender headless baseline package for dev-secondary that pins the canonical Blender version, documents the exact `blender -b --python ...` workflow and failure modes, provides a repo-tracked smoke render manifest with a minimal reproducible scene/render workflow, and exposes a deterministic validator wrapper that emits explicit pass/fail YAML evidence.

---

## Pseudocode

```text
inspect existing Blender research notes, issue #2270 acceptance criteria, PORTABILITY_CONTRACT.md, and ENGINEERING_DELIVERY_CHECKLIST.md
lock the canonical baseline:
    machine = dev-secondary
    tool = Blender
    invocation = blender -b --python <script.py>
    version = detect and pin installed version (e.g., 4.x)
    mandatory smoke case = cube-render (default cube, single frame, PNG output)
    default verdict path = logs/engineering/blender-baseline/latest-verdict.yaml

verify-blender-baseline.sh:
    check blender binary exists on PATH or at known install paths:
        BLENDER_BIN override (test-only dependency-injection)
        otherwise: `blender` on PATH
        if not found: exit non-zero with explicit missing-blender error
    probe version via `blender --version`:
        parse major.minor.patch from stdout
        record in verdict as version field
        if version < minimum supported (4.0): warn but proceed
    run smoke render:
        invoke: blender -b --python scripts/blender/smoke-render.py -- --output <temp_dir>/smoke-render.png
        check exit code from blender
        check that output PNG file exists and has non-zero size
    emit YAML verdict:
        default path = logs/engineering/blender-baseline/latest-verdict.yaml
        create parent directory if missing
        required fields: generated_at, machine, blender_path, version, overall_verdict, smoke_render (status, output_file, file_size_bytes)
        optional override via --verdict flag
    failure artifact policy:
        still write verdict on failure with overall_verdict=FAIL and error_summary

smoke-render.py (bpy script):
    import bpy, sys, argparse
    parse --output argument from sys.argv (after --)
    reset scene to factory defaults
    ensure default cube exists (bpy.ops.mesh.primitive_cube_add if missing)
    set render engine to EEVEE (fast, no GPU required)
    set render resolution to 320x240 (minimal smoke check)
    set output format to PNG
    set filepath to output argument
    render: bpy.ops.render.render(write_still=True)
    print confirmation to stdout for validator to capture
    exit with code 0 on success

write baseline workflow doc:
    supported tool/version
    binary discovery path and --version verification
    mandatory smoke render case
    exact YAML verdict schema and default artifact location
    output naming conventions (scene-name_frame-NNNN.png)
    failure modes and troubleshooting guidance
    CLI-Anything documented as convenience-only alternative

create smoke example manifest:
    required headings: Overview, Prerequisites, Commands, Expected Outputs, Failure Modes
    document: blender -b --python scripts/blender/smoke-render.py -- --output /tmp/test.png
    do not commit rendered PNG outputs into git
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/engineering/portability/blender-headless-baseline-workflow.md` | canonical operator-facing baseline workflow doc |
| Create | `scripts/blender/verify-blender-baseline.sh` | operator-facing wrapper that verifies Blender install and runs smoke render |
| Create | `scripts/blender/smoke-render.py` | minimal bpy script for headless cube render |
| Create | `examples/blender/cube-render/README.md` | repo-tracked smoke-case manifest/example with exact commands |
| Create | `tests/blender/test_verify_blender_baseline.py` | behavioral pytest harness for validator contract |
| Update | `docs/engineering/portability/PORTABILITY_CONTRACT.md` | pin exact Blender version after live verification |
| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | add cross-reference from Blender baseline package |
| Update | `docs/README.md` | add discoverability link to Blender baseline workflow |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_verify_script_succeeds_and_emits_schema_valid_verdict` | validator succeeds in a supported environment and writes schema-valid YAML | supported dev-secondary with Blender installed | exit 0 + YAML with required fields: generated_at, machine, blender_path, version, overall_verdict=PASS, smoke_render |
| `test_verify_script_fails_when_blender_missing` | validator fails with explicit missing-blender error | `BLENDER_BIN` points to nonexistent path | non-zero exit + explicit missing-blender message |
| `test_verify_script_checks_output_file_exists` | validator confirms rendered PNG exists and has non-zero size | successful smoke render | verdict smoke_render.status=PASS, file_size_bytes > 0 |
| `test_verify_script_emits_failure_verdict_on_render_error` | validator still writes a failure verdict when render fails | broken bpy script or missing display | verdict with overall_verdict=FAIL and error_summary |
| `test_smoke_render_script_produces_png` | bpy script creates a valid PNG at specified output path | `blender -b --python smoke-render.py -- --output /tmp/test.png` | PNG file exists at /tmp/test.png with non-zero size |
| `test_smoke_render_script_uses_eevee_and_minimal_resolution` | bpy script uses EEVEE engine at 320x240 | script source inspection or render metadata | render engine=EEVEE, resolution=320x240 |
| `test_manifest_instructions_do_not_commit_render_outputs` | smoke manifest is documentation-only, no rendered images committed | repo tree | `examples/blender/cube-render/README.md` present, no PNG/JPG files under example path |
| `test_workflow_doc_covers_issue_requirements` | workflow doc cross-references issue #2270 requirements | workflow doc text | traceability table covering all acceptance criteria |
| `test_verdict_schema_only_generated_at_is_volatile` | YAML verdict is deterministic except for timestamp | two consecutive runs in same environment | all fields identical except generated_at |

---

## Acceptance Criteria

- [ ] `docs/engineering/portability/blender-headless-baseline-workflow.md` declares `blender -b --python ...` as canonical headless path, pins detected version, documents output naming conventions, and lists failure modes.
- [ ] `scripts/blender/verify-blender-baseline.sh` succeeds on dev-secondary and emits schema-valid YAML verdict with required fields.
- [ ] `scripts/blender/verify-blender-baseline.sh` fails with explicit messaging when Blender is not installed.
- [ ] `scripts/blender/smoke-render.py` produces a minimal PNG via headless Blender using EEVEE at 320x240 resolution.
- [ ] `examples/blender/cube-render/README.md` exists as an instruction-only manifest with required headings; no rendered outputs committed to git.
- [ ] `tests/blender/test_verify_blender_baseline.py` exists with `@pytest.mark.blender` for host-dependent tests and fixture-only schema tests runnable anywhere.
- [ ] CLI-Anything tooling is documented as convenience-only in the workflow doc, not as the canonical path.
- [ ] Output naming convention is documented: `<scene-name>_frame-<NNNN>.png`.
- [ ] Validator produces a failure verdict artifact (not just non-zero exit) when the render fails.
- [ ] The workflow doc is linked from `docs/README.md`.
- [ ] `ENGINEERING_DELIVERY_CHECKLIST.md` is cross-referenced from the baseline package.

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

| Issue #2270 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
|---|---|---|---|
| baseline doc declares headless `blender -b --python ...` as canonical path | `docs/engineering/portability/blender-headless-baseline-workflow.md` | `test_workflow_doc_covers_issue_requirements` | workflow doc declares canonical invocation |
| minimal reproducible scene/render workflow at repo-tracked path | `scripts/blender/smoke-render.py`, `examples/blender/cube-render/README.md` | `test_smoke_render_script_produces_png`, `test_manifest_instructions_do_not_commit_render_outputs` | bpy script + manifest exist |
| output naming and artifact conventions documented | `docs/engineering/portability/blender-headless-baseline-workflow.md` | `test_workflow_doc_covers_issue_requirements` | naming convention in workflow doc |
| validator checks execution success and expected outputs | `scripts/blender/verify-blender-baseline.sh` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_checks_output_file_exists` | validator emits pass/fail YAML |
| common failure modes documented | `docs/engineering/portability/blender-headless-baseline-workflow.md` | `test_workflow_doc_covers_issue_requirements` | troubleshooting section in workflow doc |
| optional CLI-Anything tooling documented as convenience-only | `docs/engineering/portability/blender-headless-baseline-workflow.md` | `test_workflow_doc_covers_issue_requirements` | CLI-Anything section marked convenience-only |

---

## Risks and Open Questions

- **Risk:** Blender version is not pinned in PORTABILITY_CONTRACT.md — only the invocation pattern is documented. Implementation must detect and pin the actual installed version on dev-secondary.
- **Risk:** EEVEE rendering on dev-secondary may require a display server (X11/Wayland) even in headless mode on some Blender versions. Fallback to `--factory-startup` and `DISPLAY=:0` or `xvfb-run` may be needed.
- **Risk:** The NVIDIA T400 GPU on dev-secondary may affect render engine availability; implementation must verify EEVEE works headlessly and document Cycles as an alternative if EEVEE fails.
- **Open:** Should the smoke render use the default cube or a more meaningful engineering scene? Default cube keeps scope minimal and avoids committing .blend files.
- **Open:** Exact Blender version on dev-secondary is not documented — must be discovered during implementation.

---

## Complexity: T2

**T2** — new baseline documentation + validator + minimal bpy script across a small set of new files, mirroring the established OpenFOAM baseline pattern from #2269.
