# WRK-1091 Plan — Gemini Review

## Assessment

Two critical architectural issues block approval. Plan is otherwise well-structured.

## Issues Found

- [P1] Critical: Pre-push hook on assetutilities is unversioned — stored in `.git/hooks/`
  which is local-only and not committed. This violates infrastructure-as-code principles
  and makes onboarding fail silently. Fix: version-control via `.pre-commit-config.yaml`
  with `stages: [push]`, or a setup script that symlinks a versioned hook script.

- [P1] Critical: PYTHONPATH-based import resolution is brittle vs. `uv run`-based approach.
  However, workspace convention already uses this pattern in run-all-tests.sh — so this
  is acceptable as long as it's noted as following established workspace pattern.

- [P2] Important: Plan omits mandatory legal sanity scan. Any new scripts should be scanned
  via `scripts/legal/legal-sanity-scan.sh` before proceeding.

- [P3] Minor: Bash script in Step 3 should include `set -euo pipefail` and use
  `$(git rev-parse --show-toplevel)` for REPO_ROOT (not hardcoded paths).

## Verdict: MAJOR

Address [P1] hook versioning gap before approval. PYTHONPATH is acceptable given
workspace convention. Legal scan note addressed in execution stage.
