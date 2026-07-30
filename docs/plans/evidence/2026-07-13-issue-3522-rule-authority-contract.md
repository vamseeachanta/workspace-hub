# Issue 3522 Normative Rule-Authority Contract

This contract is normative. Synthetic examples use no real rule value.

## 1. Authority generations and anti-rollback anchor

Every byte change to registry, policy, or private map requires both a strictly
greater unsigned 64-bit `generation` and a new canonical lowercase UUIDv4
`authority_revision`. Revision reuse rejects. `seal` is an owner-only offline
command; CI exposes only `verify`, `audit-tree`, and `audit-history`.

Local operation uses three independently provisioned inputs:

1. the authority bundle: public registry/policy plus private map/manifest;
2. a 32-byte HMAC key from exactly one of `--key-file` or
   `LEGAL_SCAN_AUTH_KEY_B64`;
3. a canonical active anchor containing generation, revision, manifest MAC,
   approved tool SHA, and slot.

The active anchor is never read from the bundle directory. Verify requires exact
anchor equality before pattern decoding. Replaying an older valid bundle,
resealing under a reused revision/generation, or changing one component rejects
rc3. The trust boundary is compromise of the protected key plus active anchor;
that external administrative compromise is not claimed detectable.

The active anchor uses `legal-json-v1`, maximum 2 KiB:

```text
{"authority_revision":UUIDv4,"generation":u64,"manifest_mac":hex64,
 "schema_id":"legal-rule-active-anchor-v1","slot":"current"|"pending",
 "tool_sha":full lowercase Git OID,"expected_head_oid":full Git OID|null}
```

The private generation ledger is canonical JSON, maximum 2 MiB. It has
`schema_id=legal-rule-generation-ledger-v1`, a key ID, entries sorted by
generation with `{generation,authority_revision,manifest_mac}`, and a
domain-separated HMAC over the document without `ledger_mac`. Genesis is a
separately approved owner transaction. Every later seal requires the ledger,
verifies its HMAC/tip against the current anchor, requires exactly
`tip.generation+1` and a never-used UUID, and atomically appends the entry. Key
rotation cross-signs a terminal entry and requires a separately approved new
genesis. Full codec rules below apply; synthetic vectors cover anchor, ledger
genesis/append, rollback, reuse, and rotation.

## 2. Canonical codecs

All authority documents use `legal-json-v1`: UTF-8 JSON from Python
`json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,
allow_nan=False)` plus one LF. Parsing rejects BOM, invalid UTF-8, duplicate
keys, trailing bytes, non-integer numbers, unknown keys, then re-encodes and
byte-compares. Lists called `rules` sort by lowercase UUID ASCII bytes. Maximum
encoded size is 2 MiB for registry/policy/manifest and 24 KiB for the map so a
complete CI envelope remains below GitHub's 48 KiB secret limit.

### Registry

```text
{
  "authority_revision": UUIDv4,
  "generation": u64 >= 1,
  "rules": [{
    "match_mode": "exact-bytes" | "ascii-fold",
    "rule_id": UUIDv4,
    "severity": "block" | "warn",
    "target": "path" | "content" | "both"
  }],
  "schema_id": "legal-rule-registry-v1"
}
```

No label, description, source, path, pattern, or free-text field is permitted.
IDs are unique. Registry must be nonempty.

### Policy

```text
{
  "authority_revision": UUIDv4,
  "forensic_prefixes": [repo-relative ASCII prefix ending "/"],
  "generation": u64,
  "limits": {
    "max_blob_bytes": 1..10485760,
    "max_entries": 1..10000,
    "max_findings": 1..1000,
    "max_request_bytes": 1..104857600
  },
  "schema_id": "legal-rule-policy-v1"
}
```

Revision/generation match registry. Prefixes are unique, ASCII, slash-separated,
nonempty, relative, contain no `.`/`..` segment, and sort by raw ASCII bytes.

### Private map

```text
{
  "authority_revision": UUIDv4,
  "generation": u64,
  "rules": [{"pattern_b64": canonical padded RFC4648, "rule_id": UUIDv4}],
  "schema_id": "legal-rule-map-v1"
}
```

