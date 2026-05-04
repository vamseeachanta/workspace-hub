# Blender headless baseline workflow

> Issue: #2270  
> Canonical machine: dev-secondary  
> Verdict path: `logs/engineering/blender-baseline/latest-verdict.yaml`

## Purpose

This workflow standardizes the repeatable Blender headless smoke path used by engineering agents before relying on Blender for visualization or post-processing tasks.

## Canonical command

```bash
scripts/blender/verify-blender-baseline.sh \
  --verdict logs/engineering/blender-baseline/latest-verdict.yaml
```

The validator resolves `BLENDER_BIN` (default `blender`), probes `blender --version`, and runs:

```bash
blender -b --python scripts/blender/smoke-render.py -- --output /tmp/blender-baseline-smoke/smoke-render.png
```

## Expected evidence

A passing run writes a YAML verdict containing:

- `tool: blender`
- `overall_verdict: PASS`
- `version: <major.minor.patch>`
- `smoke_case: cube-render`
- `verification_method: blender -b --python scripts/blender/smoke-render.py`
- `render_output: .../smoke-render.png`

The PNG is runtime evidence and is not committed.

## Output naming and artifact conventions

Use deterministic render artifact names so smoke outputs can be compared across hosts without depending on GUI state:

- Scene/frame renders: `<scene-name>_frame-<NNNN>.png` (for example, `cube-render_frame-0001.png`).
- Validator smoke output: `smoke-render.png` under a runtime directory or the operator-provided report path.
- Verdict evidence: YAML under `logs/engineering/blender-baseline/` or a caller-provided `--verdict` path.
- Do not commit generated PNGs; commit only scripts, manifests, docs, and test fixtures.

## CLI-Anything note

CLI-Anything Blender tooling is a convenience-only operator aid for interactive experimentation. It is not required for the canonical baseline, and a portable acceptance run must still pass the raw `blender -b --python ...` validator path above.

## Failure modes

- `missing-blender`: no executable Blender binary was found. Set `BLENDER_BIN` or run on dev-secondary.
- `render-failure`: Blender launched but the cube render failed. Inspect stderr and GPU/headless display availability.
- `missing-render-output`: Blender exited zero but did not create a non-empty PNG.

## Notes

The repo-side tests use injected fake Blender binaries so CI can verify the wrapper contract without requiring Blender on every host. A live PASS still requires running the validator on a host with Blender installed, normally dev-secondary.
