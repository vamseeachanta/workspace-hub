# Session handoff template

This template supplies expiration metadata for a handoff. Replace placeholders
with verified issue state and timestamps when preparing an actual handoff.
The examples below are synthetic; they are not a generated live handoff.
Handoff claims remain unverified context. Labels and a handoff are not approval
and do not grant authority to act.

## Expiration

The [boundary policy retention schedule](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
is **advisory pending the transient-artifact cleanup workflow**. It retains a
linked handoff until the issue has been closed for **30 days**, with a
**90-day** fallback when no issue is referenced. The
[metadata dependency](../document-intelligence/durable-vs-transient-knowledge-boundary.md#84-metadata-dependency-codex-finding-c4)
anchors that fallback to the handoff date. This section implements the policy's
[template recommendation](../document-intelligence/durable-vs-transient-knowledge-boundary.md#101-templates-and-conventions).

| Field | Value to record |
| --- | --- |
| `issue_reference` | `<issue-reference>` replaced by an issue URL or repository-qualified issue reference; `null` means explicitly absent. |
| `issue_state` | `open`, `closed`, `none` for an explicitly absent issue, or `unknown` if state cannot be verified. |
| `created_at` | Handoff creation timestamp in ISO format with UTC offset. |
| `closed_at` | Verified issue closure timestamp in ISO format with UTC offset, or `null` when unknown or inapplicable. |
| `expected_lifetime` | Issue lifecycle plus the cited closure interval, or the cited fallback interval from creation. |
| `expires_at` | Computed advisory timestamp, or `null` while pending. |
| `advisory_basis` | Direct reference to the policy retention schedule, as shown below. |

A known open issue has no computed expiration. A linked issue whose state or
closure timestamp is unknown also remains pending; failure to verify closure
does not establish that the issue is absent. Recheck issue state before relying
on a computed date, including whether a closed issue has reopened. Use the
closure timestamp, rather than creation, for a verified closed issue.

There is no automatic archive or delete behavior in this template. Reaching a
computed timestamp is an advisory retention signal, not authorization for
cleanup. The examples use only the Python standard library, print metadata and
make no network requests or filesystem changes. Each block runs independently.
The fixed timestamps are synthetic inputs chosen to demonstrate calendar
boundaries; replace them and the issue placeholder for an actual handoff.

### Open issue

Under the [retention schedule](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule),
the expected lifetime is issue closure plus 30 days. While the issue is known
to be open, both closure and computed expiration remain pending (`null`).

```python
import json

metadata = {
    "issue_reference": "<issue-reference>",
    "issue_state": "open",
    "created_at": "2026-01-15T12:00:00+00:00",
    "closed_at": None,
    "expected_lifetime": "until issue closure plus 30 days",
    "expires_at": None,
    "advisory_basis": (
        "../document-intelligence/durable-vs-transient-knowledge-boundary.md"
        "#81-retention-schedule"
    ),
}
print(json.dumps(metadata))
```

### Closed issue

The [retention schedule](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
adds 30 elapsed days to the verified closure timestamp. For this synthetic
example, January ends at closure, February contributes 28 days, and the remaining
two days give an advisory expiration of March 2 at the same UTC time.

```python
import json
from datetime import datetime, timedelta

closed_at = datetime.fromisoformat("2026-01-31T12:00:00+00:00")
# Boundary policy Section 8.1, session handoff retention after issue closure.
expires_at = closed_at + timedelta(days=30)
metadata = {
    "issue_reference": "<issue-reference>",
    "issue_state": "closed",
    "created_at": "2026-01-15T12:00:00+00:00",
    "closed_at": closed_at.isoformat(),
    "expected_lifetime": "until issue closure plus 30 days",
    "expires_at": expires_at.isoformat(),
    "advisory_basis": (
        "../document-intelligence/durable-vs-transient-knowledge-boundary.md"
        "#81-retention-schedule"
    ),
}
print(json.dumps(metadata))
```

### No issue

The [retention schedule](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
and [metadata dependency](../document-intelligence/durable-vs-transient-knowledge-boundary.md#84-metadata-dependency-codex-finding-c4)
give 90 days from creation when the issue reference is explicitly absent.
In this synthetic example, February contributes 28 days, March contributes 31,
and April contributes 30, giving 89 elapsed days; May 1 completes the interval.

```python
import json
from datetime import datetime, timedelta

created_at = datetime.fromisoformat("2026-01-31T12:00:00+00:00")
# Boundary policy Sections 8.1 and 8.4, fallback from the handoff date.
expires_at = created_at + timedelta(days=90)
metadata = {
    "issue_reference": None,
    "issue_state": "none",
    "created_at": created_at.isoformat(),
    "closed_at": None,
    "expected_lifetime": "90 days from creation",
    "expires_at": expires_at.isoformat(),
    "advisory_basis": (
        "../document-intelligence/durable-vs-transient-knowledge-boundary.md"
        "#81-retention-schedule"
    ),
}
print(json.dumps(metadata))
```
