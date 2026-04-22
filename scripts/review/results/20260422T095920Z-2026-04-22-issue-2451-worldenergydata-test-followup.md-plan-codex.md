### Verdict: MAJOR

### Summary
The plan is mostly scoped correctly and the three failure clusters are well identified, but two implementation branches are underspecified enough to risk a no-op or another collection failure. The main gaps are Cluster A's unresolved root cause and Cluster C's skip strategy not guaranteeing that import-time failures are actually bypassed.

### Issues Found
- [P1] Critical: Cluster A's preferred fix is not technically justified by the evidence as written. The plan states CI already runs `uv sync --all-extras`, and `pytest-benchmark` is declared in `[project.optional-dependencies].dev`; if that declaration is wired correctly, adding `--all-groups` should not be necessary to make the fixture available. The plan acknowledges this ambiguity, but still lists the workflow edit as the preferred path and even includes it in `Files to Change` and acceptance criteria. That can produce a no-op change while leaving the failing root cause unresolved.
- [P1] Critical: Cluster C's default `pytestmark = pytest.mark.skip(...)` path does not guarantee the files will stop erroring during collection. Both NPV files currently contain broken imports at module top; if the skip marker is added after those imports, pytest will still raise `ModuleNotFoundError` before the skip is applied. The plan needs an explicit collection-safe strategy such as moving/removing the broken imports, using `pytest.skip(..., allow_module_level=True)` before the imports, or converting the module to import lazily inside tests.
- [P2] Important: Acceptance criteria are too permissive around Cluster C and residual failures. The deliverable allows either green CI or merely a reduced failure count, but the issue scope is specifically the three known failure clusters. As written, implementation could skip the legacy tests, partially improve benchmark handling, and still pass plan acceptance without proving those exact clusters are gone in CI.
- [P2] Important: The plan proposes editing both `test` and `lint` install steps in `.github/workflows/ci.yml` 'for symmetry', even though issue #2451 is explicitly scoped to the `test` job and #2452 owns `lint`. That creates unnecessary cross-scope change risk and weakens rollback/isolation if the workflow edit behaves unexpectedly.
- [P3] Minor: The verification commands are inconsistent in a few places. `verify_benchmark_plugin_loaded` relies on `pytest --version` plugin output, which is not always a stable assertion target, and `verify_npv_import_resolvable_or_skipped` references `python -c` even though workspace policy says `uv run` should always be used for Python commands.

### Suggestions
- Make Cluster A conditional, not preferred-by-default: require failed-job log inspection plus environment/package verification before choosing between workflow change, explicit `--group benchmark`, or test-local skip.
- Rewrite Cluster C as a collection-safe branch with exact edit guidance, including where the skip must be placed relative to imports or whether imports will be removed/lazily deferred.
- Tighten acceptance criteria so the three named failure signatures must each be eliminated in CI, even if other unrelated failures remain.
- Limit workflow edits to the `test` job unless a separate justification is added for touching `lint`, since #2452 already owns that lane.

### Questions for Author
- What evidence will be used to distinguish 'extras wiring bug' from 'CI environment/plugin load bug' before committing the Cluster A workflow change?
- For Cluster C, what exact edit pattern will prevent module-top import failures from firing before the skip takes effect?
- Is the intent to resolve the three #2451 clusters completely, or only to reduce total failures? The acceptance criteria should state that unambiguously.
