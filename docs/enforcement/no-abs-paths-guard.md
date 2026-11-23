# Absolute-Path Guard

`scripts/enforcement/check-no-abs-paths.sh` scans tracked shell and Python scripts for hardcoded host-specific path forms, including home-directory and mount-point prefixes, drive letters, and profile-style prefixes. It compares detected findings with `config/quality/no-abs-paths-baseline.txt` so existing findings stay visible without hiding new ones.

Run locally:

```bash
scripts/enforcement/check-no-abs-paths.sh
```

For CI reporting, `scripts/enforcement/report-no-abs-paths.sh <summary-file> <findings-file>` runs the guard with its default baseline, writes a summary with the finding count and first 50 findings, and writes the full finding list to the supplied file.

## Staged Rollout

1. Report-only CI runs now on pull requests to `main` and pushes to `main`. New findings are summarized and uploaded, but they do not fail CI.
2. The refreshed baseline merges through a reviewed PR made with the guard's own baseline-update option.
3. CI becomes blocking only after the refreshed baseline has merged and `main` has produced one week of clean reports.

The single workflow setting that changes stage 1 to stage 3 is:

```yaml
ABS_PATH_GUARD_MODE: report-only
```

Change it to:

```yaml
ABS_PATH_GUARD_MODE: blocking
```

Findings are fixed or baselined only through reviewed PRs. Do not hand-edit the baseline.
