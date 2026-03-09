### Verdict: APPROVE

### Summary
Marker-based exclusion and Phase 2 refactor deferral are defensible for WRK-1062, but `--include-live` is only partially correct: it re-selects live tests, yet those same failures remain suppressed by the global expected-failure list, so a live run can still report `ok` while the live tests fail.

### Issues Found
- `--include-live` does not restore strict live-test signaling. In [run-all-tests.sh](/mnt/local-analysis/workspace-hub/scripts/testing/run-all-tests.sh#L45), the flag only removes `-m "not live_data"`; however [expected-failures.txt](/mnt/local-analysis/workspace-hub/scripts/testing/expected-failures.txt#L10) still lists all live-data node IDs, so `parse_pytest_output.py` will continue classifying those failures as expected. If the intent of `--include-live` is true validation, this masks the exact failures the flag is supposed to surface.
- `builders.py` is serviceable scaffolding but not fully aligned with the deferred adoption path. In [builders.py](/mnt/local-analysis/workspace-hub/assethold/tests/fixtures/builders.py#L30), `sec_filing_data()` is never consumed by `mock_sec_downloader()`, so one of the fixture payloads is disconnected from the mock helper that should expose it. That makes the module less useful as the single future source of truth for test refactors.

### Suggestions
- Treat `--include-live` as a strict mode: either ignore live-data entries from `expected-failures.txt` when the flag is set, or split expected failures by mode so live runs fail loudly on current live-data breakage.
- Before broader test refactoring, tighten [builders.py](/mnt/local-analysis/workspace-hub/assethold/tests/fixtures/builders.py) into a real shared contract: add a small internal loader/helper, wire `sec_filing_data()` into the SEC mock, and document which production call patterns each builder covers.
- The deferral itself looks correct. These tests are still coupled to result YAMLs and, in some files, to current engine side effects, so forcing a partial mock refactor in WRK-1062 would have mixed concerns. Keep the marker-based exclusion for now, but capture a follow-up WRK specifically for converting selected live tests to builder-backed deterministic assertions and then removing their `live_data` marks.

### Questions for Author
- Was `--include-live` intended as a diagnostic/live-validation mode, or only as a way to execute those tests without changing the overall pass/fail contract? The current implementation supports the latter, not the former.
