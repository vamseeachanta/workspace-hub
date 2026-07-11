# Task 6 report — descriptor-bound finalization

## Scope

Implemented the approved Task 6 finalizer and the minimal `finalize-scaffold`
CLI wiring. Git object calculation and GitHub remote classification were split
into focused modules to keep every Python file at or below 400 physical lines
and every function at or below 50.

## TDD evidence

- RED: `uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_finalizer.py -q`
  failed during collection with `ImportError: cannot import name
  'bootstrap_finalizer'` because the production module did not exist.
- GREEN: the focused finalizer/contract command completed with `26 passed`.
- The end-to-end test renders and manifests the committed template, constructs
  the exact root commit through plumbing, verifies it has no parent, and proves
  the populated index writes the independently calculated tree.

## Implementation notes

- Finalization independently reloads the current trusted committed template,
  rerenders substitutions, validates the external manifest, rejects ambient
  Git authority surfaces, and computes the exact expected tree without writing
  objects.
- Initial creation writes exact blobs/trees, creates the fixed-message root
  commit, zero-old-OID CAS-creates `main`, then populates the index.
- Recovery validates raw commit grammar and repairs only the exact local index.
- Push retains the literal commit OID, canonical HTTPS destination, fixed
  credential helper, and checks HEAD before/after transport.
- GitHub classification uses repo posture first and literal
  `--hostname github.com`; only a branch-specific 404 after valid PRIVATE,
  unarchived posture maps to absence.
- Post-CAS attestation checks member inventory, trusted template/repository,
  manifest hard links, descriptor identities, and config content.

## Self-review

- Corrected default Git hook handling: executable `*.sample` files are inert
  samples; every real executable or non-regular hook remains rejected.
- Corrected recovery pre-mutation behavior: expected Git objects are calculated
  with exact SHA-1/SHA-256 framing in Python, avoiding `hash-object -w` before
  a recovery commit is accepted.
- Corrected post-CAS validation: the existing manifest validator intentionally
  accepts only unborn HEAD, so committed-state re-attestation is implemented
  as a separate strict path rather than weakening that interface.

## Verification

- `uv run --frozen pytest tests/client_llm_wiki -q` — exit 0.
- `uv run --frozen ruff check scripts/client_llm_wiki tests/client_llm_wiki` — exit 0.
- `scripts/legal/legal-sanity-scan.sh` — exit 0.
- `check_python_function_lengths.py` on all Task 6 Python paths — exit 0.

## Residue audit

EXPECTED: this approved worktree contains only the Task 6 implementation,
tests, CLI wiring, and this report before commit. No stash, scratch directory,
external write, GitHub mutation, or sibling-repository mutation was created.
The repository-referenced cleanup-audit skill path was absent in this worktree;
the equivalent status/diff/untracked inspection was performed directly.

## Rejection remediation

- Removed this report from the product index while preserving it locally.
- Added observed RED/GREEN coverage for strict surrounding-whitespace rejection
  and SHA-1/SHA-256-width zero-old-OID CAS values.
- Added held-config authorization before mutation and exact symbolic-main HEAD
  checks on every HEAD read.
- Expanded the finalizer suite from three smoke tests to parameterized raw-root
  grammar, Git authority-surface, API mapping/hostile-environment, CAS ordering,
  bounded residue, retained-literal-OID, and HEAD-substitution coverage.
- The first full rerun found one regression: an experimental config timeout
  increase violated the existing exact five-second bound. It was reverted; the
  timeout contract remains unchanged.

## Continuation status — 2026-07-11

- Added a public retained-descriptor `BoundValidationContext` which binds the
  clone parent/root/`.git`/config and manifest parent/final/backing once. All
  subsequent validation uses those descriptors without reopening the named
  target or evidence paths.
- Added trusted rendered-member comparison, rejecting a forged clone plus a
  correspondingly forged, self-consistent manifest before Git mutation.
- Added named pre/post attestation seams for each individual `hash-object`,
  `mktree`, `commit-tree`, zero-old-OID CAS, `read-tree`, push, API query, and
  final return. The post-check runs from `finally`, including exceptions.
- Added recovery integration proving exact local-only state repairs an empty
  index before push, followed by remote-equal idempotent success without push.
- Added the transport reconciliation matrix for success, nonzero, timeout,
  exception, credential-unavailable, and equal/different/absent/unknown API
  observations.
- Observed GREEN: 60 fast finalizer/transport tests; forged-manifest integration;
  initial success integration; local-only repair and remote-equal idempotence;
  Ruff; changed-file 400/50 limits.
- BLOCKED verification: two full `tests/client_llm_wiki` attempts were killed
  externally without a pytest summary or shell return-code line while unrelated
  long-running host pytest/search/push jobs were active. The second reached 162+
  passing tests (38%) before termination. The exact five-second config timeout
  remains unchanged.
- Remaining contract gap: a single integration matrix still must assert no
  mutation for every distinct pre-mutation HEAD/index/worktree/identity/origin/
  remote-SHA mismatch. Full Tasks 1-6, staged legal scan, cleanup audit, and the
  Task 6 fix commit are intentionally not claimed or performed until that matrix
  and a complete uninterrupted verification run pass.