Strict base64 decoding and re-encode comparison are required. Decoded patterns
are 1..16,384 bytes, total ≤16 KiB, unique by decoded bytes, and exactly one per
registry ID. `ascii-fold` patterns must contain ASCII bytes only. Empty/missing/
extra/duplicate/noncanonical data rejects without echoing it.

### Manifest and MAC

The manifest is:

```text
{
  "authority_revision": UUIDv4,
  "generation": u64,
  "manifest_mac": 64 lowercase hex,
  "map_sha256": 64 lowercase hex,
  "policy_sha256": 64 lowercase hex,
  "registry_sha256": 64 lowercase hex,
  "schema_id": "legal-rule-authority-manifest-v1"
}
```

Hashes cover exact canonical file bytes. MAC input is:

```text
ASCII("LEGAL-RULE-AUTHORITY\0v1\0") ||
u64be(generation) || uuid.UUID(revision).bytes ||
registry_sha256_raw32 || policy_sha256_raw32 || map_sha256_raw32
```

`manifest_mac = HMAC-SHA-256(key, input)`; comparison is constant-time. The MAC
field is not an input. `seal` requires the authenticated ledger, uses
no-overwrite output, and refuses every prior generation/revision. Checked-in
synthetic vectors freeze every complete document byte string, digest, MAC input,
and MAC result.

The key-file form is canonical base64 plus LF, current-UID regular file mode
0600 under a current-UID 0700 no-follow parent. The environment form is canonical
base64 without LF. Exactly 32 decoded bytes are required. Interface selection,
paths, values, parser fragments, and subprocess payloads never enter public logs.

## 3. Structural secret-artifact prevention

Audit scans decoded rule bytes and also rejects, at any path:

- private-map or authority-manifest schema markers;
- exact private map/manifest file bytes;
- raw/canonical-base64 key bytes and canonical base64 for every decoded pattern;
- component hash/MAC encodings and individual anchor/ledger field values;
- active anchor, ledger, private report, coverage, and COMPLETE schema markers;
- Git pack/index magic and private-mirror configuration markers;
- exact private artifact bytes plus configured prohibited basenames.

This is independent of `.gitignore`, pattern matching, or filename. Synthetic
tests force-add each artifact under arbitrary names. Public schema/registry/
policy markers remain allowlisted only at their exact canonical paths.
Hex/alternate compression/encryption not covered by these closed encodings is an
explicit residual; the plan does not claim arbitrary steganographic detection.

## 4. Private filesystem and output transaction

Mirror, bundle, and report parents/directories must be current-UID mode 0700.
The tool sets `umask 077`, walks components with retained dirfds/no-follow checks,
rejects alternates/reference repos, and never persists a remote: it uses `git
fetch <credential-free-url> <exact-oid>` then removes all remote config. Exact
0600 applies to keys/bundles/ledgers/reports; Git internals may be 0400 or 0600,
but no directory/file may have group/other permission bits. Size caps apply
before reads. Linux is the supported audit host; Git subprocesses use the stable
`/proc/self/fd/<dirfd>` directory with `pass_fds`, sanitized environment,
credential helpers disabled, hooks disabled, and pre/post device/inode checks.

Reports are built inside a new transaction directory, files opened with
`O_NOFOLLOW|O_CREAT|O_EXCL`, flushed/fsynced, then the directory is fsynced. A
canonical `COMPLETE` manifest is written and fsynced last. It binds schema,
transaction ID, authority manifest identity, ref/API snapshot identities,
coverage states, and every relative filename/size/SHA-256; a domain-separated
HMAC covers it. Readers verify MAC, reject extra/missing/changed files, and accept
only complete coverage for a clean verdict. Partial directories remain
`.incomplete.<nonce>` and
are never interpreted as evidence; a separate explicit cleanup command removes
only validated incomplete transactions. Disk-full/fsync/parent-swap failures
return rc4. Mirror retention or secure deletion is an explicit owner disposition.

## 5. Tree and history audit

`audit-tree` reads a named commit without checkout. It parses
`git ls-tree -rz --full-tree`, streams blobs with `cat-file`, scans raw path/blob
bytes, raw commit and annotated-tag objects, and ref-name bytes. Protected-event
commands select the full required surface; caller subsets are rejected.

