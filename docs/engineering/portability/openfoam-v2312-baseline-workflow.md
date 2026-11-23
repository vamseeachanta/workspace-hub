# OpenFOAM v2312 baseline workflow

## Summary

This is the canonical operator-facing OpenFOAM baseline workflow for workspace-hub issue #2269.
It standardizes ESI/OpenFOAM.com v2312 on `machine:dev-secondary` and defines the repo-tracked
artifacts, wrapper/runner split, smoke/benchmark tiers, and troubleshooting contract.

## Baseline

- Fork/version: ESI/OpenFOAM.com v2312
- Canonical host: dev-secondary
- Permanent bootstrap probe order:
  1. `/usr/lib/openfoam/openfoam2312/etc/bashrc`
  2. `/opt/openfoam2312/etc/bashrc`
- If both paths exist, the first path wins and the second is treated as skipped.
- Default verdict artifact path: `logs/engineering/openfoam-baseline/latest-verdict.yaml`

## Operator commands

### Mandatory smoke tier: cavity

```bash
bash scripts/openfoam/verify-openfoam-baseline.sh
```

### Optional benchmark tier: pitzDaily

```bash
bash scripts/openfoam/verify-openfoam-baseline.sh --benchmark pitzDaily
```

## Wrapper vs runner split

- `scripts/openfoam/verify-openfoam-baseline.sh`
  - resolves bootstrap path
  - verifies fork/version
  - exports the selected path as `OPENFOAM_BASHRC_RESOLVED`
  - invokes the delegated tutorial runner
  - owns the final normalized YAML verdict using embedded Python normalization via `uv run python`
  - fails fast with `uv-missing` instead of falling back to bare `python3`
- `scripts/openfoam/run-openfoam-tutorials.sh`
  - remains the execution engine
  - accepts `--skip-bootstrap` from the wrapper and trusts the prepared OpenFOAM environment
  - runs selected tutorial commands
  - emits raw tutorial rows for wrapper normalization

## YAML verdict contract

Required top-level fields:
- `generated_at`
- `machine`
- `resolved_bashrc_path`
- `fork`
- `version`
- `verification_method`
- `overall_verdict`
- `tutorials`

Only `generated_at` is volatile.

## Smoke / benchmark tiers

- Mandatory smoke tier: `cavity`
- Optional benchmark tier: `pitzDaily`
- Runner-only/non-canonical tutorial: `damBreak`

`damBreak` may still run inside the delegated runner for broader validation coverage, but it is not part of the canonical baseline acceptance contract for #2269.

## Troubleshooting

- Missing bashrc paths should fail with explicit probe-order messaging.
- Runner failures must surface their root cause without wrapper masking.
- Unsupported benchmark values must fail fast and name the allowed value (`pitzDaily`).
- Use the manifest at `examples/openfoam/cavity-v2312/README.md` for reproducible tutorial-copy instructions without committing copied case data.

## Requirement traceability

| Issue #2269 requirement | Deliverable | Test / proof | Acceptance criteria |
| --- | --- | --- | --- |
| declare target fork/version explicitly | this workflow doc + wrapper | `test_workflow_doc_covers_traceable_issue_requirements`, `test_verify_script_normalizes_final_yaml_contract` | workflow doc declares ESI/OpenFOAM.com v2312 and wrapper emits normalized version/fork fields |
| canonical runner command(s) documented | this workflow doc + manifest | `test_workflow_doc_covers_traceable_issue_requirements` | operator commands documented for smoke and optional benchmark tiers |
| minimal smoke case under reproducible repo-tracked path | manifest | `test_manifest_instructions_do_not_commit_case_data` | manifest exists as instruction-only path with no committed case data |
| validator produces pass/fail output with explicit checks | wrapper + pytest harness | `test_verify_script_fails_when_bashrc_missing`, `test_verify_script_surfaces_runner_failure`, `test_verify_script_normalizes_final_yaml_contract`, `test_verify_script_rejects_version_mismatch` | wrapper emits normalized success YAML and explicit failure artifacts |
| common failure modes and version/fork mismatches documented | this workflow doc + research notes | workflow doc inspection + repo docs updates | troubleshooting and mismatch behavior are documented consistently |
| workflow executable on canonical engineering host with documented prerequisites | wrapper + host-marked pytest | `@pytest.mark.openfoam` host test | host-required validation remains machine-gated to a supported OpenFOAM host |

## Acceptance criteria

- wrapper declares and enforces the two-path bootstrap baseline
- wrapper exports the resolved bashrc path to the delegated runner
- wrapper normalizes final YAML to the canonical contract
- manifest remains instruction-only and documents prerequisites / commands / expected outputs / failure modes
- docs/README and engineering checklist link the canonical baseline workflow
