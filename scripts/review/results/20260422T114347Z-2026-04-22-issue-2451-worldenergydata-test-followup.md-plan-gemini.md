### Verdict: APPROVE

### Summary
The plan is highly detailed, defensive, and well-structured. It systematically addresses the three test failure clusters with clear conditional logic, ensuring root causes are verified before applying fixes. The strict scoping and comprehensive TDD checklist are excellent.

### Issues Found
- [P3] Minor: No Attested Evidence block was provided in the prompt to independently verify the plan's claims about file existence and issue status, though the plan itself includes commands to verify these.

### Suggestions
- Ensure the follow-up issue for the legacy NPV tests (Cluster C) is created promptly to avoid losing track of the skipped tests.
- For Cluster A, if `pytest-benchmark` is installed but the fixture is missing, check if `pytest-benchmark` is inadvertently disabled in `pytest.ini` or `pyproject.toml` via `addopts = -p no:benchmark`.

### Questions for Author
- Has the module owner been consulted regarding the preferred approach for Cluster C (skip vs. repoint) prior to implementation?
- Are there any known compatibility issues with `pytest-benchmark` and the specific Python versions (3.10, 3.11, 3.12) used in the CI matrix?
