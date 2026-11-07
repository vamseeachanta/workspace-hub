# Byte preservation in bounded repository rewrites

## Summary

Text capture changes CRLF delimiters before a token edit can begin. Binary
capture and explicit byte replacement retain the independent literal payloads
tested here. In the inspected sample, the existing pointer repair already uses
byte I/O; the path migration can normalize unrelated delimiters during a rewrite;
the review-page builder consumes textual metadata and deliberately regenerates
JSON and HTML. These classifications do not establish repository-wide safety.
The broader audit in issue #4089 remains open.

## Revision history

| Revision | Date | What changed and why |
| --- | --- | --- |
| Initial | 2026-10-28 | Classify the selected read/write boundaries and add a synthetic executable example to distinguish metadata interpretation from payload preservation. |

## Evidence and scope

The main pin, abbreviated **P** in every boundary row, is
`1d9ea1140511a778dc8a75b41b230b3cc7ada328`. Initial `git status --porcelain`
was empty; `git rev-parse HEAD origin/main` returned this same revision for both
refs. Source lines below refer to P, not to a moving branch. All of each named
helper was read, and its working-tree bytes were compared with its blob at P:

| Source key | Inspected helper | Complete source interval at P |
| --- | --- | --- |
| R | [Pointer-repair helper](../../scripts/readiness/repair-sibling-sso-flow.py) | Lines 1–404 |
| M | [Path-migration helper](../../scripts/data/document-index/migrate-canonical-paths.py) | Lines 1–189 |
| B | [Review-page builder](../../scripts/workflow/build_session_review.py) | Lines 1–355 |

The intervals and call references are from the numbered source at P. The
preservation promise is taken from the code docstrings and the relevant design
text, rather than inferred from the presence of `text=True` alone:

- R:295–311 promises a bounded pointer-line edit without modifying arbitrary
  prose. The existing byte tests supply the delimiter and encoding criterion.
- The [migration design](../plans/2026-07-02-issue-3337-canonical-path-normalization.md),
  section “One-time, idempotent config rewriter”, promises text substitution
  preserving comments, key order, quoting and formatting, plus parse equivalence.
- B:5–23, 197–233 and 295–313 describe generated pages, a sorted manifest and
  derived references. The [derivation design](../plans/2026-06-28-issue-3311-derive-from-git.md)
  describes metadata extraction, not restoration of source blobs.

## Inspected read/write boundaries

Default Python text reads use universal newline handling and an implicit
encoding unless an encoding is supplied. Text writes use platform newline
translation; on the tested Linux environment the written delimiter is LF.
Strict decoding can reject undecodable input. Binary reads and writes have no
newline or encoding translation. These are the I/O distinctions exercised by
the synthetic example and the migration reproduction below.

