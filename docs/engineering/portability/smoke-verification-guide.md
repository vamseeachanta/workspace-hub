# Engineering smoke verification guide

> Issue: #2272  
> Runner: `scripts/portability/verify-engineering-baselines.sh`

## Purpose

The unified smoke verifier runs the repo-tracked OpenFOAM and Blender baseline validators from one entry point and writes a consolidated report for drift detection.

## Commands

Run every baseline:

```bash
scripts/portability/verify-engineering-baselines.sh \
  --report-dir logs/engineering/smoke-verification
```

Run one baseline:

```bash
scripts/portability/verify-engineering-baselines.sh --tool openfoam
scripts/portability/verify-engineering-baselines.sh --tool blender
```

Emit machine-readable JSON to stdout:

```bash
scripts/portability/verify-engineering-baselines.sh --json
```

## Outputs

The runner writes per-tool verdicts plus a consolidated verdict:

- `openfoam-verdict.yaml`
- `blender-verdict.yaml`
- `consolidated-verdict.yaml`

The consolidated verdict includes `overall_verdict`, `machine`, and a `tools` list with each tool's status, version, and verdict file path.

## Pass/fail semantics and common failure categories

- `PASS`: every selected per-tool validator exited successfully and wrote a parseable verdict with `overall_verdict: PASS`.
- `FAIL`: at least one selected tool ran but reported a failed tool verdict; classify this as `tool-status-failure` and inspect that tool's `error_summary`.
- `missing-validator`: the unified runner cannot find or execute the configured OpenFOAM or Blender validator script.
- `verdict-parse-failure`: a validator ran but did not produce the expected verdict file/fields, so the runner cannot trust the result.
- Environment failures such as missing OpenFOAM/Blender binaries should be reported in the per-tool verdict and propagated into the consolidated report.

## Drift detection

Re-run the verifier on the canonical engineering host and compare the new `consolidated-verdict.yaml` to the last known-good baseline. Treat these as drift signals:

- OpenFOAM or Blender version changes.
- A tool status changes from `PASS` to `FAIL`.
- A validator stops writing its per-tool verdict.

## Environment notes

Repo-side tests inject fake validators through `OPENFOAM_BASELINE_VALIDATOR` and `BLENDER_BASELINE_VALIDATOR`. Live validation still requires the real OpenFOAM and Blender installations on the intended engineering host.
