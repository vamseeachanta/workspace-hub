Result: landed in repo, but not yet fully closed.

Change summary
- landed commit `dd9593719` on `main`: `feat(openfoam): standardize v2312 baseline workflow and validator (#2269)`
- repo now includes the canonical OpenFOAM baseline workflow doc, instruction-only smoke manifest, hardened wrapper validator, stronger pytest coverage, and docs/checklist/discoverability updates

Acceptance criteria status
- repo-tracked baseline workflow/documentation artifacts: satisfied
- wrapper failure/success contract and targeted fixture-based validation: satisfied
- local targeted validation:
  - `uv run pytest tests/openfoam/test_verify_openfoam_baseline.py -q` -> `11 passed, 1 skipped`
  - `bash -n scripts/openfoam/verify-openfoam-baseline.sh scripts/openfoam/run-openfoam-tutorials.sh` -> pass
- no-uv failure-artifact fallback: verified locally
- canonical-host execution proof on `machine:dev-secondary`: still pending from this session because this work was executed on `ace-linux-1`, which does not have the OpenFOAM runtime installed

Adversarial review status
- final local adversarial review found no remaining MAJOR repo-side blocker; residual concerns are minor only

Current state decision
- keeping #2269 open until a real `@pytest.mark.openfoam` / live validator run is executed on `dev-secondary` and posted as evidence
- repo-side implementation is landed; remaining work is host-proof verification, not further design or code restructuring

Git evidence
- landed on `main`
- commit: `dd9593719`
- current `origin/main` contains the landed commit

Residual risks
- live runtime proof is still missing from `dev-secondary`
- malformed CLI usage UX could still be improved later, but it is not blocking the current baseline package