| Main pin | Source line at pin | Input kind | Documented preservation promise | Actual newline / encoding behavior | Destination | Conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| P | R:27–58; callers R:49–54, 129–155, 169–172 | Process output: filesystem type, Git status, branch, upstream and revision counts, file-type description | Interpret command metadata; no blob restoration contract | `text=True` implicitly decodes stdout/stderr, normalizes CRLF/CR to LF; callers strip or split text | Preflight decisions and diagnostics controlling R:373–379; file-type verification after R:347 | Metadata-to-control path, not captured payload-to-file. No `git show` or blob output is requested by these callers. |
| P | R:34–46; caller R:365 | Label-query process output | Interpret labels; no byte identity promise | Text capture and `splitlines()` | Apply admission decision | Control metadata only, never used as rewritten file content. |
| P | R:62 | Current-tree marker bytes | Recognize a file marker | `read_bytes()` then prefix comparison | Classification feeding R:281 | No content serialization; classification can select deliberate link replacement. |
| P | R:67, 81, 107–108, 161 | Symlink target | Compare or restore an owned target | `os.readlink()` returns filesystem text; `symlink_to()` writes a target, not file payload | Replacement or rollback symlink | Filesystem metadata path; no newline-normalizing payload I/O. |
| P | R:86 → 110–111; caller R:336, 359 | Owned regular-file snapshot and mode | Restore started actions on failure | `read_bytes()` / `write_bytes()` retain payload bytes; mode restored separately | Original owned file during rollback | Byte-preserving snapshot boundary; concurrency and ownership are distinct concerns. |
| P | R:175–176; caller R:258–287 | Registry YAML | Parse configuration; no original-spelling promise | Default text read then `yaml.safe_load()` | In-memory repair manifest and selected paths/targets | Read-only interpretation. The registry is not rewritten. |
| P | R:227; caller R:285–287 | Current-tree pointer file for classification | Identify eligible pointer patterns | Default text read with `errors="replace"`; newline normalization and replacement characters possible | Action metadata carrying path and old/new pointer strings | Lossy classification view is not written back; the actual payload is reread as bytes at R:300. |
| P | R:295–311; caller R:351–352 | Current-tree pointer-file payload | Edit only eligible contract-pointer lines | Byte read, explicit UTF-8 with `surrogateescape`, `splitlines(keepends=True)`, same-handler encode, byte write | Same pointer file | Positive control: unchanged delimiters and undecodable bytes survive the tested bounded edits. |
| P | R:353–355 | Post-write pointer file | Detect remaining stale pointers | Lossy text view with `errors="replace"` as in classification | Verification decision; failure selects byte rollback | No second text write. This check alone does not prove byte identity. |
| P | R:321–361, 375–398 | Action dictionaries, exceptions and diagnostic strings | Apply selected actions; serialize diagnostics | JSON serialization or `print()` to process streams | stdout/stderr; symlink writes at R:347 and byte writes through R:352 | No command stdout becomes file payload. Symlink recreation is deliberate replacement, not byte editing of its former marker file. |
| P | M:166 via `_pathnorm_shim.py:16` and `scripts/data/drive-index-search/pathnorm.py:13–27` | Alias-registry YAML | Parse and validate mapping values | Default text read and YAML parse; returned aliases are sorted and stripped of trailing separators | In-memory alias map for M:176 | Configuration interpretation, not registry rewriting. |
| P | M:144 → 145–146 | Current-tree YAML/JSON payload | Preserve formatting during path substitution, with deliberate metadata edits | `read_text()` normalizes delimiters before `_rewrite_aliases()` and `_rewrite_config_metadata()`; implicit strict encoding | Staged text at M:152 | Unsafe for a bounded byte-preservation contract: untouched delimiters can change whenever a write is triggered. |
| P | M:42–64, 97–128 | Text already read from the target | Substitute aliases; annotate exceptions and enforce configuration metadata | `keepends=True` retains only the delimiters still present after reading. Exception annotation and warning/disabled-field edits introduce explicit LF | Returned string consumed by M:149–152 | Additional deliberate edits must be distinguished from unrelated byte churn; a future fix must specify delimiters for inserted lines. |
| P | M:131–140, 149 | Before/after text | Parse equivalence modulo allowed changes | JSON/YAML parsing ignores many lexical differences, including delimiters; no file write here | Validation decision | Parse equivalence does not establish byte preservation. |
| P | M:147–154; caller M:164–178 | Rewritten string | Write only if changed; stage and replace target | `write_text()` uses implicit encoding and platform newlines, then `.tmp` replaces target; check mode never writes | Same target through adjacent staging file | Replacement staging does not recover lost input bytes. No-change branch returns before writing; line-ending loss is not persisted on that branch. |
| P | B:290–305, 334–338 | Git log messages, changed filenames, branch and merge-base identifiers | Extract reference metadata | Text capture, stripping, NUL-separated message parsing and line-separated filenames | Derived payload → optional JSON output or B:348 `build()` | Subprocess-to-generated-output path is intentional interpretation, not token repair of Git blob bytes. Unusual filename quoting/encoding is a separate, unqualified limit. |
| P | B:330 via `scripts/workflow/session_review_sanitize.py:40–54` | Deny-pattern YAML configuration | Load patterns for output sanitization | Explicit UTF-8 text read and YAML parse | In-memory patterns used by B:218, 226 | Read-only interpretation; sanitization deliberately transforms generated text. |
| P | B:343 → 348 | Manual JSON input | Parse a payload for rendering | Explicit UTF-8 text read and `json.loads()`; delimiters normalized before parsing | Sanitized generated page and manifest | Input payload is not overwritten; no byte identity promise for generated artifacts. |
| P | B:201 → 202–205; caller B:231 | Existing JSON manifest | Replace entry by slug, sort newest-first and persist | UTF-8 read, parse, filter/append/sort, `json.dumps(indent=2)` and trailing LF; platform text write | Same manifest | Deliberate JSON reserialization. Whitespace, escape spelling and original delimiters are not preserved by contract. |
| P | B:224–227 | Sanitized payload rendered to HTML text | Generate a public page, not preserve an old page | Rendered string written as UTF-8 with platform newlines | Generated page | Existing destination is regenerated intentionally; no source-blob repair path. |
| P | B:232 | Manifest entries rendered to index HTML | Regenerate rolling index | UTF-8 text write with platform newlines | Generated index | Deliberate regeneration. |
| P | B:338 | Derived in-memory payload | Emit JSON for curation | `json.dumps(indent=2)` plus trailing LF, explicit UTF-8 text write | Requested payload output | Deliberate serialization; not byte-preserving mutation of Git output. |
| P | B:339–340, 349–350 | Output path and reference-count metadata | Report generated artifacts | Text `print()` | stdout only | Diagnostics, not a payload rewrite. |

