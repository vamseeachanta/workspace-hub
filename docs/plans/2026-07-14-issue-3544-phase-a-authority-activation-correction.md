# Plan for #3544: Correct and Operationalize Phase A Authority Activation

> **Status:** draft-needs-decision
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3544
> **Client:** N/A
> **Lane:** lane:codex
> **Execution:** planning `parallel-readonly`; implementation `single-lane`; external activation isolated owner transaction
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3544-custom-ansys-r1.md`; `scripts/review/results/2026-07-14-plan-3544-prepare-fer-extraction-r1.md`

---

## Blocking Owner Decisions

This plan is not approval-ready until the owner resolves both decisions. Unknowns
remain fail-closed; review may proceed, but no implementation or external
activation may start.

1. **Merge-review posture.** Live API readback shows `vamseeachanta` is the only
   collaborator. GitHub does not allow a PR author to approve their own PR, so
   `require_code_owner_review=true`, one required approval, and no bypass would
   permanently lock `main`.
   - **A — second trusted collaborator/code owner:** owner supplies an exact
     login/user ID, grants and verifies write access in a separately approved
     mutation, and updates the base-branch `.github/CODEOWNERS` authority rows to
     name both `@vamseeachanta` and that collaborator before the ruleset requires
     one approval plus code-owner review. For an owner-authored PR the second
     actor must approve; for a second-actor-authored PR the owner must approve.
     The author never supplies the counted approval.
   - **B — solo-safe interim:** retain no bypass but set
     `required_approving_review_count=0` and
     `require_code_owner_review=false`. The PR rule still rejects direct pushes;
     the exact authority status check remains mandatory. A later reviewed change
     may strengthen review after a second trusted reviewer exists.
2. **Private Linux owner host.** `ace-win-1` is Windows, has no installed WSL
   distribution, and no usable Linux/SSH owner endpoint is configured. The owner
   must identify either (a) an existing private Linux host and native-Linux 0700
   storage root or (b) a separately planned/approved WSL installation and
   hardening transaction. `/mnt/d`, `D:\\ws`, network shares, and Windows mode
   emulation do not satisfy this contract.

## Resource Intelligence Summary

### Existing repo code

- `scripts/legal/manage_rule_authority.py` at merged Phase A exposes `seal`, but
  it requires an existing authenticated anchor and ledger and only emits a new
  manifest/ledger. `materialize-envelope` only decodes an existing envelope.
  There is no supported genesis or envelope-packaging operator interface.
- `scripts/legal/rule_authority/{authority,envelope,private_io}.py` contains the
  required primitives (`build_manifest`, `make_anchor`, `new_ledger`, canonical
  envelope decoding, no-follow 0600 writes), but composing them ad hoc would
  bypass a reviewed operator boundary.
- `scripts/legal/rule_authority/codec.py`,
  `schemas/legal-rule-policy.schema.json`, and
  `config/legal-rule-authority-policy.json` accept/carry
  `max_entries=100000`; the approved normative contract still caps it at 10,000.
- `.github/workflows/legal-rule-authority-reusable.yml` uses pinned
  `astral-sh/setup-uv` without inputs. On GitHub-hosted runners its documented
  `enable-cache` default is `auto`, which enables Actions cache despite the
  contract claiming caches are disabled. Authority code is standard-library
  only, so the action is unnecessary.
- `scripts/legal/rule_authority/protection.py` normalizes only a subset of the
  environment/ruleset response. It omits `can_admins_bypass`, wait/self-review,
  custom branch policies, complete required PR/status parameters, effective
  rules, and preservation of the pre-existing `protect-main` ruleset.

### Prior authority and issue decisions

- `docs/plans/2026-07-13-issue-3522-private-rule-authority-migration.md` and
  `docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md` define
  the two-phase boundary, private storage, dual-slot future migration, and
  explicit external-state gate. The merged contract must be revised before any
  activation because its 10,000 cap and GitHub payload claims are not executable.
- PR #3535 merged Phase A at
  `966401108fa45eae95927918bae34044d8ba20fa`; its reusable workflow is pinned to
  tool commit `51c547409ba5c62c8f4ef99de6496d290fa8a1fa`.
- Issue #3544 explicitly forbids Phase B, PENDING/CAS, history work, provider or
  cache deletion, and all external activation until a corrected plan receives
  fresh owner approval.

### Live GitHub preflight

Read-only API inspection on 2026-07-14 found:

- repository `vamseeachanta/workspace-hub`, ID `1066339206`, is public/personal;
  owner ID `23155845`; `vamseeachanta` is its only direct collaborator;
- current `main` was `11af29c0c9a45a004ca702f3ab3c075b8095dc10`
  with tree `aea9abb16585e1263bd5fd8382e4a32c2788885d`;
- environment `legal-rule-authority`, ID `18130831018`, exists with no reviewers,
  `deployment_branch_policy=null`, `can_admins_bypass=true`, and zero environment
  secrets;
- only authority-adjacent ruleset is `protect-main`, ID `17369764`, active with
  empty bypass actors and exactly `deletion` plus `non_fast_forward`; it must be
  preserved byte-for-byte after normalization;
- workflow ID is `313008799`; the observed same-repository GitHub Actions check
  context is exactly `strict-scan / authority`, integration ID `15368`; the fork
  job is the separate terminal `strict-scan` failure;
- no `legal-rule-authority-main` ruleset and no `LEGAL_SCAN_AUTH_CURRENT` secret
  exist.

### GitHub primary documentation

- [Environment REST endpoint](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10)
  requires `protected_branches` and `custom_branch_policies` to be opposites; the
  previous both-false object is invalid. `null` means all refs.
- [Deployment branch policies](https://docs.github.com/en/rest/deployments/branch-policies?apiVersion=2026-03-10)
  accept `name` plus `type`; wildcard `*` does not cross `/`.
- [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
  identifies PR refs as `refs/pull/<number>/merge` and documents the
  `refs/pull/*/merge` custom-policy form. It also documents the UI-only
  administrator-bypass posture.
- [Repository rulesets REST schema](https://docs.github.com/en/rest/repos/rules?apiVersion=2022-11-28)
  defines the complete pull-request/status-check payloads. The `update` rule
  means only bypass actors may update a ref; it is not a direct-update boolean.
  Required-workflow rules are not used because this is a user-owned repository;
  the supported required status check is the enforcement primitive.
- [`setup-uv` inputs](https://github.com/astral-sh/setup-uv) document
  `enable-cache=auto` as enabled on GitHub-hosted runners.

### Drive-file search and other knowledge sources

The required drive-index query `legal rule authority GitHub environment ruleset
activation` returned two unrelated environmental-engineering documents. Five
indexes were unreachable and three reported stale metadata. No drive result is
relevant to this GitHub security-control transaction. No engineering standard or
LLM wiki page applies.

### Gaps identified

- No supported, Linux-only, owner-gated genesis/current-envelope CLI.
- No bounded `key_id` codec or atomic complete genesis transaction.
- No corrected public activation contract/payload/readback/rollback artifacts.
- No exact proof-PR state machine or fail-closed rollback executor/guide.
- No tested reconciliation between the 10,000 normative cap and current tree.
- No owner decision for reviewer feasibility or private Linux execution host.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-14T19:11Z):

```text
#3544 OPEN — security(legal): correct and operationalize Phase A authority activation
labels: status:needs-plan, gate:completeness, lane:codex
```

**Reproduction proofs** (2026-07-14T19:11Z):

```text
$ git rev-parse HEAD
11af29c0c9a45a004ca702f3ab3c075b8095dc10
$ git ls-tree -r --name-only HEAD | count
tracked_blob_entries=22936
$ inspect normative policy bound and merged policy
contract: "max_entries": 1..10000
config:   "max_entries":100000
$ GET environment + secrets + rulesets
legal-rule-authority: can_admins_bypass=true; protection_rules=[];
deployment_branch_policy=null; environment secrets=[]
rulesets: protect-main only
```

The issue describes a pre-activation contract failure rather than a deployed
runtime regression. The observed 22,936-entry tree cannot satisfy 10,000 and the
live GitHub state matches all reported blockers.

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3544-phase-a-authority-activation-correction.md` |
| Revised normative activation contract | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-activation-contract.md` |
| Canonical non-secret GitHub payload/readback preview | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-github-preview.json` |
| Genesis/operator guide | `.claude/docs/legal-rule-authority.md` |
| Owner CLI | `scripts/legal/manage_rule_authority.py` |
| Authority/private transaction modules | `scripts/legal/rule_authority/{authority,codec,envelope,private_io,protection}.py` |
| Workflow | `.github/workflows/legal-rule-authority-reusable.yml` |
| Tests | `scripts/legal/tests/test_rule_authority_{cli,codec,private_io,protection,workflow,audit}.py` |
| Plan reviews | `scripts/review/results/2026-07-14-plan-3544-<provider>-rN.md` |

## Deliverable

A freshly owner-approved, Linux-private, TDD-backed Phase A activation contract
and toolchain that can create and locally verify a synthetic CURRENT genesis,
prove same-repository PR execution without cache or lockout, activate a valid
required-check ruleset last, and roll back only transaction-created state while
preserving `protect-main` and all legacy enforcement.

## Corrected Normative Design

### Exact supersession and replacement-contract gate

The replacement contract must enumerate, rather than implicitly drift from, the
four #3522 clauses it supersedes:

1. resource bound `max_entries <= 10000` becomes `<= 100000`;
2. the frozen operator interface gains the owner-only `genesis-current` command;
3. environment admission changes from protected/main-only to the exact custom
   policies `main` and `refs/pull/*/merge` required by PR `GITHUB_REF`;
4. the old `legal-rule-authority / strict-scan` and workflow-prefixed preview
   context are replaced by observed check context `strict-scan / authority`,
   GitHub Actions integration ID `15368`.

It also corrects the cache posture by removing `setup-uv`, rejects the invalid
`update` rule, and replaces the unsupported user-repository `workflows` rule with
the required status check. Every other #3522 boundary remains in force.

Implementation commit A contains the replacement contract and all trusted tool
bytes. After A exists, its full Git OID, the replacement-contract Git blob OID,
and canonical contract SHA-256 are recorded in the private activation preview.
Commit B changes only the mutable caller pin and its public non-secret pin
evidence to reference A. No activation approval is valid unless it binds exact A
and B OIDs and readback proves main contains B, the caller at B pins A, the
reusable/tool checkout is A, the current anchor binds A, and the three contract
identities recompute exactly. A stale #3522 plan/approval SHA cannot satisfy this
gate.

Public policy and schema remain exactly 100,000. Activation preflight records the
exact target tree entry count and requires `1 <= count <= 100000`; current
evidence is 22,936. The cap applies fail-closed—no truncation, sampling,
auto-growth, or clean verdict after rc3. Phase B history/API scaling remains
outside this issue.

### Secure genesis interface

Add this frozen owner-only command:

```text
genesis-current --tool-repo GIT_DIR --tool-sha FULL_OID
                --out-parent PRIVATE_DIR --transaction-id UUID
