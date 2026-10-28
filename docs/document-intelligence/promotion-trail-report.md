# Promotion trail evidence report

The reporting-only tool `scripts/knowledge/promotion_trail_report.py` classifies
explicitly supplied promotion evidence as `traced`, `missing`, `ambiguous` or
`legacy`. It addresses the missing-trail report in issue 2382. It records
traceability evidence; it cannot authenticate a promotion decision or rights.
Its evidence mechanisms follow [boundary policy Section 7.4](durable-vs-transient-knowledge-boundary.md#74-auditable-promotion-trail-revised-2026-04-19-resolves-c5).

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-26 | Define the supplied evidence shape and conservative status rules so missing and conflicting trails remain visible. |
| 1 | 2026-10-27 | State the reporting scope, three deliverables and verification plan so the delivery boundary is explicit. |

## Plan-lite

Scope: report explicitly supplied promotion evidence and retain its locators.
The three deliverables are the standard-library reporter
`scripts/knowledge/promotion_trail_report.py`, its literal synthetic tests in
`tests/knowledge/test_promotion_trail_report.py`, and this input-format and
limitations document.

Verification: run the focused tests, compare the documented example with its
hand-classified rows, and run the applicable file-level checks. Page discovery,
referenced-page inspection and authentication of promotion authority, source
identities or reuse rights are excluded.

## Supplied evidence shape

Run from a directory containing an explicitly prepared, synthetic or otherwise
authorized JSON manifest:

```sh
uv run --no-project python scripts/knowledge/promotion_trail_report.py \
  --root . evidence.json
```

The root is an explicit containment boundary for the input manifest, page paths,
source paths and evidence locators. The tool reads only the named manifest.
It does not discover pages, open referenced files, parse Markdown or YAML, fetch
issues, infer promotion eligibility, or write anything. A caller shall supply
the page selection and normalized metadata. This adapter shape does not change
the wiki frontmatter or provenance registry schemas.

```json
{
  "pages": [
    {"page": "wiki/metadata.md", "promoted_from": "sources/run.md#finding"},
    {"page": "wiki/logged.md"},
    {"page": "wiki/registered.md", "doc_key": "summary-key"},
    {"page": "wiki/missing.md"},
    {"page": "wiki/conflict.md", "promoted_from": "#17"},
    {"page": "wiki/old.md", "legacy": {
      "reason": "Predates recorded lineage",
      "locator": "notes/history.md#entry"
    }}
  ],
  "page_logs": [
    {"page": "wiki/logged.md", "locator": "wiki/log.md#entry",
     "promoted_from": "#17"},
    {"page": "wiki/conflict.md", "locator": "wiki/log.md#conflict",
     "promoted_from": "#18"}
  ],
  "registry": [
    {"doc_key": "summary-key", "locator": "registry.jsonl#record",
     "promoted_from": "doc_key:source-key"}
  ]
}
```

`pages` is required; `page_logs` and `registry` default to empty arrays. Every
page has a unique root-relative `page` path and may supply a unique `doc_key`.
Log records bind to a supplied page path. Registry records bind to a supplied
page's exact `doc_key`; no alias or identity resolution is attempted. Unknown
targets, duplicate page identities, unknown fields, malformed record collections
and duplicate JSON keys reject the manifest rather than discard evidence.

`promoted_from` accepts a source string or a nonempty array of source strings:

- A positive decimal issue reference such as `#17`.
- An explicit document identity such as `doc_key:source-key` or
  `doc_key:sha256:abc`. Identity bodies use ASCII letters, digits, underscores,
  periods, colons and hyphens, beginning with a letter or digit. The syntax does
  not validate digests, issue existence or catalog membership.
- A canonical root-relative file path with a suffix, optionally followed by a
  nonempty fragment, such as `sources/run.md#finding`.

Paths use forward slashes and exclude empty, dot and parent components, URI
schemes, percent escapes, query strings, whitespace and Markdown link wrappers.
Absolute paths and paths resolving through symlinks outside the root are invalid.
References are compared literally, including case and fragments; links that might
denote the same artifact are not merged by inference. File existence and fragment
resolution are not checked. These restrictions deliberately support a narrow
normalized input format; arbitrary URLs and unqualified document slugs require
explicit adaptation by the caller.

## Classification and evidence

| Status | Meaning |
| --- | --- |
| `traced` | At least one well-formed trail is supplied and every supplied trail agrees on the complete source set. |
| `missing` | No trail and no legacy declaration is supplied. Missing metadata alone never implies legacy. |
| `ambiguous` | Evidence is malformed, source sets disagree, or a legacy declaration accompanies promotion evidence. A valid trail cannot hide another malformed trail. |
| `legacy` | A legacy declaration explicitly supplies a nonempty reason and valid relative evidence locator, with no promotion trail. This is a declaration, not an exemption or authenticated finding. |

Source arrays describe the complete claimed lineage for each trail. Order and
duplicates do not matter; a partial overlap between source sets is disagreement.
The union of valid source references is reported even when evidence conflicts.
Malformed `promoted_from`, log locators and legacy declarations produce
`ambiguous`, whereas unsafe page paths reject the manifest itself.

Output is a JSON array sorted by page path. Each row contains `page`, `status`,
sorted `sources`, sorted `errors` and `evidence`. Evidence retains its `mechanism`,
`locator`, valid `sources` and `errors`; legacy evidence also retains its `reason`.
Metadata evidence uses the page path plus `#promoted_from`. Supplied log, registry
and legacy locators are retained unchanged, including malformed locator values
for diagnosis. Callers shall keep restricted input and output private.

For the literal example above, the following rows are hand classified by the
rules in this section; identifiers are synthetic, not observations of live pages:

| Page | Status | Sources |
| --- | --- | --- |
| `wiki/conflict.md` | `ambiguous` | `#17`, `#18` |
| `wiki/logged.md` | `traced` | `#17` |
| `wiki/metadata.md` | `traced` | `sources/run.md#finding` |
| `wiki/missing.md` | `missing` | empty |
| `wiki/old.md` | `legacy` | empty |
| `wiki/registered.md` | `traced` | `doc_key:source-key` |

The CLI returns zero when it successfully produces a report, regardless of row
statuses. Invalid input returns the argparse conventional usage-error code and
a generic diagnostic that does not echo filesystem paths. No hook, gate,
scheduler, backfill, content modification or publication integration is added.

## Verification and limitations

The new-suite baseline is zero collected, passed, failed and skipped tests because
the suite did not exist at the base revision. No live wiki census is claimed.
The focused check uses temporary, literal synthetic inputs and independently
hand-classified expected rows:

```sh
uv run --no-project --with pytest python -m pytest \
  tests/knowledge/test_promotion_trail_report.py -q -rA -p no:cacheprovider
```

Coverage includes separate evidence mechanisms, agreeing and conflicting trails,
malformed references, explicit legacy declarations, deterministic ordering,
root containment and a CLI preservation check. Files and issue references are
not dereferenced. A `traced` result establishes supplied syntactic consistency
only; it cannot establish source truth, promotion authority or reuse rights.
