# Manifest FIFO substitution: Plan-lite

The reader will reject a manifest replaced by a FIFO between pathname checks and
open, without waiting for a writer. This plan covers the bounded change for
issue #3439 and its regression coverage.

## Plan-lite

1. Retain canonical relative-path, containment, regular-file and symlink/reparse
   checks in `_regular_file()` before opening a manifest.
2. Open with `O_NONBLOCK` where supported so a substituted FIFO cannot wait for a
   writer before descriptor validation. Preserve `O_NOFOLLOW` and `O_NOATIME`,
   including the existing missing-flag fallbacks.
3. Validate the opened descriptor with `fstat()` before creating a stream. Close
   rejected descriptors; transfer accepted descriptors to a context-managed
   stream so success and read failures release them.
4. Run a native FIFO substitution regression without a writer in a child with an
   explicit safety timeout. Treat a timeout as failure and require the fixed
   UNRESOLVED diagnostic with empty partitions.
5. Cover six injected non-regular descriptor types, closure before stream creation,
   supported flags and a regular-file control with hand-calculated partitions.
   Run both reachability suites to check existing behavior.

## Implementation and test references

- `scripts/reporting/asset_reachability.py`: `_regular_file()` retains pathname
  checks; `_read()` applies open flags, descriptor validation and closure.
- `tests/reporting/test_asset_reachability_fifo_race.py`: native FIFO substitution,
  injected descriptor types and the independent regular-file partition example.
- `tests/reporting/test_asset_reachability.py`: existing valid-input and rejection
  coverage for the reachability planner.

## Acceptance and limits

Both suites will pass without failures or skips on a platform with native FIFO
and nonblocking-open support. The FIFO case will finish within its safety budget;
the descriptor cases will reject non-regular types before stream creation.

This change will not establish atomic snapshots or ancestor race safety. Injected
device metadata will not establish native device-open behavior, and one local
platform run will not establish coverage on other platforms.
