# Contributor response examples

This local example supports the response-playbook slice of issue #3637. It maps
synthetic, already classified events to recommendations. It does not ingest live
messages, identify contributors, deliver responses or change repository settings.
It does not complete the epic or establish a deployed response service.

## Basis and boundaries

- Issue #3637 calls for an external-contributor and unsolicited-paid-help
  response runbook, with a defined ingestion vector and privacy boundary.
- The existing [runbook plan](../plans/2026-04-29-issue-2552-external-contributor-runbook.md),
  under "Runbook document outline", distinguishes legitimate contributions,
  unsolicited paid-help offers and private-context onboarding. Its default for
  unsolicited offers is no public engagement. This example's `decline` is a
  recommendation to decline engagement; it sends no reply and performs no
  moderation action. Agreed paid collaboration is outside the example.
- The [public issue projection](../../scripts/lib/issue_publication.py) withholds
  prose fields before public reporting. This example similarly returns fixed
  categories rather than copying event content. It does not call or replace that
  projection, and the categories are not public-response templates.

The ingestion vector here is only a literal in-memory dictionary of boolean
signals. A maintainer would establish those signals separately; no message text
parser, webhook or API adapter is provided. Missing or non-boolean signals lead
to private escalation. Additional metadata is ignored and never rendered.
Synthetic markers in the tests represent withheld content without using private
material or real identities.

`review` recommends maintainer review of an ordinary contribution. It grants no
access and authorizes no merge. `decline` recommends declining unsolicited paid
help without public engagement. `private_escalation` recommends confidential
maintainer review without repeating the request or sending any notification.
It neither authorizes disclosure nor supplies a private contact destination.

## Literal decision table

Private-material requests take precedence over all other signals. Otherwise,
unsolicited paid help takes precedence over an ordinary contribution. An event
with no recognized signal remains unclassified and requires private escalation.
These are example decisions within the cited scope, not platform policy numbers.

| ordinary_contribution | unsolicited_paid_help | requests_private_material | Recommendation |
| --- | --- | --- | --- |
| False | False | False | private_escalation |
| False | False | True | private_escalation |
| False | True | False | decline |
| False | True | True | private_escalation |
| True | False | False | review |
| True | False | True | private_escalation |
| True | True | False | decline |
| True | True | True | private_escalation |

Hand count: each of the three boolean signals has two values, giving eight rows.
The four rows requesting private material and the row with no signal give five
private escalations. Paid help without a private request gives two declines.
The remaining ordinary contribution gives one review. These literal expectations
are independent of the executable classifier.

## Runnable example

This Python block uses built-ins only. Its demonstration prints the categories
for an ordinary contribution, unsolicited paid help and a private-material
request, in that order. It writes no files and makes no external calls.

```python
SIGNALS = (
    "ordinary_contribution",
    "unsolicited_paid_help",
    "requests_private_material",
)


def recommend(event):
    if not isinstance(event, dict):
        return "private_escalation"
    if any(type(event.get(signal)) is not bool for signal in SIGNALS):
        return "private_escalation"
    if event["requests_private_material"]:
        return "private_escalation"
    if event["unsolicited_paid_help"]:
        return "decline"
    if event["ordinary_contribution"]:
        return "review"
    return "private_escalation"


if __name__ == "__main__":
    events = (
        {"ordinary_contribution": True,
         "unsolicited_paid_help": False, "requests_private_material": False},
        {"ordinary_contribution": False,
         "unsolicited_paid_help": True, "requests_private_material": False},
        {"ordinary_contribution": False,
         "unsolicited_paid_help": False, "requests_private_material": True},
    )
    for event in events:
        print(recommend(event))
```

From the repository root, this stdlib-only command extracts and runs that block
without creating a script file:

```sh
python - <<'PY'
from pathlib import Path
import re

text = Path("docs/security/contributor-response-examples.md").read_text()
source, = re.findall(r"^```python\n(.*?)^```$", text, re.M | re.S)
exec(compile(source, "<documented-example>", "exec"), {"__name__": "__main__"})
PY
```

Expected output, hand-derived from the demonstration events and literal table:

```text
review
decline
private_escalation
```

## Verification and limits

The tests in [test_contributor_response_examples.py](../../tests/security/test_contributor_response_examples.py)
extract the Python block and run it in an isolated interpreter without site
packages. An audit hook rejects file opening and audited operating-system,
socket and subprocess operations during the example. The tests check the literal
table against an independent enumeration, run every table row, check the exact
demonstration output, and check private-request precedence with synthetic metadata.
They also exercise incomplete and malformed input. The temporary working
directory remains empty. A successful child process has exit status zero by the
Python subprocess convention; it is not a policy threshold.

The audit hook is a test guard, not a sandbox for untrusted code. The input
contract is limited to synthetic dictionaries; real ingestion, provenance,
message classification and exception handling for hostile objects are untested.
No platform protection audit, interaction-limit renewal or live-data coverage is
claimed. Current interaction settings are not measured here. Any real
contribution path must be checked against current settings by the maintainers;
this example neither assumes that external interactions are enabled nor changes
those controls. The full runbook, approved contact destinations, access decisions,
moderation and outbound responses remain follow-up under issue #3637.
