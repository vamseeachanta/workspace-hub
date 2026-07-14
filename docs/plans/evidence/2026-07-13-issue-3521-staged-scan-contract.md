# Issue 3521 Normative Staged-Scan Contract

This file is normative for the issue-3521 plan. V1 is a point-in-time scan plus
post-commit detection protocol; it does not make Git commit or push atomic.

## 1. Prerequisites and authority

- Git 2.43+ with SHA-1 or SHA-256 object format and `cat-file
  --batch-command -Z` is required. Bare, unborn, or non-Git roots return rc2.
- `--repo-root` must resolve to exactly `git rev-parse --show-toplevel`; a
  subdirectory, symlink alias, or mismatched resolved root returns rc2. Linked
  worktrees are supported through Git plumbing, never `.git/` guessing.
- #3522 owns and must merge the registry schema, private-map schema, public
  registry, authority policy, and migration before any #3521 implementation.
  Afterward this plan will pin its merge SHA and authority blob digests, undergo
  fresh review, and require fresh user approval.
- The external map named by `LEGAL_SCAN_RULE_MAP` must be current-UID-owned mode
  0600, outside the target repo, complete for the registry, and free of unknown
  or duplicate IDs. Strict mode never reads `.legal-deny-list.yaml` or writes a
  pattern, matched bytes, private-map digest, or reversible identity publicly.

## 2. Exact transaction

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
  --private-receipt="$evidence_dir/private-receipt.json" \
  --public-receipt="$evidence_dir/public-receipt.json"
uv run --no-project python scripts/legal/scan_staged_blobs.py verify \
  --repo-root . --request "$evidence_dir/request.json" \
  --private-receipt "$evidence_dir/private-receipt.json" \
  --public-receipt "$evidence_dir/public-receipt.json"
git commit -m "type(scope): message"
uv run --no-project python scripts/legal/scan_staged_blobs.py verify-commit \
  --repo-root . --request "$evidence_dir/request.json" \
  --private-receipt "$evidence_dir/private-receipt.json" --commit HEAD
```

The isolated implementation lane commits the complete verified index with no
pathspec. A pathspec commit is forbidden because Git may read worktree bytes
instead of the already-verified index.

`pathset0` is NUL-delimited raw repository-relative path bytes. It may be made by
`--all-staged` or provided explicitly. Every record is independently validated;
Git paths cannot contain NUL. Empty/duplicate/absolute/`..`/outside-delta records,
untracked paths, intent-to-add, and empty staged sets fail closed.

Strict flags cannot mix with legacy flags. Legacy repo/all/diff/json/quiet
stdout, stderr, help, and exit bytes remain golden-compatible. Non-attesting
status is documented only in new strict-command documentation.

## 3. Canonical framing and identities

```text
frame(domain, fields):
    bytes = ASCII("LEGAL-STAGED-SCAN\0v1\0")
    append u64be(len(domain)), domain
    for field in fields: append u64be(len(field)), field
    return SHA-256(bytes)

record_list(records):
    append u64be(record_count)
    for record: append u64be(field_count), then each length-framed field
