> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_commit_attestation_narrow_scope.md

---
name: Commit-message attestation has narrow scope
description: A commit's embedded "gates passed" attestation only covers the files the commit touched — subsequent commits to other files on the same branch can regress the broader gate; always re-run the full gate live, not just verify the commit's own files are untouched.
type: feedback
originSessionId: 0af51b6e-3c2d-424f-a6b4-dd84c80ac95f
---
When a commit message says "black clean, isort clean, pytest collection clean" at merge, those claims are only trustworthy for files within that commit's diff. A `git log <fix>..HEAD -- <fix's files>` query that returns empty proves those specific files haven't moved — it does NOT prove the broader `src/`/`tests/` surface is still gate-clean.

**Why:** During #2433 verification (2026-04-23), relying on fix commit `0f8ac026`'s attestation alone produced a wrong verdict. Three subsequent PRs (#345/#346/#347) merged on 2026-04-22 added ~1100 lines of new `src/` and `tests/` code that failed both `black --check` and `isort --check-only`. The fix commit's own files (`tests/conftest.py`, `.github/workflows/ci.yml`) were untouched, so the narrow `git log` query returned empty and falsely implied "attestation still current." The broader CI `lint` gate was actually red on main. I had to post a correction comment to the same issue.

**How to apply:** For any verification-first lane that claims "previous commit's gates are still passing," run the full live gate — not just prove the gated files in that commit haven't moved. Especially important for `black`, `isort`, `flake8`, `mypy`, and any gate whose scope is a directory (`src/`, `tests/`) rather than specific files. Live gate re-run is the authoritative evidence; commit-message attestation is an indicator only. If the live gate re-run is blocked by tool contention, disclose that explicitly rather than falling back to narrow-scope git-log inference.