M has no subprocess call. R's command results select actions, while its payload
mutation reads the current file independently. B's Git output feeds a new data
model and generated files. None of these inspected call paths captures
`git show` payload bytes and writes them back. That observation is limited to
the callers in this table; it does not qualify generic wrappers for future
payload callers.

## Executable example

This is the only Python fence in this document. The
[example tests](../../tests/docs/test_byte_preservation_audit_example.py) extract
and execute it with scratch as the working directory. The child writes the
literal acceptance payload supplied in issue #4089; no Git command, production
utility or private content is involved. The expected output is written
independently as a literal, not computed by another replacement.

```python
import subprocess
import sys

child = "import sys; sys.stdout.buffer.write(b'alpha\\r\\nbeta\\r\\n')"
command = [sys.executable, "-c", child]
binary_capture = subprocess.run(command, capture_output=True, check=True).stdout
text_capture = subprocess.run(command, capture_output=True, text=True, check=True).stdout
assert binary_capture == b"alpha\r\nbeta\r\n"
assert text_capture == "alpha\nbeta\n"


def replace_token(payload):
    return payload.replace(b"alpha", b"gamma")


rewritten = replace_token(binary_capture)
assert rewritten == b"gamma\r\nbeta\r\n"
```

The byte escapes are literal synthetic fixture delimiters and invalid UTF-8
sentinels, not engineering constants. The independent hand calculation for
every fixture is: spell `gamma` wherever the literal `alpha` occurred, and
copy all other bytes exactly. The test fixtures enumerate CRLF, LF, CR, mixed
CRLF/LF/CR, an unterminated final line, undecodable bytes and a no-match payload.
Equality checks the complete payload, including delimiters, rather than a
decoded substring or a length derived from the implementation. The lossy text
assertion is a calibration control, not desired payload behavior.

## Existing pointer-repair positive control

[The independent pointer tests](../../tests/readiness/test_sibling_sso_pointer_bytes.py)
exercise R:295–311 directly against disposable files, without running the repair
entry point. The parametrized test at line 23 substitutes only the contract
pointer with independently constructed expected segments, including LF, CRLF,
CR, optional BOM and optional final delimiter, and repeats the edit for
idempotence. The test at line 51 checks mixed endings, valid UTF-8, undecodable
bytes and an unterminated tail against a separate literal. The test at line 83
requires exact byte identity when no eligible line matches. This audit reuses
those tests and does not implement a second pointer repair.

## Bounded finding and follow-up

**Path migration: unrelated delimiters can change.** Reproduction of the I/O
boundary uses only synthetic scratch content and the same standard-library
operations as M:144 and M:152–153; it does not invoke or import the migration.
The independently specified Linux trace is:

```text
Input file bytes:       b"path: alpha/item\r\nnote: unchanged\r\n"
read_text() result:     "path: alpha/item\nnote: unchanged\n"
Alias substitution:    "path: gamma/item\nnote: unchanged\n"
write_text + replace:  b"path: gamma/item\nnote: unchanged\n"
Bounded byte oracle:   b"path: gamma/item\r\nnote: unchanged\r\n"
```

This primitive trace was executed in scratch. Both parses remain equivalent
after mapping the alias, but the unrelated note delimiter changes. Without an
alias or deliberate metadata change, M:147–148 returns without writing. With
undecodable input, the implicit strict decoder can reject the read instead of
silently preserving bytes. The annotation and configuration insertion branches
also deliberately add lines; their newline policy is presently implicit.

Follow-up under issue #4089: constrain a migration-only change to define the
encoding and insertion-delimiter policy, retain unrelated original bytes, and
add literal byte tests for alias-only edits, annotation/configuration insertions,
check/no-change behavior and idempotence. Preserve the existing structural
equivalence guard. No production utility is repaired in this audit. No additional
payload mutation defect was established in R or B under their inspected contracts.

## Verification

Counts below come from the local pytest collection/execution on 2026-10-28;
they are case counts, not a repository coverage metric.

