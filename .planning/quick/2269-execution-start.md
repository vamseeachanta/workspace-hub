Execution start for approved issue #2269.

Mode: central

Scope for this pass
- run the implementation pre-check against the approved plan deliverables
- add the missing OpenFOAM baseline workflow artifacts in repo scope
- use TDD for the wrapper/test/doc surfaces named in the approved plan

Validation intent
- first create failing targeted pytest coverage for `tests/openfoam/test_verify_openfoam_baseline.py`
- then implement the minimal repo changes to satisfy those tests
- local host note: this session is on `ace-linux-1`, not the approved execution target `machine:dev-secondary`, and no OpenFOAM runtime is currently present here; fixture-only tests and repo validation will run locally, while host-required `@pytest.mark.openfoam` checks will remain explicitly machine-gated
