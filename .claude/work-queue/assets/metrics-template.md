# Metrics Template for INDEX.md

> Paste this section into INDEX.md after the Summary section.
> Values are placeholders — replace with computed data from generate-index.py.

## Metrics

### Throughput

| Metric | Value |
|--------|-------|
| Total captured | {total_captured} |
| Total archived | {total_archived} |
| Completion rate | {archived}/{captured} ({pct_complete}%) |
| Monthly rate (current month) | {archived_this_month} archived |
| Monthly rate (prior month) | {archived_prior_month} archived |

### Plan Coverage

| Metric | Count | Percentage |
|--------|-------|------------|
| Pending items with plans | {pending_with_plan} / {total_pending} | {pct_plan_coverage}% |
| Plans cross-reviewed | {reviewed_count} | {pct_reviewed}% |
| Plans user-approved | {approved_count} | {pct_approved}% |

### Aging

| Bucket | Count | Items |
|--------|-------|-------|
| Pending > 30 days | {aged_30} | {aged_30_ids} |
| Pending > 14 days | {aged_14} | {aged_14_ids} |
| Working > 7 days | {stale_working} | {stale_working_ids} |
| Blocked > 7 days | {stale_blocked} | {stale_blocked_ids} |

### Priority Distribution (active items only)

| Priority | Pending | Working | Blocked |
|----------|---------|---------|---------|
| High     | {high_pending} | {high_working} | {high_blocked} |
| Medium   | {med_pending}  | {med_working}  | {med_blocked}  |
| Low      | {low_pending}  | {low_working}  | {low_blocked}  |