| Run | Collected | Passed | Failed | Skipped |
| --- | --- | --- | --- | --- |
| Before: existing pointer file | 14 | 14 | 0 | 0 |
| After: existing pointer file | 14 | 14 | 0 | 0 |
| After: new example file | 8 | 8 | 0 | 0 |
| After: combined required run | 22 | 22 | 0 | 0 |

The example tests were written first and initially produced setup errors because
this document did not yet exist. The completed example then passed. The required
combined command, with scratch variables supplied by the execution environment,
was:

```sh
uv run --no-project --with pytest --with PyYAML python -m pytest tests/readiness/test_sibling_sso_pointer_bytes.py tests/docs/test_byte_preservation_audit_example.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/bt-combined"
```

The command was invoked through the configured absolute uv executable, with
scratch basetemp and redirected logs. Checks run on the uncommitted tree.
No repair, migration, build or rollout entry point was executed. Other existing
tests listed below were inspected, not run; the scope of the executed positive
control is the pointer function and the synthetic example only.

Direct file checks also passed: the engineering-register checker reported no
violations for this report; whitespace checks included each new file; the
configured secret scanner and the publication-form scan found no findings in
the deliverables and publishing text. File-list validation found only the
report and its example test, neither ignored nor LFS-tracked. Cleanup classified
these uncommitted deliverables and scratch evidence as expected residue.

## Inspected context and coverage gaps

In addition to the complete R/M/B sources, the inspected context was:

- Repair tests: `tests/readiness/test_sibling_sso_pointer_bytes.py`,
  `tests/readiness/test_sibling_sso_repair_dry_run.py`,
  `tests/readiness/test_sibling_sso_native_preflight.py`, and the repair-specific
  cases at lines 21–222 of `tests/readiness/test_rollback_ownership_audit.py`.
  These show the apply caller, byte snapshot/recovery boundary and independent
  pointer expectations; broader rollback cases are outside this audit.
- Migration tests: `tests/data/document-index/test_canonical_migration.py`,
  its import bridge `scripts/data/document-index/_pathnorm_shim.py`, and the
  alias-map loader in `scripts/data/drive-index-search/pathnorm.py`.
  The existing tests check logical substitution, warnings, parse structure,
  check mode and idempotence using text views; they do not assert input delimiter
  identity. M's direct production caller is its own `main()`.
- Builder tests: `tests/workflow/test_build_session_review.py`,
  `tests/workflow/test_session_review_derive.py`,
  `tests/workflow/test_build_session_review_cli_privacy.py`, and
  `tests/workflow/test_session_review_page_hook.py`.
  These document generated-output semantics and parsing/sanitization behavior,
  not byte preservation of old JSON spelling.
- The builder's delegated configuration reader at lines 40–54 of
  `scripts/workflow/session_review_sanitize.py`; the rest of that module was not
  audited for byte preservation.
- Direct wrapper: `.claude/hooks/session-review-page.sh`, including its builder
  invocation at line 53. Downstream consumer: only `build_sessions()` and its
  adjacent contract at lines 126–165 of `scripts/build_pages.py`. Its text-mode
  copying is outside the named-helper mutation sample; generated HTML has no
  byte-identity qualification here.
- The migration design's rewriter section and the
  [repair design](../plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md)'s
  apply/preflight section, plus the derivation design cited above, supply intended behavior.
  Reference search was limited to `scripts/`, `tests/`, `docs/plans/`,
  `docs/standards/`, `.claude/hooks/`, `config/` and `.github/`.

Uninspected coverage includes the remaining helpers in `scripts/readiness/`,
`scripts/data/document-index/` and `scripts/workflow/`, other `scripts/` subtrees,
the full site builder, live alias-registry contents and live target catalogs,
remaining hooks/configuration, sibling repositories, archives and binary data.
Reference search does not constitute read/write auditing of those directories.
No live catalog, sibling checkout, private payload, historical blob mutation,
cross-platform execution or repository-wide repair was performed. Metadata
encoding and unusual Git filename handling remain unqualified.

## Baseline

None: no baseline check failure was observed.

## Hooks that could not run

`command -v pre-commit` returned exit status 1 without an executable path.
The hook framework is unavailable in this environment and was not invoked;
the unchanged hook entry on main was inspected in `.pre-commit-config.yaml`.
File-level checks are run directly; commit hooks remain the publishing runner's
responsibility. A second-provider review remains pending before merge.

## Follow-up

The migration-only delimiter/encoding work and the uninspected coverage remain
open under issue #4089. The reusable lesson is to classify a boundary by its
preservation promise before selecting text or binary I/O; parsed equivalence
cannot serve as an oracle for unrelated byte identity.
