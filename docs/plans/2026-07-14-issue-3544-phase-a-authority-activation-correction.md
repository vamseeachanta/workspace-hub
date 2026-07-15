# Plan for #3544: Correct and Operationalize Phase A Authority Activation

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3544
> **Client:** N/A
> **Lane:** lane:codex
> **Execution:** planning `parallel-readonly`; implementation `single-lane`; external activation isolated owner transaction
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3544-custom-ansys-r4.md`; `scripts/review/results/2026-07-14-plan-3544-prepare-fer-extraction-r4.md`; `scripts/review/results/2026-07-15-plan-3544-codex-{security,transaction}-r{5,6,7}.md`; `scripts/review/results/2026-07-15-plan-3544-{consumption,verifier}-r{8,9,10,11}.md`

---

## Recorded Owner Decisions

The owner resolved both design decisions on 2026-07-15. These choices will remain
fail-closed until the revised plan receives focused adversarial review and a
fresh approval bound to its exact commit. No implementation or external
activation may start before that approval.

1. **Merge-review posture — Variant B selected.** Live API readback shows
   `vamseeachanta` is the only
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
   - **B — solo-safe interim (selected):** retain no bypass but set
     `required_approving_review_count=0` and
     `require_code_owner_review=false`. The PR rule still rejects direct pushes;
     the exact authority status check remains mandatory. A later reviewed change
     may strengthen review after a second trusted reviewer exists.
   Variant A is not authorized by this plan and will require a later reviewed
   change plus a named second trusted collaborator.
2. **Private Linux owner host — existing `ace-linux-1` selected.** The
   owner-facing notation for the proposed private parent is
   `$HOME/.local/share/workspace-hub/legal-rule-authority`. The genesis preview
   must resolve the account home from a trusted OS account record, not the
   process environment; bind the canonical absolute path, UID, host identity,
   and verified SSH fingerprint in private evidence; and require the launcher
   argument to match that path exactly. Every component must already exist and
   resolve without symlinks. System ancestors such as `/` and `/home` must be
   root-owned and not group/other-writable; the trusted account home and every
   descendant through the selected parent must be owned by the bound account UID
   and not group/other-writable; and the final parent must be exact mode 0700 on
   a native local `ext4`, `xfs`, or `btrfs` filesystem.
   Missing or incorrect state stops before entropy or writes and requires a
   separately approved host-root provisioning transaction; genesis does not
   create or repair the parent. A read-only connection attempt from `ace-win-1`
   stopped at host-key verification, so the host fingerprint, resolved home path, mount identity,
   ownership, and permissions remain mandatory fail-closed preflight evidence;
   they are not assumed by this decision. `/mnt/d`, `D:\\ws`, network shares,
   Windows mode emulation, and any filesystem outside the approved native-local
   allowlist do not satisfy this contract. Host-key onboarding will require
   out-of-band fingerprint verification and will never use an insecure SSH
   override.

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
- The selected Linux host is recorded, but its SSH fingerprint and native-local
  mount/ownership/mode evidence are not yet verified from this workstation.

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
| Private genesis approval-record schema | `schemas/legal-rule-genesis-approval.schema.json` |
| Private genesis approval record | off-repo 0600 canonical JSON; exact path and SHA-256 supplied only in the separately approved genesis transaction |
| Genesis/operator guide | `.claude/docs/legal-rule-authority.md` |
| Pre-Python genesis verifier/launcher | `scripts/legal/launch_rule_authority_genesis.sh` |
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
preserving `protect-main` and all legacy enforcement. The frozen activation
posture will be Variant B on `ace-linux-1` using the selected private parent only
after its host and filesystem preflight passes.

## Corrected Normative Design

### Exact supersession and replacement-contract gate

The replacement contract must enumerate, rather than implicitly drift from, the
four #3522 clauses it supersedes:

1. resource bound `max_entries <= 10000` becomes `<= 100000` (supersedes
   #3522 contract **§2 Canonical codecs**, lines 45–83, specifically the Policy
   `max_entries` bound at line 83);
2. the frozen operator interface gains the owner-only `genesis-current` command
   (supersedes the closed frozen CLI list in **§7 Exit classes and exact
   acceptance**, lines 285–315, specifically its start at line 295);
3. environment admission changes from protected/main-only to the exact custom
   policies `main` and `refs/pull/*/merge` required by PR `GITHUB_REF`
   (supersedes #3522 contract **§6 / Phase A**, lines 240–244, plus the old
   preview's `custom_branch_policies:false`/`protected_branches:true` fields);
4. the old `legal-rule-authority / strict-scan` and workflow-prefixed preview
   context are replaced by observed check context `strict-scan / authority`,
   GitHub Actions integration ID `15368` (supersedes the required-check identity
   in #3522 contract **§6 / Phase A**, lines 243–245, plus the old preview's
   `Legal Rule Authority / strict-scan / authority` context).

It also corrects the cache posture by removing `setup-uv`, rejects the invalid
`update` rule, and replaces the unsupported user-repository `workflows` rule with
the required status check. The replacement contract cross-links each numbered
clause to its exact superseded heading in
`2026-07-13-issue-3522-rule-authority-contract.md`. The old
`2026-07-14-issue-3522-phase-a-protection-preview.json` is explicitly marked
deprecated/non-executable and cross-links the replacement contract and preview;
tests reject it as activation input. Every other #3522 boundary remains in force.

Implementation commit A contains the replacement contract and all trusted tool
bytes. After A exists, its full Git OID, the replacement-contract Git blob OID,
and canonical contract SHA-256 are recorded in the private activation preview.
Commit B changes only the mutable caller pin and its public non-secret pin
evidence to reference A. No activation approval is valid unless it binds exact A
and B OIDs and readback proves main contains B, the caller at B pins A, the
reusable/tool checkout is A, the current anchor binds A, and the three contract
identities recompute exactly. A stale #3522 plan/approval SHA cannot satisfy this
gate.

The public pin evidence is
`config/legal-rule-authority-implementation-pin.json`, canonical JSON with schema
`legal-rule-authority-implementation-pin-v1` and exactly these keys:
`schema`, `tool_commit` (A full OID), `contract_blob_oid`, `contract_sha256`,
`caller_path` (`.github/workflows/legal-rule-authority-gate.yml`), and
`reusable_path` (`.github/workflows/legal-rule-authority-reusable.yml`). Commit B
owns both this file and the caller; its own OID is derived after commit creation
and recorded in private evidence, avoiding a self-referential B field.

Public policy and schema remain exactly 100,000. Activation preflight records the
exact target tree entry count and requires `1 <= count <= 100000`; current
evidence is 22,936. The cap applies fail-closed—no truncation, sampling,
auto-growth, or clean verdict after rc3. Phase B history/API scaling remains
outside this issue.

### Secure genesis interface

Add this frozen owner-only public launcher command:

```text
launch_rule_authority_genesis.sh genesis-current
                --tool-repo GIT_DIR --tool-sha FULL_OID
                --out-parent PRIVATE_DIR --transaction-id UUID
                --approval-record PRIVATE_JSON --approval-sha256 HEX
                --python-realpath ABSOLUTE_PATH --python-sha256 HEX
```

It is unavailable when `GITHUB_ACTIONS` is set and requires
`LEGAL_RULE_OWNER_GENESIS=1`. It supports Linux only. It reads the public
registry and policy as Git blobs from exact tool commit A—not from arbitrary path
arguments—and verifies their blob OIDs and canonical SHA-256 values against the
replacement contract. These public inputs are intentionally not subject to the
private 0600 rule; all generated private files are. `--approval-record` is an
allowed private path and `--approval-sha256` is the exact non-secret digest the
owner separately approves. The genesis preview and separate owner approval will
also bind the exact non-secret `--python-realpath` and `--python-sha256` command
arguments before the launcher reads the approval JSON, removing any circular
trust in interpreter fields parsed by that interpreter. `manage_rule_authority.py`
will not expose a public `genesis-current` command. It will expose only a distinct
internal genesis dispatch that will be unreachable through the documented CLI
and will validate the inherited launcher capability described below before any
authority-module import. The launcher opens the record no-follow as a retained
FD, requires current-UID 0600 regular-file state, hashes that FD, and passes only
`/proc/self/fd/<approval-fd>` into the verified Python entry point. The canonical
record schema binds the plan/A/B/post-merge identities, transaction UUID,
`ace-linux-1`, root-owned SSH-host-key fingerprint evidence, machine-id digest,
trusted account name/UID/home, canonical parent, and native mount identity.
Before the authority entry point, authority-module imports, approval consumption,
entropy, or output writes, the launcher will recompute host-key and machine-id
evidence from root-owned system files with approved absolute tools. It will then
invoke only the separately verified, commit-A-pinned approval verifier described
below and will reject every record/digest/host/account/path mismatch or replayed
transaction UUID.

Before requesting entropy, the operator creates a fresh private detached
checkout or exact Git-object extraction of commit A, verifies A is reachable
from the approved post-merge main, verifies the entry point and every imported
authority-module blob OID against the A manifest/contract, rejects local or
untracked substitutions, and executes only that verified extraction with
isolated Python. A mutable working-tree script is never executable genesis input.

The minimal external pre-authority boundary will comprise
`scripts/legal/launch_rule_authority_genesis.sh` and the self-contained,
standard-library-only
`scripts/legal/verify_rule_authority_genesis_approval.py`. Their blob OIDs and
SHA-256 values will be in the replacement contract and genesis-only approval.
Using only absolute-path
trusted system Git, `sha256sum`, shell/core filesystem tools, and Python, it
resolves A, requires post-merge reachability, extracts the contract-allowlisted
verifier/entry point/modules into a newly created private 0700 directory, verifies
every Git blob OID and SHA-256, then makes files 0400 and directories 0500. It will
retain an open directory descriptor plus verifier and entry-point FDs. Any
descriptor/path, mode, inode, device, or digest change will abort before the
approval verifier or entropy. Before
invocation the operator opens the launcher once as a retained FD, requires a
regular file with approved owner/mode/inode/device, hashes
`/proc/self/fd/<launcher-fd>` with the approved absolute system `sha256sum`,
rechecks `fstat`, and invokes `/bin/bash /proc/self/fd/<launcher-fd>` without
reopening the pathname. The FD remains open until the launcher exits; pathname
replacement after open is irrelevant, and launcher-FD/inode/device/digest drift
will abort before the approval verifier or entropy. The trust assumption is
explicit: that verified launcher, the Linux kernel, approved native filesystem, absolute
system Git/hash/shell/Python binaries, root-owned system libraries, and absence
of a hostile same-UID process are trusted; repository worktree code, hooks,
configuration, PATH resolution, and extracted bytes are not trusted until
verified. The private approval will bind the exact approved system-Python
realpath and executable SHA-256. The plan will explicitly trust its root-owned
standard library/shared libraries; hashing the interpreter will not be described
as attesting those dependencies.

The launcher will open the approval record no-follow as a retained FD; require a
current-UID, link-count-one regular file with exact mode 0600, stable device,
inode, mode, size, and `1..16384` bytes; and require the raw SHA-256 to equal the
approved digest. It will open the canonical approved interpreter realpath
no-follow as a retained root-owned, non-group/other-writable regular-file FD,
fstat/hash that FD, and require the independently approved SHA-256. It will
execute the verified verifier FD first as
`/proc/self/fd/<python-fd> -I -S -B /proc/self/fd/<verifier-fd>`, with a sanitized
environment, fixed private working directory, closed unrelated FDs, and no
`PYTHONPATH`, `site`, `.pth`, `sitecustomize`, user site, global site-packages, or
repository path. The verifier will import only the standard library,
will contain its own parser, will import no authority/repository module, and will
request no randomness. Its interface will receive only retained FD numbers plus
the immutable non-secret identities already bound by the verified contract and
launcher arguments; it will independently recompute dynamic host/account/mount
facts from retained descriptors and root-owned system sources rather than
accepting a shell-serialized JSON comparison object. It will reject duplicate keys, BOM, CRLF, malformed
UTF-8, leading/trailing whitespace, floats, non-finite numbers,
boolean-as-integer coercion, noncanonical escapes/order, missing/extra fields,
and noncanonical bytes. Accepted bytes will be canonical ASCII `legal-json-v1`
with sorted keys, compact separators, `ensure_ascii=true`, `allow_nan=false`, and
exactly one LF.

The record schema will have `additionalProperties:false` at every object and will
bind exact typed values for `schema_id`, Git object format, plan/A/B/post-merge
OIDs, transaction UUID, contract, launcher, verifier, approved Python, and a host
object containing hostname, machine-id digest, SSH host-key evidence, trusted
account name/UID/home, output parent, and complete mount identity. The verifier
will compare every leaf without coercion against independently recomputed facts
and will emit fixed verdict metadata only. The same long-lived verifier process
will perform the final re-fstat/rehash of the approval record, verifier, and
interpreter, durably consume the approval as specified below, and directly
`execve` the verified internal authority entry without returning to the shell
launcher. The authority entry point will reparse through the same verifier module and
recheck dynamic facts immediately before entropy; corpus-driven differential
tests will require identical parsing decisions at both stages.

The exact top-level record will use `schema_id` =
`legal-rule-genesis-approval-v1`, `git_object_format` = `sha1`, the 40-lowercase-
hex `plan_commit`, `tool_commit_a`, `caller_commit_b`, and `post_merge_main`, a
canonical lowercase UUIDv4 `transaction_id`, and exact objects `contract`,
`launcher`, `approval_verifier`, `python`, and `host`. `contract`, `launcher`,
and `approval_verifier` will each contain exactly `path`, `blob_oid`, and
`sha256`; their paths will equal the contract's literal allowlisted repo-relative
paths, OIDs will be 40 lowercase hex because object format is `sha1`, and hashes
will be 64 lowercase hex. `python` will contain exactly `realpath` and `sha256`,
must byte-equal the independently approved CLI values, and will use a canonical
absolute no-symlink path plus 64 lowercase hex.

`host` will contain exactly `hostname`, `machine_id_sha256`, `ssh_host_key`,
`account`, `output_parent`, and `mount`. Hostname will equal `ace-linux-1`;
machine ID will be 64 lowercase hex. `ssh_host_key` will contain exactly `path`,
`key_type`, and `sha256_fingerprint`: a canonical absolute root-owned key path,
the recomputed first public-key token, and an unpadded OpenSSH
`SHA256:<43-base64-characters>` fingerprint of decoded key bytes. `account` will
contain exactly POSIX `name`, non-boolean integer `uid` in `1..2147483647`, and
canonical absolute `home`. `output_parent` will be the canonical approved
absolute descendant of that home. `mount` will contain exactly integer
`mount_id`, string `major_minor`, decoded absolute `root`, decoded absolute
`mountpoint`, `filesystem_type`, `source`, and `options`; mount ID will be a
positive non-boolean integer, major/minor will match decimal `N:N`, filesystem
will be one of `ext4|xfs|btrfs`, and options will be a sorted unique JSON array of
nonempty mount-option tokens. All strings will reject NUL/control characters and
will be length-bounded to 4096 bytes; the schema may impose tighter per-field
bounds. The normative JSON schema and verifier's manual validator will encode
these same names, types, literals, bounds, and `additionalProperties:false`, and
one-leaf mutation tests will require parity. Parse/schema/digest/comparison
failures will return fixed rc2; interpreter/verifier/host/account/path/mount/
integrity failures will return fixed rc4; unexpected exceptions will map to
fixed rc4. No failure will emit a parsed field, path, hash, JSON fragment, or
subprocess output.

Before state inspection, the verifier will acquire a nonblocking exclusive Linux
`flock` on the retained output-parent dirfd. It will retain that same open file
description across approval consumption and `exec` of the verified authority
entry point by explicitly marking only that dirfd, the retained interpreter FD,
and the other contract-required
FDs inheritable immediately before `exec`; every unrelated FD will remain
close-on-exec. Authority code will confirm the expected inherited FD identities
and keep the locked parent FD open through final-directory
verification. Recovery or cleanup will open the same parent, acquire the same
lock nonblocking, and refuse classification or mutation while the lock is held.
This parent-scoped lock intentionally serializes every genesis/recovery operation
under the selected private parent.

After every read-only validation succeeds—but before the authority entry point,
entropy, output creation, or external mutation—the verifier will atomically
consume the approval through the retained output-parent dirfd. As its final
successful action, the isolated verifier will use Python `os.open(..., dir_fd=)`
to create
`.genesis-consumed.<transaction-uuid>.json` with
`O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0600, and canonical content containing exactly
`schema` (`legal-rule-genesis-consumption-v1`), `approval_sha256`, and
`transaction_id`; write and fsync it; revalidate
owner, mode, link count, device, inode, size, and bytes; then fsync and revalidate
the retained parent dirfd. Without returning to the launcher, the verifier will
then `execve` the verified authority entry point through the same
`/proc/self/fd/<python-fd> -I -S -B /proc/self/fd/<entry-fd>` identity while
preserving only the required interpreter, approval, extraction, and locked-parent
FDs. Interpreter-path replacement after initial open will be irrelevant. Only
after that durable commit point may
authority code or entropy run. The tombstone will never be deleted, renamed, truncated, or
overwritten on success, handled failure, crash recovery, or incomplete-output
cleanup.

The internal authority dispatch will be `_genesis-current-from-launcher`; it will
not appear in the public frozen command list. `manage_rule_authority.py` will
move its current top-level authority imports behind a standard-library-only
bootstrap gate. Before importing any authority module, that gate will require and
revalidate the exact allowlisted inherited interpreter, approval, verifier,
entry/extraction, and locked-parent FDs. To prove the inherited candidate—rather
than some unrelated process—owns the lock, a newly opened probe FD's nonblocking
exclusive-lock attempt must first fail with `EWOULDBLOCK`; reasserting
`LOCK_EX|LOCK_NB` on the inherited candidate FD itself must then succeed; and a
second independent probe must still fail. The gate will then require the canonical tombstone to
match the approved digest/UUID with stable owner/mode/link/device/inode/bytes.
Missing, unlocked, renumbered, extra, or mismatched capability FDs and ordinary
direct `manage_rule_authority.py genesis-current ...` invocations will reject
with fixed output before imports, entropy, or output. This is an accidental/
workflow bypass boundary under the explicit no-hostile-same-UID trust assumption,
not an unforgeable same-UID capability or FD-provenance claim; a deliberate
same-UID process that reconstructs the entire locked FD/tombstone state is outside
the threat model and the plan will not claim to distinguish it.

Genesis state will be fail-closed: after the recovery process acquires the parent
lock, no tombstone/output is `UNUSED`; failure to acquire the lock is
`CONSUMED_RUNNING` and permits no inspection-based classification or cleanup;
tombstone plus an
independently valid final UUID directory is terminal `COMPLETE`; tombstone with
absent/incomplete output is terminal `SPENT`; and any partial/malformed marker,
final-without-marker, invalid final, or contradictory state is terminal
`CONFLICT`. A crash before the file-and-parent fsync commit point will remain
`UNUSED` and safely retryable because no entropy or output can precede that point;
any surviving marker entry will nevertheless block replay even if its content is
partial. Every post-commit crash will be irrevocably consumed. Recovery will
never re-enter entropy. Cleanup may remove only the matching incomplete output
after acquiring the parent lock and will reject the tombstone namespace. Every
failed or crashed consumed attempt will require a fresh preview, UUID, digest,
and approval. Consumption evidence will be retained permanently; a future
retention change would have to atomically migrate its key into an equally durable
no-overwrite consumed index that genesis checks before any old marker is removed.

The command obtains a 32-byte HMAC key and one unique 32-byte synthetic exact
pattern per public rule directly from the Linux kernel CSPRNG with no fallback.
The key file is exactly RFC 4648 canonical base64 of those 32 bytes followed by
one LF, with no other whitespace; the map is canonical `legal-json-v1`, binds the
public generation/revision/rule IDs, and contains only those generated synthetic
patterns. `key_id` is generated as `phase-a-` plus a canonical lowercase UUIDv4.
The generation-ledger JSON schema and codec both enforce this exact form and a
64-byte maximum. No generated private key, synthetic map/pattern, `key_id`, or
private content digest is accepted on argv/stdin or written to stdout; the
frozen repository/output path flags and transaction UUID are allowed. The
command never reads `.legal-deny-list.yaml` or
creates/migrates real rule bytes.

Every path component is opened no-follow through retained dirfds. Root-owned
system ancestors must not be group/other-writable; the trusted account home and
private descendants must match the bound non-root UID and must not be
group/other-writable; the final parent must be exact mode 0700. Before entropy
or private writes, the command requires Linux, resolves the output device and
longest mount through `/proc/self/mountinfo`, and binds mount ID, major:minor,
root, mountpoint, filesystem type, source, and options before/after the
transaction. Only owner-approved native local `ext4`, `xfs`, or `btrfs` is
accepted; `drvfs`, `9p`, FUSE, overlay, bind, NFS/CIFS, FAT/NTFS, `/mnt/<drive>`,
or changed/ambiguous mounts reject rc4. Encryption at rest is outside this
contract; neither preview nor acceptance claims or attests it. Outputs are created
no-overwrite 0600 under an incomplete 0700 child,
fsynced, verified, and atomically renamed no-replace to
`PRIVATE_DIR/UUID`. Output will be exactly `map.json`, `manifest.json`, `anchor.json`,
`ledger.json`, `key.b64`, and canonical `envelope.json` (<=32 KiB). The current
anchor binds the reviewed implementation tool SHA, `slot=current`, and
`expected_head_oid=null`. A failed consumed attempt will leave its durable
tombstone even when no final transaction exists; cleanup will be explicit and
will never make that approval reusable. Output is fixed verdict metadata only—never values, paths, hashes,
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

The selected transaction uses repository ID `1066339206`, name
`legal-rule-authority-main`, target `branch`, conditions exactly
`refs/heads/main`, `bypass_actors=[]`, and initially `enforcement=disabled`.
Its Variant B payload contains neither `update` nor `workflows`. Activation
preview, tooling, and tests reject Variant A or any other review posture; a
future Variant A transaction requires a new reviewed plan and owner approval.

Common required status rule:

```json
{"type":"required_status_checks","parameters":{"do_not_enforce_on_create":false,"required_status_checks":[{"context":"strict-scan / authority","integration_id":15368}],"strict_required_status_checks_policy":false}}
```

The selected Variant B solo-safe PR rule is fully specified:

```json
{"type":"pull_request","parameters":{"allowed_merge_methods":["merge","squash","rebase"],"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false,"required_approving_review_count":0,"required_review_thread_resolution":false}}
```

Variant A is non-executable reference material and is not authorized for this
transaction. Its future contract would use
the same object with `require_code_owner_review=true` and
`required_approving_review_count=1`, but is invalid until an exact second trusted
collaborator has write access, is named with the owner on every relevant
authority row in the base branch `.github/CODEOWNERS`, and proves they can
approve. For an owner-authored proof PR the second actor approves; for a
second-actor-authored proof PR the owner approves. The author never supplies the
counted approval, and head-only CODEOWNERS changes never satisfy the gate.
The base branch must end with this exact contiguous Variant-A ownership block in
this frozen order, replacing `<second-login>` with the separately approved
collaborator login. Because CODEOWNERS is last-match-wins, no later row may exist
and tests resolve every authority path to both actors with no shadowing:

```text
/.github/CODEOWNERS @vamseeachanta @<second-login>
/.github/workflows/legal-rule-authority-* @vamseeachanta @<second-login>
/scripts/legal/ @vamseeachanta @<second-login>
/schemas/legal-rule-* @vamseeachanta @<second-login>
/config/legal-rule-registry.json @vamseeachanta @<second-login>
/config/legal-rule-authority-* @vamseeachanta @<second-login>
/docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md @vamseeachanta @<second-login>
/docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json @vamseeachanta @<second-login>
/docs/plans/evidence/2026-07-14-issue-3544-phase-a-activation-contract.md @vamseeachanta @<second-login>
/docs/plans/evidence/2026-07-14-issue-3544-phase-a-github-preview.json @vamseeachanta @<second-login>
/docs/legal-rule-authority/phase-a-activation-proof-v1.txt @vamseeachanta @<second-login>
```

The proof matrix is tested in both directions: owner author/second actor reviewer,
and second actor author/owner reviewer. In each case the non-author's approval is
the sole counted approval and the effective last-match owner set is identical.

Creation uses POST with
the full disabled document. Activation is the final mutation and uses PUT—not
PATCH—with the same full document and only `enforcement` changed to `active`.
Normalized readback must match, effective rules for `main` must contain both the
existing `protect-main` protections and this new ruleset, and a proof PR must be
mergeable under the chosen review posture. The proof PR is never merged.

## Ordered Implementation and External Transaction

### Implementation after a future plan approval

1. Record Variant B, `ace-linux-1`, the selected private parent, and the exact
   revised plan SHA in the approval marker. Write each RED test before code.
2. Write RED tests, then create commit A containing the replacement contract,
   genesis transaction, corrected codecs/readbacks, reusable cache-free workflow,
   schemas, tests, and canonical non-secret preview. Record A's full OID, the
   contract blob OID, and canonical contract SHA-256.
3. Create commit B changing only the mutable caller and public pin evidence to
   pin A. The caller at B, reusable/tool at A, and anchor at A are invariant.
4. Run focused/full acceptance and T3 adversarial code/artifact review.
5. Present exact A and B identities. Merge the implementation PR with a merge
   commit only—never squash or rebase—so A and B OIDs are preserved. Verify after
   merge that both are ancestors reachable from `main`, B has exactly the allowed
   caller/pin-evidence delta, and all recorded A blobs recompute exactly.
6. Prepare a **genesis-only** private preview binding post-merge main, A, B,
   contract/blob identities, verified `ace-linux-1` fingerprint/host identity,
   trusted-account UID, canonical absolute pre-existing private parent and native
   mount identity, transaction UUID, and rollback of local partial output in the
   canonical private approval record. Independently compute its SHA-256 and stop
   for approval of the exact record digest plus the launcher digest. A
   missing, symlinked, wrong-owner, wrong-mode, or disallowed parent stops for a
   separate host-root provisioning plan/approval; this preview cannot create or
   repair it. That separate explicit genesis approval authorizes only one local
   `genesis-current` invocation consuming the exact record/digest and no GitHub
   mutation. A changed, missing, replayed, or alternate record requires a new
   preview and approval.
7. Execute the commit-A-pinned approval verifier as the only pre-authority Python
   process. After exact record/local-fact comparison succeeds, durably create and
   fsync the no-overwrite consumption tombstone before authority import, entropy,
   or output. Execute the approved genesis transaction once from the verified
   detached/extracted A bytes, independently materialize/verify/audit it, and
   retain the exact canonical `envelope.json` bytes plus canonical SHA-256 in
   private 0600 evidence. Success, handled post-commit failure, and post-commit
   crash will leave the approval consumed; a pre-commit crash will remain UNUSED
   and retryable because no entropy/output can precede consumption. Any consumed
   failure will require a fresh preview, UUID, digest, and approval and will never
   silently regenerate.
8. Only after successful retained genesis, prepare the separate activation
   preview binding the same envelope digest, A/B/post-merge identities, live tree,
   chosen ruleset variant, exact baselines, frozen proof identity, and rollback.
   Stop for fresh explicit activation approval. Activation consumes those exact
   retained envelope bytes and never invokes or regenerates genesis.

### External activation only after that separate approval

1. **Exclusive-owner and drift preflight:** the activation approval must attest
   a short, bounded maintenance window in which the owner is the sole repository
   administrator/mutator, no other session or credential will change environment
   secrets, environments, policies, rulesets, or the proof branch, and every
   unexpected actor/change ends the transaction. The GitHub endpoints used here
   do not provide a plan-verified conditional-write contract, so readback is a
   drift detector—not atomic compare-and-swap—and the plan makes no zero-TOCTOU
   claim. Then reread main head/tree, caller B and its A pin, workflow/tool
   A, post-merge reachability of unchanged A/B, contract blob OID/SHA-256,
   retained envelope SHA-256, collaborators/base CODEOWNERS, full environment,
   branch policies, environment secret names/timestamps, repository/effective
   rulesets, workflow/check identity, and `protect-main`. Abort on any mismatch,
   pre-existing CURRENT, or same-name ruleset.
2. **Retained-genesis proof:** acquire the same retained-parent exclusive lock
   nonblocking and hold it through COMPLETE classification and the full local
   materialize/verify/audit proof. Lock contention classifies
   `CONSUMED_RUNNING` and permits zero external adapters. Require genesis state
   `COMPLETE`, rehash the immutable consumption tombstone and retained canonical envelope, and require
   the activation-preview digest, materialize it into a second private 0700
   directory, verify, and audit the exact main tree with A. Require rc0 and
   complete coverage; do not run `genesis-current`.
3. **First-write drift check:** immediately after retained proof/audit and
   immediately before the first environment PUT, repeat the full drift check.
   Observed proof-to-check drift permits zero external writes. The unavoidable
   check-to-write window is accepted only under the explicit exclusive-owner
   assumption; exact post-write readback is mandatory and cannot prove atomicity.
4. **Environment:** PUT the exact environment, create the two policies, perform
   the manual admin-bypass UI change, and verify exact GET/list readback.
5. **CURRENT drift check and write:** repeat the full drift check immediately before uploading
   the exact retained `LEGAL_SCAN_AUTH_CURRENT` envelope bytes by stdin only;
   require name and
   timestamp metadata readback. GitHub cannot return the value, so local canonical
   envelope retention is mandatory for recovery.
6. **Proof PR:** from the bound main SHA, create exact branch
   `phase-a-activation-proof-v1`, title
   `[phase-a] activation proof v1`, and a one-file mode-100644 diff adding
   `docs/legal-rule-authority/phase-a-activation-proof-v1.txt` whose complete
   bytes are ASCII `phase-a-activation-proof-v1` plus one LF. Any pre-existing
   branch/path/PR aborts. Open it as a draft PR,
   approve the environment deployment, and require the exact
   `strict-scan / authority` check from integration `15368` to return success.
   Then transition the PR from draft to ready-for-review and verify ready state.
   Require the selected Variant B posture and zero PR approvals; any Variant A
   payload or review requirement aborts. Immediately after creation, capture
   the numeric PR database ID/number, numeric head-repository ID, exact head
   commit OID, numeric check-run ID, and check-suite/workflow-run IDs where
   exposed. Every later drift check requires those
   exact identities, branch/title/path/bytes/diff, ready state, and check app/
   context; replacement or rerun identities require a new preview and approval.
   Fixture/adversarial tests prove the fork path remains constant-fail before
   environment access; no live fork/provider creation is authorized.
7. **Disabled-ruleset drift check:** repeat the full drift check, including proof ready/check/
   review state, immediately before POSTing the chosen full payload with
`enforcement=disabled`,
   capture its new ID, and verify normalized plus raw readback. Any 422/shape drift
   rolls back; never substitute an update/workflows rule.
8. **Activation drift check and activate last:** repeat the full drift check after disabled
   readback and immediately before PUTting the same full document with
`enforcement=active`; verify
   raw/normalized/effective rules, unchanged `protect-main`, exact required check,
   and proof-PR mergeability under the chosen review posture. Do not merge it.
9. **Close proof:** close the unmerged proof PR and delete only its transaction
   branch. Publish only fixed non-sensitive verdict/evidence. #3544 remains open
   until implementation completeness and post-activation review pass.

### Rollback and stop order

At the first failed readback or proof, stop forward progress. Before every
rollback mutation, re-attest the exclusive-owner window and reread the resource;
continue only when its captured numeric identity and complete state equal the
transaction-created state. Any other state, unexpected actor, or expired window
stops for manual reconciliation without further mutation. The same unavoidable
read-to-write window remains an explicit trust assumption; rollback is not
described as atomic.

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
cannot prove the intended payload: an ambiguous secret PUT stops and escalates;
it is never automatically retried or deleted. Rollback mutations use the same
exclusive-window and reconcile-before-next-step rule. Every repeated drift check
rechecks all A/B/contract, main/tree, collaborators/CODEOWNERS, environment/
policies/admin, secret metadata, ruleset/effective, `protect-main`, and proof
facts applicable at that boundary; drift permits no further forward write.

## Pseudocode

```text
genesis_current(tool_repo, tool_sha_A, out_parent, transaction_id,
                approval_record, approval_sha256):
    sole public entry is verified launcher; Python CLI has internal dispatch only
    require owner gate, non-Actions Linux, exact tool OID
    open approved interpreter once; shell retained-FD verify it, approval, verifier, immutable A
    run only pinned `-I -S -B` stdlib verifier before authority imports or entropy
    acquire nonblocking exclusive flock on retained parent dirfd; hold across authority exec/final verify
    verifier requires canonical exact-schema record and compares every recomputed fact
    resolve home from trusted account record, never environment; bind host/fingerprint/UID
    canonicalize selected absolute parent with no symlink components
    require exact pre-existing current-UID 0700 parent; never create/repair it
    qualify stable approved native mount; retained-dirfd validate parent
    extract/detach A; verify reachability and every executable/imported blob
    read registry/policy as exact Git blobs at A; verify contract blob identities
    verifier final-revalidates approval/verifier/interpreter before consumption
    verifier creates O_EXCL 0600 tombstone; fsyncs file and parent; revalidates
    classify any surviving marker as consumed; never delete or resume after failure/crash
    verifier directly execves authority through same interpreter FD without returning to shell
    internal stdlib bootstrap verifies inherited FD allowlist, lock probe, tombstone before imports
    recheck dynamic facts; only then import authority and request entropy
    generate key, synthetic map, and bounded key_id internally from kernel CSPRNG
    build manifest, current anchor, authenticated genesis ledger, CI envelope
    require canonical envelope <= 32 KiB and verify bundle before decoding pattern
    write six files into new incomplete 0700 child with O_EXCL and fsync
    materialize/verify in-memory; fsync child+parent; rename no-replace to UUID
    emit fixed rc0 metadata; on failure emit fixed rc2/3/4 and no accepted final directory
    activation preview requires COMPLETE (valid tombstone plus verified final directory)
    recovery/cleanup must acquire the same parent lock nonblocking before classify/mutate

build_activation_preview(live, decision, implementation_sha):
    require exact main/tree, sole-or-approved collaborator set, empty secret slot
    require baseline environment and protect-main equal approved snapshot
    require decision == variant_b; reject variant_a and every other posture
    emit canonical non-secret environment/policy/ruleset/order/rollback document

verify_activation_readback(preview, live):
    compare full environment reviewer/self-review/wait/branch/admin posture
    compare exact branch policies and environment secret metadata presence
    compare raw+normalized new ruleset and effective main rules
    require protect-main unchanged and exact check app/context
    reject missing/extra/type-coerced fields; return fixed verdict only

activate_owner_transaction(preview):
    require separately approved retained envelope; never call genesis
    require bounded exclusive-owner mutation-window attestation
    perform drift preflight and retained-envelope proof; do not claim atomic CAS
    environment -> policies -> UI admin bypass -> CURRENT -> proof PR
    create disabled ruleset -> activate ruleset last -> final proof
    on failure rollback only exact transaction state while window remains exclusive
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-activation-contract.md` | superseding exact activation/resource/rollback contract |
| Create | `docs/plans/evidence/2026-07-14-issue-3544-phase-a-github-preview.json` | canonical non-secret API request/readback variants |
| Create (commit B) | `config/legal-rule-authority-implementation-pin.json` | exact public v1 A/contract/caller/reusable pin evidence |
| Modify | `docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md` | cross-link all four exact superseded clauses; preserve Phase B text |
| Modify | `docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json` | mark deprecated/non-executable and point to #3544 replacements |
| Modify | `scripts/legal/manage_rule_authority.py` | lazy-import internal `_genesis-current-from-launcher` dispatch with inherited-capability/tombstone gate; no public genesis command |
| Create | `scripts/legal/launch_rule_authority_genesis.sh` | sole public owner-only `genesis-current` interface and FD-bound pre-authority launcher |
| Create | `scripts/legal/verify_rule_authority_genesis_approval.py` | commit-A-pinned stdlib-only canonical approval parser/comparator that runs before authority imports or entropy |
| Modify | `scripts/legal/rule_authority/codec.py` | bounded key ID and canonical activation structures |
| Modify | `schemas/legal-rule-generation-ledger.schema.json` | enforce `phase-a-<lowercase UUIDv4>` key ID and 64-byte bound |
| Create | `schemas/legal-rule-genesis-approval.schema.json` | canonical private preview/approval record consumed by the launcher and CLI |
| Modify | `scripts/legal/rule_authority/{authority,envelope,private_io}.py` | atomic genesis/envelope transaction with Linux guarantees |
| Modify | `scripts/legal/rule_authority/protection.py` | exact payload validation and complete readback/effective-rule comparison |
| Modify | `.github/workflows/legal-rule-authority-reusable.yml` | remove setup-uv/cache and use isolated system Python |
| Modify (commit B) | `.github/workflows/legal-rule-authority-gate.yml` | pin the commit-A reusable workflow/tool by full OID |
| No change in selected Variant B | `.github/CODEOWNERS` | Variant A ownership changes remain outside this approved transaction |
| Modify | `.claude/docs/legal-rule-authority.md` | Linux owner runbook, proof, rollback, and value-withholding rules |
| Modify/Create | `scripts/legal/tests/test_rule_authority_*.py` and fixtures | RED matrix below |
| Create | `scripts/legal/tests/test_rule_authority_genesis_launcher.py` | execute launcher fixtures for trust, substitution, and no-Python-before-verify boundaries |
| Update | `docs/plans/README.md` | index this plan and later reflect reviewed state |

No implementation may silently change the public registry/policy authority bytes.
If implementation discovers such a change is required, stop, increment generation
and revision in a revised plan, and obtain another owner decision before sealing.

## TDD Test List

| Test | RED condition and required result |
|---|---|
| `test_genesis_command_is_frozen_and_owner_only` | public launcher command absent today; require exact flags including independent interpreter identity, owner gate, no Actions execution, and no public Python genesis command |
| `test_direct_internal_genesis_invocation_cannot_bypass_launcher` | ordinary direct public/internal `manage_rule_authority.py` calls, missing/extra FDs, absent lock, bad three-step lock proof, or missing/mismatched tombstone reject before authority import/entropy/output sentinels; an unlocked inherited candidate while another process owns the parent lock must reject; tests will not claim provenance against a deliberate same-UID reconstruction |
| `test_genesis_rejects_non_native_or_ambiguous_mounts` | require stable `/proc/self/mountinfo` identity and approved ext4/xfs/btrfs; Windows, `/mnt`, drvfs/9p/FUSE/overlay/bind/network/FAT/NTFS and mount drift reject before entropy/private reads |
| `test_genesis_requires_preexisting_0700_parent_and_0600_outputs` | trusted-account home resolution must match the canonical approved absolute path; root-owned non-writable `/` and `/home` fixtures pass, while writable/foreign-owned system ancestors, foreign-owned or writable account-home/private components, absent parent, environment substitution, wrong final UID/mode, symlink component, parent swap, output hardlink/non-regular, or mode drift rejects rc4 before entropy/writes; genesis never creates/repairs the parent and public A blobs are not treated as 0600 inputs |
| `test_genesis_preview_binds_verified_host_identity` | fixture-backed canonical approval record/digest requires exact `ace-linux-1` SSH-host-key and machine-id evidence, trusted-account name/UID/home, canonical path, mount, A/B/plan identities, and transaction UUID; launcher and the isolated verifier recompute/compare local evidence and every missing/mismatched/replayed field rejects before authority import, consumption, entropy, or writes |
| `test_approval_verifier_requires_exact_canonical_bytes` | duplicate keys, BOM, CRLF, whitespace, malformed UTF-8, noncanonical escapes/order, floats/non-finite numbers, bool-as-int, and 16,385 bytes reject before authority/entropy sentinels |
| `test_approval_verifier_schema_and_bound_facts_are_exact` | removing/adding/mutating every top-level or nested leaf across plan/A/B/main, contract, launcher, verifier, interpreter, UUID, host, account, parent, SSH key, machine ID, and mount rejects without coercion |
| `test_approval_verifier_supply_chain_and_fd_boundary` | independently approved CLI Python realpath/hash must match one retained regular root-owned FD used through `/proc/self/fd` for both verifier and authority; post-consumption interpreter-path replacement, verifier blob/hash, PATH/PYTHONPATH, `site`, `.pth`, global/user `sitecustomize`, global/user site-packages, repository path, mutable extraction, approval/verifier/interpreter FD replacement, or inode/device/mode/size/byte drift rejects or remains irrelevant before authority import/entropy |
| `test_verifier_and_authority_share_parser_contract` | corpus-driven differential test requires both stages to accept/reject identical bytes and produce the same typed record |
| `test_verified_order_is_parser_then_consumption_then_authority_then_entropy` | event ledger and sentinels prove no tombstone precedes successful exact comparison; after durable tombstone file+parent fsync/revalidation the verifier directly execves authority without a shell return; no authority import, CSPRNG, or output can skip that chain |
| `test_consumption_marker_is_owner_only_no_overwrite` | symlink/non-regular/hardlinked/wrong-owner/wrong-mode/malformed/pre-existing marker and O_EXCL collision reject before entropy |
| `test_replay_after_success_or_post_commit_failure_is_rejected` | inject entropy, output-create, file-fsync, verify, rename, parent-fsync, and final-verify failures; the same approval/UUID never reaches entropy twice |
| `test_crash_replay_is_rejected_at_every_post_commit_boundary` | SIGKILL/os._exit after marker create/fsync, entropy, incomplete writes, or final rename leaves COMPLETE, SPENT, or CONFLICT and never resumes/regenerates |
| `test_precommit_crash_is_unused_and_safe_to_retry` | crash before tombstone file+parent fsync reaches no entropy/output; absent marker remains UNUSED, while any surviving partial entry is CONFLICT and blocks reuse |
| `test_marker_fsync_failure_and_partial_marker_fail_closed` | no entropy runs before durable commit; any surviving partial/malformed entry is terminal CONFLICT and blocks replay |
| `test_concurrent_recovery_and_cleanup_require_parent_lock` | subprocess exec fixture proves only allowlisted FDs inherit and the same retained-parent flock survives into authority through final verification; nonblocking recovery/cleanup observes CONSUMED_RUNNING and performs no classification, removal, or output access until release |
| `test_cleanup_never_removes_consumption_marker` | incomplete cleanup rejects the marker namespace; disposition requires a separate approved transaction |
| `test_activation_preview_requires_complete_consumed_genesis` | retained-genesis proof acquires/holds the parent lock during classification and local verification; contention plus UNUSED, CONSUMED_RUNNING, SPENT, and CONFLICT invoke zero external adapters; only marker plus independently verified final output is COMPLETE |
| `test_genesis_creates_private_entropy_without_output` | internally create 32-byte key and unique 32-byte synthetic patterns; generated private values/digests never use argv/stdin/stdout; key file is exact RFC4648 base64 plus one LF |
| `test_genesis_csprng_failure_and_collision_fail_closed` | entropy failure, short read, repeated pattern, UUID/key ID collision, and output collision leave no accepted final transaction and never fall back/retry silently |
| `test_ledger_key_id_schema_and_codec_match` | schema and codec accept only `phase-a-<lowercase UUIDv4>` within 64 bytes and reject every alternate form |
| `test_genesis_binds_public_blobs_to_commit_a` | public registry/policy blob OIDs and canonical hashes match contract at A; private generated files alone require 0600 |
| `test_genesis_executes_verified_commit_a_extraction` | reject mutable checkout, unreachable A, entry-point/import blob mismatch, untracked substitution, or entropy request before all module blobs verify |
| `test_genesis_launcher_uses_trusted_absolute_tools` | execute launcher fixture; reject PATH aliases, hooks/config, unapproved binaries, wrong launcher/verifier/interpreter blob or hash, or missing explicit trust inputs |
| `test_genesis_launcher_fd_boundary_blocks_substitution` | execute race fixtures; retained launcher/approval-record/dir/verifier/entry FDs plus 0500/0400 tree reject pathname replacement and inode/device/mode/digest swaps; launcher is hashed and invoked through the same FD, and sentinels prove the approval verifier is the only Python before complete approval validation |
| `test_genesis_is_atomic_no_overwrite` | collisions, disk-full/fsync/rename crash leave no accepted final transaction |
| `test_genesis_outputs_exact_canonical_bundle` | exact six 0600 files, current/null-head anchor, fresh ledger, <=32 KiB envelope |
| `test_genesis_materialize_verify_roundtrip` | independent materialization and verification return rc0 at exact tool SHA |
| `test_genesis_output_allowlist` | all rc2/3/4 paths withhold values, paths, hashes, base64, parser fragments |
| `test_policy_contract_cap_reconciles_real_tree` | normative/schema/codec/config cap exactly 100,000; current tree >10,000 and <=cap |
| `test_tree_over_100000_fails_closed` | 100,001 entries return rc3; no sampling/truncation/clean result |
| `test_workflow_has_no_cache_or_dependency_action` | no setup-uv/actions-cache/artifact; exact `python3 -B -E -s`, no user site |
| `test_two_commit_caller_topology` | A contains contract/reusable/tool/schema/tests; B changes only caller/public evidence; B pins A and anchor binds A |
| `test_merge_commit_preserves_a_b_reachability` | squash/rebase merge rejects; post-merge main must retain exact A/B OIDs as ancestors and recompute B delta/A blobs |
| `test_public_pin_schema_and_b_ownership` | exact path/v1 six-key canonical schema; B owns caller and pin evidence and neither contains a self-referential B field |
| `test_supersession_and_old_preview_deprecation` | all four #3522 clauses cross-link replacements; old preview is marked non-executable and rejected as activation input |
| `test_genesis_and_activation_approvals_are_separate` | genesis-only approval permits one local transaction/no GitHub writes; later preview binds retained envelope digest and activation never regenerates |
| `test_environment_put_schema_is_exact` | typed reviewer ID and opposite branch-policy booleans; missing/extra/coerced fields reject |
| `test_pr_and_main_custom_policy_patterns` | exactly `main` and `refs/pull/*/merge`; fork job never references environment |
| `test_environment_readback_binds_admin_bypass` | require false, reviewer, self-review false, wait zero, exact policies/no extras |
| `test_solo_repo_review_decision_fails_closed` | preview requires exact Variant B with count0/codeowner false; Variant A, count1, code-owner review, or any alternate posture rejects regardless of collaborator state |
| `test_variant_a_is_outside_selected_transaction` | preview, implementation adapters, and activation reject Variant A and make no CODEOWNERS or external-state mutation |
| `test_ruleset_payload_uses_supported_complete_schema` | full PR/status params; exact context/app; no `update` or `workflows` |
| `test_ruleset_disabled_then_active_full_put` | POST disabled then PUT full active document; PATCH/partial update rejects |
| `test_effective_rules_preserve_protect_main` | baseline ID/rules/bypass unchanged and effective main includes both rulesets |
| `test_proof_pr_state_machine` | draft check succeeds, PR transitions to verified ready state, exact Variant B requires zero PR approvals, active reevaluation is mergeable but unmerged, and any Variant A state aborts |
| `test_proof_identity_is_frozen_and_drift_bound` | exact branch/title/one-file path/mode/ASCII-plus-LF diff, unchanged base CODEOWNERS blob identity, and no code-owner requirement; capture and recheck PR number/database ID, head OID, and numeric check/run IDs |
| `test_fork_constant_fail_pre_secret` | fork result fixed and no environment/secret/data scan |
| `test_activation_drift_checks_and_exclusive_window` | exact bounded owner attestation is required; full A/B/contract/main/CODEOWNERS/environment/secret/ruleset/proof drift checks run preflight, immediately pre-first-PUT, pre-CURRENT, pre-disabled POST, and pre-active PUT; observed drift produces zero further writes, and tests explicitly reject any atomic-CAS claim for unsupported endpoints |
| `test_read_write_toctou_is_explicit_and_fail_closed` | fixture injects mutation before adapter dispatch and requires no write; mutation during an unavoidably unconditional request is classified as exclusive-window violation, never claimed atomic, and stops after readback without overwriting further state |
| `test_ambiguous_mutation_reconciliation` | lost 200/201/204 and timeout fixtures reconcile intended/baseline/other; ambiguous secret PUT stops without automatic retry/delete; rollback ambiguity reconciles or stops before continuing |
| `test_rollback_disables_ruleset_first` | injected failures assert exact disable, secret, UI, policies/environment order |
| `test_rollback_touches_only_created_ids` | pre-existing env/protect-main/secret/ruleset are never overwritten/deleted |
| `test_external_adapters_are_fixture_only` | tests perform no live writes and validate official 200/201/204/303/404/422 shapes |

Tests must be committed RED before their matching implementation slice.

## Acceptance Criteria

- [x] Owner decisions select Variant B, `ace-linux-1`, and owner-facing notation
      `$HOME/.local/share/workspace-hub/legal-rule-authority`; the trusted account
      record must resolve and privately bind an exact canonical absolute path,
      UID, host fingerprint/identity, and native mount before genesis approval.
- [ ] The selected private parent pre-exists with no symlink components as
      current-UID mode 0700 on an allowed native-local filesystem. Root-owned
      system ancestors are non-writable by group/other; account-home/private
      components match the bound UID and are non-writable by group/other.
      Missing or incorrect state stops for a separate provisioning approval;
      genesis never creates or repairs it.
- [ ] Fresh approval binds the revised plan SHA and explicitly accepts the
      100,000 cap plus chosen review posture; no stale #3522 approval is reused.
- [ ] Exact genesis command passes Linux permissions, atomicity, roundtrip,
      native-filesystem qualification, hostile-input, size, crash, exact
      base64-plus-LF, internal synthetic-map creation, and value-withholding tests.
- [ ] The retained-FD private approval record and exact approved digest bind the
      plan/A/B/transaction, local SSH-host-key and machine-id evidence, account
      name/UID/home, canonical parent, and mount; mismatch or replay stops before
      authority import, approval consumption, entropy, or writes.
- [ ] The external launcher's recorded blob/hash, trusted absolute tools,
      allowlisted A verifier/module identities, approved interpreter realpath/hash,
      immutable extracted tree, and retained-FD execution pass real launcher/
      approval/verifier/path-swap race tests. The commit-A-pinned stdlib verifier
      is the only Python allowed before authority import and entropy; it enforces
      exact canonical bytes/schema and compares every typed bound fact.
- [ ] The launcher is the sole public genesis entry. Both verifier and internal
      authority execute through the same retained verified interpreter FD. The
      Python CLI lazy-import bootstrap rejects direct invocation and every
      missing/extra/unlocked/mismatched inherited capability or tombstone before
      authority imports, entropy, or output.
- [ ] Successful approval verification durably creates and revalidates an
      immutable owner-only no-overwrite tombstone, including file and parent
      fsync, before authority import or entropy. A retained-parent exclusive lock
      prevents concurrent recovery/cleanup through final verification. Success,
      handled post-commit failure, post-commit crash, partial marker, and cleanup
      tests prove a consumed approval/UUID can never be reused; pre-commit crash
      is retryable only when no marker survives and no entropy/output occurred.
      Activation requires terminal COMPLETE state.
- [ ] Contract blob identities, public registry/policy blobs, reusable workflow,
      tool, schema, and anchor bind commit A; commit B changes only the caller and
      public pin evidence and its caller pins A by full OID.
- [ ] A merge commit preserves exact A/B OIDs and post-merge main reachability;
      squash/rebase is prohibited, and the exact public pin v1 schema passes.
- [ ] All four #3522 superseded clauses cross-link their replacements and the old
      #3522 protection preview is visibly deprecated and rejected by tests.
- [ ] A separately approved, one-time genesis-only transaction verifies the
      canonical approval, durably consumes it, and executes verified extracted A
      bytes before the activation preview exists; exact retained envelope
      bytes/digest and tombstone identity are consumed without regeneration.
- [ ] Public contract, JSON schema, codec, config, and tests agree on 100,000;
      the then-live exact tree is measured and below it.
- [ ] Workflow contains no setup/dependency/cache/artifact action and executes
      pinned checked-out standard-library code with isolated Python flags.
- [ ] Environment payload and policies match the valid documented API schemas;
      admin bypass is manually disabled and bound by GET readback.
- [ ] Exact Variant B ruleset has complete valid PR/status parameters, exact
      `strict-scan / authority`/15368 identity, no update/workflows rule, and no
      bypass; Variant A is rejected and `protect-main` is unchanged.
- [ ] Same-repository proof PR succeeds as draft, transitions to verified ready
      state with the exact Variant B zero-approval/no-code-owner posture, and remains
      mergeable after active ruleset readback; frozen branch/title/path/bytes/diff
      and captured PR/head/check identities survive every drift check. It is never merged. Fork fixtures remain
      constant-fail before secret access.
- [ ] Full legal authority suite, focused enforcement tests, Ruff, compileall,
      schema validation, workflow checks, legal scan, and diff checks pass.
- [ ] T3 adversarial plan review has no MAJOR before user approval; T3 code and
      artifact review has no MAJOR before implementation merge.
- [ ] A genesis-only preview receives separate approval before producing and
      retaining the envelope; only afterward does an activation preview bind live
      SHAs/digests/IDs/timestamps/host/path and receive its own explicit approval.
- [ ] Retained-genesis proof and activation-preview construction acquire the same
      parent lock nonblocking and hold it through COMPLETE classification and
      local verification; contention produces zero external adapters.
- [ ] Failure injection proves rollback touches only exact transaction-created
      state while the exclusive-owner window remains valid; drift or ambiguity
      stops without overwriting a stale baseline.
- [ ] The activation approval explicitly accepts the bounded sole-admin mutation
      window and the unavoidable read-to-write TOCTOU of endpoints without a
      verified conditional-write contract. Drift checks run at preflight,
      immediately pre-first-environment-PUT, pre-CURRENT, pre-disabled-POST, and
      pre-active-PUT; observed drift permits no further write, exact readback is
      required, and no artifact claims atomic CAS.
- [ ] No Phase B/PENDING/CAS/history/provider/cache-deletion action occurs; issue
      closure still requires the completeness gate.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| `custom_ansys_runners` R4 | APPROVE | exact supersession references, first-write CAS, and canonical CODEOWNERS matrix resolve R3 findings |
| `prepare_fer_extraction` R4 | APPROVE | trusted pre-Python launcher, FD boundary, trust assumptions, and executable race tests resolve R3 findings |
| Codex security R5 | MAJOR | impossible current-UID ownership rule for root-owned system ancestors |
| Codex transaction R5 | MAJOR | missing host-identity RED test, Variant-B/CODEOWNERS contradiction, and ambiguous approval wording |
| Codex security R6 | MAJOR | genesis did not consume approved host evidence; launcher pathname was reopened after hashing |
| Codex transaction R6 | MAJOR | missing approval-record data path and false atomic-CAS/lost-update guarantee |
| Codex security R7 | MAJOR | no durable approval-consumption marker; impossible pre-Python structured-record validation boundary |
| Codex transaction R7 | MAJOR | failed genesis can replay the same unconsumed approval record/digest/UUID |
| Consumption R8 | MAJOR | impossible rc0/consume order, live-vs-spent overlap, pre-commit crash overclaim, and weak future disposition |
| Verifier R8 | MAJOR | circular interpreter pin, insufficient `-I -B` isolation, same ordering contradiction, and underspecified exact schema |
| Consumption R9 | MAJOR | R8 fixed; interpreter FD was not retained across authority exec and activation did not explicitly join the parent lock |
| Verifier R9 | MAJOR | R8 fixed; public Python genesis command could bypass the mandatory launcher and early imports |
| Consumption R10 | MAJOR | R9 fixed; separate probe did not prove inherited candidate FD owned the lock |
| Verifier R10 | MAJOR | R9 fixed; same invalid lock-provenance proof left internal bootstrap bypassable |
| Consumption R11 | APPROVE | structural verifier-to-authority exec, three-step candidate proof, crash/recovery, permanence, and activation locking verified |
| Verifier R11 | APPROVE | sole launcher, lazy-import gate, retained interpreter, isolation, exact schema, lock proof, and narrowed threat claim verified |

**Overall result:** PLAN-REVIEW — both focused R11 reviewers returned APPROVE
after affirmatively verifying the complete R7→R10 correction chain. The plan is
ready for user approval, but implementation and activation remain blocked until
the user explicitly approves this exact plan revision and the required approval
marker/status are created outside this session's authority.

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
- A new collaborator changes repository access and is outside this plan.
  Variant A remains unauthorized until the owner names the actor in a later
  reviewed change.
- Host-key onboarding and creation or permission repair of the selected private
  parent are external host changes. They require verified fingerprint and
  mount/UID/mode preflight and are not implied by naming `ace-linux-1`.
- The 100,000 cap is sufficient for the current Phase A tree, not a claim that
  future Phase B history/API coverage fits. Overflow remains an explicit rc3.
- Required-review and environment-review friction are separate. Variant B removes
  PR approval only; it retains owner environment approval and the strict check.

## Complexity: T3

Security-sensitive multi-module tooling, private filesystem transactions, GitHub
external-state schemas, lockout-safe ordering, manual/UI state, and reversible
activation require fresh decisions, TDD, adversarial review, and distinct owner
approval gates.
