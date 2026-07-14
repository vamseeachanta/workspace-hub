# Plan for #3522: Private Legal-Rule Authority Migration

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3522
> **Client:** N/A
> **Lane:** lane:codex
> **Execution:** isolated single-lane implementation after explicit approval
> **Review artifacts:** `scripts/review/results/2026-07-13-plan-3522-{claude,codex,gemini}-rN.md`

---

## Resource Intelligence Summary

### Existing repo code

- `.legal-deny-list.yaml` currently carries 23 pattern records across two
  policy sections and 14 exclusions. Its nine reachable revisions span
  2026-02-03 through 2026-07-02. Values were inspected only in the private
  working session and will not be repeated in this public plan or review.
- `scripts/legal/legal-sanity-scan.sh:108-179` parses public YAML pattern values
  and exclusions directly, then emits matching paths/lines. It has no opaque
  rule registry, sealed private map, or history-audit mode.
- `scripts/legal/check-client-pii.py` and `redact-client-pii.py` already keep a
  separate client-redaction map outside Git, with value-withholding output.
  The local default map is untracked and gitignored. The guard has strict,
  `--all`, PR metadata, and commit-message surfaces, but skips non-UTF-8 files.
- `.github/workflows/legal-client-pii-gate.yml` materializes one private secret
  into runner temp storage. It currently degrades open when the secret is absent
  and its public comments include a reversible private-source location.
- The 21 existing guard/redactor tests use synthetic values. No test proves a
  sealed authority, raw-byte tree cleanliness, public-output non-enumerability,
  or reachable-history coverage.

### Standards

- `docs/standards/CONTROL_PLANE_CONTRACT.md` requires public schemas, policy,
  and tooling to remain durable control-plane artifacts; private rule bytes,
  signing keys, manifests, and incident reports remain external evidence.
- `.claude/rules/patterns.md` places CI validation at Level 2 and hooks at Level
  3. This issue will build the authority and tree/history audit; #3521 will own
  staged-blob attestation and #3398 will own hook adoption.
- Universal legal/security rules require no secrets in Git, no sensitive values
  in public logs, validation of hostile input, and legal-scan passage.

### LLM Wiki pages consulted

Not applicable. This is public-repository security infrastructure and will not
touch client or engineering wiki content.

### Documents consulted

