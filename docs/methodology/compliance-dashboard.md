# Compliance Dashboard Guide

> How monitoring, tracking, and enforcement actually works

## What It Is

The compliance dashboard tracks whether AI agents (Claude, Codex, Gemini, Hermes) follow the required engineering workflow: plan -> review -> implement -> review -> ship.

## The Scripts

| Script | Location | Purpose |
|---|---|---|
| `compliance-dashboard.sh` | scripts/enforcement/ | Generates compliance reports from commit history |
| `require-plan-approval.sh` | scripts/enforcement/ | Pre-commit gate: blocks implementation without plan |
| `require-review-on-push.sh` | scripts/enforcement/ | Pre-push gate: checks review evidence exists |
| `require-cross-review.sh` | scripts/enforcement/ | PR creation gate: requires review artifacts |
| `require-tdd-pairing.sh` | scripts/enforcement/ | TDD gate: warns on unpaired test changes |
| `extract-learnings.sh` | scripts/learnings/ | Post-commit: detects patterns worth capturing |
| `cross-agent-bridge.sh` | scripts/learnings/ | Syncs agent knowledge across systems |

## How Compliance is Calculated

1. **Scan recent commits** (default: last 24 hours, configurable)
2. **Classify each commit**:
   - Skip: docs, chore, test, ci, style, sync, merge, revert, build, skill-only, email-only
   - Reviewable: feat, fix, refactor, perf, security
3. **Check each reviewable commit for evidence**:
   - Plan approval markers in `.planning/plan-approved/`
   - Review files in `.planning/phases/*/REVIEWS.md`
   - Review reports in `.claude/reports/*review*`
   - Review keywords in commit messages
4. **Calculate rate**: reviewed / reviewable * 100
5. **Compare to threshold**: default 80%

## Running the Dashboard

```bash
# Default: last 24h, 80% threshold
bash scripts/enforcement/compliance-dashboard.sh

# Custom window: last 72h, 90% threshold
COMPLIANCE_WINDOW_HOURS=72 COMPLIANCE_THRESHOLD=90 \
  bash scripts/enforcement/compliance-dashboard.sh
```

### Example Output

```
============================================================
Compliance Report — Last 24h
============================================================

Total commits:      42
Skipped (docs/etc): 19
Reviewable:         23

Reviewed:           1
Unreviewed:         22
--------------------------------------------
Compliance rate:    4% (threshold: 80%)
Verdict:            FAIL
```

## Log Files

| File | Location | What it tracks |
|---|---|---|
| `compliance-YYYYMMDD.json` | logs/compliance/ | Daily compliance metrics |
| `plan-gate-events.jsonl` | logs/hooks/ | Plan gate blocks/events |
| `review-gate-bypass.jsonl` | logs/hooks/ | Bypass attempts with user/branch |
| `review-gate-latency.jsonl` | logs/hooks/ | Gate execution latency |
| `patterns.jsonl` | logs/learnings/ | Repeated patterns detected |

## Enforcement Levels

```
Level 1 (advisory): Prints warnings, allows commit
  export FORCE_PLAN_GATE_STRICT=0
  export REVIEW_GATE_STRICT=0

Level 3 (hard): Blocks commit, requires fix
  export FORCE_PLAN_GATE_STRICT=1
  REVIEW_GATE_STRICT=1
```

## Integration with GitHub Issues

The compliance dashboard feeds into:

- **#1876** -- Workflow enforcement (implementation)
- **#2012** -- Review backlog audit (daily report)
- **#2017** -- Agent bypass resistance (metrics)

A cron job runs the dashboard and auto-creates issues when compliance drops below threshold.

### Daily alert interpretation

The daily wrapper validates the current invocation's JSON report through
`scripts/enforcement/compliance-alert.py`. It reads top-level metrics only;
stage-prompt telemetry cannot supply a second verdict or count. Counts must be
nonnegative integers and satisfy both partitions:

```text
reviewable = total_commits - skipped
reviewable = reviewed + unreviewed
rate = floor(100 * reviewed / reviewable), when reviewable > 0
```

The arithmetic source is
[`compliance-dashboard.sh`](../../scripts/enforcement/compliance-dashboard.sh),
the Calculate rates and Determine verdict sections (2026). The integer rate is
retained for compatibility with saved daily reports. A zero reviewable count
means compliance is `NOT_EVALUATED` by the alert wrapper. The dashboard's legacy
numeric zero and passing verdict remain in its output; that pair is not evidence
of a review failure.

Alert severity follows issue #3940 (2026), Thresholds table: below 30% is critical,
30% through 49% is high, 50% through 79% is medium, and at least 80% produces no
alert. These alert limits remain independent of a custom dashboard threshold.
The wrapper also verifies that the dashboard's verdict and exit status match its
own threshold. Invalid JSON, contradictory metrics or an execution error return
a nonzero status without posting a compliance alert. No saved daily report is
used as a fallback.

### Worked example: empty samples and genuine violations

The following inputs are synthetic. Each answer is an independent hand
calculation using the equations above and the issue #3940 severity table.

| Total | Skipped | Reviewed | Method | Daily alert answer |
|---|---|---|---|---|
| 0 | 0 | 0 | Reviewable = 0 - 0 = 0; no denominator | NOT_EVALUATED; no alert |
| 1 | 1 | 0 | Reviewable = 1 - 1 = 0; no denominator | NOT_EVALUATED; no alert |
| 1 | 0 | 0 | Reviewable = 1; rate = floor(100 × 0 / 1) = 0% | Critical; one unreviewed item |
| 4 | 1 | 2 | Reviewable = 3; rate = floor(200 / 3) = 66% | Medium; one unreviewed item |
| 5 | 0 | 4 | Reviewable = 5; rate = floor(400 / 5) = 80% | No alert |

This reproduces the distinction missing from the original alert: one skipped
commit is an empty sample, whereas one unreviewed qualifying commit is a genuine
zero-percent sample. Nested stage-prompt verdicts do not change either answer.

Run an operational preview with `DRY_RUN=true bash
scripts/enforcement/compliance-cron.sh`. The preview writes local reports and
logs but makes no GitHub calls. The regression suite is
`tests/enforcement/test_compliance_cron.py`; its disposable fixtures run the real
dashboard and replace Git and GitHub commands with local test doubles.

The historical alert is not a completed review audit. Commit-message keyword
matching and existing review-file heuristics remain unchanged, and a passing
metric does not authenticate independent review. Historical commits require
separate inspection; deployment, issue closure and changes to weekly aggregation
are not performed by this correction.

## Related

- docs/methodology/enforcement-over-instruction.md (why this exists)
- docs/methodology/compound-engineering.md (Lesson 1: enforcement)
- #1876 -- Enforce engineering workflow
- #2017 -- Agent bypass resistance
- #2012 -- Review backlog (4% compliance audit)