`audit-history` runs only in a fresh private mirror. It will:

1. snapshot `git ls-remote` before fetch, including every advertised ref and
   explicit `refs/pull/*/{head,merge}` queries;
2. fetch each exact full OID into private audit refs without hooks, checkout,
   submodules, LFS smudge, alternates, or credential persistence;
3. snapshot again and fail rc3 on drift;
4. scan raw commit/tag/tree/blob objects and ref names;
5. deduplicate byte scanning while retaining every reverse reachability edge to
   all refs, commits, and raw paths in the private report.

The companion GitHub API inventory snapshots before/after cursors/ETags and
paginates issues/PRs, timeline events, comments, reviews/review comments, commit
comments, discussions, releases/assets, Actions runs/logs/artifacts/caches,
Pages, wiki, LFS, packages, and enumerated forks. `scanned` means every accessible
metadata and downloadable content byte was fetched and scanned. Bounded adapters
decompress archives in a private scratch tree with entry/count/ratio/expanded-
byte/depth caps and no links/devices; a cap or snapshot drift yields rc3. API-
discovered commit IDs enter the Git reachability graph. Each surface is
`scanned`, `queried-no-access`, `provider-follow-up`, or `unknown-residual` with
permissions, pagination, byte/edge counts, and snapshot identity in the private
coverage manifest. Provider caches, deleted refs, inaccessible forks, expired
content, or third-party copies are never clean.

Global bounds cap refs, objects, edges, API pages, downloads, compressed and
expanded bytes; overflow is rc3 with partial coverage. No public output includes
finding-specific counts, paths, refs, commits, object
IDs, URLs, hashes, rule IDs, exception text, or source locations. Public output
is restricted to command class, active opaque revision/generation, aggregate
objects examined, coverage class, verdict, and rc. Precedence is rc4 > rc3 > rc1
> rc0: findings remain private when later coverage fails, and `clean` is reserved
for COMPLETE coverage with no block finding. Exceptions map to fixed messages.

## 6. CI and two-phase rollout

### Phase A — bootstrap, no private migration

An approved first PR will land schemas, tooling, synthetic tests, a minimal
caller plus reusable workflow, and docs while retaining every legacy protection/
value. It carries no authority secret and performs no private scan. The reusable
workflow owns the protected Environment and is invoked as
`uses: vamseeachanta/workspace-hub/.github/workflows/legal-rule-authority-reusable.yml@<approved-full-SHA>`;
the mutable caller never receives secrets. The called workflow checks out tools
at the same SHA and verifies it against the anchor before scanning.

After merge, an owner transaction will configure `.github/CODEOWNERS` for the
caller/reusable workflow, authority code, schemas, and policy; create Environment
`legal-rule-authority` limited to `main` with required owner review; provision a
single canonical <=32 KiB `LEGAL_SCAN_AUTH_CURRENT` envelope; and install ruleset
`legal-rule-authority-main` on `refs/heads/main` with no bypass/direct update and
required GitHub-Actions check `legal-rule-authority / strict-scan`. Exact expected
JSON, integration ID, owner, and target ref are versioned in the owner preview;
live normalized API readback must match before Phase B.

The envelope contains canonical base64 key/map/manifest/anchor/ledger fields and
is the CI trust root. Local interfaces remain separate files. CI exposes verify/
audit, never seal. Actions are commit-SHA-pinned; permissions are contents read
only; `persist-credentials:false`; caches/artifacts disabled; hooks/config/
credential helpers/Python user site and PR-controlled dependencies disabled.

Fork PRs always receive terminal constant failure `owner review required` before
Environment access, secret materialization, or data scanning and are never
directly mergeable. A maintainer privately scans/redacts a candidate, then
creates an independent same-repository PR; the fork PR remains closed with the
same result. Only the same-repo PR can satisfy the required check. Its full head
OID is fetched as inert objects, never checked out/imported/executed or shell-
interpolated. PR metadata travels only through fixed files/environment.

### Phase B — owner-attended migration