```

Integers are unsigned fixed-width big-endian. Null uses a dedicated one-byte
presence tag before its value and is distinct from empty or an all-zero OID.
Canonical JSON `legal-json-v1` is UTF-8 from Python
`json.dumps(sort_keys=True,separators=(",",":"),ensure_ascii=True,
allow_nan=False)` plus LF. Parsers reject duplicate keys and validators
re-encode/byte-compare inputs.

- `index_digest`: object format, HEAD, expected-tree OID, and exact raw stdout
  of `git ls-files --stage -z`. Assume-unchanged/skip-worktree flags are
  deliberately excluded because they do not change `git write-tree`; conflicts
  remain visible as nonzero stages.
- `delta_digest`: sorted records with ordered fields status, path, nullable old
  mode/OID, nullable new mode/OID, nullable index stage.
- `pathset_digest`: sorted one-field raw-path records.
- `tool_digest`: records sorted by raw repo-relative tool path, then path and
  SHA-256 of raw file bytes (not Git object framing).
- `private_request_digest`: canonical private request bytes with a fresh 256-bit
  nonce. It never leaves private evidence. Public output has no request digest.

Checked-in golden vectors cover zero/one/two records, null versus empty,
255/256-byte boundaries, and reordered inputs. `expected_tree_oid = git
write-tree`; creating a tree object is an acknowledged object-store-only side
effect.

## 4. Raw delta and request schema

Request, scan, and verify independently derive:

```text
git diff-index --cached --raw -z --no-renames --abbrev=full HEAD --
git ls-files --stage -z
```

The raw parser consumes colon-prefixed fixed metadata followed by NUL path bytes
and joins the commands by exact raw path. Transport `(000000, zero_oid)` becomes
null only for A-old or D-new. Zero OIDs elsewhere reject. Canonical entries are:

```text
entry_id: e000001... after raw-path sort (not a path hash)
status: A | M | D | T
path_b64: raw path, private request only
old_mode/old_oid: value or null
new_mode/new_oid: value or null
index_stage: 0 for new entry, null for deletion
```

| Status | Old | New | Rule |
|---|---|---|---|
| A | null | mode/OID/stage0 | content/path scan |
| M | mode/OID | same type class/new mode/OID/stage0 | chmod remains M |
| D | mode/OID | null | path scan; no new content |
| T | mode/OID | different type class/mode/OID/stage0 | new-type policy |

Type classes are regular (100644/100755), symlink (120000), and gitlink
(160000). Schema/request literal zero or abbreviated OIDs, conflicts, ITA, and
unknown statuses reject rc3. Renames are D+A. Explicit pathset equals the delta
path multiset.

Private request fields include resolved root/remote identity, raw paths, private
map digest, private MAC key, nonce, every digest above, policy/authority identity,
HEAD, object format, expected tree, caps, and old/new object metadata. Content
SHA-256 is present only for blob sides. Old non-blobs are metadata-checked only;
new gitlinks reject. None of these identities enters public output.

## 5. Git transport and bounds

One `batch-check -Z` pass validates order, full OID, type, and decimal size for
every object before contents. Only blobs are read. A 120000 blob contains the
link target and is scanned without dereference. New 160000 rejects rc3.

Compiled hard maxima are 10 MiB/blob, 100 MiB/request, 10,000 entries, and 1,000
findings. #3522 authority and then request may only lower effective values.
Finding overflow returns rc3, never a truncated verdict. Preflight bounds occur
before content reads.

`cat-file --batch-command -Z` uses NUL command, NUL `<oid> <type> <size>` header,
exactly `size` content bytes, and trailing NUL. A streaming parser reads at most
64 KiB chunks, maintains overlap, and rejects truncated/reordered/extra/missing/
wrong-type/wrong-size/trailing responses. Preflight and content metadata agree.

Exact rules scan arbitrary bytes. ASCII-fold requires ASCII patterns and folds
ASCII only. ZIP/gzip/7z/bzip2/xz/RAR/tar magic rejects rc3 before expansion.
Other binary blobs scan within caps; oversize rejects before read.

## 6. Rules, severity, and forensic disposition

The exact #3522 authority revision supplies UUID, target, match mode, severity,
and pattern encoding; private bytes come only from the complete external map.
Closed enums are target `path|content|both`, mode `exact-bytes|ascii-fold`, and
severity `block|warn`. Block findings yield `prohibited`/rc1. Warn-only findings
yield `clean-with-warnings`/rc0. Unknown values reject rc2. Scan and verify bind
authority, map, policy, and tool before/after; consistent pre-request weakening
or values above compiled hard maxima reject.

Raw paths scan for every entry type; new A/M/T blobs scan content. Private
findings carry path/identity evidence. Public findings carry only opaque entry
ID, stable UUID, target, offset/length, severity, suppression state, and verdict.

The only V1 suppression is ASCII `LEGAL_SCAN_FORENSIC_OK:<rule-uuid>` at the end
of the same LF-delimited line as a single-line content finding, under:

- `docs/plans/`
- `docs/standards/`
- `scripts/review/results/`
- `scripts/legal/tests/fixtures/forensic/`

It exempts only that occurrence. It is invalid for paths, multiline matches,
adjacent lines, wrong IDs, whole-file tokens, ordinary source, malformed byte
ambiguity, YAML aliases, or multiline scalars. Each suppression is recorded.

## 7. Evidence publication and verification

Pathset/request/receipt directories must already exist, be outside the repo,
current-UID-owned mode 0700, and opened via no-follow component traversal to a
retained parent dirfd. Output names are single components and cannot exist.
Temp/link/unlink/fsync operations are dirfd-relative. The helper rechecks parent
device/inode/owner/mode, writes a 0600 `O_NOFOLLOW|O_EXCL` temp, flushes/fsyncs,
hard-links without overwrite, fsyncs the directory, then removes the temp.

If link succeeds but directory fsync fails, the final is renamed to reserved
`.invalid.<nonce>` when possible and rc4 returns; any surviving final is called
unusable in non-sensitive stderr and retry rejects it. Crash cleanup never
removes caller files.

The private receipt contains all transaction, Git, content, path, and authority
evidence. The public projection contains schema/revision, random transaction ID,
HMAC-derived opaque entry IDs, public finding fields, verdict, and exit class.
The HMAC key remains private. Public output contains no path, Git/content/repo
hash, nonce, request commitment, private digest, pattern, or snippet. Neither
artifact self-hashes.

`verify` trusts neither artifact: it revalidates identities, rereads and rescans
OIDs, regenerates both canonical artifacts, and byte-compares. `verify-commit`
requires one parent equal to request HEAD, tree equal to expected tree, matching
delta, rescanned committed blobs, and regenerated private receipt. A bad local
commit cannot receive a valid receipt and MUST NOT be promoted. Push blocking is
future #3398 scope, not a #3521 claim.

## 8. Exit classes and fixtures

| rc | Class | Receipt rule |
|---|---|---|
| 0 | clean or warnings-only | both artifacts after ownership |
| 1 | unsuppressed block finding | both artifacts |
| 2 | usage/config/schema/root/Git/rule/set error | best effort before ownership |
| 3 | integrity/policy/drift/protocol/edge/overflow/forgery mismatch | mandatory after ownership |
| 4 | unsafe/unwritable/failed atomic evidence output | impossible or best effort |

Required hermetic fixtures cover SHA-1/SHA-256, linked/sparse/split index,
unborn/bare, path byte adversaries, A/M/D/T, chmod M, type T, D+A rename,
conflict/ITA/untracked, old symlink/gitlink, worktree/index inverse, identity
drift, malformed cat-file responses, delete/symlink path findings, binary chunk
boundaries, archive/caps/finding overflow/disk full, forged private/public
artifacts, dictionary guesses, parent replacement/crashes, sentinel misuse,
authority weakening, and golden legacy/digest behavior.

## 9. Exact acceptance commands

```bash
bash -n scripts/legal/legal-sanity-scan.sh
uv run --no-project ruff check scripts/legal/scan_staged_blobs.py scripts/legal/staged_scan scripts/legal/tests/test_staged_scan_*.py
uv run --no-project python -m compileall -q scripts/legal
uv run --no-project pytest -q scripts/legal/tests/test_staged_scan_contract.py -k 'schema or golden_digest'
uv run --no-project pytest -q scripts/legal/tests/test_staged_scan_*.py
uv run --no-project pytest -q scripts/legal/tests tests/enforcement/test_check_no_conflict_markers.py
uv run --no-project pytest -q tests/enforcement/test_python_function_lengths.py
bash scripts/enforcement/check-no-abs-paths.sh
scripts/legal/legal-sanity-scan.sh --diff-only
```

With `LEGAL_SCAN_RULE_MAP` provisioned from #3522, the literal §2 block scans the
complete staged index and returns rc0, commits with no pathspec, and passes
`verify-commit` rc0. Fixtures exercise rc1/2/3/4 and clean external evidence.
Legacy scan is compatibility evidence only. T3 artifact/code review and a fresh
strict transaction follow every patch.
