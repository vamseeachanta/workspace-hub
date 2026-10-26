# Handoff expiration worked example

## Summary

Handoffs without issue linkage cannot support an issue-closure calculation.
The [metadata dependency policy, section 8.4](durable-vs-transient-knowledge-boundary.md#84-metadata-dependency-codex-finding-c4)
identifies that gap; the [template discussion, section 10.1](durable-vs-transient-knowledge-boundary.md#101-templates-and-conventions)
records the missing formal handoff template. This example demonstrates metadata
and a calculation without changing either policy or any live handoff.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-26 | Add synthetic inputs and a runnable recipe to demonstrate computable advisory dates. |

## Policy basis and scope

The [retention schedule, section 8.1](durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
specifies **30 days after issue closure** for handoffs with an associated issue,
and **90 days when no issue is referenced**. The [metadata dependency, section 8.4](durable-vs-transient-knowledge-boundary.md#84-metadata-dependency-codex-finding-c4)
anchors that fallback to the handoff date. These counts are advisory under
section 8.1, pending the cleanup workflow. A computed date establishes neither
cleanup eligibility nor authority to archive or delete anything.

This example treats a retention day as an elapsed UTC calendar day, preserving
the time of day. It computes an advisory threshold, without deciding whether a
threshold has passed. It accepts supplied evidence only: no current clock,
GitHub request, handoff write, archive operation or cleanup action is used.
The synthetic issue reference is an opaque stand-in, not a live issue.

## Expiration

Copy this heading and block when experimenting with the metadata. This is an
example convention, not an adopted repository-wide template.

```yaml
handoff_at: "2028-01-01T06:00:00Z"
issue_ref: "synthetic-issue"
issue_state: "open"
closed_at: null
```

| Input field | Meaning |
|---|---|
| `handoff_at` | Supplied handoff timestamp, including timezone; `null` means unknown. |
| `issue_ref` | Nonempty issue reference, or explicit `null` for no linkage. |
| `issue_state` | Supplied `open` or `closed` for a linked issue; `null` when unlinked or unknown. |
| `closed_at` | Supplied closure timestamp with timezone; `null` if absent or unknown. |

All input rows include these fields. Missing keys are treated as unknown.
Only explicit `issue_ref: null` selects the no-issue fallback. A missing,
blank or malformed reference does not establish absence of linkage.

| Output field | Meaning |
|---|---|
| `state` | `open_issue`, `closed_issue`, `no_issue_fallback`, `unknown` or `conflicting_metadata`. |
| `expires_at` | Computed UTC threshold, or `null` when no date can be computed. |
| `advisory` | Always `true`, reflecting section 8.1. |
| `cleanup_eligibility` | Always `not_assessed`; this calculation makes no eligibility decision. |
| `cleanup_authority` | Always `false`; metadata cannot grant permission. |

An open issue has no computed expiry. A closed issue with unknown closure time
returns `unknown`, without falling back to the handoff date. The no-issue case
also returns `unknown` if its handoff timestamp is unavailable. Malformed dates,
timestamps without a timezone and unrecognized issue states are unknown evidence.
An unused handoff timestamp does not prevent calculation from known closure time.

An open issue with a closure timestamp, or closure/state metadata without issue
linkage, returns `conflicting_metadata` and no date. Resolve conflicting evidence
before recomputing; do not choose whichever source would produce an earlier date.
Previously recorded expiration dates are derived observations, not inputs to this
recipe. If such a date disagrees with recomputation, retain the discrepancy for
review rather than treating either value as cleanup authority. Issue-state
freshness and the truth of supplied timestamps require independent verification.

## Structured synthetic input

The rows below are, in order: open issue, closed issue, no linked issue, unknown
closure time and conflicting metadata. All dates are synthetic calendar fixtures.

```json
[
  {"handoff_at": "2028-01-01T06:00:00Z", "issue_ref": "synthetic-issue", "issue_state": "open", "closed_at": null},
  {"handoff_at": "2028-01-01T06:00:00Z", "issue_ref": "synthetic-issue", "issue_state": "closed", "closed_at": "2028-01-31T12:00:00Z"},
  {"handoff_at": "2027-11-30T06:00:00Z", "issue_ref": null, "issue_state": null, "closed_at": null},
  {"handoff_at": "2028-01-01T06:00:00Z", "issue_ref": "synthetic-issue", "issue_state": "closed", "closed_at": null},
  {"handoff_at": "2028-01-01T06:00:00Z", "issue_ref": "synthetic-issue", "issue_state": "open", "closed_at": "2028-01-31T12:00:00Z"}
]
```

## Runnable recipe

Copy the Python block to `recipe.py` and the input block to `input.json` in a
supplied scratch directory. Run `python recipe.py < input.json` there. The only
output is a JSON array on standard output. The focused documentation test extracts
and executes this exact block in its supplied temporary directory.

```python
import json
import sys
from datetime import datetime, timedelta, timezone


def utc_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def expiration(row):
    result = {
        "state": "unknown",
        "expires_at": None,
        "advisory": True,
        "cleanup_eligibility": "not_assessed",
        "cleanup_authority": False,
    }
    if "issue_ref" not in row:
        return result
    issue_ref = row["issue_ref"]
    issue_state = row.get("issue_state")
    closed_at = row.get("closed_at")
    if issue_ref is None:
        if issue_state is not None or closed_at is not None:
            result["state"] = "conflicting_metadata"
            return result
        basis = utc_timestamp(row.get("handoff_at"))
        # Retention policy sections 8.1 and 8.4: fallback from handoff date.
        retention = timedelta(days=90)
        state = "no_issue_fallback"
    elif not isinstance(issue_ref, str) or not issue_ref.strip():
        return result
    elif issue_state == "open":
        result["state"] = (
            "open_issue" if closed_at is None else "conflicting_metadata"
        )
        return result
    elif issue_state == "closed":
        basis = utc_timestamp(closed_at)
        # Retention policy section 8.1; linkage dependency in section 8.4.
        retention = timedelta(days=30)
        state = "closed_issue"
    else:
        return result
    if basis is None:
        return result
    try:
        expires_at = (basis + retention).isoformat().replace("+00:00", "Z")
    except OverflowError:
        return result
    result.update(state=state, expires_at=expires_at)
    return result


if __name__ == "__main__":
    print(json.dumps([expiration(row) for row in json.load(sys.stdin)]))
```

## Explicit expected output

For the closed row, January ends at the supplied closure instant; February in
the synthetic leap year has 29 days, followed by one further day to March 1.
Thus the **30-day interval** from [section 8.1](durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
ends at `2028-03-01T12:00:00Z`.

For the no-issue row, November 30 to December 31 contributes 31 days, then
31 days to January 31, then 28 days to February 28: the **90-day fallback**
from [sections 8.1](durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
and [8.4](durable-vs-transient-knowledge-boundary.md#84-metadata-dependency-codex-finding-c4)
ends at `2028-02-28T06:00:00Z`. These independent calendar sums supply the test
expectations; they are not generated from the recipe's output.

```json
[
  {"state": "open_issue", "expires_at": null, "advisory": true, "cleanup_eligibility": "not_assessed", "cleanup_authority": false},
  {"state": "closed_issue", "expires_at": "2028-03-01T12:00:00Z", "advisory": true, "cleanup_eligibility": "not_assessed", "cleanup_authority": false},
  {"state": "no_issue_fallback", "expires_at": "2028-02-28T06:00:00Z", "advisory": true, "cleanup_eligibility": "not_assessed", "cleanup_authority": false},
  {"state": "unknown", "expires_at": null, "advisory": true, "cleanup_eligibility": "not_assessed", "cleanup_authority": false},
  {"state": "conflicting_metadata", "expires_at": null, "advisory": true, "cleanup_eligibility": "not_assessed", "cleanup_authority": false}
]
```

## Verification and follow-up

Run `uv run --no-project --with pytest python -m pytest tests/docs/test_handoff_expiration_example.py -q -rA -p no:cacheprovider`
with temporary output directed to supplied scratch. The starting focused-test
count was zero because the test file did not exist. The test uses explicit UTC
dates and checks both the documented rows and additional uncertain inputs.
The ending focused-test count is 25 passing cases.

Workflow-wide template adoption, issue-state retrieval, metadata migration,
freshness checks and cleanup automation remain follow-up work. This example
does not establish a new retention policy or resolve other artifact classes.
