# WRK-1090 Plan — Codex Review (Claude Opus substitute — Codex quota exhausted)

## Assessment

The plan is well-structured and follows established workspace-hub patterns (mirrors check-all.sh,
uses REPO_MAP/REPO_ORDER, flock for atomicity). The TDD-first approach is correct. However,
two P1 technical issues make the CVE and outdated-detection phases non-functional as specified.

## Issues Found

- [P1] Critical: `uv pip list --outdated --format=json` requires an activated virtual environment.
  Running it bare will fail or report against the wrong env. Correct invocation: `uv run pip list
  --outdated --format=json` from each repo root (where pyproject.toml exists). Test T2 mock would
  mask this failure mode without the fix.

- [P1] Critical: `uv audit` does not exist as of uv 0.5.x. The probe will always fail — drop it
  and go straight to `uvx pip-audit --format=json`. Additionally pip-audit cannot scan uv.lock
  directly; it needs a requirements source. Correct: `uvx pip-audit --requirement <(uv export
  --format requirements-txt)` or equivalent per-repo approach.

- [P2] Important: `uvx` must also be mocked in TDD (not just `uv`). Since uv audit is gone, uvx
  is the only CVE code path. Tests must mock uvx: not installed (graceful warn), findings present,
  and clean scan.

- [P2] Important: `uv lock --check` may attempt network resolution if registry unreachable, causing
  false failures in offline cron. Should specify `--offline` flag or document network prerequisite.

- [P2] Important: YAML report same-day overwrite unspecified. Second run silently overwrites first.
  Should use timestamped filename (dep-health-YYYY-MM-DDTHHMM.yaml) or document overwrite intent.

- [P2] Important: `flock` needs `--timeout` to avoid deadlock from stale lock. T4 should verify
  timeout/stale-lock behavior.

- [P3] Minor: ">2 minor versions behind" heuristic fails for CalVer/non-semver packages. Simpler:
  any outdated = warn.
- [P3] Minor: `--repo` flag not mentioned — should mirror check-all.sh ergonomics.
- [P3] Minor: Live crontab application is out of scope (WRK-1021 handles it) — note explicitly.

## Verdict: MAJOR
