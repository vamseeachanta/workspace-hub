# Issue 3521 Normative Staged-Scan Contract

This file is normative for the issue-3521 plan. V1 is a point-in-time scan plus
post-commit detection protocol; it does not claim to make Git commit atomic.

## 1. Prerequisites and authority

- Git 2.43+ with SHA-1 or SHA-256 object format and `cat-file
  --batch-command -Z` is required. Bare, unborn, or non-Git roots return rc2.
- `--repo-root` must resolve to exactly `git rev-parse --show-toplevel`; a
  subdirectory, symlink alias, or path whose resolved root differs returns rc2.
  Linked worktrees are supported through Git plumbing, never `.git/` guessing.
- #3522 must merge first. It will provide `config/legal-rule-registry.yaml`, a public registry of stable opaque
  rule UUIDs, target (`path`, `content`, `both`), severity, match mode, and public
  revision ID plus the external private map named by `LEGAL_SCAN_RULE_MAP`, from UUID to pattern bytes. The map
  must be owned by the current UID, mode 0600, outside the target repo, complete
  for the registry, and free of unknown/duplicate IDs.
- Strict mode never reads `.legal-deny-list.yaml`, never honors its exclusions,
  and never writes a rule pattern, private-map digest, or matched bytes to output.

## 2. CLI and transaction sequence

```bash
evidence_dir="$(mktemp -d "${TMPDIR:-/tmp}/legal-stage.XXXXXXXX")"
chmod 700 "$evidence_dir"
uv run --no-project python scripts/legal/scan_staged_blobs.py pathset \
  --repo-root . --all-staged --out "$evidence_dir/pathset0"
uv run --no-project python scripts/legal/scan_staged_blobs.py request \
  --repo-root . --pathset0 "$evidence_dir/pathset0" \
  --out "$evidence_dir/request.json"
scripts/legal/legal-sanity-scan.sh --repo-root=. \
  --staged-request="$evidence_dir/request.json" \
  --receipt="$evidence_dir/receipt.json"
uv run --no-project python scripts/legal/scan_staged_blobs.py verify \
  --repo-root . --request "$evidence_dir/request.json" \
  --receipt "$evidence_dir/receipt.json"
git commit -m "type(scope): message" -- <exact-pathspecs>
uv run --no-project python scripts/legal/scan_staged_blobs.py verify-commit \
  --repo-root . --request "$evidence_dir/request.json" \
  --receipt "$evidence_dir/receipt.json" --commit HEAD
```

`pathset0` is a NUL-delimited sequence of raw repository-relative path bytes.
Callers may generate it with `--all-staged` or provide it explicitly. Empty
records, duplicate paths, absolute paths, `..`, NUL inside a record, and paths
not represented by the staged delta fail. Thus an explicitly declared untracked
or intent-to-add path fails instead of disappearing. Empty staged sets return rc2.

The shell strict mode requires all three strict flags and rejects every legacy
mode flag. Legacy repo/all/diff/json/quiet modes remain byte/output/exit compatible
and print `attestation=false` in help/structured metadata.

## 3. Canonical byte framing

All identities use this collision-resistant profile:

```text
frame(domain, fields):
    bytes = ASCII("LEGAL-STAGED-SCAN\0v1\0")
    append u64be(len(domain)), domain
    for field in fields:
        append u64be(len(field)), field
    return SHA-256(bytes)
```

Integers inside fields are unsigned big-endian fixed-width values; null is a
zero-length field and is distinct from an all-zero OID. Records are sorted by
raw path bytes, then status byte. Canonical JSON profile `legal-json-v1` is UTF-8
from Python `json.dumps(sort_keys=True,separators=(",",":"),ensure_ascii=True,
allow_nan=False)` plus one newline. Parsers reject duplicate keys and validators
re-encode/byte-compare inputs; schema validity alone is insufficient.

- `index_digest`: domain `index`; fields are object-format, HEAD OID, and exact
  raw stdout of `git ls-files --stage -z` (including index stages/flags visible
  through the declared Git commands).
- `delta_digest`: domain `delta`; one framed delta record per §4.
- `pathset_digest`: domain `pathset`; sorted raw path records.
- `tool_digest`: domain `tool`; relative path/blob SHA-256 pairs for wrapper,
  entrypoint, and package modules.
