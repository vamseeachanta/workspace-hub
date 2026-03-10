# WRK-1091 Plan — Codex Review

## Assessment

The plan has a critical enforcement gap and structural issues that require revision before approval.

## Issues Found

- [P1] Critical: `assetutilities/.git/hooks/pre-push` is NOT version-controlled. `.git/hooks`
  is local-only and bypassed by `git push --no-verify`. This means the "gate" is advisory-only
  across clones, CI, and other contributors. Fix: version-control via `.pre-commit-config.yaml`
  with `stages: [push]` (assetutilities already has a pre-commit config per MEMORY.md).

- [P2] Important: PYTHONPATH-based import resolution can mask packaging defects and differ
  by environment. However, this is the established workspace pattern (see run-all-tests.sh
  line 168). Note explicitly that this follows workspace convention and is acceptable here.

- [P2] Important: `SKIP_CROSS_REPO_CHECK=1` is too broad without audit trail. Should log
  bypass to `logs/hooks/pre-push-bypass.jsonl` (pattern already established in hub pre-push).

- [P3] Minor: `config/deps/cross-repo-graph.yaml` must be read by the integration script,
  not just documentation. Otherwise it creates drift risk (script hardcodes deps separately).

- [P3] Minor: TDD tests must cover: downstream-repo-missing edge case, bypass audit logging,
  per-repo PYTHONPATH isolation. 6 tests may not be enough for full coverage.

## Verdict: MAJOR

The hook versioning gap [P1] must be resolved before approval. Revise to use
`.pre-commit-config.yaml stages: [push]` on assetutilities.