```

It is unavailable when `GITHUB_ACTIONS` is set and requires
`LEGAL_RULE_OWNER_GENESIS=1`. It supports Linux only. It reads the public
registry and policy as Git blobs from exact tool commit A—not from arbitrary path
arguments—and verifies their blob OIDs and canonical SHA-256 values against the
replacement contract. These public inputs are intentionally not subject to the
private 0600 rule; all generated private bytes are.

The command obtains a 32-byte HMAC key and one unique 32-byte synthetic exact
pattern per public rule directly from the Linux kernel CSPRNG with no fallback.
The key file is exactly RFC 4648 canonical base64 of those 32 bytes followed by
one LF, with no other whitespace; the map is canonical `legal-json-v1`, binds the
public generation/revision/rule IDs, and contains only those generated synthetic
patterns. `key_id` is generated as `phase-a-` plus a canonical lowercase UUIDv4.
The generation-ledger JSON schema and codec both enforce this exact form and a
64-byte maximum. No key, map, ID, digest, or path is accepted on argv/stdin or
written to stdout. The command never reads `.legal-deny-list.yaml` or
creates/migrates real rule bytes.

Every path component is opened no-follow through retained dirfds. Before entropy
or private writes, the command requires Linux, resolves the output device and
longest mount through `/proc/self/mountinfo`, and binds mount ID, major:minor,
root, mountpoint, filesystem type, source, and options before/after the
transaction. Only owner-approved native local `ext4`, `xfs`, or `btrfs` is
accepted; `drvfs`, `9p`, FUSE, overlay, bind, NFS/CIFS, FAT/NTFS, `/mnt/<drive>`,
or changed/ambiguous mounts reject rc4. The private preview separately attests
the selected mount's encrypted-at-rest posture, which the filesystem type alone
cannot prove. The final parent must be current-UID mode 0700. Outputs are created
no-overwrite 0600 under an incomplete 0700 child,
fsynced, verified, and atomically renamed no-replace to
`PRIVATE_DIR/UUID`. Output is exactly `map.json`, `manifest.json`, `anchor.json`,
`ledger.json`, `key.b64`, and canonical `envelope.json` (<=32 KiB). The current
anchor binds the reviewed implementation tool SHA, `slot=current`, and
`expected_head_oid=null`. Failure leaves no final transaction; cleanup is
explicit. Output is fixed verdict metadata only—never values, paths, hashes,
base64, parser fragments, or subprocess payloads.

### Cache-free immutable workflow

Remove `setup-uv` entirely. The checked-out tool is standard-library-only and is
invoked as `python3 -B -E -s scripts/legal/manage_rule_authority.py ...` with
`PYTHONNOUSERSITE=1`. No cache/artifact action or dependency resolution is
allowed. Existing SHA-pinned checkout, `contents:read`, inert full-OID fetch,
disabled credentials/hooks, fork pre-secret constant failure, and
`job.workflow_sha` binding remain. Commit A contains the replacement contract,
reusable workflow, tool, schemas, and tests. Commit B changes only
`.github/workflows/legal-rule-authority-gate.yml` and its public pin evidence so
the caller at B invokes reusable workflow/tool A by full OID. The immutable
anchor binds A, never B; activation readback must prove this A/B topology.

### Exact environment payload

The reviewed PUT body is:

```json
{"wait_timer":0,"prevent_self_review":false,"reviewers":[{"type":"User","id":23155845}],"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}
```

Custom policies are created only if the baseline list is empty, using exactly:

```json
{"name":"main","type":"branch"}
{"name":"refs/pull/*/merge","type":"branch"}
```

Any extra, duplicate, or changed policy aborts. `prevent_self_review=false` is
necessary because the sole owner triggers and approves environment deployments.
The REST API cannot set administrator bypass; the owner must manually deselect
**Allow administrators to bypass configured protection rules** in the GitHub UI,
then GET readback must show `can_admins_bypass=false`. No secret is uploaded
before reviewer, branch-policy, and admin-bypass readback is exact. Forks never
call the environment-owning reusable job.

### Exact ruleset variants

Both variants use repository ID `1066339206`, name
`legal-rule-authority-main`, target `branch`, conditions exactly
`refs/heads/main`, `bypass_actors=[]`, and initially `enforcement=disabled`.
Neither contains `update` or `workflows`.

Common required status rule:

```json
{"type":"required_status_checks","parameters":{"do_not_enforce_on_create":false,"required_status_checks":[{"context":"strict-scan / authority","integration_id":15368}],"strict_required_status_checks_policy":false}}
```

Variant B's solo-safe PR rule is fully specified:

```json
{"type":"pull_request","parameters":{"allowed_merge_methods":["merge","squash","rebase"],"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false,"required_approving_review_count":0,"required_review_thread_resolution":false}}
```

Variant A uses the same object with `require_code_owner_review=true` and
`required_approving_review_count=1`, but is invalid until an exact second trusted
collaborator has write access, is named with the owner on every relevant
authority row in the base branch `.github/CODEOWNERS`, and proves they can
approve. For an owner-authored proof PR the second actor approves; for a
second-actor-authored proof PR the owner approves. The author never supplies the
counted approval, and head-only CODEOWNERS changes never satisfy the gate.
Creation uses POST with
the full disabled document. Activation is the final mutation and uses PUT—not
PATCH—with the same full document and only `enforcement` changed to `active`.
Normalized readback must match, effective rules for `main` must contain both the
existing `protect-main` protections and this new ruleset, and a proof PR must be
mergeable under the chosen review posture. The proof PR is never merged.

## Ordered Implementation and External Transaction

### Implementation after a future plan approval

1. Record the two owner decisions and exact revised plan SHA in the approval
   marker. Write each RED test before code.
2. Write RED tests, then create commit A containing the replacement contract,
   genesis transaction, corrected codecs/readbacks, reusable cache-free workflow,
   schemas, tests, and canonical non-secret preview. Record A's full OID, the
   contract blob OID, and canonical contract SHA-256.
3. Create commit B changing only the mutable caller and public pin evidence to
   pin A. The caller at B, reusable/tool at A, and anchor at A are invariant.
4. Run focused/full acceptance and T3 adversarial code/artifact review.
5. Present exact A and B identities. Merge only through a separately reviewed
   PR. This stage performs no external activation.
6. Generate a private owner preview binding the then-live main/tool SHA, tree
   count, CURRENT envelope digest, Linux host identity/private root, chosen
   ruleset variant, exact baseline responses, proof branch/PR names, and rollback.
   Stop for fresh explicit activation approval.

### External activation only after that separate approval

1. **CAS preflight:** reread main head/tree, caller B and its A pin, workflow/tool
   A, contract blob OID/SHA-256, collaborators/base CODEOWNERS, full environment,
   branch policies, environment secret names/timestamps, repository/effective
   rulesets, workflow/check identity, and `protect-main`. Abort on any mismatch,
   pre-existing CURRENT, or same-name ruleset.
2. **Offline proof:** on the approved Linux host, run `genesis-current`,
   materialize to a second private 0700 directory, verify, and audit the exact
   main tree with the reviewed tool. Require rc0 and complete coverage.
3. **Environment:** PUT the exact environment, create the two policies, perform
   the manual admin-bypass UI change, and verify exact GET/list readback.
4. **CURRENT CAS and write:** repeat the full CAS immediately before uploading
   `LEGAL_SCAN_AUTH_CURRENT` by stdin only; require name and
   timestamp metadata readback. GitHub cannot return the value, so local canonical
   envelope retention is mandatory for recovery.
5. **Proof PR:** from the bound main SHA, create a same-repository proof branch
   containing only the fixed public marker `phase-a-activation-proof-v1`; open a
   draft PR, approve the environment deployment, and require the exact
   `strict-scan / authority` check from integration `15368` to return success.
   Then transition the PR from draft to ready-for-review and verify ready state.
   Under Variant A apply the exact author/reviewer matrix and require the counted
   approval; under Variant B require none.
   Fixture/adversarial tests prove the fork path remains constant-fail before
   environment access; no live fork/provider creation is authorized.
6. **Disabled-ruleset CAS:** repeat the full CAS, including proof ready/check/
   review state, immediately before POSTing the chosen full payload with
`enforcement=disabled`,
   capture its new ID, and verify normalized plus raw readback. Any 422/shape drift
   rolls back; never substitute an update/workflows rule.
7. **Activation CAS and activate last:** repeat the full CAS after disabled
   readback and immediately before PUTting the same full document with
`enforcement=active`; verify
   raw/normalized/effective rules, unchanged `protect-main`, exact required check,
   and proof-PR mergeability under the chosen review posture. Do not merge it.
8. **Close proof:** close the unmerged proof PR and delete only its transaction
   branch. Publish only fixed non-sensitive verdict/evidence. #3544 remains open
   until implementation completeness and post-activation review pass.

### Rollback and stop order

At the first failed readback or proof, stop forward progress:

1. If the new ruleset exists, PUT its exact full document with
   `enforcement=disabled` and verify. Delete it only if its ID was created by this
   transaction; confirm absence and unchanged `protect-main`.
2. Delete `LEGAL_SCAN_AUTH_CURRENT` only if the transaction created it; verify
   name absence. Never overwrite or delete a pre-existing secret.
3. Manually re-enable administrator bypass only if this transaction disabled it;
   GET must return the baseline `true`.
4. Delete only the two captured transaction branch-policy IDs, then PUT the exact
   baseline environment (`wait_timer=0`, `prevent_self_review=false`, no
   reviewers, `deployment_branch_policy=null`) and verify the baseline.
5. Close/delete only the captured proof PR/branch. Retain private genesis evidence
   pending owner disposition. Never delete the pre-existing environment.

If disabling the new ruleset fails, stop and escalate before touching the secret
or environment. Rollback commands and resource IDs are generated from the
approved baseline preview, never guessed. No automatic retries or broad cleanup.

### Ambiguous-response reconciliation

After any timeout, connection loss, or unexpected response following a possible
mutation, do not retry. GET/list the exact resource: exact intended state is
recorded as applied, exact baseline is recorded as not applied, and any other
state stops and escalates. For a lost disabled-ruleset response, reconcile by the
unique exact name and complete normalized shape; one exact match supplies the
transaction ID, while zero, multiple, or drifted matches stop. UI mutations are
reconciled by GET. Because a secret value cannot be read back, metadata presence
cannot prove the intended payload: an ambiguous secret PUT is rollback-only,
deleting the transaction-created name after confirming it was absent at baseline.
Rollback mutations use the same reconcile-before-next-step rule. Every repeated
CAS rechecks all A/B/contract, main/tree, collaborators/CODEOWNERS, environment/
policies/admin, secret metadata, ruleset/effective, `protect-main`, and proof
facts applicable at that boundary; drift permits no further forward write.

## Pseudocode

```text
genesis_current(tool_repo, tool_sha_A, out_parent, transaction_id):
    require owner gate, non-Actions Linux, exact tool OID
    qualify stable approved native mount; retained-dirfd validate 0700 parent
    read registry/policy as exact Git blobs at A; verify contract blob identities
    generate key, synthetic map, and bounded key_id internally from kernel CSPRNG
    build manifest, current anchor, authenticated genesis ledger, CI envelope
    require canonical envelope <= 32 KiB and verify bundle before decoding pattern
    write six files into new incomplete 0700 child with O_EXCL and fsync
    materialize/verify in-memory; fsync child+parent; rename no-replace to UUID
    emit fixed rc0 metadata; on failure emit fixed rc2/3/4 and no final directory

build_activation_preview(live, decision, implementation_sha):
    require exact main/tree, sole-or-approved collaborator set, empty secret slot
    require baseline environment and protect-main equal approved snapshot
    select only owner-approved ruleset variant
    emit canonical non-secret environment/policy/ruleset/order/rollback document

verify_activation_readback(preview, live):
    compare full environment reviewer/self-review/wait/branch/admin posture
    compare exact branch policies and environment secret metadata presence
    compare raw+normalized new ruleset and effective main rules
    require protect-main unchanged and exact check app/context
    reject missing/extra/type-coerced fields; return fixed verdict only

activate_owner_transaction(preview):
    perform CAS preflight and offline proof
    environment -> policies -> UI admin bypass -> CURRENT -> proof PR
    create disabled ruleset -> activate ruleset last -> final proof
    on failure execute captured rollback in dependency-safe order
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-activation-contract.md` | superseding exact activation/resource/rollback contract |
| Create | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-github-preview.json` | canonical non-secret API request/readback variants |
| Modify | `docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md` | cross-link explicit 10k-to-100k supersession; preserve Phase B text |
| Modify | `scripts/legal/manage_rule_authority.py` | owner-only `genesis-current` command and exact CLI |
| Modify | `scripts/legal/rule_authority/codec.py` | bounded key ID and canonical activation structures |
| Modify | `schemas/legal-rule-generation-ledger.schema.json` | enforce `phase-a-<lowercase UUIDv4>` key ID and 64-byte bound |
| Modify | `scripts/legal/rule_authority/{authority,envelope,private_io}.py` | atomic genesis/envelope transaction with Linux guarantees |
| Modify | `scripts/legal/rule_authority/protection.py` | exact payload validation and complete readback/effective-rule comparison |
| Modify | `.github/workflows/legal-rule-authority-reusable.yml` | remove setup-uv/cache and use isolated system Python |
| Modify (commit B) | `.github/workflows/legal-rule-authority-gate.yml` | pin the commit-A reusable workflow/tool by full OID |
| Modify if Variant A | `.github/CODEOWNERS` | name owner and exact second actor on every relevant authority row in base branch |
| Modify | `.claude/docs/legal-rule-authority.md` | Linux owner runbook, proof, rollback, and value-withholding rules |
| Modify/Create | `scripts/legal/tests/test_rule_authority_*.py` and fixtures | RED matrix below |
| Update | `docs/plans/README.md` | index this plan and later reflect reviewed state |

No implementation may silently change the public registry/policy authority bytes.
If implementation discovers such a change is required, stop, increment generation
and revision in a revised plan, and obtain another owner decision before sealing.

## TDD Test List

| Test | RED condition and required result |
|---|---|
| `test_genesis_command_is_frozen_and_owner_only` | command absent today; require exact flags, owner gate, no Actions execution |
| `test_genesis_rejects_non_native_or_ambiguous_mounts` | require stable `/proc/self/mountinfo` identity and approved ext4/xfs/btrfs; Windows, `/mnt`, drvfs/9p/FUSE/overlay/bind/network/FAT/NTFS and mount drift reject before entropy/private reads |
| `test_genesis_requires_0700_parent_0600_inputs` | wrong UID/mode, symlink, parent swap, hardlink/non-regular, size drift reject rc4 |
| `test_genesis_creates_private_entropy_without_output` | internally create 32-byte key and unique 32-byte synthetic patterns; no argv/stdin/stdout values, IDs, digests, or paths; key file is exact RFC4648 base64 plus one LF |
| `test_ledger_key_id_schema_and_codec_match` | schema and codec accept only `phase-a-<lowercase UUIDv4>` within 64 bytes and reject every alternate form |
| `test_genesis_binds_public_blobs_to_commit_a` | public registry/policy blob OIDs and canonical hashes match contract at A; private generated files alone require 0600 |
| `test_genesis_is_atomic_no_overwrite` | collisions, disk-full/fsync/rename crash leave no accepted final transaction |
| `test_genesis_outputs_exact_canonical_bundle` | exact six 0600 files, current/null-head anchor, fresh ledger, <=32 KiB envelope |
| `test_genesis_materialize_verify_roundtrip` | independent materialization and verification return rc0 at exact tool SHA |
| `test_genesis_output_allowlist` | all rc2/3/4 paths withhold values, paths, hashes, base64, parser fragments |
| `test_policy_contract_cap_reconciles_real_tree` | normative/schema/codec/config cap exactly 100,000; current tree >10,000 and <=cap |
| `test_tree_over_100000_fails_closed` | 100,001 entries return rc3; no sampling/truncation/clean result |
| `test_workflow_has_no_cache_or_dependency_action` | no setup-uv/actions-cache/artifact; exact `python3 -B -E -s`, no user site |
| `test_two_commit_caller_topology` | A contains contract/reusable/tool/schema/tests; B changes only caller/public evidence; B pins A and anchor binds A |
| `test_environment_put_schema_is_exact` | typed reviewer ID and opposite branch-policy booleans; missing/extra/coerced fields reject |
| `test_pr_and_main_custom_policy_patterns` | exactly `main` and `refs/pull/*/merge`; fork job never references environment |
| `test_environment_readback_binds_admin_bypass` | require false, reviewer, self-review false, wait zero, exact policies/no extras |
| `test_solo_repo_review_decision_fails_closed` | count1/codeowner with sole collaborator rejects preview; variant B or proven second actor required |
| `test_ruleset_payload_uses_supported_complete_schema` | full PR/status params; exact context/app; no `update` or `workflows` |
| `test_ruleset_disabled_then_active_full_put` | POST disabled then PUT full active document; PATCH/partial update rejects |
| `test_effective_rules_preserve_protect_main` | baseline ID/rules/bypass unchanged and effective main includes both rulesets |
| `test_proof_pr_state_machine` | draft check succeeds, PR transitions to verified ready state, Variant A exact non-author approval matrix or Variant B zero approvals, active reevaluation is mergeable but unmerged |
| `test_fork_constant_fail_pre_secret` | fork result fixed and no environment/secret/data scan |
| `test_activation_cas_at_every_boundary` | full A/B/contract/main/CODEOWNERS/environment/secret/ruleset/proof CAS runs preflight, pre-CURRENT, pre-disabled POST, and pre-active PUT; drift produces zero further writes |
| `test_ambiguous_mutation_reconciliation` | lost 200/201/204 and timeout fixtures reconcile intended/baseline/other; ambiguous secret PUT is rollback-only; rollback ambiguity reconciles before continuing |
| `test_rollback_disables_ruleset_first` | injected failures assert exact disable, secret, UI, policies/environment order |
| `test_rollback_touches_only_created_ids` | pre-existing env/protect-main/secret/ruleset are never overwritten/deleted |
| `test_external_adapters_are_fixture_only` | tests perform no live writes and validate official 200/201/204/303/404/422 shapes |

Tests must be committed RED before their matching implementation slice.

## Acceptance Criteria

- [ ] Owner decisions identify exact merge-review variant and private Linux host/root.
- [ ] Fresh approval binds the revised plan SHA and explicitly accepts the
      100,000 cap plus chosen review posture; no stale #3522 approval is reused.
- [ ] Exact genesis command passes Linux permissions, atomicity, roundtrip,
      native-filesystem qualification, hostile-input, size, crash, exact
      base64-plus-LF, internal synthetic-map creation, and value-withholding tests.
- [ ] Contract blob identities, public registry/policy blobs, reusable workflow,
      tool, schema, and anchor bind commit A; commit B changes only the caller and
      public pin evidence and its caller pins A by full OID.
- [ ] Public contract, JSON schema, codec, config, and tests agree on 100,000;
      the then-live exact tree is measured and below it.
- [ ] Workflow contains no setup/dependency/cache/artifact action and executes
      pinned checked-out standard-library code with isolated Python flags.
- [ ] Environment payload and policies match the valid documented API schemas;
      admin bypass is manually disabled and bound by GET readback.
- [ ] Chosen ruleset has complete valid PR/status parameters, exact
      `strict-scan / authority`/15368 identity, no update/workflows rule, and no
      bypass; `protect-main` is unchanged.
- [ ] Same-repository proof PR succeeds as draft, transitions to verified ready
      state, satisfies the selected exact author/reviewer matrix, and remains
      mergeable after active ruleset readback; it is never merged. Fork fixtures remain
      constant-fail before secret access.
- [ ] Full legal authority suite, focused enforcement tests, Ruff, compileall,
      schema validation, workflow checks, legal scan, and diff checks pass.
- [ ] T3 adversarial plan review has no MAJOR before user approval; T3 code and
      artifact review has no MAJOR before implementation merge.
- [ ] A second private preview binds live SHAs/digests/IDs/timestamps/host/path
      and receives explicit owner approval before external activation.
- [ ] Failure injection proves exact rollback and preservation of the existing
      environment, `protect-main`, legacy deny-list, and all legacy enforcement.
- [ ] Full CAS passes at preflight, pre-CURRENT, pre-disabled-POST, and
      pre-active-PUT boundaries; ambiguous forward and rollback responses are
      reconciled without blind retries.
- [ ] No Phase B/PENDING/CAS/history/provider/cache-deletion action occurs; issue
      closure still requires the completeness gate.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| `custom_ansys_runners` | MAJOR | Variant-A ownership matrix, ready transition, A/B topology, genesis encoding/schema, repeated CAS, ambiguity, and retention corrections required |
| `prepare_fer_extraction` | MAJOR | exact supersession/SHA gate, base CODEOWNERS, ready proof, mount qualification, and repeated CAS required |
| Independent re-review | PENDING | revised blocked draft must be re-reviewed after owner decisions |

**Overall result:** BLOCKED-DRAFT — both R1 MAJOR finding sets are incorporated,
but two owner decisions and independent re-review are required before the plan
may advance to `status:plan-review`.

## Risks and Open Questions

- GitHub administrator-bypass configuration is UI-only; automation cannot claim
  an API-only atomic transaction. Manual action and GET proof are mandatory.
- GitHub secret values are write-only. Because baseline has no CURRENT secret,
  activation rollback deletes only the transaction-created name and does not
  require the retained envelope. Retention remains mandatory for later recovery,
  reprovisioning, and audit; missing retention blocks activation/recovery.
- An active required check can lock `main` if its context/app is wrong or CURRENT
  stops passing. Activation-last and ruleset-disable-first rollback are load
  bearing.
- A new collaborator changes repository access and must not be inferred from
  this plan. Variant A remains incomplete until the owner names the actor.
- WSL installation/hardening and a Linux private storage root are external host
  changes, not implied by selecting WSL.
- The 100,000 cap is sufficient for the current Phase A tree, not a claim that
  future Phase B history/API coverage fits. Overflow remains an explicit rc3.
- Required-review and environment-review friction are separate. Variant B removes
  PR approval only; it retains owner environment approval and the strict check.

## Complexity: T3

Security-sensitive multi-module tooling, private filesystem transactions, GitHub
external-state schemas, lockout-safe ordering, manual/UI state, and reversible
activation require fresh decisions, TDD, adversarial review, and distinct owner
approval gates.