- Issue [#3522](https://github.com/vamseeachanta/workspace-hub/issues/3522) will
  own exposure assessment, private-map migration, and history disposition.
- Issue [#3521](https://github.com/vamseeachanta/workspace-hub/issues/3521) is
  blocked on an exact rule codec and an independently trusted map anchor.
- Issues [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095),
  [#3099](https://github.com/vamseeachanta/workspace-hub/issues/3099), and
  [#3169](https://github.com/vamseeachanta/workspace-hub/issues/3169) established
  private client maps, value-withholding output, and metadata scanning, but not
  generic raw-byte rule authority or history remediation.
- `docs/plans/2026-06-16-issue-3169-pii-guard-commit-msg-pr-body.md` supplies the
  synthetic-fixture and public-log precedent; this plan will not weaken it.
- Drive-index query `legal scanner private rule map` returned five unrelated
  documents across six queried indexes. Two indexes were unreachable and three
  were stale; no drive document is an authority source for this security design.

### Gaps identified

- No canonical public registry/private-map codec or independently trusted seal.
- No private, raw-byte, all-reachable-ref assessment with non-sensitive output.
- No strict CI proof that the checked commit tree contains no private rule bytes.
- No safe owner transaction for provisioning/rotation or history disposition.
- Current public policy and workflow surfaces can reveal values or reversible
  storage locations and can degrade open on protected repository events.

### Evidence (embedded verification)

Verified 2026-07-13:

```text
#3522 OPEN status:needs-plan lane:codex
#3521 OPEN status:needs-plan lane:codex
#3095 CLOSED; #3099 CLOSED; #3169 CLOSED
current deny records: 23; exclusions: 14; reachable file revisions: 9
private local client map: untracked=yes; gitignored=yes
existing synthetic guard/redactor tests: 21
related baseline: 47 passed in 43.64s (captured by #3521 planning)
```

The issue is a security/governance migration, so no prohibited value was copied
into a reproduction. The current tracked-file/history counts reproduce the
unsafe storage class without publishing content. Source count is 10+.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-13-issue-3522-private-rule-authority-migration.md` |
| Public registry schema | `schemas/legal-rule-registry.schema.json` |
| Private map schema | `schemas/legal-rule-map.schema.json` |
| Private seal schema | `schemas/legal-rule-authority-manifest.schema.json` |
| Public authority policy | `config/legal-rule-authority-policy.yaml` |
| Public opaque registry | `config/legal-rule-registry.yaml` |
| Authority CLI/package | `scripts/legal/manage_rule_authority.py`; `scripts/legal/rule_authority/*.py` |
| Synthetic tests | `scripts/legal/tests/test_rule_authority_{codec,seal,audit,workflow}.py` |
| CI gate | `.github/workflows/legal-rule-authority-gate.yml` |
| Legacy public deny list | `.legal-deny-list.yaml` |
| Operator documentation | `.claude/docs/legal-rule-authority.md` |
| Private outputs | external 0700 directory only; never Git |
| Plan index/reviews | `docs/plans/README.md`; `scripts/review/results/...3522...` |

---

## Deliverable

A public opaque rule registry and exact private-map codec will be bound by a
separately keyed HMAC authority manifest; strict CI and private audit commands
will prove the current commit tree clean and produce an owner-only reachable-
history assessment without publishing values, paths, object IDs, or findings.

## Authority and Threat Contract

### Public registry and policy

`legal-rule-registry-v1` will contain only:

```text
schema_version: 1
authority_revision: canonical lowercase UUIDv4
rules: sorted list of {
  rule_id: canonical lowercase UUIDv4,
  target: path | content | both,
  match_mode: exact-bytes | ascii-fold,
  severity: block | warn
}
```

Unknown/duplicate IDs or fields, identifying labels/descriptions, unsorted
records, and invalid enums will reject. The public policy will bind the same
authority revision, forensic prefixes, and limits no greater than 10 MiB/blob,
100 MiB/request, 10,000 entries, and 1,000 findings. It will contain no pattern.

### Private map codec

`legal-rule-map-v1` will be canonical UTF-8 JSON plus LF:

```text
schema_version: 1
authority_revision: same UUIDv4
rules: sorted list of {rule_id, pattern_b64}
```

JSON duplicate keys will reject before schema validation. Base64 will use
canonical padded RFC 4648 form, strict decoding, and re-encode comparison.
Decoded patterns will be 1..65,536 bytes, total decoded bytes ≤10 MiB, one entry
per public rule, and unique by decoded bytes. Empty, extra, missing, duplicate,
or noncanonical entries will reject without echoing data.

### Independent trust anchor

The owner-only `seal` transaction will require a separately provisioned
`LEGAL_SCAN_AUTH_KEY` containing exactly 32 random bytes in canonical base64.
It will write a private canonical manifest containing schema/revision and
SHA-256 of the exact public registry, public policy, and private map bytes. Its
MAC will be:

```text
HMAC-SHA-256(key,
  "LEGAL-RULE-AUTHORITY\0v1\0" ||
  u64be(len(revision)) || revision_ascii ||
  u64be(32) || registry_sha256_raw ||
  u64be(32) || policy_sha256_raw ||
  u64be(32) || map_sha256_raw)
```

The key and manifest will be provisioned through separate secrets/files; neither
will be derived from or stored beside mutable repo content by default. Verify
will use constant-time MAC comparison before decoding patterns. Map, manifest,
key file/parent ownership, regular-file type, mode 0600/0700, and no-follow
component traversal will fail closed. Pattern substitution/deletion, severity/
target/mode weakening, revision drift, or key/manifest mismatch will return rc3.

### Evidence and public output

Private audit reports will be canonical JSON written atomically to an external
0700 directory as 0600 files. They may contain paths/OIDs/findings only there.
Public stdout/stderr/CI summaries will contain command class, authority revision,
aggregate object counts, verdict, and rc only—never matched bytes, rule-specific
counts, paths, commits, refs, hashes that locate findings, map/manifest digests,
or private source locations.

## Audit and History Boundary

`audit-tree` will scan raw path and blob bytes from a caller-selected commit via
`git ls-tree -rz --full-tree` and streaming `cat-file`, never filesystem reads.
It will also scan commit message bytes and ref metadata selected by the caller.
Missing authority, malformed Git output, unsupported objects, caps, or read
errors will fail closed.

`audit-history` will operate only in a fresh private mirror. The operator will
fetch visible heads/tags and pull-request heads, enumerate all reachable commit,
tag, tree, path, and blob bytes, deduplicate objects, and write exact findings
only to the private report. A public issue comment will state assessment status
and owner disposition only.

Actual history rewriting, force-pushing, cache/support requests, collaborator
coordination, credential rotation, or deletion of remote refs will require a
separate issue, transaction preview, and explicit owner approval. #3522 will not
self-authorize that irreversible action and will remain open until the owner
records either an approved follow-on or an explicit residual-history decision.

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `schemas/legal-rule-{registry,map}.schema.json` | Freeze public/private codecs. |
| Create | `schemas/legal-rule-authority-manifest.schema.json` | Freeze private seal fields. |
| Create | `config/legal-rule-{registry,authority-policy}.yaml` | Publish opaque rules and bounded policy. |
| Create | `scripts/legal/manage_rule_authority.py` | Thin validate/seal/verify/audit CLI. |
| Create | `scripts/legal/rule_authority/*.py` | Split codec, seal, Git transport, audit, output. |
| Create | `scripts/legal/tests/test_rule_authority_*.py` | Hermetic synthetic TDD suite. |
| Create | `.github/workflows/legal-rule-authority-gate.yml` | Trusted-tool strict tree/metadata scan. |
| Modify | `.legal-deny-list.yaml` | Remove private values; retain public-safe legacy policy only. |
| Modify | `.github/workflows/legal-client-pii-gate.yml` | Remove reversible private location; preserve existing guard. |
| Modify | `.claude/docs/client-pii-prevention.md` | Route generic rules to sealed authority. |
| Create | `.claude/docs/legal-rule-authority.md` | Provisioning, rotation, audit, incident runbook. |
| Update | `docs/plans/README.md` | Index reviewed plan state. |

## TDD Test List

| Test | Verification |
|---|---|
| `test_codec_rejects_noncanonical_inputs` | Duplicate keys/IDs/bytes, bad UUID/base64/order/size/enums reject without echo. |
| `test_registry_contains_no_identifying_text` | Closed schema permits only opaque IDs and enums. |
| `test_seal_golden_vector` | Exact HMAC formula matches a checked-in synthetic hex vector. |
| `test_seal_detects_stable_weakening` | Pre-request map substitution/deletion and registry/policy downgrade reject. |
| `test_key_manifest_file_security` | Symlink, owner/mode, parent swap, short key, overwrite reject. |
| `test_tree_scans_raw_paths_and_blobs` | Non-UTF-8/binary/symlink and odd raw paths scan without dereference. |
| `test_tree_scans_commit_and_ref_metadata` | Synthetic message/ref finding blocks without public locator. |
| `test_history_covers_all_visible_refs` | Heads/tags/PR heads and shared objects are complete/deduplicated. |
| `test_private_report_atomicity` | 0700/0600/no-follow/no-overwrite/fsync/crash behavior is closed. |
| `test_public_output_is_non_enumerable` | No path/OID/hash/pattern/rule-specific count/source path leaks. |
| `test_ci_uses_trusted_base_tooling` | PR code is data only; no PR script/action executes with secrets. |
| `test_ci_secret_absence_fails_protected_events` | Internal PR/push/schedule cannot degrade open. |
| `test_fork_flow_requires_owner_rescan` | Fork PR cannot expose secrets or claim strict pass. |
| `test_legacy_list_has_no_private_values` | Private map finds zero matches in tracked public policy. |
| `test_existing_pii_guard_regression` | Existing 21 synthetic guard/redactor tests remain green. |

## Implementation Sequence

1. Add RED codec/seal golden-vector and hostile-file tests.
2. Implement canonical schemas, parser, HMAC seal, and independent verification.
3. Add RED raw tree/history transport, coverage, caps, and private-output tests.
4. Implement tree/history audits with synthetic rules and private reports.
5. Add RED workflow trust-boundary and protected-event tests; wire trusted-base
   `pull_request_target`, push, and schedule scans without executing PR code.
6. In an owner-attended private transaction, convert each current private value
   to an opaque rule/map entry, seal it, and provision separate CI secrets.
7. Remove private values from the public deny list and reversible private-source
   comments; run strict HEAD and metadata audit before commit.
8. Run the fresh-mirror reachable-history audit; deliver the 0600 report to the
   owner and create a generic follow-on issue if rewrite/rotation is chosen.
9. Run T3 code/artifact review. Any authority/content patch will require reseal,
   strict re-audit, and review before promotion.

## Acceptance Criteria

- [ ] RED evidence precedes each implementation slice.
- [ ] Exact schema/HMAC golden vectors and hostile codec tests pass.
- [ ] Public registry/policy contain only schema-approved opaque fields.
- [ ] Private map/manifest/key remain untracked, external, sealed, and protected.
- [ ] Strict `verify` rejects every stable weakening case before any scan.
- [ ] `audit-tree HEAD` reports zero private-rule findings across raw paths,
      blobs, commit message, and selected ref metadata.
- [ ] Trusted-base CI scans PR data without executing PR-controlled code; secret
      absence fails protected events and fork PRs cannot claim strict passage.
- [ ] Fresh-mirror audit covers all enumerated visible heads/tags/PR heads and
      writes only the private report; public output satisfies the withholding test.
- [ ] Existing 21 guard/redactor tests and the 47-test legal/enforcement baseline
      pass; new focused tests, Ruff, compileall, schema, workflow, function/file
      size, no-absolute-path, and legal checks pass.
- [ ] `.legal-deny-list.yaml` contains no private rule value; existing public-safe
      legacy behavior has golden regression coverage.
- [ ] Issue receives a non-sensitive implementation/assessment comment. History
      rewrite/rotation proceeds only under a separately approved transaction.
- [ ] T3 code/artifact review has no MAJOR. No self-merge, self-close, or
      self-approval occurs.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | pending | exact pushed revision required |
| Codex r1 | pending | exact pushed revision required |
| Gemini r1 | pending | exact pushed revision required |

**Overall result:** draft; implementation is blocked pending adversarial review
and explicit user approval. No agent may apply `status:plan-approved` or create
its marker.

## Risks and Open Questions

- **History reachability:** hosting-provider caches and hidden refs may outlive a
  force-push. The private assessment will distinguish Git-visible remediation
  from provider-support follow-up.
- **Irreversibility:** rewrite, force-push, rotation, and remote deletion remain
  separately approved owner transactions.
- **Forks:** no secret will be exposed to fork code. A fork will require trusted
  base-revision scanning and owner rerun before merge.
- **Dependency:** #3521 will remain draft until this authority merges and its
  exact SHA/schema/policy can be pinned and re-reviewed.

---

## Complexity: T3

This is a public security migration spanning private authority, Git history,
CI trust boundaries, schemas, raw-byte audit, and irreversible follow-on risk.
