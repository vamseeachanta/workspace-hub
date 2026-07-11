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
