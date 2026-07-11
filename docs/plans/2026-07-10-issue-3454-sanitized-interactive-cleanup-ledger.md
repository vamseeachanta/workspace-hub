# Plan for #3454: Publish a sanitized interactive cleanup ledger and prune stale local permission residue

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3454
> **Private evidence authority:** opaque; repository and issue identifiers intentionally withheld
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** planning/review `parallel-readonly`; implementation `single-lane`
> **Schemas:** `local-analysis-cleanup/public-projection/v1`; `local-analysis-cleanup/permission-edit-authority/v1`
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3454-{claude,codex,gemini,disagreement}.md`; `...-codex-inline-r{1,2,3,4,7,8,9}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `docs/reports/2026-07-10-local-analysis-cleanup-flow-design.html` defines the user-approved local/public/private boundary, five dispositions, artifact locations, and fail-closed behavior. Its privacy-redacted approved-design blob SHA-256 is `7c458a10d6b9a7fd66ec828e78ad7f4731e1010fcb162d37d43125834947188d`.
- `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md` defines origin/residue/archive checks, per-action approval, race checks, a cleanup lock, trash stage, verification, and the public Markdown handoff. Its TSV/checksum examples are not arbitrary-name-safe and are tracked separately by [#3458](https://github.com/vamseeachanta/workspace-hub/issues/3458).
- `docs/sessions/2026-05-19-mnt-analysis-cleanup.md` and `docs/sessions/2026-05-24-mnt-local-analysis-conservative-cleanup.md` provide transaction precedents but publish exact paths, so they cannot be copied into this public run.
- `scripts/legal/check-client-pii.py --strict`, `scripts/workflow/render_completeness_html.py`, `tests/workflow/test_render_completeness_html.py`, `docs/reports/sessions/manifest.json`, and `scripts/build_pages.py` provide value-withholding, canonical round-trip, and Pages patterns.
- The machine-local settings JSON is valid, with eight allow entries and exactly two stale candidates. Raw values remain withheld. The root is `fuseblk`; chmod does not change its reported `0777` modes, so mount/ACL hardening belongs to [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456).
- No #3454 plan, public cleanup schemas, sanitized-bundle validator/renderer, guarded permission editor, or approval marker exists on live `origin/main`.

### Standards and wiki

Not applicable. This issue will not touch engineering calculations, standards-derived constants, data pipelines, or wiki content.

### Documents and issues consulted

- [#3454](https://github.com/vamseeachanta/workspace-hub/issues/3454) defines the public outcome and local permission edit.
- An opaque private evidence authority owns exact ledger instances, exact sidecars, and every live mutation; its repository, issue, and path identities will not enter public artifacts.
- [#2572](https://github.com/vamseeachanta/workspace-hub/issues/2572) is the persistent sanitized milestone sink.
- [#3453](https://github.com/vamseeachanta/workspace-hub/issues/3453), [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456), and [#3458](https://github.com/vamseeachanta/workspace-hub/issues/3458) own scheduled cleanup, mount permissions, and arbitrary-name manifests; [#3461](https://github.com/vamseeachanta/workspace-hub/issues/3461) promotes r4 staged-evidence findings, while [#3467](https://github.com/vamseeachanta/workspace-hub/issues/3467) owns the independently reviewed structured-review bootstrap, provider layout contracts, retained-input gate, FD allowlists, and parity/redaction rules exposed by r8/r9.
- `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, `docs/architecture/report-publication-gates.md`, and `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md` require control-plane ownership, durable ledgers, publication gates, empirical sibling coverage, and private-to-public promotion.
- The mandatory drive-index query for `local-analysis cleanup ledger permissions` timed out twice before returning usable JSON. Drive coverage is **UNAVAILABLE**, not “no relevant files”; no ad-hoc drive crawl substitutes for it.

### Gaps identified

- A versioned public projection schema and bounded public modules will need to be built.
- The opaque private authority will need its own exact schema, validator/tests, write-ahead events, legal/residency policy, and pinned dependency on the reviewed public tool commit.
- Permission editing will need optimistic concurrency, same-mount durability probes, value-withholding authority input, and an explicit residual TOCTOU boundary.
- Cross-repo delivery will need non-self-referential A→B-local→Q→R:PASS→B-push→C receipts and reconciliation.
- The original 124-directory observation has no immutable manifest. It will remain `historical_observation`; only a fresh `baseline_v1` will be authoritative.

### Evidence (embedded verification)

**Resource-intel base snapshot** (remote refs verified 2026-07-11T07:19:13-05:00):

```text
workspace-hub origin/main = 41bc08be724726de66405e234cad4206fa0906e6
private authority base = attested only in private scope; identifier withheld
```

Immediately before review dispatch/push, a separate attestation will record the reviewed tip, GitHub-fetched `main`, merge-base, ahead/behind counts, overlap paths, and observed remote branch head. Dispatch requires `merge-base(tip, main) == main` and behind=0; upstream overlap requires rebase and re-review, while later non-overlap drift will be recorded and re-attested. Immediate-parent equality applies only if the branch is intentionally squashed.

**Issue state** (verified 2026-07-11): #3454 is OPEN at `status:needs-plan`; the opaque private authority is open but its lifecycle identifiers remain private; #2572 remains OPEN; #3453, #3456, #3458, #3461, and #3467 are OPEN at `status:needs-plan`.

**Live value-withholding probe:**

```text
settings_valid_json=true
allow_count=8
stale_candidate_count=2
candidate_target_exists_count=0
candidate_registered_worktree_count=0
mount_type=fuseblk
reported_modes=0777,0777,0777
live_immediate_directory_observation=128
```

**Gap proofs:**

```text
$ git grep -n '3454' origin/main -- docs/plans
<no output; exit 1>
$ git ls-tree -r --name-only origin/main -- scripts/operations schemas | grep local_analysis_cleanup
<no output>
```

**Reproduction:** YES — two stale candidates remain and their targets are absent/unregistered. The 124→128 observations cannot establish intervening deltas; the implementation will start a fresh baseline.

Distinct sources: 12.

## Parent/Child Ownership and Dependency Lock

| Owner | Exclusive responsibility |
|---|---|
| Public #3454 | Public projection and permission-authority schemas; reusable synthetic-tested permission editor; sanitized-bundle validation; public Markdown/HTML rendering; public leakage/legal/Pages checks; pure publication-reconciliation library; bounded local candidate/receipt handoff refs. |
| Opaque private authority | Exact ledger schema/instances; fresh baseline; exact evidence and WAL; private projection export; persistent publication state and external-action wrapper; every live `--apply` invocation; every manual folder transaction; private pre/post-action commits and pushes. |

Private execution will remain blocked until the public plan is pushed/approved, Phase A tooling passes code review, and a public implementation commit is pushed. The opaque private authority will pin that commit, tool blob hashes, and both cross-repo public schema blob hashes/versions; its wrapper will refuse any mismatch. Workspace-hub will consume only a sanitized runtime bundle and never read the private ledger. The public library will remain pure; the public verifier alone may retain bounded local candidate/handoff refs, while the private wrapper exclusively owns ledger/cross-repo receipt persistence and authorized remote/comment actions.

Public approval requires user-created `status:plan-approved` plus `.planning/plan-approved/3454.md`. Private approval requires its separately provisioned canonical lifecycle labels and user-created private marker, each binding the reviewed plan commit. No agent will create or self-apply approval.

## Versioned Public Contracts

Public #3454 will own cross-repo `public-projection/v1` and `permission-edit-authority/v1`, plus internal `public-verification-result/v1` and `public-validation-attestation/v1` machine-evidence schemas. The opaque private authority will pin the two cross-repo schema blobs, the runtime-manifest blob, and the identical manifest-selected public executable/import closure.

Canonical JSON payloads use UTF-8, sorted keys, `separators=(",",":")`, `ensure_ascii=false`, standard escaping, no NaN/Infinity, and one trailing LF; duplicate keys, invalid UTF-8, and lone surrogates reject. The LF applies only to canonical JSON documents; raw file/scalar/64-byte payloads add none. Schema-selected projection fields use NFC; settings strings never normalize. Every non-raw SHA-256 input is `ASCII-domain-tag + NUL + payload`. `projection-document-v1`, `permission-authority-document-v1`, and `approval-record-v1` hash full canonical documents; `public-promotion-v1` hashes canonical allowed `{run_id,projection_digest,revision}` only; `provider-cli-closure-v1` hashes the canonical sorted `[{label,mode,sha256}]` closure array; `provider-cli-argv-v1` hashes the canonical argv string array; `review-scope-v1` hashes canonical `{target_kind,base_oid,reviewed_oid,reviewed_tree_oid,commit_sha256,blob_map,review_stage,check_set,subject_transport,prompt_text,prompt_sha256}` with `blob_map` path-sorted and an exact transport object; `review-unavailable-evidence-v1` hashes the canonical embedded `unavailable_evidence`; `non-allow-subtree-v1` hashes canonical root settings minus `/permissions/allow`; `retained-allow-sequence-v1` hashes the exact ordered string array; `target-value-v1` hashes exact scalar UTF-8; `target-set-v1` hashes `min(c1,c2) || max(c1,c2)`, lexicographically ordering two distinct raw 32-byte commitments with no LF. Raw `before-file-sha256`, `prompt_sha256`, `commit_sha256`, carrier-manifest/blob/artifact/adjudication `sha256`, and provider prompt/response/diagnostic/CLI `sha256` fields hash complete stored exact bytes and cannot substitute for a domain commitment. Prompt bytes are finalized/stored first and exclude scope digest, dependency lock, and U identity; only then is scope digest computed. Literal transport is pushed `{kind:"pushed_commit",host:"github.com",repository,remote_oid}` or private snapshot `{kind:"private_scope_snapshot",carrier_host:"github.com",carrier_repository,carrier_oid,target_host:"github.com",target_repository,base_oid,manifest_path,manifest_blob_oid,manifest_sha256}`. Every reviewed commit has sole raw parent `base_oid`, raw commit bytes rehash to `reviewed_oid`/`commit_sha256`, and `blob_map` is set-equal to its complete no-renames A/M diff with unique canonical-safe exact new-tree `{path,mode,blob_oid,sha256}` regular-file rows; deletion, type/rename, symlink/gitlink, unsafe path, or omission rejects. The private carrier manifest is canonical `local-analysis-cleanup/review-subject-carrier/v1` exact `{schema_id,target_host,target_repository,target_oid,target_tree_oid,base_oid,commit_blob_oid,commit_sha256,blob_map}` plus LF at safe `manifest_path` ending `/candidate-scope/manifest.json`; sibling `commit.raw` rehydrates the exact commit and `files/<path>` rehydrates every changed blob. `manifest_blob_oid`/raw `manifest_sha256` bind manifest bytes, which exclude carrier/Q/R/scope/prompt identities. Missing/non-array allow, domain, duplicate, normalization, order, or framing drift rejects. Settings payloads/digests stay private.

| Field | Contract |
|---|---|
| `run_id` | UUIDv4; immutable |
| `alias` | `la1_` + 20 random base32 chars; run-scoped, collision-checked, tombstoned, never reused |
| `class` | `canonical_repo|linked_worktree|standalone_clone|runtime_config|system_managed|preservation|data|cache|scratch|unknown` |
| `disposition` | `keep|delete|relocate|archive|defer`; independent of transaction outcome |
| `transaction_state` | `discovered|evidence_ready|decision_recorded|preflight_verified|wal_pushed|executing|verified|deferred|failed_no_effect|rollback_pending|rolled_back|rollback_failed` |
| `action_blocked` | Boolean run-level quarantine flag; true after any unresolved `rollback_failed` |
| `resolution_status` | `none|authority_pushed|correcting|resolved|resolution_failed`; sanitized only |
| `resolution_incident` | Nonnegative run-scoped ordinal; increments on each new `rollback_failed` |
| `resolution_revision` | Nonnegative retry ordinal within the active incident |
| `public_promotion_commitment` | `public-promotion-v1` digest over allowed run/projection/revision bytes; no private identity |
| `reason_code` | `canonical_active|active_worktree|system_managed|machine_runtime|unique_evidence|redundant_verified|reconstructible|relocate_by_contract|insufficient_evidence|user_directive|other_private` |
| `size_bucket` | `empty|lt_1m|m1_99|m100_999|g1_9|gte_10g|unknown` |
| `age_bucket` | `lt_1d|d1_7|d8_30|d31_90|gt_90d|unknown` |
| `repo_state` | `not_git|clean_synced|clean_diverged|dirty|unmerged|unverified` |

The permission-authority schema will require schema ID/version, algorithm version, raw before-file SHA-256, exactly two distinct domain-separated target commitments, unchanged non-allow-subtree digest, ordered retained-allow-sequence digest, cardinality-two target-set digest, reviewed plan commit, approval-record digest/approver identity/reference/timestamp, exact issuance/expiry timestamps, and expected target absence/registration state. Optional `adjacent_temp_exposure_decision: reject|accept` defaults to `reject`; `accept` requires an explicit matching user record. Raw targets/unknown fields are forbidden.

The folder audit predicate will be immediate entries for which `is_dir(follow_symlinks=False)` is true. Files, symlinks, broken symlinks, permission errors, and timeouts will be recorded as root anomalies but excluded from the folder count. Inode data on FUSE will be advisory; mount identity/remount ambiguity will defer private remapping.

Allowed revision-monotonic edges are `discovered→evidence_ready|deferred|failed_no_effect`; `evidence_ready→decision_recorded|deferred|failed_no_effect`; `decision_recorded→preflight_verified|deferred|failed_no_effect`; `preflight_verified→wal_pushed|deferred|failed_no_effect`; `wal_pushed→executing|deferred|failed_no_effect`; `executing→verified|failed_no_effect|rollback_pending`; `rollback_pending→rolled_back|rollback_failed`; `failed_no_effect→evidence_ready|deferred`; `rolled_back→evidence_ready|deferred`; and `deferred→evidence_ready`; `verified`/`rollback_failed` are terminal. A new rollback failure increments `resolution_incident`, sets revision 0/status `none`/blocked. Within it, `none|resolution_failed→authority_pushed→correcting→resolved|resolution_failed`; retry requires revision+1 and fresh approval, preserves prior events, and remains blocked until `resolved`. A later rollback after resolution opens incident+1. The truth table requires blocked for every active non-resolved status and unblocked only with no incident or resolved; terminal entries never mutate.

Public timestamps will be date-level or milestone ordinals. Public hashes will cover projection/prepared/verification bytes only—never names or paths. Exact sizes, timestamps, branches, remotes, and free text stay private.

Private token policy will classify values as `confidential|approved_public|common_nonidentifying`. Confidential values will fail in boundary, case-folded, HTML/JSON escaped, URL-encoded, filename, comment, and attribute forms. Common tokens will fail only in path-aware combinations. Any allow decision will bind one token/encoding/artifact instance; no directory-wide exemption.


## Transaction and Publication States

Folder actions will remain manual, one-at-a-time commands under the cleanup skill; no automatic delete/relocate executor will be added. Private tooling will prepare/push a write-ahead event, verify freshness, and reconcile incomplete events before another action.

Publication will use:

`draft → validated_local → private_committed(A) → private_pushed(A) → public_candidate_committed(B) → candidate_receipt_pushed(Q) → review_receipt_pushed(R) → public_pushed(B) → comments_partial → comments_complete → private_receipt_committed(C) → private_receipt_pushed_verified(C) → local_refs_cleaned → published`.

Private A binds run/projection. Complete detached B contains only allowed bytes—never A identity—and has one base plus set-equal safe regular-file A/M scope. Raw B is exactly `tree FINAL_TREE`, `parent BASE_HEAD`, author/committer `Workspace Hub Automation <workspace-hub@users.noreply.github.com> 1783684800 +0000`, blank separator, and `chore(cleanup): publish sanitized cleanup ledger\n`, with no other headers/signature. Pushed private Q binds A↔commitment and exact B/base/tree, stores canonical manifest, `commit.raw`, and every new blob under sibling `files/<path>`, sufficient to rebuild B from fetched public base. Providers receive Q/base/manifest/raw-byte verification plus retained-CLI challenges; exact transport/response bind R. PASS pushes unchanged B; failures preserve B/Q/R and start revision+1. C binds comments; its commit, push, and remote-OID verification precede exact-CAS cleanup of atomic local candidate/receipt refs.


## Artifact Map

| Artifact | Path |
|---|---|
| Plan/design | `docs/plans/2026-07-10-issue-3454-sanitized-interactive-cleanup-ledger.md`; `docs/reports/2026-07-10-local-analysis-cleanup-flow-design.html` |
| User approval marker | `.planning/plan-approved/3454.md` (user-created after review) |
| Public schemas | `schemas/local-analysis-cleanup/{public-projection-v1,permission-edit-authority-v1,public-verification-result-v1,public-validation-attestation-v1}.schema.json` |
| Public package | `scripts/operations/local_analysis_cleanup/{schema.py,projection.py,privacy.py,render.py,publication.py,cli.py,runtime-closure.json}`; `scripts/operations/{launch_issue_3454_verification.py,verify_issue_3454_package.sh}` |
| Permission editor | `scripts/operations/prune_local_claude_permissions.py` |
| Public tests | `tests/operations/test_local_analysis_cleanup_public.py`; `tests/operations/test_prune_local_claude_permissions.py` |
| Skill routing test/update | `tests/skills/test_mnt_analysis_cleanup_visibility_routing.py`; `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md` |
| Public outputs | `docs/sessions/2026-07-10-mnt-analysis-cleanup.md`; `docs/reports/sessions/2026-07-10-mnt-analysis-cleanup.html`; `docs/reports/sessions/manifest.json` |
| Validation attestation | `docs/reports/2026-07-10-local-analysis-cleanup-verification.json` |
| Private plan/schema | Opaque private authority; exact repository, issue, and path identities remain private |
| Reviews/completeness | `scripts/review/results/2026-07-10-plan-3454-*.md`; `docs/reports/2026-07-10-3454-completeness.html` |


## Deliverable and Pseudocode

A reviewed public toolkit will validate/render only sanitized bundles, guard the two-rule local edit, and publish a recoverable public record while the opaque private authority exclusively records and executes the interactive run.

```text
validate_bundle(bundle):
    validate public-projection/v1 and canonical digest
    reject unknown fields and private-detail shapes
    verify alias uniqueness, tombstones, counts, buckets, and state enums

render_public(bundle):
    embed identical canonical projection in Markdown and escaped self-contained HTML
    emit deterministic comment bodies with marker/body digest
    round-trip both artifacts before publication

guarded_permission_replace(settings_root_fd, settings_leaf, probe_root_fd, authority_fd, runtime_dir):
    require both root fds inherited from O_RDONLY|O_DIRECTORY|O_NOFOLLOW opens
    require current-user-owned distinct identities; probe rejects mount/settings/repos/worktrees/shared roots
    require one safe settings leaf; reject empty, dot, dot-dot, slash, NUL, or wrong-type fd
    require authority schema/version, reviewed plan, user approval, before digest, and two target commitments
    treat missing/reject D1 as defer_until_3456; never enter guarded replacement
    require equal fdinfo mount IDs; device/source equality is diagnostic only
    for accept, require matching explicit D1 record and green exact-mount synthetic probes
    open/recheck settings only with openat(settings_root_fd, settings_leaf, O_NOFOLLOW)
    openat temp O_CREAT|O_EXCL|O_NOFOLLOW|O_RDWR mode 0600 and mkdirat probe mode 0700; EEXIST rejects
    fsync/replace/verify only with *at operations on retained fds
    fsync root fds; clean only created leaves; document residual non-cooperating-writer TOCTOU

plan_publication_reconciliation(observation):
    compare expected and observed remote OIDs without force
    require current pushed Q and aggregate R:PASS bind exact B commit/tree; R:FAIL|STALE revises B/Q
    validate supplied remote/reflog evidence after rejection
    return one deterministic next action from supplied comment-marker observations
    never persist receipts, call GitHub, or mutate private/public state
```

Rollback in `/run/user/<uid>` will cover process failure only. Crash safety will rely on validated temp + atomic rename + successful file/parent fsync; interruption tests will cover before replace, after replace, and before verification. No persistent adjacent rollback will be retained on fuseblk.

**Decision D1 — adjacent raw-temp exposure.** Recommended/default: **REJECT** and defer the permission change until [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456) resolves the mount posture. Generic plan approval without an explicit D1 choice is allowed only on this safe REJECT route. Alternative **ACCEPT** requires a separate explicit user record bound to the reviewed plan commit plus green same-mount probes. No unspecified editor is a fallback because editors may create adjacent swap/temp files.

D1 REJECT/defer will not satisfy #3454's permission-removal acceptance criterion, completeness gate, or closure. The issue will remain open until #3456 enables a safe route or the user explicitly accepts D1 and the verified postcondition proves both stale rules absent.


## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `schemas/local-analysis-cleanup/{public-projection-v1,permission-edit-authority-v1,public-verification-result-v1,public-validation-attestation-v1}.schema.json` | Freeze cross-repo and machine-evidence contracts. |
| Create | `scripts/operations/local_analysis_cleanup/{*.py,runtime-closure.json}`; `scripts/operations/{launch_issue_3454_verification.py,verify_issue_3454_package.sh}` | Keep bounded modules plus an exact inline-bootstrap/launcher/driver/runtime closure. |
| Create | `scripts/operations/prune_local_claude_permissions.py` | Supply the reusable guarded editor; the opaque private authority alone will invoke live apply. |
| Create | `tests/operations/test_local_analysis_cleanup_public.py`; `tests/operations/test_prune_local_claude_permissions.py` | Drive public behavior test-first. |
| Update | `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md`; `tests/skills/test_mnt_analysis_cleanup_visibility_routing.py` | Route exact evidence away from public repos. |
| Create/update | Public plan/design/session/report/manifest/review/completeness paths in the Artifact Map, including `docs/reports/2026-07-10-local-analysis-cleanup-verification.json` | Preserve reviewed public artifacts and a non-self-referential validation attestation. |
| Update | `docs/plans/README.md` | Index the draft/review state. |

No public code will read the private ledger. No automatic folder executor, raw archive, raw settings copy, root-settings generator, mount change, scheduled-cleanup fix, or #3458 manifest redesign will be added.


## TDD Test List

Tests will be written first with synthetic-only private values:

| Test | Verification |
|---|---|
| `test_public_schema_contract` | All four public schema IDs/versions, digest byte grammars, cross-domain substitution, enums, authority/D1 shape, duplicate/reused aliases, count drift, and blob mismatch reject. |
| `test_transaction_graph` | Partial/unknown effects cannot defer; terminal entries stay immutable; incident/revision/status/block truth, failed-retry supersession, and later-incident reset enforce one approved corrective lane at a time. |
| `test_public_round_trip` | Bundle/Markdown/HTML share canonical bytes/digest; markup escapes; no network assets. |
| `test_token_policy` | Confidential/common/public tokens, boundaries, substrings, comments, attributes, filenames, Unicode, and encodings behave without value logs. |
| `test_permission_authority` | Missing/reject D1 defers; accept requires a bound user record, reviewed plan, exactly two targets, fresh authority, absent targets, fd/path identity, and quiescence. |
| `test_fuse_guarded_replace` | Wrong/duplicate FDs, ownership/mount/protected-root failures, temp/probe collision, symlink/stale-leaf reuse, and equal-device/source-but-different-`mnt_id` reject; retained FDs prove exclusive `*at` creation, rename, fsync, and child-only cleanup. |
| `test_permission_value_withholding` | Six unrelated values/non-allow subtree remain; stdout/stderr/attestations/repo/comments contain no raw value. |
| `test_publication_recovery` | A→B-local→Q→aggregate-R→B-push→C-commit→C-push/remote-verify→ref-cleanup; artifact hash/OID/quorum/degradation/`R:FAIL|STALE`, B revision, remotes, crashes, comments, and retry verify. |
| `test_visibility_routing` | Exact sidecars require a private sink; #3458 retains arbitrary-name format ownership. |
| `test_pages_output` | Pages builds/scans only the sanitized report. |
| `test_public_contract_pin_gate` | Sanitized bundle public schema/tool-version mismatch blocks rendering without reading private pin state. |
| `test_validation_attestation` | Unique-run nonce/tree/tool/check-set-bound results reject replay/tamper/concurrency; attestation excludes itself and C binds B. |
| `test_staged_snapshot_boundary` | Staged/working divergence, deletion/type change, missing path, implicit-HEAD movement, object substitution, exact runtime closure, ancestor archive attributes, contained tracked symlinks, raw attestation insertion, hostile child shell/Python/uv state after the trusted-parent loader boundary, inline-bootstrap/launcher drift, pipe/unsealed/wrong-hash driver FDs, retained-byte tool/uv fencing, `-I -S -B` compatibility, map/output tamper, and concurrent rewrite cannot evade exact-tree checks. |
| `test_final_commit_fence` | Complete A/M review-map equality, output/index drift, hook failure, wrong tree/parent, namespace/preexisting-pair ambiguity, candidate/receipt construction/import/ref-CAS/trap failure, remote movement, auto-sync risk, and OID mismatch block; exact durable detached B and receipt verify. |


## Implementation Sequence

1. The public exact commit will rebase/push, receive adversarial review, enter `status:plan-review`, then only the user-created commit-bound marker/approval may permit `status:plan-approved`; the private plan will remain `status:needs-plan` until #3467 lands, its exact D contract is imported, and the revised private commit repeats that order.
2. Phase A will land public schemas/modules/tests and complete code review. The private plan will pin the landed commit/blob digests.
3. The opaque private authority will create `baseline_v1`; the 124 and 128 counts will remain incomplete historical observations, not reconstructed deltas.
4. For the permission edit and every later mutation, the opaque private authority will validate approval/preflight JSON, commit/push pre-action WAL, verify remote OID, reacquire an execution ASCP claim, rerun freshness checks, apply manually or via the pinned permission editor, then commit/push result evidence.
5. Private export will write a sanitized-only runtime bundle under the verified user-private runtime directory. Public code will consume only that bundle; private validation will rescan final public bytes.
6. Private A will push; after required hooks/scans pass, pinned public candidate tooling will create detached B with only allowed public bytes/promotion commitment, then pushed private Q will bind A↔commitment and carry the verified exact B review-scope bytes without public delivery; pushed/remote-verified C will precede local ref cleanup.
7. T3 aggregate R will bind exact B/provider artifacts plus carrier transport; only current PASS permits unchanged non-force B push, scanned comments, and C binding B/Q/R. Later milestones repeat.
8. The interactive folder audit will resume one folder at a time; unknown state will defer, and completeness evidence, temporary-worktree removal, and cleanup audit will precede closeout.


## Verification Commands

Provisional bootstrap (deliberately non-executable until #3467 replaces/reviews its FD contract): `echo 'BLOCKED: #3467' >&2; exit 78; unset LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT; /usr/bin/env -i PATH=/usr/bin:/bin HOME="${HOME:?}" PINNED_PUBLIC_TOOL_COMMIT="${PINNED_PUBLIC_TOOL_COMMIT:?}" LEGAL_CLIENT_MAP="${LEGAL_CLIENT_MAP:?}" LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD="${LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD:?}" LOCAL_ANALYSIS_SETTINGS_ROOT_FD="${LOCAL_ANALYSIS_SETTINGS_ROOT_FD:?}" PINNED_UV_BIN="${PINNED_UV_BIN:?}" PINNED_UV_SHA256="${PINNED_UV_SHA256:?}" PINNED_UV_VERSION="${PINNED_UV_VERSION:?}" /usr/bin/python3 -I -S -B -c 'import hashlib,json,re,subprocess,sys; c=sys.argv[1]; assert re.fullmatch(r"[0-9a-f]{40}",c); env={"PATH":"/usr/bin:/bin","HOME":__import__("os").environ["HOME"],"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null","GIT_NO_REPLACE_OBJECTS":"1","GIT_ATTR_NOSYSTEM":"1","LC_ALL":"C"}; git=lambda *a:subprocess.run(["/usr/bin/git",*a],env=env,stdout=subprocess.PIPE,check=True).stdout; cb=git("cat-file","commit",c); assert hashlib.sha1(b"commit "+str(len(cb)).encode()+b"\0"+cb).hexdigest()==c; mp="scripts/operations/local_analysis_cleanup/runtime-closure.json"; mb=git("cat-file","blob",c+":"+mp); mo=git("rev-parse",c+":"+mp).strip().decode(); assert hashlib.sha1(b"blob "+str(len(mb)).encode()+b"\0"+mb).hexdigest()==mo; bad=lambda z:(_ for _ in ()).throw(ValueError(z)); hook=lambda q:dict(q) if len(q)==len({k for k,_ in q}) else bad("duplicate"); x=json.loads(mb.decode(),object_pairs_hook=hook,parse_constant=bad); assert mb==(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode(); lp="scripts/operations/launch_issue_3454_verification.py"; e=next(v for v in x["files"] if v["path"]==lp); lb=git("cat-file","blob",c+":"+lp); lo=git("rev-parse",c+":"+lp).strip().decode(); assert e["mode"]=="100755" and e["blob_oid"]==lo and hashlib.sha1(b"blob "+str(len(lb)).encode()+b"\0"+lb).hexdigest()==lo and hashlib.sha256(lb).hexdigest()==e["sha256"]; sys.argv=[lp,"launch","--pinned-tool-commit",c]; exec(compile(lb,lp,"exec"),{"__name__":"__main__","__file__":lp,"__runtime_manifest_bytes__":mb,"__pinned_tool_commit__":c})' "$PINNED_PUBLIC_TOOL_COMMIT"`
```bash
# shellcheck disable=SC2317,SC2329
echo 'BLOCKED: #3467 must land and replace/review this provisional executable fence before use' >&2; exit 78
set -euo pipefail; : "${LOCAL_ANALYSIS_DRIVER_FD:?launcher-retained sealed driver fd}"; : "${LOCAL_ANALYSIS_MANIFEST_FD:?launcher-retained sealed manifest fd}"; : "${LOCAL_ANALYSIS_DRIVER_SHA256:?manifest-bound driver digest}"; : "${LOCAL_ANALYSIS_MANIFEST_SHA256:?pinned manifest digest}"; : "${PINNED_PUBLIC_TOOL_COMMIT:?GitHub-present code-reviewed tool commit}"; [[ "$LOCAL_ANALYSIS_DRIVER_FD" =~ ^[0-9]+$ && "$LOCAL_ANALYSIS_MANIFEST_FD" =~ ^[0-9]+$ && "$LOCAL_ANALYSIS_DRIVER_SHA256" =~ ^[0-9a-f]{64}$ && "$LOCAL_ANALYSIS_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ && "$PINNED_PUBLIC_TOOL_COMMIT" =~ ^[0-9a-f]{40}$ && "$0" == "/proc/self/fd/$LOCAL_ANALYSIS_DRIVER_FD" && "${BASH_SOURCE[0]}" == "/proc/self/fd/$LOCAL_ANALYSIS_DRIVER_FD" ]]; [[ -z "${BASH_ENV-}${ENV-}" && -z "$(builtin compgen -A function)" ]]; unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR GIT_SHALLOW_FILE GIT_CEILING_DIRECTORIES LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME TAR_OPTIONS GZIP BZIP2 BZIP XZ_OPT; PATH=/usr/bin:/bin; export PATH GIT_NO_REPLACE_OBJECTS=1 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1; /usr/bin/python3 -I -S -B -c 'import fcntl,os,stat,sys; fds=[int(x) for x in sys.argv[1:]]; ss=[os.fstat(x) for x in fds]; need=fcntl.F_SEAL_SEAL|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_GROW|fcntl.F_SEAL_WRITE; assert all(stat.S_ISREG(s.st_mode) and (fcntl.fcntl(f,fcntl.F_GET_SEALS)&need)==need for f,s in zip(fds,ss)); assert (ss[0].st_dev,ss[0].st_ino)!=(ss[1].st_dev,ss[1].st_ino)' "$LOCAL_ANALYSIS_DRIVER_FD" "$LOCAL_ANALYSIS_MANIFEST_FD"; test "$(sha256sum -- "/proc/self/fd/$LOCAL_ANALYSIS_DRIVER_FD" | awk '{print $1}')" = "$LOCAL_ANALYSIS_DRIVER_SHA256"; test "$(sha256sum -- "/proc/self/fd/$LOCAL_ANALYSIS_MANIFEST_FD" | awk '{print $1}')" = "$LOCAL_ANALYSIS_MANIFEST_SHA256"
SOURCE_SHALLOW="$(git rev-parse --is-shallow-repository)"; test "$SOURCE_SHALLOW" = false
SOURCE_REPLACE_REFS="$(git for-each-ref --format='%(refname)' refs/replace)"; test -z "$SOURCE_REPLACE_REFS"; SOURCE_GRAFTS="$(git rev-parse --path-format=absolute --git-path info/grafts)"; test ! -e "$SOURCE_GRAFTS"
: "${LEGAL_CLIENT_MAP:?must point to a readable private client map}"
: "${LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD:?must be an inherited O_RDONLY|O_DIRECTORY|O_NOFOLLOW fd for the synthetic test root}"
: "${LOCAL_ANALYSIS_SETTINGS_ROOT_FD:?must be an inherited O_RDONLY|O_DIRECTORY|O_NOFOLLOW fd for the actual settings parent}"
test -f pyproject.toml
test -f scripts/legal/check-client-pii.py
test -f scripts/build_pages.py
test -f scripts/enforcement/check-no-abs-paths.sh
: "${PINNED_UV_BIN:?absolute no-symlink uv path}"; : "${PINNED_UV_SHA256:?reviewed 64-hex uv digest}"; : "${PINNED_UV_VERSION:?reviewed bounded uv version}"; [[ "$PINNED_UV_BIN" == /* && "$PINNED_UV_SHA256" =~ ^[0-9a-f]{64}$ && "$PINNED_UV_VERSION" =~ ^uv\ [0-9A-Za-z._+-]{1,64}$ ]]; UV_BIN="$PINNED_UV_BIN"; UV_BIN_SHA256="$PINNED_UV_SHA256"; UV_VERSION="$PINNED_UV_VERSION"
test -r "$LEGAL_CLIENT_MAP"
test -d "/proc/self/fd/$LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD" && test -r "/proc/self/fdinfo/$LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD"
test -d "/proc/self/fd/$LOCAL_ANALYSIS_SETTINGS_ROOT_FD" && test -r "/proc/self/fdinfo/$LOCAL_ANALYSIS_SETTINGS_ROOT_FD"

RUNTIME_DIR="/run/user/$(id -u)"
test -d "$RUNTIME_DIR" && test ! -L "$RUNTIME_DIR"
test "$(stat -c %u "$RUNTIME_DIR")" = "$(id -u)" && test "$(stat -c %a "$RUNTIME_DIR")" = 700
umask 077
: "${LOCAL_ANALYSIS_VERIFY_LOCK_FD:?launcher-held canonical lock fd}"; [[ "$LOCAL_ANALYSIS_VERIFY_LOCK_FD" =~ ^[0-9]+$ ]]; /usr/bin/python3 -I -S -B -c 'import fcntl,os,stat,sys; fd=int(sys.argv[1]); root=sys.argv[2]; rd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW); canonical=os.open("issue-3454.verify.lock",os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600,dir_fd=rd); a=os.fstat(fd); b=os.fstat(canonical); assert stat.S_ISREG(a.st_mode) and a.st_uid==os.getuid() and stat.S_IMODE(a.st_mode)==0o600 and (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino); fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB); os.close(canonical); os.close(rd)' "$LOCAL_ANALYSIS_VERIFY_LOCK_FD" "$RUNTIME_DIR"
RUN_TMP="$(mktemp -d "$RUNTIME_DIR/issue-3454.XXXXXX")"
trap 'rm -rf --one-file-system "$RUN_TMP"' EXIT
RUN_NONCE="${LOCAL_ANALYSIS_RUN_NONCE:?launcher-generated for zero refs or derived from the sole validated pair}"; [[ "$RUN_NONCE" =~ ^[A-Za-z0-9_-]{6,64}$ ]]; SANITIZED_HOME="$RUN_TMP/home"; TOOL_SNAPSHOT="$RUN_TMP/tool"; TRUSTED_GIT_DIR="$RUN_TMP/trusted.git"; TEST_ENV_ROOT="$RUN_TMP/test-env"; UV_CACHE_ROOT="$RUN_TMP/uv-cache"
mkdir -m 700 "$SANITIZED_HOME" "$TOOL_SNAPSHOT" "$TEST_ENV_ROOT" "$UV_CACHE_ROOT"
SOURCE_OBJECTS="$(realpath -e -- "$(git rev-parse --path-format=absolute --git-path objects)")"; /usr/bin/env -i PATH=/usr/bin:/bin HOME="$SANITIZED_HOME" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null LC_ALL=C /usr/bin/git init --bare -q "$TRUSTED_GIT_DIR"; mkdir -p "$TRUSTED_GIT_DIR/objects/info"; (set -C; printf '%s\n' "$SOURCE_OBJECTS" > "$TRUSTED_GIT_DIR/objects/info/alternates")
trusted_git() { /usr/bin/timeout 600 /usr/bin/env -i PATH=/usr/bin:/bin HOME="$SANITIZED_HOME" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_NO_REPLACE_OBJECTS=1 LC_ALL=C /usr/bin/git --git-dir="$TRUSTED_GIT_DIR" "$@"; }
trusted_index_git() { /usr/bin/timeout 600 /usr/bin/env -i PATH=/usr/bin:/bin HOME="$SANITIZED_HOME" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_NO_REPLACE_OBJECTS=1 LC_ALL=C GIT_INDEX_FILE="$ACTIVE_INDEX" GIT_WORK_TREE="$REPO_ROOT" /usr/bin/git --git-dir="$TRUSTED_GIT_DIR" "$@"; }
run_snapshot_cli() { local seconds="$1"; shift; /usr/bin/timeout "$seconds" /usr/bin/env -i PATH=/usr/bin:/bin HOME="$SANITIZED_HOME" XDG_RUNTIME_DIR="$RUNTIME_DIR" TMPDIR="$RUN_TMP" LC_ALL=C.UTF-8 GIT_NO_REPLACE_OBJECTS=1 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I -S -B -c 'import hashlib,json,os,stat,sys; p,mfd,mh,*a=sys.argv[1:]; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW); st=os.fstat(fd); assert stat.S_ISREG(st.st_mode); b=os.fdopen(fd,"rb").read(st.st_size+1); assert len(b)==st.st_size; mf=int(mfd); ms=os.fstat(mf); assert stat.S_ISREG(ms.st_mode); mb=os.pread(mf,ms.st_size+1,0); assert len(mb)==ms.st_size and hashlib.sha256(mb).hexdigest()==mh; x=json.loads(mb.decode("utf-8")); e=next(v for v in x["files"] if v["path"]=="scripts/operations/local_analysis_cleanup/cli.py"); assert hashlib.sha256(b).hexdigest()==e["sha256"]; sys.argv=[p]+a; exec(compile(b,p,"exec"),{"__name__":"__main__","__file__":p,"__runtime_manifest_bytes__":mb})' "$TOOL_SNAPSHOT/scripts/operations/local_analysis_cleanup/cli.py" "$LOCAL_ANALYSIS_MANIFEST_FD" "$TOOL_MANIFEST_SHA256" "$@"; }
safe_rel() { [[ "$1" =~ ^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$ && ! "$1" =~ (^|/)\.{1,2}($|/) ]]; }
strict_json() { /usr/bin/timeout 30 /usr/bin/python3 -I -S -B -c 'import json,sys; b=open(sys.argv[1],"rb").read(); bad=lambda x:(_ for _ in ()).throw(ValueError(x)); hook=lambda p:dict(p) if len(p)==len({k for k,_ in p}) else bad("duplicate key"); x=json.loads(b.decode("utf-8"),object_pairs_hook=hook,parse_constant=bad); c=(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8"); assert b==c' "$1"; }
materialize_public_tool() { local rows="$TOOL_ROWS"; while IFS=$'\t' read -r rel mode blob sha; do safe_rel "$rel"; test "$(trusted_git --literal-pathspecs ls-tree -r --format='%(objectmode) %(objecttype) %(objectname)' "$SUBJECT_TREE" -- "$rel")" = "$mode blob $blob"; test "$(trusted_git --literal-pathspecs ls-tree -r --format='%(objectmode) %(objecttype) %(objectname)' "$PINNED_PUBLIC_TOOL_COMMIT" -- "$rel")" = "$mode blob $blob"; file="$TOOL_SNAPSHOT/$rel"; mkdir -p -- "$(dirname -- "$file")"; test ! -e "$file"; (set -C; trusted_git cat-file blob "$blob" > "$file"); if [[ "$mode" == 100755 ]]; then chmod 700 "$file"; else chmod 600 "$file"; fi; done < "$rows"; cut -f1 "$rows" | LC_ALL=C sort > "$rows.expected"; find "$TOOL_SNAPSHOT" \( -type f -o -type l \) -printf '%P\n' | LC_ALL=C sort > "$rows.actual"; cmp "$rows.expected" "$rows.actual"; while IFS=$'\t' read -r rel mode blob sha; do file="$TOOL_SNAPSHOT/$rel"; test -f "$file" && test ! -L "$file" && test "$(git hash-object "$file")" = "$blob" && test "$(sha256sum "$file" | awk '{print $1}')" = "$sha"; done < "$rows"; }
SUBJECT_SNAPSHOT="$RUN_TMP/subject"; FINAL_SNAPSHOT="$RUN_TMP/final"
SUBJECT_RESULTS="$RUN_TMP/subject-results.json"; FINAL_RESULTS="$RUN_TMP/final-results.json"
EXPECTED_PUBLIC_SUBJECT_MANIFEST="$RUN_TMP/expected-subject.nul"
EXPECTED_PUBLIC_FINAL_MANIFEST="$RUN_TMP/expected-final.nul"; ACTUAL_PUBLIC_MANIFEST="$RUN_TMP/actual.nul"
REPO_ROOT="$(git rev-parse --show-toplevel)"; SOURCE_GIT_DIR="$(git rev-parse --absolute-git-dir)"; BASE_HEAD="$(git rev-parse HEAD)"
GIT_METADATA_DIR="$TRUSTED_GIT_DIR"; trusted_git cat-file -e "$BASE_HEAD^{commit}"; trusted_git cat-file -e "$PINNED_PUBLIC_TOOL_COMMIT^{commit}"
SUBJECT_TREE="$(git write-tree)"; trusted_git cat-file -e "$SUBJECT_TREE^{tree}"; ATTR_INDEX="$RUN_TMP/attrs.index"; ACTIVE_INDEX="$ATTR_INDEX"; trusted_index_git read-tree "$SUBJECT_TREE"; ATTR_PATHS="$RUN_TMP/archive-paths.nul"; trusted_git ls-tree -r -t -z --full-tree --format='%(path)' "$SUBJECT_TREE" > "$ATTR_PATHS"; printf '%s\0' docs docs/reports docs/reports/2026-07-10-local-analysis-cleanup-verification.json >> "$ATTR_PATHS"; ATTR_RESULTS="$RUN_TMP/archive-attrs.nul"; trusted_index_git check-attr --cached --stdin -z export-subst export-ignore < "$ATTR_PATHS" > "$ATTR_RESULTS"; while IFS= read -r -d '' _attr_path && IFS= read -r -d '' _attr_name && IFS= read -r -d '' attr_value; do test "$attr_value" = unspecified; done < "$ATTR_RESULTS"
TOOL_MANIFEST_REL="scripts/operations/local_analysis_cleanup/runtime-closure.json"; test "$(trusted_git --literal-pathspecs ls-tree -r --format='%(objectmode) %(objecttype)' "$SUBJECT_TREE" -- "$TOOL_MANIFEST_REL")" = "100644 blob"; test "$(trusted_git --literal-pathspecs ls-tree -r --format='%(objectmode) %(objecttype)' "$PINNED_PUBLIC_TOOL_COMMIT" -- "$TOOL_MANIFEST_REL")" = "100644 blob"; TOOL_MANIFEST_OID="$(trusted_git rev-parse "$SUBJECT_TREE:$TOOL_MANIFEST_REL")"; PINNED_TOOL_MANIFEST_OID="$(trusted_git rev-parse "$PINNED_PUBLIC_TOOL_COMMIT:$TOOL_MANIFEST_REL")"; test "$TOOL_MANIFEST_OID" = "$PINNED_TOOL_MANIFEST_OID"; TOOL_MANIFEST="/proc/self/fd/$LOCAL_ANALYSIS_MANIFEST_FD"; TOOL_ROWS="$RUN_TMP/tool-rows.tsv"; test ! -e "$TOOL_ROWS"; TOOL_MANIFEST_SHA256="$(/usr/bin/python3 -I -S -B -c 'import hashlib,json,os,re,stat,sys; mfd,oid,driver,expected,rows=sys.argv[1:]; fd=int(mfd); st=os.fstat(fd); assert stat.S_ISREG(st.st_mode); b=os.pread(fd,st.st_size+1,0); actual=hashlib.sha256(b).hexdigest(); assert len(b)==st.st_size and hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==oid and actual==expected; bad=lambda z:(_ for _ in ()).throw(ValueError(z)); hook=lambda q:dict(q) if len(q)==len({k for k,_ in q}) else bad("duplicate"); x=json.loads(b.decode("utf-8"),object_pairs_hook=hook,parse_constant=bad); assert b==(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode() and sorted(x)==["files","schema_id"] and x["schema_id"]=="local-analysis-cleanup/public-runtime-closure/v1"; f=x["files"]; assert isinstance(f,list) and f and f==sorted(f,key=lambda v:v["path"]) and len(f)==len({v["path"] for v in f}) and all(sorted(v)==["blob_oid","mode","path","sha256"] and v["mode"] in ("100644","100755") and re.fullmatch(r"[0-9a-f]{40}",v["blob_oid"]) and re.fullmatch(r"[0-9a-f]{64}",v["sha256"]) and re.fullmatch(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*",v["path"]) and all(s not in (".","..") for s in v["path"].split("/")) for v in f); required={"scripts/operations/local_analysis_cleanup/cli.py","scripts/operations/launch_issue_3454_verification.py","scripts/operations/prune_local_claude_permissions.py","scripts/operations/verify_issue_3454_package.sh","schemas/local-analysis-cleanup/public-projection-v1.schema.json","schemas/local-analysis-cleanup/permission-edit-authority-v1.schema.json","schemas/local-analysis-cleanup/public-verification-result-v1.schema.json","schemas/local-analysis-cleanup/public-validation-attestation-v1.schema.json"}; assert required<={v["path"] for v in f}; d=next(v for v in f if v["path"]=="scripts/operations/verify_issue_3454_package.sh"); assert d["mode"]=="100755" and d["sha256"]==driver; out=os.open(rows,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600); data="".join("\t".join((v["path"],v["mode"],v["blob_oid"],v["sha256"]))+"\n" for v in f).encode(); q=os.fdopen(out,"wb"); assert q.write(data)==len(data); q.close(); print(actual)' "$LOCAL_ANALYSIS_MANIFEST_FD" "$TOOL_MANIFEST_OID" "$LOCAL_ANALYSIS_DRIVER_SHA256" "$LOCAL_ANALYSIS_MANIFEST_SHA256" "$TOOL_ROWS")"
test "$(sha256sum -- "$TOOL_MANIFEST" | awk '{print $1}')" = "$TOOL_MANIFEST_SHA256"
materialize_public_tool; run_snapshot_cli 180 reconcile-durable-candidates --source-git-dir "$SOURCE_GIT_DIR" --candidate-ref-namespace refs/cleanup-candidates/ --receipt-ref-namespace refs/cleanup-candidate-receipts/ --requested-nonce "$RUN_NONCE" --require-zero-or-exact-requested-pair --output-root "$RUN_TMP" --results-relative recovery-results.json; run_snapshot_cli 180 validate-results --kind recovery --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --check-set issue-3454-v1 --input-root "$RUN_TMP" --results-relative recovery-results.json
mkdir -m 700 "$SUBJECT_SNAPSHOT"
test ! -e "$TRUSTED_GIT_DIR/info/attributes"; trusted_git archive --format=tar "$SUBJECT_TREE" | /usr/bin/timeout 300 /usr/bin/tar -xf - -C "$SUBJECT_SNAPSHOT"
(
  cd "$SUBJECT_SNAPSHOT"
  run_snapshot_cli 1200 verify-subject \
    --source-root . --git-metadata-dir "$GIT_METADATA_DIR" --subject-tree "$SUBJECT_TREE" --rehash-tree-objects --output-root "$RUN_TMP" --run-date 2026-07-10 --uv-bin "$UV_BIN" --uv-bin-sha256 "$UV_BIN_SHA256" --uv-version "$UV_VERSION" --test-env-root "$TEST_ENV_ROOT" --uv-cache-root "$UV_CACHE_ROOT" \
    --fuse-test-root-fd "$LOCAL_ANALYSIS_FUSE_TEST_ROOT_FD" \
    --settings-root-fd "$LOCAL_ANALYSIS_SETTINGS_ROOT_FD" \
    --legal-client-map-readonly "$LEGAL_CLIENT_MAP" \
    --subject-manifest-relative expected-subject.nul --final-manifest-relative expected-final.nul \
    --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --results-relative subject-results.json
  test -s "$SUBJECT_RESULTS"
  run_snapshot_cli 180 validate-results \
    --kind subject --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --tree "$SUBJECT_TREE" --check-set issue-3454-v1 --input-root "$RUN_TMP" --results-relative subject-results.json
)
test "$(git write-tree)" = "$SUBJECT_TREE"
(
  cd "$SUBJECT_SNAPSHOT"
  run_snapshot_cli 180 write-validation-attestation \
    --source-root . --git-metadata-dir "$GIT_METADATA_DIR" --output-root "$RUN_TMP" \
    --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --subject-tree "$SUBJECT_TREE" \
    --runtime-input-root "$RUN_TMP" --subject-manifest-relative expected-subject.nul --subject-results-relative subject-results.json \
    --output-relative validation-attestation.json
)
ATTEST_REL="docs/reports/2026-07-10-local-analysis-cleanup-verification.json"; ATTEST_SOURCE="$RUN_TMP/validation-attestation.json"; test -f "$ATTEST_SOURCE" && test ! -L "$ATTEST_SOURCE"; ACTIVE_INDEX="$RUN_TMP/final.index"; trusted_index_git read-tree "$SUBJECT_TREE"; ATTEST_BLOB="$(/usr/bin/python3 -I -S -B -c 'import hashlib,os,re,stat,subprocess,sys; p,g,h=sys.argv[1:]; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW); st=os.fstat(fd); assert stat.S_ISREG(st.st_mode); b=os.fdopen(fd,"rb").read(st.st_size+1); assert len(b)==st.st_size; env={"PATH":"/usr/bin:/bin","HOME":h,"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null","GIT_NO_REPLACE_OBJECTS":"1","LC_ALL":"C"}; o=subprocess.run(["/usr/bin/git","--git-dir="+g,"hash-object","-w","--no-filters","--stdin"],input=b,stdout=subprocess.PIPE,check=True,env=env).stdout.strip(); assert re.fullmatch(b"[0-9a-f]{40}",o) and hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest().encode()==o; print(o.decode())' "$ATTEST_SOURCE" "$TRUSTED_GIT_DIR" "$SANITIZED_HOME")"; trusted_index_git update-index --add --cacheinfo 100644 "$ATTEST_BLOB" "$ATTEST_REL"; trusted_git cat-file -e "$ATTEST_BLOB^{blob}"
test -s "$EXPECTED_PUBLIC_SUBJECT_MANIFEST"; FINAL_TREE="$(trusted_index_git write-tree)"; trusted_git cat-file -e "$FINAL_TREE^{tree}"; FINAL_ATTR_PATHS="$RUN_TMP/final-archive-paths.nul"; trusted_git ls-tree -r -t -z --full-tree --format='%(path)' "$FINAL_TREE" > "$FINAL_ATTR_PATHS"; FINAL_ATTR_RESULTS="$RUN_TMP/final-archive-attrs.nul"; trusted_index_git check-attr --cached --stdin -z export-subst export-ignore < "$FINAL_ATTR_PATHS" > "$FINAL_ATTR_RESULTS"; while IFS= read -r -d '' _attr_path && IFS= read -r -d '' _attr_name && IFS= read -r -d '' attr_value; do test "$attr_value" = unspecified; done < "$FINAL_ATTR_RESULTS"
trusted_git diff-tree --no-commit-id -r --name-only -z --no-renames --no-ext-diff --no-textconv "$BASE_HEAD^{tree}" "$FINAL_TREE" | LC_ALL=C sort -z > "$ACTUAL_PUBLIC_MANIFEST"
cmp "$EXPECTED_PUBLIC_FINAL_MANIFEST" "$ACTUAL_PUBLIC_MANIFEST"
mkdir -m 700 "$FINAL_SNAPSHOT"
test ! -e "$TRUSTED_GIT_DIR/info/attributes"; trusted_git archive --format=tar "$FINAL_TREE" | /usr/bin/timeout 300 /usr/bin/tar -xf - -C "$FINAL_SNAPSHOT"
(
  cd "$FINAL_SNAPSHOT"
  run_snapshot_cli 900 verify-final-package \
    --source-root . --git-metadata-dir "$GIT_METADATA_DIR" --final-tree "$FINAL_TREE" --rehash-tree-objects --output-root "$RUN_TMP" \
    --runtime-input-root "$RUN_TMP" --final-manifest-relative expected-final.nul \
    --attestation docs/reports/2026-07-10-local-analysis-cleanup-verification.json \
    --legal-client-map-readonly "$LEGAL_CLIENT_MAP" \
    --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --results-relative final-results.json
  test -s "$FINAL_RESULTS"
  run_snapshot_cli 180 validate-results \
    --kind final --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --tree "$FINAL_TREE" --check-set issue-3454-v1 --input-root "$RUN_TMP" --results-relative final-results.json
)
test "$(git write-tree)" = "$SUBJECT_TREE" && test "$(trusted_index_git write-tree)" = "$FINAL_TREE"
trusted_git diff --check --no-ext-diff --no-textconv --no-renames "$BASE_HEAD^{tree}" "$FINAL_TREE"
test "$(git write-tree)" = "$SUBJECT_TREE" && test "$(trusted_index_git write-tree)" = "$FINAL_TREE"; run_snapshot_cli 600 create-durable-candidate --trusted-git-dir "$TRUSTED_GIT_DIR" --source-git-dir "$SOURCE_GIT_DIR" --base-head "$BASE_HEAD" --final-tree "$FINAL_TREE" --fixed-public-commit-v1 --fixed-receipt-commit-v1 --receipt-parent candidate --require-complete-am-scope --carrier-root-relative candidate-scope --include-raw-commit --candidate-ref "refs/cleanup-candidates/$RUN_NONCE" --receipt-ref "refs/cleanup-candidate-receipts/$RUN_NONCE" --atomic-ref-transaction --expected-absent-or-exact-replay --output-root "$RUN_TMP" --results-relative candidate-results.json; run_snapshot_cli 180 validate-results --kind candidate --run-nonce "$RUN_NONCE" --base-head "$BASE_HEAD" --tree "$FINAL_TREE" --check-set issue-3454-v1 --input-root "$RUN_TMP" --results-relative candidate-results.json
```

The opaque private wrapper will supply `PINNED_PUBLIC_TOOL_COMMIT` only after authenticating its GitHub OID, code-review receipt, and user approval; this is an external trust precondition, while the public bootstrap proves exact local object/blob equivalence. From a trusted parent with loader variables cleared before `/usr/bin/env`, the inline bootstrap will read the canonical manifest and launcher only from that pin, raw-rehash both blobs, and execute retained launcher bytes under `env -i`. The launcher will verify every closure row, copy manifest/driver into sealed memfds, derive the single lock root as fixed `/run/user/<uid>`, open its fixed leaf with `O_NOFOLLOW`, acquire the kernel lock, scan both ref namespaces, generate a nonce only for zero refs or derive it from the sole exact pair, and pass only retained FDs plus that nonce to `/bin/bash --noprofile --norc -p`. The driver will use offset-independent reads, require subject closure equal the pin, raw-rehash trees in batches, and verify inherited settings/probe FDs. Collision-safe mutation uses retained FDs/`*at`; outputs expose only sanitized codes.

All tests, PII checks, Pages builds, attestation validation, and output scans will read exact `git write-tree` snapshots. Every archive ancestor attribute will be checked separately; tracked symlinks must have relative, recursively contained, manifest-present targets, and all snapshot readers will enforce no-follow/verified-containment policy. Sensitive CLI/editor entrypoints will be opened no-follow, hash-checked, retained, and executed from immutable bytes; mapped imports will likewise load once from retained verified bytes under `/usr/bin/python3 -I -S -B`, with bytecode/test caches confined to `$RUN_TMP`. The fully sealed manifest FD is the sole executable-closure byte source; each hash-bound reparse duplicates that same FD, never reopens a path, and every closure row must be identical in the subject tree and `PINNED_PUBLIC_TOOL_COMMIT`. The opaque private authority must prove its consumed subset identical. The generated attestation will enter a temporary index by `hash-object --no-filters` plus exact `update-index`, never worktree `git add`. `LEGAL_CLIENT_MAP` and the pinned UV executable are explicit retained-FD inputs with bounded identity/hash/version checks before and after use. The legal diff scan will use exact staged scanner blobs. Tests cover staged/working divergence, deletion/type drift, output tamper, and concurrent rewrites.

The canonical kernel lock auto-releases on death. Under it, the launcher will validate zero refs before generating a nonce, or one suffix-matched exact pair before deriving its nonce; caller-supplied resume nonces are forbidden, and the driver repeats reconciliation. Pinned tooling builds exact B and atomically transactions expected-absent-or-exact-replay candidate/receipt refs. The receipt tree contains only mode-100644 `candidate-scope/{result.json,manifest.json,commit.raw,files/<path>}`; canonical result excludes receipt identity, its sole parent is B, and fixed author/committer `Workspace Hub Automation <workspace-hub@users.noreply.github.com> 1783684800 +0000` plus exact message `chore(cleanup): retain candidate receipt\n` permits replay. Missing/multiple/mismatched refs block. Only remote-OID-verified C removes refs by old-OID CAS; failures preserve them. Only R:PASS permits unchanged B push.

## Acceptance Criteria

- [ ] The byte-identical shared contract/state blocks, all four public schemas, cross-repo pins, and semantically compatible public/private ownership will agree; private extensions/identities will remain private rather than matching public text.
- [ ] Public code will never read the private ledger; only private code will export the sanitized runtime bundle and invoke live mutation.
- [ ] A fresh folder-only `baseline_v1` and root anomalies will replace any claim of reconstructing the 124→128 history.
- [ ] Plan approval, disposition, permission authority, and destructive-action authority will remain separate.
- [ ] D1 missing/REJECT will defer without satisfying permission removal or closure; explicit ACCEPT alone can enable guarded probes and a verified two-rule-absent postcondition.
- [ ] Every live mutation will have a validated, pushed pre-action WAL and a pushed post-action result; push failure will block mutation.
- [ ] Private A→B-local→Q→R:PASS→public B-push→private C-commit/push/remote-verify→local-ref cleanup will verify without circular hashes or force push.
- [ ] Exact B bytes and promotion evidence will pass T3 code/artifact review before any B push, comment, or other public delivery.
- [ ] Public reconciliation code will remain pure; bounded local candidate/handoff refs will stay public-verifier state, while the opaque private authority alone persists ledger/cross-repo receipts and performs remote/comment actions.
- [ ] Public projection/HTML/Markdown/comments/generated Pages will contain only allowed fields/buckets/digests and will pass non-vacuous scans.
- [ ] Public validation will bind a nonzero subject-file map without self-reference; private receipt C will bind the pushed public package identity.
- [ ] Folder actions will remain manual, explicit, no-overwrite transactions under the opaque private authority and the cleanup skill.
- [ ] #2572 will receive sanitized milestones and remain open; #3453/#3456/#3458/#3461/#3467 will remain separate, and #3467 will land before any sensitive review/promotion lane.
- [ ] T3 code/artifact review, completeness, cleanup audit, and temporary-worktree removal will pass before closure.

## Adversarial Review Summary

| Provider | Verdict | Result |
|---|---|---|
| Claude CLI | UNAVAILABLE | rc=137 timeout/no stderr |
| Codex CLI | UNAVAILABLE | rc=124 stdin regression on 0.144.1 |
| Gemini CLI | UNAVAILABLE | no non-interactive auth |
| Codex inline r1 | MAJOR | 10 blockers; ownership/schema/CAS/WAL/publication/scan defects revised in v2 |
| Codex inline r2 | MAJOR | D1/state/digest/same-mount and immutable-snapshot attestation defects revised in v3 |
| Codex inline r3 | MAJOR | Rollback/runtime/root/base/closure defects revised in v4 |
| Codex inline r4 | MAJOR | Digest framing and FD-relative exact-mount defects revised in v5 |
| Codex inline r7 | MAJOR | Privacy, sealed-driver, namespace-recovery, receipt, and paired-review defects revised in v8 |
| Codex inline r8 | MAJOR | Bootstrap, canonical-lock, nonce-recovery, sealed-manifest, parity, and ownership defects revised in v9 |
| Codex inline r9 | MAJOR | FD leakage, mutable legal-map input, lifecycle order, and missing independent D owner remain blocking |

**Overall result:** BLOCKED — exact local R9 review remains MAJOR. Generalized trust-root/FD findings are promoted to #3467; this plan will not advance or execute until that dependency lands and a revised exact SHA receives fresh review. Provider unavailability is not consensus.

## Risks and Open Questions

- **Residual settings race:** advisory quiescence cannot stop a non-cooperating writer. Failure to obtain green same-mount probes/quiescence will defer to #3456.
- **Decision D1 — mount exposure:** fuseblk chmod is ineffective and #3456 owns durable hardening. Missing/REJECT prevents guarded apply; explicit ACCEPT alone can authorize the guarded route after same-mount probes pass.
- **Public push/history gate:** docs-only new-branch publication remains blocked by [#3198](https://github.com/vamseeachanta/workspace-hub/issues/3198); before any push, the final sanitized tree will be rebuilt as one parent-on-current-main commit so superseded local blobs containing private identifiers never become remotely reachable. No hook bypass is authorized.
- **Provider outage:** fresh T3 review cannot complete until provider capacity/auth works; no label will advance on unavailable artifacts alone.
- **Independent bootstrap:** #3467 must land a D0-reviewed retained-input/FD-allowlist protocol before this plan can replace its provisional executable fence or enter `status:plan-review`.
- **Root drift:** a new execution claim, fresh baseline, per-action remote checkpoint, and preflight will fence concurrent work.
- **Open:** no D1 selection is needed for the safe REJECT/defer route; ACCEPT requires a separate explicit bound record.

---

## Complexity: T3

**T3** — public/private/machine-local state, a versioned security boundary, guarded configuration mutation, manually executed irreversible actions, cross-repo receipts, and provider/code review require T3 treatment.
