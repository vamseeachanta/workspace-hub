### Verdict: APPROVE

### Summary
The plan is well-structured, correctly identifies the root causes of the three test failure clusters, and provides sensible, reversible mitigation paths. The emphasis on empirical verification and deferring broader architectural decisions to module owners is highly appropriate.

### Issues Found
- [P3] Minor: The plan proposes using `--all-groups` for `uv sync`, but this could potentially install other unrelated dependency groups that might affect the test environment. It might be safer to explicitly use `--group benchmark` if only benchmark dependencies are needed.

### Suggestions
- Verify the exact `uv` version used in CI before implementing Cluster A1 to ensure `--all-groups` or `--group` flags are fully supported.
- For Cluster C, consider filing the follow-up issue for the legacy NPV API re-enablement concurrently with this fix to ensure it is not forgotten.

### Questions for Author
- Has the `astral-sh/setup-uv@v7` action version been confirmed to install a `uv` version >= 0.4.0 that supports the `--all-groups` flag?
- If CI already installs the `dev` group containing `pytest-benchmark`, could there be a plugin registration issue (e.g., `conftest.py` modifying `pytest_plugins` or an environment isolation issue) rather than an installation issue?