Only after Phase A enforcement is live will a separately reviewed migration PR
be prepared. Before opening it, the owner will receive an exact private preview
and explicitly accept that deleting already-public lines republishes them in the
public diff/review/notification surface. If not accepted, history remediation
must be separately approved first. Legacy values remain until the replacement
gate is strict. Phase B uses dual slots: immutable CURRENT remains active for
ordinary checks; the owner provisions `LEGAL_SCAN_AUTH_PENDING` plus a descriptor
binding its revision to one exact Phase-B head OID. Only that OID selects PENDING;
concurrent old-base/ordinary PRs use CURRENT.

After successful merge, an owner-gated compare-and-swap verifies unchanged
CURRENT, expected merge tree, and PENDING identity, replaces CURRENT with the
exact PENDING envelope, verifies readback/main, then deletes PENDING. Failed or
unmerged migration never promotes. Post-promotion failure invokes only the
previewed owner-approved rollback. No plan approval alone authorizes secrets,
pending descriptor, migration PR, CAS, or rollback.

Push/schedule jobs also require the protected environment reviewer and pinned
tool SHA; a push result is detection, not prevention. Prevention is claimed only
after live required-check/direct-update ruleset verification.

## 7. Exit classes and exact acceptance

| rc | Meaning |
|---|---|
| 0 | verified/clean |
| 1 | prohibited finding |
| 2 | usage/config/schema/missing authority |
| 3 | integrity/rollback/drift/Git/API/coverage/cap failure |
| 4 | private filesystem/output failure |

Frozen operator interfaces (all outputs are no-overwrite):

```text
validate-public --registry FILE --policy FILE
seal --registry FILE --policy FILE --map FILE --key-file FILE
     --current-anchor FILE --ledger FILE --out-dir PRIVATE_DIR
verify --registry FILE --policy FILE --map FILE --manifest FILE
       (--key-file FILE | --key-env LEGAL_SCAN_AUTH_KEY_B64)
       --anchor FILE --ledger FILE
audit-tree --repo GIT_DIR --commit FULL_OID --required-ref FULL_REF
       --authority-dir PRIVATE_DIR --out-dir PRIVATE_DIR
audit-history --remote-url-env LEGAL_SCAN_REMOTE_URL --github-repo OWNER/REPO
       --authority-dir PRIVATE_DIR --mirror-dir PRIVATE_DIR
       --out-dir PRIVATE_DIR --github-token-env GITHUB_TOKEN
cleanup-incomplete --parent PRIVATE_DIR --transaction-id UUID
promote --current-envelope-env NAME --pending-envelope-env NAME
       --expected-head FULL_OID --expected-tree FULL_OID --preview FILE
```

Map/manifest/anchor/ledger may instead arrive in one canonical CI envelope;
file and envelope modes are mutually exclusive. `audit-tree` protected-event
mode forbids subset flags. `audit-history` requires all adapters or records a
non-clean residual. `promote` is owner-only and unavailable in CI verify jobs.

```bash
uv run --no-project pytest -q scripts/legal/tests/test_rule_authority_*.py
uv run --no-project pytest -q scripts/legal/tests tests/enforcement/test_check_no_conflict_markers.py
uv run --no-project ruff check scripts/legal/manage_rule_authority.py scripts/legal/rule_authority scripts/legal/tests/test_rule_authority_*.py
uv run --no-project python -m compileall -q scripts/legal
uv run --no-project pytest -q tests/enforcement/test_python_function_lengths.py
bash scripts/enforcement/check-no-abs-paths.sh
scripts/legal/legal-sanity-scan.sh --diff-only
uv run --no-project python scripts/legal/manage_rule_authority.py validate-public --registry config/legal-rule-registry.json --policy config/legal-rule-authority-policy.json
```

Hermetic tests run exact synthetic `seal`, `verify`, `audit-tree`, and
`audit-history` commands for rc0/1/2/3/4, complete golden vectors, rollback,
reseal/revision reuse, stdout/stderr/job-summary withholding, same-repo/fork event
fixtures, action SHA pins, immutable tool selection, mirror permissions/coverage,
ruleset response fixtures, and crash injection. Live Phase A acceptance adds
GitHub environment/ruleset API readback and a no-secret bootstrap run; live Phase
B commands are generated only in the separately approved private preview.
