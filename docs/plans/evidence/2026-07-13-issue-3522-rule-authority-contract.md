# Issue 3522 Normative Rule-Authority Contract

This contract is normative. Synthetic examples use no real rule value.

## 1. Authority generations and anti-rollback anchor

Every byte change to registry, policy, or private map requires both a strictly
greater unsigned 64-bit `generation` and a new canonical lowercase UUIDv4
`authority_revision`. Revision reuse rejects. `seal` is an owner-only offline
command; CI exposes only `verify`, `audit-tree`, and `audit-history`.

Three independently provisioned inputs establish trust:

1. the authority bundle: public registry/policy plus private map/manifest;
2. a 32-byte HMAC key from exactly one of `--key-file` or
   `LEGAL_SCAN_AUTH_KEY_B64`;
3. `LEGAL_SCAN_ACTIVE_ANCHOR`, a protected-environment secret containing
   canonical JSON `{generation,authority_revision,manifest_mac}`.

The active anchor is never read from the bundle directory. Verify requires exact
anchor equality before pattern decoding. Replaying an older valid bundle,
resealing under a reused revision/generation, or changing one component rejects
rc3. The trust boundary is compromise of the protected key plus active anchor;
that external administrative compromise is not claimed detectable.

## 2. Canonical codecs

All four documents use `legal-json-v1`: UTF-8 JSON from Python
`json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,
allow_nan=False)` plus one LF. Parsing rejects BOM, invalid UTF-8, duplicate
keys, trailing bytes, non-integer numbers, unknown keys, then re-encodes and
byte-compares. Lists called `rules` sort by lowercase UUID ASCII bytes. Maximum
encoded size is 2 MiB for registry/policy/manifest and 16 MiB for the map.

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
are 1..65,536 bytes, total ≤10 MiB, unique by decoded bytes, and exactly one per
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
field is not an input. `seal` uses no-overwrite output and refuses a generation
or revision appearing in a supplied private generation ledger. Checked-in
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
- raw and canonical-base64 key bytes;
- the active-anchor exact bytes;
- configured prohibited private artifact basenames.

This is independent of `.gitignore`, pattern matching, or filename. Synthetic
tests force-add each artifact under arbitrary names. Public schema/registry/
policy markers remain allowlisted only at their exact canonical paths.

## 4. Private filesystem and output transaction

Mirror, bundle, and report parents must be pre-created current-UID directories
mode 0700. The tool sets `umask 077`, walks every component with retained dirfds
and no-follow checks, rejects alternates/reference repos, and uses a sanitized
credential-free remote display label. Files are regular, current-UID, mode 0600;
size caps apply before reads.

Reports are built inside a new transaction directory, files opened with
`O_NOFOLLOW|O_CREAT|O_EXCL`, flushed/fsynced, then the directory is fsynced. A
canonical `COMPLETE` manifest is written and fsynced last. Readers accept only a
valid COMPLETE transaction. Partial directories remain `.incomplete.<nonce>` and
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

The companion GitHub API inventory paginates and snapshots issues/PRs, comments,
reviews/review comments, releases/assets, Actions run/log/artifact metadata,
Pages, wiki repository, LFS, packages, and enumerated forks when authorized.
Each surface is `scanned`, `queried-no-access`, `provider-follow-up`, or
`unknown-residual` in the private coverage manifest. Provider caches, deleted
refs, inaccessible forks, expired logs/artifacts, and third-party copies are
never labeled clean.

No public output includes finding-specific counts, paths, refs, commits, object
IDs, URLs, hashes, rule IDs, exception text, or source locations. Public output
is restricted to command class, active opaque revision/generation, aggregate
objects examined, verdict, and rc. Exceptions are mapped to fixed messages.

## 6. CI and two-phase rollout

### Phase A — bootstrap, no private migration

An approved first PR will land schemas, tooling, synthetic tests, workflow, and
docs while retaining every legacy protection/value. It will carry no authority
secret and perform no private scan. After merge, the owner will record the exact
tool/workflow SHA, configure CODEOWNERS for workflow/tool/schema/policy, create a
protected GitHub Environment with required reviewer, provision bundle/key/anchor
as separate secrets, and approve an exact ruleset transaction adding the named
required check plus direct-update/bypass restrictions. Live API readback must
confirm enforcement before Phase B.

Secret-bearing jobs execute only after environment approval and only from the
owner-approved immutable 40-hex tool/workflow SHA. CI has verify/audit commands,
never seal. Actions are SHA-pinned; token permissions are read-only;
`persist-credentials:false`; caches/artifact upload are disabled; Git hooks,
global/system config, credential helpers, Python user site, and PR-controlled
dependencies/configs are disabled.

Fork PRs are rejected/skipped with one constant `owner review required` result
before environment access, secret materialization, or PR-data scanning. This
prevents a chosen-input membership oracle. Same-repo PR heads are fetched by
validated full OID as inert objects; never checked out, imported, executed, or
interpolated into shell. PR metadata travels through fixed files/environment.

### Phase B — owner-attended migration

Only after Phase A enforcement is live will a separately reviewed migration PR
be prepared. Before opening it, the owner will receive an exact private preview
and explicitly accept that deleting already-public lines republishes them in the
public diff/review/notification surface. If not accepted, history remediation
must be separately approved first. Legacy values remain until the replacement
gate is demonstrated strict. Phase B will reseal/provision, run the active base
gate, remove values, and verify the proposed tree with base-resident trusted
tooling. No implementation-plan approval alone authorizes this transaction.

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
