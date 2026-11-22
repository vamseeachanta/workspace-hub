# Issue prose in public control reports

Public control reports withhold issue titles, bodies, body excerpts and plan
prose. They retain references and classification results so that readers can
open the authoritative issue using their own access. This implements recurrence
prevention for issue #3768; it does not claim to remove historical disclosures.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Define public report projection and test the remaining writers to prevent issue prose disclosure. |

## Publication boundary

The existing local-only mirror policy in the root `.gitignore` remains in force.
Ignored files are working copies, not public publication targets. Copying them
to another destination requires a separate publication review. A successful
local identifier scan without a private map does not establish publishability.

| Writer | Boundary |
|---|---|
| `scripts/kanban/reconcile.py` | Generated boards remain ignored and untracked; the authored ecosystem board is separate. |
| `scripts/dispatch/dispatch.py` | Public queues already omit titles. |
| `scripts/ai/provider-kanban.py` | Generated JSON, Markdown and HTML remain local only, including plan hover prose. |
| `scripts/ai/provider-work-queue.py` | Generated JSON and Markdown remain local only. Classification may use source prose locally. |
| `scripts/ai/continuous-planning-pipeline.py` | Public title fields are fixed markers; JSON and Markdown also project legacy input. |
| `scripts/ai/provider-autolabel.py` | Candidate copying withholds prose after confidence calculation; Markdown projects legacy input. |
| `scripts/refresh-agent-work-queue.py` | Every public issue row displays a fixed marker. |
| `scripts/cron/ecosystem-rework-retriage.sh` | State queries do not fetch titles; new-candidate rows display a fixed marker. |
| `scripts/ai/build-orca-kanban.py` | Generated JSON and HTML remain local only. |
| `scripts/kanban/domain_coverage.py` | Public Markdown summaries and JSON withhold titles; violation counts remain unchanged. |

The shared `scripts/lib/issue_publication.py` projection recursively copies
structured reports. Fields named `title`, `body`, `body_excerpt`, `plan_summary`,
`risks` and `tests` become `[withheld; see issue]`. It preserves field names for
existing consumers and never mutates its input. Repeated projection gives the
same result. Classification must precede projection when it needs source prose.

This is a field contract rather than a private deny-list replacement or a general
secret scanner. Unknown prose fields require explicit review before adding a
public writer. Repository references, URLs, labels, paths and other metadata are
outside this projection; their presence does not imply authorization to publish
them. Existing secret checks remain independent.

## Worked example

Input, entirely synthetic:

```json
{"number": 1, "title": "synthetic unpublished prose", "body_excerpt": "synthetic details", "url": "https://example.test/issues/1", "execution_ready": true}
```

Method: apply `public_issue_view` after classification. Replace the two prose
values with the literal marker and copy the remaining fields without alteration.
No equation, numerical coefficient or engineering acceptance limit is involved.
The expected answer is obtained by inspecting the field names:

```json
{"number": 1, "title": "[withheld; see issue]", "body_excerpt": "[withheld; see issue]", "url": "https://example.test/issues/1", "execution_ready": true}
```

The regression tests in `tests/legal/test_issue_publication.py` check this rule,
nested prose, unchanged source objects, repeated projection, legacy inputs,
retained references, public command output and local-only boundaries. The
retriage regression also checks its written report. Expected values are literal
field substitutions and hand counts, independent of the code under test.

## Verification and limits

Run the new regression tests and the existing suites for planning, autolabel,
domain coverage, queue refresh and retriage. Run Ruff on touched Python files and
`bash -n` on the retriage script. Existing local-mirror and dispatch tests verify
the publication boundaries that this change preserves.

Existing tracked snapshots are not regenerated or hand-edited here. Regeneration
must use the corrected writers and receive publication review of the resulting
metadata. Git history and other historical documents require separate maintainer
remediation; no history rewrite or deletion is performed. Source rights and
access controls continue to apply to local copies. Second-provider review is
required before merge and is not established by these tests.

## Sources

- Issue #3768 (2026): writer inventory, public Actions summary disclosure and
  the limitation of map-dependent scanning.
- Linked issues #3763, #3755 and #3149 (2026): title-fetch regression, generated
  mirror remediation at the source and damage from broad text substitutions.
- Root `.gitignore`, generated-board policy, and
  `tests/test_kanban_reconcile.py`: current local-only mirror boundary.
- `scripts/dispatch/dispatch.py`, `TITLE_POLICY`, and
  `tests/dispatch/test_queue_omits_issue_titles.py`: public queue omission contract.