- `public_rule_revision`: stable ID from #3522 registry. The private map digest
  stays only in the 0600 request.
- `request_digest`: domain `request`; canonical request bytes include a fresh
  256-bit nonce, preventing dictionary enumeration of private request fields.

The request also binds `expected_tree_oid = git write-tree`. Creating tree
objects is an acknowledged object-store side effect; it does not change refs,
index, or worktree and supplies the later commit-binding authority.

## 4. Delta and request schema

The staged delta is independently derived during request, scan, and verify with
`git diff-index --cached --raw -z --no-renames --abbrev=full HEAD --`. The parser
does not use rename heuristics. Every record is:

```text
entry_id: e000001... assigned after raw-path sort (not a path hash)
status: A | M | D | T
path_b64: raw path, request only
old_mode: six octal digits or null
old_oid: full object-format OID or null
new_mode: six octal digits or null
new_oid: full object-format OID or null
index_stage: 0 for a new entry, null for deletion
```

Invariants:

| Status | Old | New | Result |
|---|---|---|---|
| A | null | mode/OID/stage0 | content/path scan |
| M | mode/OID | same mode/new OID/stage0 | content/path scan |
| D | mode/OID | null | raw path scan; no new content |
| T | mode/OID | different mode/OID/stage0 | apply new-mode policy |

All-zero/abbreviated OIDs, nonzero conflict stages, and intent-to-add reject rc3.
Rename/copy is represented as deletion plus addition. The explicit pathset must
equal the delta path multiset; order may differ. Mutation that returns to the
same canonical identity is harmless because the attested bytes are identical.

Request-only fields include resolved root/remote identity, full path bytes,
private map digest, nonce, index/delta/pathset/tool/policy identities, HEAD,
object format, expected tree, caps, and expected old/new object types/sizes and
SHA-256. These fields never appear in the public-safe receipt.

## 5. Git transport and resource bounds

Before requesting contents, one `batch-check -Z` pass validates response order,
full OID, type, and decimal size for every old/new object. Only `blob` is readable;
new mode 160000 (gitlink) rejects rc3. Mode 120000 is a blob containing the link
target and is scanned without filesystem dereference.

Default reviewed caps are 10 MiB/blob, 100 MiB/request, 10,000 entries, and
1,000 findings. Caps are policy fields and cannot be raised by the request.
Type/size/count/aggregate checks occur before any `contents` command.

`cat-file --batch-command -Z` commands and responses follow Git 2.43 grammar:
NUL-terminated command; NUL-terminated `<oid> <type> <size>` header; exactly
`size` bytes; trailing NUL. A streaming parser reads at most 64 KiB per chunk,
maintains pattern overlap, and rejects truncated, reordered, extra, missing,
wrong-type, wrong-size, or trailing responses. It never uses `capture_output`
for contents. Preflight and contents OID/type/size must agree.

Byte-exact rules scan all path/content bytes. ASCII-casefold rules require an
ASCII pattern and apply ASCII-only folding to arbitrary bytes. No Unicode locale
or decoding affects matching. Archive magic (ZIP, gzip, 7z, bzip2, xz, RAR, tar
ustar) rejects rc3 before expansion regardless of filename; archives are never
opened. Other binary blobs are scanned within caps. Oversize rejects before read.

## 6. Rule and forensic contract

Stable UUIDs and match semantics come from the immutable public registry; bytes
come only from the complete external private map. Scan and verify bind registry,
map, policy, and tool before/after. Destination is not caller configurable: the
only receipt is public-safe, while the external request is private transaction
evidence.

Raw path bytes are scanned for A/M/D/T entries when a rule targets path/both.
Content rules scan only new A/M/T blobs. Findings contain entry ordinal, stable
rule UUID, target, byte offset/length, severity, and verdict—never path/pattern/
snippet/private digest.

V1 sentinel grammar is ASCII `LEGAL_SCAN_FORENSIC_OK:<rule-uuid>` at the end of
the same LF-delimited byte line as a single-line content finding. It is honored
only under these raw-byte prefixes:

- `docs/plans/`
- `docs/standards/`
- `scripts/review/results/`
- `scripts/legal/tests/fixtures/forensic/`

