# Compliance alert evaluation

## Summary

The daily alert wrapper distinguishes a measured zero compliance rate from an
empty reviewable set. It reads the root fields of one JSON report rather than
searching human text and nested JSON. Invalid evidence is reported as
`NOT_EVALUATED`, with a nonzero exit and no GitHub action.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Validate daily alert evidence and suppress empty-window alerts after the contradictory report in issue #3927. |

## Scope and sources

- `scripts/enforcement/compliance-dashboard.sh`, `main`, defines commit counts,
  integer percentage calculation and the dashboard verdict.
- Issue #3927, **Thresholds**, dated 2026-09-28, defines the default pass boundary
  and severity bands. The alert displayed a critical rate with no unreviewed
  commits and a passing dashboard verdict.
- Issue #2031, implementation summary dated 2026-04-09, records the operational
  alert policy and weekly deduplication. These are repository policy sources;
  no engineering standard or empirical coefficient is involved.

## Inputs and method

`compliance-cron.sh` runs the existing dashboard and passes its complete output
and exit status to `compliance_alert.py`. The helper expects exactly one
`JSON Report:` section with these root fields:

| Field | Meaning |
|---|---|
| `total_commits` | Number of commits observed |
| `skipped` | Number excluded by the existing classifier |
| `reviewable` | Number remaining for review |
| `reviewed` | Number with evidence recognized by the existing detector |
| `unreviewed` | Number without recognized evidence |
| `compliance_rate` | Integer percentage emitted by the dashboard |
| `threshold` | Configured dashboard pass threshold |
| `verdict` | Dashboard `PASS` or `FAIL` |

Counts shall be nonnegative integers; booleans, floats and numeric strings do
not satisfy the contract. The count identities are:

```text
total_commits = skipped + reviewable
reviewable = reviewed + unreviewed
```

For a positive denominator, the percentage is:

```text
compliance_rate = floor(100 * reviewed / reviewable)
```

The factor converting a fraction to percent and integer rounding follow
`compliance-dashboard.sh`, `main`, **Calculate rates**. An empty denominator has
no measured compliance rate. The dashboard's existing zero placeholder and
`PASS` verdict remain compatible; the helper emits `EMPTY` and the wrapper
logs that there are no reviewable commits. Neither no-commit nor skipped-only
windows create or update alerts.

A nonempty report passes when its rate meets the report's threshold. Below that
threshold, severity follows issue #3927, **Thresholds** (2026-09-28): below 30%
is critical, 30–49% is high, and other below-threshold rates are medium. The
default pass threshold is 80% per the same source; a configured threshold takes
precedence over the default. The verdict and dashboard exit status shall agree:
`PASS` exits successfully and `FAIL` exits with status 1, as specified by the
dashboard's **Exit code based on verdict** block.

Missing fields, inconsistent counts or percentages, duplicate JSON keys,
nonfinite numbers, multiple report sections, unexpected trailing output and
mismatched exit status prevent evaluation. Diagnostics identify the failed
condition without repeating raw input. The existing daily log retains the
dashboard output and validation diagnostics.

## Worked examples

These are synthetic inputs. Each answer below is an independent hand
calculation using the count identities and percentage equation above.

| Total | Skipped | Reviewable | Reviewed | Unreviewed | Threshold | Calculation | Answer |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 80% | No denominator | `EMPTY`; no alert |
| 1 | 1 | 0 | 0 | 0 | 80% | All commits excluded | `EMPTY`; no alert |
| 1 | 0 | 1 | 0 | 1 | 80% | floor(100 × 0 / 1) = 0% | Critical alert |
| 3 | 0 | 3 | 1 | 2 | 80% | floor(100 × 1 / 3) = 33% | High alert |
| 5 | 0 | 5 | 4 | 1 | 80% | 100 × 4 / 5 = 80% | `PASS`; no alert |
| 5 | 0 | 5 | 4 | 1 | 90% | 100 × 4 / 5 = 80% | Medium alert |

For the skipped-only example, the legacy displayed placeholder is zero, but
no review was required. For the third example, the denominator is positive and
the zero rate represents an actual missing review. This distinction prevents
the contradictory alert without suppressing a valid zero-rate alert.

## Running and testing

Run the wrapper from the repository root:

```bash
DRY_RUN=true bash scripts/enforcement/compliance-cron.sh
```

Dry runs still generate the dashboard report and daily log, but make no GitHub
calls. Tests use isolated temporary repositories and a local fake GitHub command;
no real issue is created, edited or commented on. The regression suite also
passes an actual dashboard report through the wrapper for an empty repository.

```bash
uv run --no-project --with pytest python -m pytest \
  tests/enforcement/test_compliance_cron.py \
  tests/enforcement/test_compliance_dashboard.py -q -rA -p no:cacheprovider
uv run --no-project --with ruff ruff check \
  scripts/enforcement/compliance_alert.py tests/enforcement/test_compliance_cron.py
bash -n scripts/enforcement/compliance-cron.sh
shellcheck scripts/enforcement/compliance-cron.sh
```

## Limits and follow-up

The existing commit classifier and review detector are unchanged. Recognized
review keywords are observations, not authenticated review approval. The tests
establish reporting behavior for controlled inputs, not historical compliance
or the absence of bypass attempts. Existing alerts are not reconciled or closed.
Weekly aggregation and GitHub authentication, search and publication failure
handling retain their existing behavior. Independent review remains required
before merging.
