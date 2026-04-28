# Blender headless baseline workflow

## Summary

This is the canonical operator-facing Blender baseline workflow for workspace-hub issue #2270. It standardizes script-first, headless Blender execution on `machine:dev-secondary` using `blender -b --factory-startup --python ...`, a procedural cube smoke scene, and structure/metadata validation before any pixel comparison.

## Baseline

- Tool/version: Blender 5.0.1, matching the current repo-local Blender skill validation baseline.
- Canonical host: dev-secondary
- Canonical invocation: `blender -b --factory-startup --python scripts/blender/smoke-render.py -- --output <output> --metadata <metadata>`
- Default verdict artifact path: `logs/engineering/blender-baseline/latest-verdict.yaml`
- Smoke scene: `cube-render`
- Output naming convention: `<scene-name>_frame-<NNNN>.png`, concretely `cube-render_frame-0001.png`

## Operator Commands

```bash
bash scripts/blender/verify-blender-baseline.sh
```

With explicit binary and output location:

```bash
BLENDER_BIN=/path/to/blender bash scripts/blender/verify-blender-baseline.sh --output-dir /tmp/blender-smoke
```

Direct smoke render:

```bash
blender -b --factory-startup --python scripts/blender/smoke-render.py -- --output /tmp/cube-render_frame-0001.png --metadata /tmp/cube-render_frame-0001.metadata.yaml
```

## YAML Verdict Contract

Required top-level fields:
- `generated_at`
- `machine`
- `blender_path`
- `version`
- `canonical_invocation`
- `overall_verdict`
- `smoke_render`
- `output_validation`

Only `generated_at` is volatile.

The validator checks these structure/metadata signals before accepting the smoke render:
- `metadata_schema_valid`
- `png_signature_valid`
- scene name equals `cube-render`
- frame equals `1`
- render engine is version-safe EEVEE: `BLENDER_EEVEE` or `BLENDER_EEVEE_NEXT`
- resolution equals `320x240`
- object list contains `Smoke_Cube` as a mesh
- camera metadata is present

## Failure modes

- Missing Blender binary: install Blender or set `BLENDER_BIN`.
- Headless display crash or segmentation fault: use `xvfb-run -a blender -b ...` or configure `DISPLAY`/EGL on the execution host.
- EEVEE enum mismatch: use the version-gated engine selection from `scripts/blender/smoke-render.py`; Blender 4.x uses `BLENDER_EEVEE_NEXT`, while 3.x and 5.x use `BLENDER_EEVEE`.
- No camera: procedural scripts must set `bpy.context.scene.camera`.
- Metadata-invalid verdict: inspect `cube-render_frame-0001.metadata.yaml`; validator acceptance is based on output structure/metadata before visual diffing.
- Output permissions: ensure the chosen `--output-dir` or render path is writable.

## CLI-Anything

CLI-Anything Blender tooling remains a convenience-only interface for interactive or experimental command wrapping. It is not required for this baseline and is not the canonical path. The durable baseline is the direct Blender CLI command above.

## Requirement traceability

| Issue #2270 requirement | Deliverable | Test / proof | Acceptance criteria |
| --- | --- | --- | --- |
| baseline doc declares headless `blender -b --python ...` as the canonical path | this workflow doc + validator | `test_workflow_doc_covers_traceable_issue_requirements` | canonical invocation documented |
| minimal reproducible scene/render workflow exists at a repo-tracked path | `scripts/blender/smoke-render.py`, manifest | `test_manifest_instructions_do_not_commit_render_outputs`, host-marked smoke test | procedural cube render path exists |
| output naming and artifact conventions are documented | this workflow doc + manifest | doc inspection test | `cube-render_frame-0001.png` convention documented |
| validator checks execution success and expected outputs | `scripts/blender/verify-blender-baseline.sh` | fake-render contract tests and host-marked test | pass/fail YAML verdict emitted |
| common failure modes are documented | this workflow doc | doc inspection test | failure modes section exists |
| optional CLI-Anything tooling is convenience-only | this workflow doc | doc inspection test | CLI-Anything marked convenience-only |

## Acceptance Criteria

- validator emits a failure verdict for missing Blender, render failure, and metadata failure
- smoke script uses version-safe EEVEE selection at 320x240
- metadata validation is required before PASS
- docs/README and engineering checklist link the canonical baseline workflow
- shared Blender skill references the repo-tracked baseline package