The sentinel exempts only that rule occurrence on that line. It is invalid for
path findings, multiline patterns, adjacent lines, wrong IDs, whole-file tokens,
ordinary source paths, malformed/non-UTF-8 ambiguity, or YAML aliases/multiline
scalars. There is no structural pattern-field exemption because private patterns
are external. Every suppression is recorded by entry ordinal and rule ID.

## 7. Receipt, verification, and commit binding

Request/receipt directories must already exist, be current-UID-owned mode 0700,
outside the repo, and free of symlink components. Output files must not exist.
The helper writes a same-directory 0600 temp with `O_NOFOLLOW|O_EXCL`, flushes and
fsyncs it, publishes without overwrite using hard-link creation, fsyncs the
directory, and removes the temp. Crash cleanup never removes caller files.

Receipt fields are schema/revision, transaction nonce, salted request digest,
expected tree, HEAD, entry ordinals with old/new modes/OIDs/blob SHA-256/size/
media/disposition, stable-rule findings/suppressions, verdict, and exit class.
No path, repository identity, private rule/map digest, pattern, or snippet is
present. The receipt has no self-hash.

`verify` does not trust receipt verdicts. It revalidates identities, rereads and
rescans exact OIDs, regenerates canonical receipt bytes, and byte-compares them.
Forged verdict, finding, suppression, media, size, or SHA therefore fails rc3.

`verify-commit` requires a single-parent commit whose parent equals request HEAD,
whose tree equals `expected_tree_oid`, and whose selected D/A/M/T entries match
the request. It rescans committed tree blobs and regenerates the receipt. Index
mutation after pre-commit verification is detected against the resulting commit;
the bad commit may exist locally but cannot receive a valid receipt or be pushed.
#3398 will later wire pre/post-commit enforcement; #3521 supplies the verifier.

## 8. Exit and edge table

| rc | Class | Receipt |
|---|---|---|
| 0 | clean scan/verify | mandatory after request ownership |
| 1 | prohibited finding | mandatory |
| 2 | usage/config: CLI/schema/root/Git version/unborn/empty rules or set | best-effort before output ownership; mandatory afterward |
| 3 | integrity/policy: drift, Git protocol, conflict/ITA, gitlink, archive/oversize, forgery, commit mismatch | mandatory after validated output ownership |
| 4 | evidence-output failure: unsafe/unwritable/full directory or atomic publish/fsync failure | impossible or best-effort; stderr contains only class/code |

Deletion produces a path-scanned `deleted` disposition; clean deletion may rc0.
Symlink scans its target blob; finding rc1. Type-change applies the new type and
records both identities. Empty staged set rc2. Archive/oversize/gitlink rc3.
All Git/read/parser/rule errors fail closed. No class may return rc0 by fallback.

## 9. Required adversarial fixtures

- SHA-1/SHA-256, linked/sparse/split index, root/subdir/symlink root, unborn/bare.
- Space/tab/newline/dash/colon/non-UTF-8 paths and length-boundary collisions.
- A/M/D/T, rename D+A, conflict stages, intent-to-add, explicit untracked.
- Staged/worktree inverse bytes; index/rules/tool drift; post-verify mutation.
- Truncated/reordered/extra/wrong cat-file records and declared-size mismatch.
- Path findings on delete/symlink; binary chunk-boundary match; archive magic
  under renamed/malformed files; cap, entry-count, finding-count, disk-full.
- Forged receipt fields; output symlink/ownership/mode/overwrite/crash cases.
- Wrong/adjacent/path/whole-file sentinel; YAML aliases/multiline; rule ID/map
  mismatch; private destination/bypass flags rejected.
- Golden legacy help/output/findings/exclusions/exit behavior.

## 10. Exact acceptance commands

```bash
bash -n scripts/legal/legal-sanity-scan.sh
uv run --no-project python -m compileall -q scripts/legal
uv run --no-project pytest -q scripts/legal/tests/test_staged_scan_*.py
uv run --no-project pytest -q scripts/legal/tests tests/enforcement/test_check_no_conflict_markers.py
uv run --no-project pytest -q tests/enforcement/test_python_function_lengths.py
```

The strict transaction in §2 must then scan the staged implementation, pass
pre-commit verify, commit by explicit pathspec, and pass `verify-commit`. A
mutation fixture must produce rc3. Legacy `--diff-only` is compatibility evidence
only. T3 artifact/code review and a fresh strict transaction follow any patch.
