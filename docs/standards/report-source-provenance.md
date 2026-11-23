# Report source provenance

The standalone verifier checks exact source bytes, pinned reader links and
prerequisite continuity. A content match does not establish engineering
acceptance, source rights, execution provenance or remote publication.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Define scoped byte checks and prerequisite retention to prevent false source mismatches and silent loss of unresolved requirements. |
| Decoder boundary | 2026-10-26 | Document the detached decoder-error contract and deterministic regression strategy without changing acceptance rules. |

## Method and sources

For a byte sequence B, the recorded value is d = SHA-256(B). Verification
requires exact equality with the digest of the identified representation.
There is no line-ending conversion, decoding, whitespace removal or tolerance.
The digest is lowercase hexadecimal without a prefix. It is a content digest,
not a Git object identifier; optional `git_blob_oid` records the latter separately.

The method follows [RFC 6234 (2011), sections 6 and 8.5](https://www.rfc-editor.org/rfc/rfc6234).
The [Git gitattributes manual, text and eol attributes](https://git-scm.com/docs/gitattributes)
explains why checkout line endings can differ from stored blobs. The
[Git cat-file manual, OPTIONS](https://git-scm.com/docs/git-cat-file) defines
raw object reads separately from `--filters` and `--textconv`; the verifier uses
neither transformation. The [Git ls-tree manual, OUTPUT FORMAT](https://git-scm.com/docs/git-ls-tree)
defines the mode, type, object and path fields used to identify regular blobs.
The [Git index format, Index entry](https://git-scm.com/docs/gitformat-index)
defines the regular-file type bits and permitted file modes.
These online Git manuals were consulted on 2026-10-22.

A source's `revision` must be the complete commit identifier available in the
specified repository. Branch names, tags and abbreviated identifiers are rejected.
Git replacement objects and inherited repository bindings are disabled for reads.
The repository argument must identify the checkout root, including a linked
worktree root. Only regular files are supported. Symlinks and submodules are
rejected. A blob may be verified even when its checkout file is absent.

## Sidecar contract and use

The JSON sidecar requires `schema: "report-provenance-v1"`, `report_id`, a string
report `revision`, `repository_url`, a nonempty `sources` list and a `prerequisites`
list, which may be empty. Source identifiers and prerequisite identifiers are
unique within their respective lists. Duplicate JSON fields and non-finite
JSON constants are rejected. The checker does not modify the sidecar or sources.

Each source requires `source_id`, repository-relative POSIX `path`, immutable
`revision`, `byte_scope` and `sha256`. Choose the scope explicitly:

| Scope | Bytes checked | Reader link |
| --- | --- | --- |
| `checkout-bytes` | Current file bytes, including any local conversion or edit | Omitted; a Git hosting link cannot identify a local observation |
| `git-blob-bytes` | Blob content at the pinned commit, without filters | Required and matched to repository, commit and path |

Both scopes may describe the same path at the same baseline revision using
different source identifiers. The checkout revision identifies its baseline;
it does not assert that the current file equals that baseline or was executed.
Checkout files must remain stable while being captured or checked.

The repository URL must use HTTPS and the canonical GitHub repository form.
Reader links support GitHub `blob` permalinks and `raw.githubusercontent.com`
URLs. Query strings and fragments are rejected. Percent-encoded paths are
compared after URL decoding. See [GitHub's permanent-link documentation](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files).
A local match does not authenticate the repository URL or prove that the
corresponding object has been pushed or is accessible to the reader.

Run against a supplied sidecar and a local repository:

```sh
uv run --no-project python scripts/reporting/report_provenance.py \
  report.provenance.json --repository .
```

For a replacement report, provide the exact predecessor sidecar bytes:

```sh
uv run --no-project python scripts/reporting/report_provenance.py \
  replacement.provenance.json --repository . --previous issued.provenance.json
```

The Python API `capture_source` constructs a source entry from the explicit
repository, source identifier, path, revision, scope and repository URL; blob
entries also require `reader_url`. Persist its returned values unchanged.
`load_manifest` parses sidecar bytes. `check_manifest` returns separate source
and supersession diagnostics, retaining source results after a continuity failure.

`PASS` means every declared byte claim and applicable continuity check passed,
with at least one checked reader link. `NOT_EVALUATED` means all byte checks
passed but there is no reader link, as for a checkout-only sidecar. The command
exits successfully only for `PASS`; malformed inputs, mismatches and
`NOT_EVALUATED` return a failure exit code. A first report has supersession
status `NOT_APPLICABLE`. An unmet prerequisite does not prevent a provenance
`PASS`: its engineering status remains explicitly unmet.

## Supersession and prerequisite disposition

Each prerequisite has a stable `id` and `status: "met"` or `"unmet"`. The replacement
sidecar carries `supersedes` with the predecessor's `report_id`, report `revision`
and SHA-256 of the exact predecessor sidecar bytes. The report identity must
remain the same and the report revision must change. Reserializing the predecessor
changes its digest. Supplying `--previous` without a pointer is rejected.

Every unmet predecessor prerequisite follows this issue-derived truth table:

| Current entry | Explicit disposition | Result |
| --- | --- | --- |
| Same identifier, still unmet | None | Retained; continuity passes |
| Same identifier, met | None | Fails: relabeling cannot establish satisfaction |
| Absent | None | Fails: omission cannot erase the prerequisite |
| Same identifier, met | `satisfied` | Passes continuity with a reason and pinned evidence source |
| Absent | `withdrawn` | Passes continuity with a reason and pinned evidence source |
| Any other combination | Any | Fails |

Dispositions use `id`, `action`, a nonempty `reason` and `evidence_source_id`
referring to a `git-blob-bytes` source in the replacement. Evidence digest checks
must pass for the overall check to pass. Duplicate, unknown or contradictory
dispositions fail. For example:

```json
{
  "id": "qualified-quantity",
  "action": "satisfied",
  "reason": "The qualified quantity is established in the linked assessment.",
  "evidence_source_id": "assessment"
}
```

This records a disposition, not its engineering correctness or authorization.
The maintainer must establish that the predecessor is the actual issued revision
and that the disposition is valid. Omitting both the predecessor argument and
pointer cannot reveal an undeclared history. Carry every unresolved prerequisite
forward to preserve continuity through later revisions. Issued archives and raw
source evidence remain unchanged.

## Worked example

[The example sidecar](../../examples/reporting/provenance-sidecar.json) uses a
synthetic repository and commit created by the regression fixture. Its links
are illustrative and are not claimed to exist remotely. The fixture defines:

| Representation | Literal bytes in hexadecimal | Independent digest oracle |
| --- | --- | --- |
| Stored Git blob | `61 62 63 0a` (`abc` plus LF) | `edeaaff3f1774ad2888673770c6d64097e391bc362d7d6fb34982ddf0efd18cb` |
| Checkout file | `61 62 63 0d 0a` (`abc` plus CRLF) | `552bab6864c7a7b69a502ed1854b9245c0e1a30f008aaa0b281da62585fdb025` |

The newline oracles were calculated independently using `sha256sum` over
`printf 'abc\n'` and `printf 'abc\r\n'`. The suite separately checks the published
RFC 6234 section 8.5 SHA256 test 1 for literal `abc` without a newline.

The verifier reads the pinned LF blob for `published-input` and the CRLF file
for `checkout-input`. Both hashes match their declared scopes, so the answer
is provenance `PASS`. Substituting the checkout digest into the published entry
gives `FAIL: digest mismatch`. Neither outcome changes the unmet
`qualified-quantity` prerequisite.

Run the executable worked-example regression:

```sh
uv run --no-project --with pytest --with PyYAML python -m pytest \
  tests/reporting/test_report_provenance.py -k documented_worked_sidecar -q
```

## Plan-lite: manifest decoding

Production changes are confined to `load_manifest`. Decoder `ValueError`
(including syntax and encoding errors), `RecursionError`, `OverflowError` and
`MemoryError` become `ProvenanceError` with the message
`invalid or ambiguous JSON manifest`. Raising after the handler leaves neither
an explicit cause nor an implicit decoder exception context on that error.

The regression strategy injects resource errors deterministically and checks
the public message, detached cause and context, and formatted traceback.
Malformed syntax and UTF-8, duplicate keys, non-finite constants and bounded
nesting exercise rejection; literal valid-input oracles exercise string, bytes
and bytearray inputs. The executable cases are in
`tests/reporting/test_manifest_decoder_boundary.py`; the existing provenance
suite checks that source and prerequisite behavior remains unchanged.

Duplicate-key and non-finite-token rejection and valid-input acceptance remain
unchanged. No input-size or numeric limits are added. These tests do not exhaust
memory, bound decoder work or guarantee recovery from actual memory exhaustion.

## Coverage and limits

Tests cover exact newline bytes, a published SHA-256 vector, immutable revision
and link matching, malformed input, source diagnostics after failure,
repository-variable isolation, symlink rejection, predecessor digest binding,
and prerequisite carry-forward and disposition. No physical coefficients or
engineering acceptance limits are introduced.

This is an opt-in sidecar checker. It does not change the calculation renderer,
existing report schemas, archived reports or source normalization policy.
Automatic rendering/publication integration, remote availability checks,
non-GitHub link formats, LFS payload resolution and authenticated engineering
approval are follow-up work. LFS pointer bytes, if present, are ordinary stored
blob bytes; they must never be described as the downloaded payload.
