# Provider auto-label explanations

The auto-labeler reads a work queue and writes candidate reports. Its default
mode performs no GitHub reads or writes. `--comment` alone also leaves GitHub
untouched. Confidence scoring, the eligibility threshold and the public issue
projection remain unchanged.

To opt in to explanations when applying labels, pass both `--apply` and
`--comment` to `scripts/ai/provider-autolabel.py`. Use `--work-queue`,
`--output-json` and `--output-md` to select inputs and report destinations.
`--limit` continues to bound eligible candidates considered per run; skipped
candidates do not cause additional candidates beyond that bound to be attempted.
Applying without `--comment` remains label-only.

Before applying a label, the script reads current issue labels. Any `ai:` or
legacy `agent:` label suppresses writes, including a manually assigned label
missing from stale queue input. With `--comment`, it also reads every page of
comments before either write. A stable hidden marker binds the explanation to
the target issue number and provider label in the current repository. An
existing matching marker suppresses both writes, even after label removal;
markers for other issues or labels do not suppress the target action.

After a successful new label, the explanation contains only the target label,
confidence, a recognized routing reason, provider priority and execution-ready
state, followed by the marker. It excludes issue titles, bodies, identities and
private telemetry. Unknown routing reasons and priorities render as unavailable
rather than copying arbitrary metadata.

Unavailable or malformed label or comment reads abort before a write. A failed
label application produces no explanation. If the label succeeds but posting the
comment fails, the error is reported; a later run sees the label and does not
backfill a comment or claim a manual label. These operations are not atomic.
Concurrent distributed writers are outside this bounded single-writer mode:
reads do not lock the issue against another writer between the reads and writes.

The focused suite uses local GitHub stubs, fixture queues and temporary report
paths. It rejects unstubbed subprocess calls. No live apply is needed to test
this mode:

```sh
uv run --no-project --with pytest python -m pytest tests/analysis/test_provider_autolabel.py -q -rA -p no:cacheprovider
```
