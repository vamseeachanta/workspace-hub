Implementation progress update for #2269.

Completed in repo scope
- tightened `scripts/openfoam/verify-openfoam-baseline.sh` so canonical version/fork gating happens before delegated runner execution
- enforced wrapper-to-runner bashrc handoff via `OPENFOAM_BASHRC`
- hardened normalized verdict handling so malformed raw runner output becomes an explicit failure artifact instead of a traceback-only failure
- strengthened the pytest harness with additional adversarial checks for version mismatch, malformed raw verdicts, and dual-path bootstrap precedence
- updated baseline docs/manifest/checklist/discoverability links to match the approved workflow more closely

Validation run in this session
- `uv run pytest tests/openfoam/test_verify_openfoam_baseline.py -q` -> `10 passed, 1 skipped`
- `bash -n scripts/openfoam/verify-openfoam-baseline.sh scripts/openfoam/run-openfoam-tutorials.sh` -> pass

Execution-host note
- this session is on `ace-linux-1`, which does not have the OpenFOAM runtime installed, so the host-required `@pytest.mark.openfoam` path remains intentionally skipped here
- real host validation still belongs on `machine:dev-secondary`
