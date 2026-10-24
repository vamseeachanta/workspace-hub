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
   - Review or provider keywords in commit messages (a legacy heuristic)
   - Legacy lookup of matching short hashes in `.planning/**/REVIEWS.md`
   - These heuristics do not authenticate independent review or approval
4. **Calculate integer rate**: floor(reviewed / reviewable * 100)
5. **Compare to threshold**: default 80%

### Alert reliability

Commit classification accepts scoped and unscoped subjects, including breaking
change markers: `ci(build):`, `ci:`, `docs!:` and `docs(api)!:`. Ordinary merge and
revert subjects are exempt too. The `feat(skill)`, `feat(email)` and `feat(wiki)`
exemptions require a complete scope or a slash-separated subscope;
`feat(skillful)` remains reviewable. Unknown subjects remain reviewable.

The daily wrapper passes the dashboard's JSON section to
`scripts/enforcement/compliance_report.py`. The parser validates nonnegative
integer counts, count reconciliation, integer percentage and the top-level
verdict. Duplicate JSON keys, missing fields, extra report sections and trailing
payloads fail validation. Nested diagnostics cannot supply alert metrics.
Dashboard errors and inconsistent exit statuses return an error instead of
silently reporting compliance.

When `reviewable = 0`, the percentage is undefined. The dashboard retains its
legacy numeric `0` and `PASS` fields for existing consumers; the alert action is
`not_evaluated`, logged as `NOT_EVALUATED`, and no issue is created. Otherwise the
fixed alert bands are critical below 30%, high from 30% to below 50%, medium from
50% to below 80%, and pass from 80%. These are repository policy from issue #3794,
Thresholds table (2026-08-03), consistent with the monitoring request in #2031;
they are not engineering acceptance limits. `COMPLIANCE_THRESHOLD` changes the
dashboard verdict threshold, while the alert bands remain fixed.

`DRY_RUN=true` prepares the alert locally without any GitHub calls, including
authentication or issue searches. `COMPLIANCE_REPORTS_DIR` directs both dashboard
JSON and cron logs to a supplied directory; the default remains `logs/compliance`.
Test fixtures use this option to keep all output outside the checkout.

### Worked alert example

Inputs, from the original issue #3794 alert: total 10 commits, reviewed 2,
unreviewed 1. The implied skipped count is `10 - 2 - 1 = 7`, and reviewable count
is `2 + 1 = 3`. By the percentage method above, `floor(100 * 2 / 3) = 66`.
The 80% dashboard threshold gives `FAIL`; the fixed alert bands give `medium`.
This reproduces the count arithmetic without asserting that the historical
review evidence was authenticated.

```bash
uv run --no-project python scripts/enforcement/compliance_report.py <<'JSON'
JSON Report:
{"total_commits":10,"skipped":7,"reviewable":3,"reviewed":2,"unreviewed":1,"compliance_rate":66,"threshold":80,"verdict":"FAIL","stage_prompt_drift":{"latest_event":{"verdict":"pass"}}}
JSON
```

The tab-separated answer is `66`, `10`, `2`, `1`, `3`, `FAIL`, `medium`:
rate, total, reviewed, unreviewed, reviewable, top-level verdict, alert action.
The nested `pass` is diagnostic data and does not enter that answer.

For a window containing only 6 exempt commits, the hand counts are skipped 6,
reviewable 0, reviewed 0 and unreviewed 0. No ratio can be evaluated, so the alert
action is `not_evaluated` rather than critical. This addresses the empty-window
pattern recorded in the later updates on #3794.

Historical cross-provider review, authenticated evidence and deployment of the
updated scripts remain separate follow-up work. Regression tests cover these
calculation and parsing paths without publishing alerts or invoking reviewers.

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

## Related

- docs/methodology/enforcement-over-instruction.md (why this exists)
- docs/methodology/compound-engineering.md (Lesson 1: enforcement)
- #1876 -- Enforce engineering workflow
- #2017 -- Agent bypass resistance
- #2012 -- Review backlog (4% compliance audit)
