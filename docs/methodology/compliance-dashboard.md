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
3. **Apply the existing review-evidence heuristic**:
   - Match review-related keywords in the commit subject or body.
   - Search for a matching hash prefix in `.planning/**/REVIEWS.md`.
   - These checks are historical heuristics, not authenticated review evidence.
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

## Related

- docs/methodology/enforcement-over-instruction.md (why this exists)
- docs/methodology/compound-engineering.md (Lesson 1: enforcement)
- #1876 -- Enforce engineering workflow
- #2017 -- Agent bypass resistance
- #2012 -- Review backlog (4% compliance audit)

## Daily alert report contract

The daily wrapper consumes `compliance-dashboard.sh --json`, which emits a single
JSON object and saves the same object in the daily report. The default text mode
remains available for interactive use. `COMPLIANCE_FORMAT=json` selects the same
transport; `COMPLIANCE_REPORTS_DIR` sets the output directory for both scripts.
The schema version is `1`. Reports add `unreviewed_commits`, an array of objects
with full `hash` and `subject` fields; existing metric fields remain available.
Hash lengths follow [Git 2.55.0, hash-function-transition, Object names](https://git-scm.com/docs/hash-function-transition),
accessed 2026-10-22: SHA-1 and SHA-256 use 40 and 64 hexadecimal digits.

`compliance_alert.py` validates the version, timestamp, nonnegative integer
counters, count identities, integer rate, top-level verdict and complete backlog
before preparing an alert. Booleans are not counts. The timestamp must include a
timezone and have the same calendar date as the wrapper's run date. Invalid data
or an inconsistent dashboard exit status fails the wrapper without publishing.
Only the top-level `verdict` describes review compliance; nested stage prompt
drift verdicts describe separate diagnostics.

The source for the alert boundaries is issue #3596, **Thresholds** (2026): below
30 percent is critical, below 50 percent is high, and the remaining failing range
is medium. The dashboard's configured pass threshold is authoritative (default
80 percent). An empty or all-skipped window has no review obligations and produces
no alert even though its legacy numeric rate remains zero. The percentage uses
integer truncation, consistent with the existing daily and weekly reports.

Alerts use the ISO week year and number in a deduplication key. The search uses
that key in the issue body, avoiding matches from another year. A failed search
stops publication rather than creating a duplicate. New and updated alerts carry
the same validated counts, full backlog hashes and limitations. Commit subjects
are indented literal text so backticks cannot close a Markdown fence.

### Worked example: the reported alert

Inputs from issue #3596 (2026): total commits = 49, reviewed = 3, unreviewed = 13.
The skipped count is obtained by subtraction rather than assumed:

- Reviewable = reviewed + unreviewed = 3 + 13 = 16.
- Skipped = total minus reviewable = 49 minus 16 = 33.
- Rate = floor(100 × reviewed / reviewable) = floor(300 / 16) = 18 percent.
- Since 18 is below the cited critical boundary of 30 percent, severity is critical.
- With the default threshold of 80 percent, the compliance verdict is `FAIL`.

A nested drift verdict of `pass` has no effect on that answer. For zero total
commits, or four commits that are all skipped, reviewable is zero and the answer
is **no alert**, rather than a critical alert about an undefined ratio.

An offline exercise uses the normal wrapper with publication disabled:

```bash
DRY_RUN=true COMPLIANCE_REPORTS_DIR="$TMPDIR/compliance-example" \
  bash scripts/enforcement/compliance-cron.sh
```

Dry-run prepares and logs the full alert without invoking any publishing command,
including authentication. Tests use synthetic histories and a fake publisher to
exercise creation, updates and failures; a separate test runs the actual dashboard
through the actual wrapper in a disposable repository.

### Qualification limits and follow-up

These changes repair alert transport, validation and actionable backlog reporting.
The review-evidence heuristic and commit classification remain unchanged. The
heuristic can match ordinary review-related words or author attribution and can
misclassify evidence; it does not establish that an independent review occurred.
Review authenticity and bypass attribution are `NOT_EVALUATED`. No historical
commit is certified, reviewed or exempted by this change, and no enforcement gate
is changed. The weekly aggregator continues consuming the existing integer fields.

Independent review of the historical backlog and replacement of heuristic evidence
with a separately specified authenticated record remain follow-up work. A low rate
alone is insufficient evidence that any contributor bypassed a gate.
