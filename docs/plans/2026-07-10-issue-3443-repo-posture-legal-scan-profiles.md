# Plan for [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443): Repository-posture legal scan profiles

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3443
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly planning/review; central-engine writer plus serialized per-repo rollout after approval
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3443-*.md`

---

## Resource Intelligence Summary

### Existing code and policy

- `scripts/legal/legal-sanity-scan.sh:113-130,158-240` currently reduces every deny-list entry to `pattern|case_flag`; category, severity, surface, and repository posture are lost, and every match blocks.
- `.claude/skills/coordination/legal-sanity-scan/SKILL.md` declares the scan mandatory for catalogs and mount-drive intelligence but documents false-positive bypasses. The policy cannot express a private-internal skip safely.
- `config/agents/SHARED_SOUL.md` makes the legacy scan a universal hard gate. `.claude/docs/legal-scanning.md` and related skills cite a deleted `.claude/rules/legal-compliance.md` path.
- `.pre-commit-config.yaml` contains independent gitleaks coverage for workspace-hub. `scripts/security/secrets-scan.sh` can scan siblings but does not include every private repo by default, and gitleaks is not installed on this Windows host.
- `scripts/data/document-index/phase-d-data-sources.py` and `phase-e-registry.py` pass an unsupported positional target to the shell scanner and fail open when it is absent.
- `scripts/readiness/nightly-readiness.sh` checks for a literal scanner string rather than executable policy coverage.
- `llm-wiki-acma/REDACTION-POSTURE.md` and `tests/test_build_domain_pack.py` already establish the desired content boundary: exact identifiers are allowed internally while outward packs fail closed.

### Private-repository universe

Live GitHub enumeration on 2026-07-10 found:

| Measure | Count |
|---|---:|
| Private repositories | 29 |
| Active private repositories | 26 |
| Archived private repositories | 3 |
| Private forks | 0 |
| Repositories with substantive scanner/deny controls | 6 |
| Repositories with successful active exact legal-scan CI | 1 |
| Repositories with a separate active deny/leak gate | 1 |

The tier-1 ecosystem contract names seven repositories. Four are checked out under the live workspace; three are absent. None of the four has functioning local automatic legacy legal-scan coverage: one declared hook resolves to a nonexistent sibling path, two have no invocation, and workspace-hub does not invoke the legacy scanner from pre-commit.

Implementation will re-enumerate GitHub visibility and the live checkout set. The counts above are a baseline, not a permanent N/N claim. Archived repositories will be classified in the registry but will not receive mutation PRs unless unarchived.

### Prior issues and documents

- [#3398](https://github.com/vamseeachanta/workspace-hub/issues/3398) owns downstream hook/path wiring and explicitly does not own scan breadth.
- [#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) owns the public-egress validator.
- [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424) and ACMA [#214](https://github.com/vamseeachanta/llm-wiki-acma/issues/214) are downstream private-catalog consumers.
- [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) requires per-line or path-restricted forensic sentinels and rejects blanket exemptions.
- [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) and [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) define the public/private routing boundary.
- [#3099](https://github.com/vamseeachanta/workspace-hub/issues/3099), [#3169](https://github.com/vamseeachanta/workspace-hub/issues/3169), and [#3073](https://github.com/vamseeachanta/workspace-hub/issues/3073) provide PII, false-positive, and genuine-leak precedents.
- Drive-file query `legal sanity private repository policy` returned no relevant file. Five configured indexes reported coverage-gap reason `unreachable`.

### Standards and LLM Wiki pages

Not applicable. This is repository governance and enforcement design, not an engineering calculation or wiki-content claim.

### Gaps identified

- No repository-posture policy schema or category-aware engine exists.
- The current wrapper cannot skip private-internal disclosure checks without also losing unrelated tripwires.
- No authoritative staged-blob/path scan or complete sibling/private-repo enumeration exists.
- Private-internal skip evidence, public-egress strict evidence, visibility-drift checks, and rollout evidence are not standardized.
- Security/secret coverage is separate but incomplete and must not be represented as supplied by the legal scanner.
- The first adversarial pass found that caller-selected surfaces, visibility-only authorization, public rollout details, and skip-before-security activation would create bypasses. The revised design will remove those conditions rather than document them as accepted risk.

### Evidence and reproduction proofs

This is a governance change, so runtime-failure reproduction is N/A. Empirical commands verified the current behavior:

```text
gh repo list vamseeachanta --visibility private --limit 1000 --json name,visibility,isArchived,isFork
# 29 private; 26 active; 3 archived; 0 forks

rg legal-sanity-scan across private default branches and local tier-1 configs
# 6 substantive controls; 1 successful active exact scanner CI; 0/4 working local automatic coverage

inspect legal-sanity-scan.sh parse_deny_list and scan_directory
# category/severity discarded; --diff-only reads working-tree paths from git diff --name-only HEAD
```

Distinct sources consulted: issue body, scanner/deny implementation, canonical legal skill and SHARED_SOUL, security scanner/pre-commit, document-intelligence callers, private routing tests, GitHub repository inventory, and seven related issue families.

---

## Artifact Map

| Artifact | Planned path |
|---|---|
| Plan | `docs/plans/2026-07-10-issue-3443-repo-posture-legal-scan-profiles.md` |
| Policy engine | `scripts/legal/legal_policy.py` and bounded modules under `scripts/legal/policy/` |
| Compatibility wrapper | `scripts/legal/legal-sanity-scan.sh` |
| Policy schema/default | `config/legal/legal-policy.schema.json`, `config/legal/default-policy.json` |
| Legacy rule migration | `.legal-deny-list.yaml`, `scripts/legal/migrate_legal_rules.py`, migration manifest under `config/legal/` |
| Public aggregate registry | `config/legal/repo-policy-aggregate.yml` with counts and non-reversible run IDs only |
| Trust roots | `config/legal/trust-roots.json` with public verification keys, roles, validity, and revocation metadata |
| Private authority and rollout journal | signed exact repo IDs, names, URLs, attestations, and PR links in a verified private governance repository; its identity/location will not be committed to this public repo |
| Reproducible local distribution | source-built `tools/legal-policy/legal-policy.pyz`, dependency/SBOM manifest, checksum, and repo-relative wrapper in each activated private repo |
| Immutable CI distribution | reusable workflow in `.github/workflows/legal-policy.yml`, called by exact workspace-hub commit SHA |
| Tests | `tests/legal_policy/` plus focused pipeline/readiness tests |
| Repo-local posture | canonical `.legal-policy.json` in each active repository through its own issue/plan/approval/PR lifecycle; an external signed attestation will authorize its digest |
| Governance | `config/agents/SHARED_SOUL.md`, generated provider runtimes, `.claude/rules/legal-compliance.md`, `.claude/docs/legal-scanning.md` |
| Skills/adapters | `.claude/skills/coordination/legal-sanity-scan/SKILL.md`, affected PR/review skills |
| Pipeline callers | Phase D/E, cron/backfill, readiness, hook templates and CI workflows |
| Public rollout report | aggregate-only HTML/JSON under `docs/reports/`; no private names, IDs, URLs, workflow names, or mappings |
| Private rollout report | detailed HTML/JSON in the private governance store |
| Bypass checker | `scripts/legal/check_legal_policy_bypasses.py` and focused tests |
| Plan/code reviews | `scripts/review/results/2026-07-10-{plan,code}-3443-*.md` |

---

## Deliverable

A tested repository-posture policy engine and gated rollout will make authorized private repositories skip legacy client-identity/topology deny matching for internal at-rest commits. Public-egress scanning and independent secret, privacy, provenance/IP, and raw-data residency controls will remain non-downgradeable parts of the composite decision.

---

## Policy Contract

### Closed decision model

Every component will emit one closed action: `PASS`, `SKIP`, `REVIEW_REQUIRED`, `BLOCK`, or `ERROR`. Unknown actions/categories will be schema errors. Precedence will be `ERROR > BLOCK > REVIEW_REQUIRED > PASS`. An authorized identity/topology `SKIP` will be neutral in composite reduction; it will become overall `PASS` only when every non-skipped mandatory component is `PASS`. Any unauthorized `SKIP` will become `ERROR`.

The process exit contract will be fixed: `0=PASS`, `2=BLOCK`, `3=REVIEW_REQUIRED`, and `4=ERROR`. A review-required result will never pass in place. An authorized role will use a separate command to sign a finding-specific resolution; a later complete re-evaluation will validate that resolution and emit component `PASS` with its resolution ID. Secret findings, tool errors, missing evidence, and public-egress disclosure findings will not be review-resolvable.

| Derived operation | Client identity | Approved private topology | Secrets | Personal PII | Provenance / third-party IP | Raw-data residency | Composite floor |
|---|---|---|---|---|---|---|---|
| public repository or public PR metadata | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | strict |
| authorized private + internal staged/range work | `SKIP` | `SKIP` | `BLOCK` on finding/error | targeted `PASS` or `REVIEW_REQUIRED` | targeted `PASS` or `REVIEW_REQUIRED` | targeted `PASS` or `REVIEW_REQUIRED` | allow only when every mandatory independent gate passes |
| any public-egress artifact/metadata operation | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | `BLOCK` | strict |
| code/data import or ingest | derived category action | derived category action | `BLOCK` | `REVIEW_REQUIRED` floor | clean-room `BLOCK`/`REVIEW_REQUIRED` floor | residency `BLOCK`/`REVIEW_REQUIRED` floor | targeted, never disclosure-only |
| forensic fixture | exact reviewed disclosure sentinel only | exact reviewed disclosure sentinel only | never exempt | never exempt | never exempt | never exempt | scoped and expiring |
| missing/invalid identity, policy, visibility, evidence, tool, or required check | n/a | n/a | n/a | n/a | n/a | n/a | `ERROR`, fail closed |

Protected floors for public-egress, secrets, privacy, provenance/IP, and residency will live in the engine default policy and will not be weakenable by repo-local policy. Repo-local policy may only narrow allowed operations or add blocks. Tests will cover the full reduction table: all-pass, authorized disclosure-skip plus all-pass, each single and multiple `REVIEW_REQUIRED`/`BLOCK`/`ERROR` combination, unauthorized skip, and valid/invalid review resolution.

### Trust and signature authority

Policy and attestation payloads will use UTF-8 canonical JSON with duplicate-key rejection, RFC 8785-style deterministic serialization, and SHA-256 content digests. Detached Ed25519 signatures will bind a schema version, payload type, key ID, issued/expiry times, nonce, and digest. The reproducible zipapp will vendor a selected pure-Python Ed25519 verifier and canonical-JSON implementation at pinned source hashes; the build will emit their licenses/SBOM and will run published test vectors plus parser-differential tests. The plan will not claim stdlib-only distribution.

`config/legal/trust-roots.json` will pin public keys and non-overlapping roles: `posture-authority`, `review-authority`, and `revocation-authority`. A target repo will never choose or add its own trust root. Private signing keys will remain in an approved OS/GitHub environment secret service, never in any repo or journal. Rotation will require an old-root plus revocation-authority transition signature; emergency compromise will revoke the key ID, force strict mode everywhere, and require newly signed attestations. CI will use trusted UTC and bounded clock skew; invalid time, unknown/stale/revoked/self-signed keys, wrong role, duplicate JSON keys, or signature/parser disagreement will be `ERROR`.

### Private/internal authorization

`skipped_private_internal` will require all of the following before the legacy disclosure component can return `SKIP`:

1. the private authority service will present a live signed posture attestation binding the immutable GitHub node ID, protected ref, strict-install baseline commit/tree, policy digest, engine release digest, allowed entrypoint bindings, exact ruleset/check/workflow IDs and digests, activation request ID, nonce, and expiry;
2. every local and CI skip decision will query GitHub for live node ID/private visibility and retrieve the current non-revoked attestation; offline/cached/unknown evidence will force strict legacy disclosure scanning rather than authorize `SKIP`;
3. the immutable CI workflow pinned by commit SHA will be installed, green at the exact candidate SHA, and enforced by an active ruleset covering every accepted persistent ref, with the expected GitHub App/workflow identity and no admin, bot, repository-role, or merge-queue bypass path;
4. staged and CI secret checks will be installed, tool-available, pinned, and passing on the same blob/range manifest;
5. required privacy, provenance/IP, and residency components will pass or produce a separately approved signed review decision; and
6. the target repository's own issue, future-tense plan, adversarial review, and user approval will be recorded.

If any prerequisite is absent, the repo will remain in strict compatibility mode and will be reported as `DEFERRED_NOT_ACTIVATED`; it will not receive the private/internal skip.

### Trusted operation derivation

The engine will expose no generic `--surface` or caller-supplied `requested_surface` downgrade. It will derive an operation from a signed entrypoint binding plus authoritative context:

- local staged work: repo-relative pre-commit entrypoint and the snapshotted index tree;
- GitHub PR/push: event payload, protected workflow reference, trusted base/head SHAs, and live repository identity;
- public issue/PR metadata: API-fetched title/body/comments bound to immutable node IDs;
- Pages, packs, exports, and external-send tools: a deterministic artifact manifest produced by a registered public-egress entrypoint; and
- import/ingest: registered destination and source/provenance manifest.

Changing a workflow, policy, entrypoint binding, required check, or ruleset in the candidate change will force strict mode and require separate policy approval. Attempts to label a registered outward path or workflow as internal will return `ERROR`.

The activation attestation will remain external to the target commit, avoiding a self-referential SHA. A strict-install commit will merge first; the authority will then verify that commit on the protected ref and mint an attestation bound to its control-surface digests. Later candidates may use the skip only when their base descends from that baseline and neither staged/range evidence nor live ruleset state changes any bound control. The final CI verdict will bind the candidate SHA. Direct-push, wrong-ref, check-name-collision, stale-green-run, inactive/evaluate-mode ruleset, branch-pattern gap, bypass-actor, disabled-workflow, and same-change control mutation fixtures will fail activation.

### Sentinel contract

The implementation will remove blanket directory/file exemptions. A disclosure sentinel will be valid only on an allowlisted governance or fixture line and will bind an exact disclosure rule ID, the [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443)-style issue URL, reviewer identity, expiry date, and normalized line digest. It will not exempt secrets, PII, provenance/IP, or residency rules. Spoofed, expired, moved, broadened, or self-authored sentinels will fail. Policy/schema source files will use a path-restricted parser rule rather than a blanket scanner exclusion.

The bypass checker will be semantic, not a repository-wide literal-string ban. It will inspect executable Python/shell AST/token streams and structured hook/workflow configuration for operative bypass assignments, flags, aliases, wrappers, and split-token construction. Historical documents and guidance will not be executable surfaces. A separate signed forensic-allowance registry may admit only an exact test/checker-source line hash with rule ID, issue, reviewer, reason, and expiry; it will never authorize runtime bypass behavior. Whole-delivery tests will cover the plan, rules, checker, fixtures, reviews, and the existing tracked corpus, and will distinguish safe documentation from malicious execution.

---

## Pseudocode

```text
function authorize(repo, live_attestation, authoritative_context):
    validate closed schema and non-weakenable default floors
    verify trust-root role, signature, revocation, immutable repo node ID, policy/engine/control digests, and expiry
    derive operation from protected entrypoint + event/artifact context; reject caller downgrade
    verify live visibility for every skip and exact required-check/ruleset activation
    return strict mode unless every private/internal activation prerequisite is green

function collect_staged_manifest(repo):
    snapshot index tree OID and parse raw NUL-delimited A/M/D/R/C/T/U records
    reject unmerged and intent-to-add entries; preserve old/new path, mode, and blob OID
    represent deletion as a tombstone with old path/blob metadata; do not require a new blob
    inspect names and applicable old/new blobs; stream oversize content and fail closed on unsupported required evidence
    re-read index tree OID and fail on mutation; require at least one manifest record, not one new blob

function collect_ci_manifest(context):
    bind API-verified base/head/tree OIDs, merge base, commit metadata, and PR metadata
    recover a shallow fetch deterministically or fail; reject force-push drift before verdict

function scan_and_publish_artifact(authoritative_root, registered_transport):
    independently enumerate the resolved, symlink-safe root; reject caller-supplied omissions
    stage a read-only content-addressed artifact and rescan its exact bytes
    let the gate-owned transport publish only that artifact/digest; reject post-scan mutation

function composite_evaluate(policy, manifest):
    run the required components over the same immutable manifest/range
    run zero disclosure-pattern searches only for authorized private/internal identity/topology
    enforce protected action floors and exact sentinel grammar
    emit component verdicts, tool/config/engine digests, blob/tree OIDs, and final exit code

function inventory_and_rollout(owner):
    paginate all repositories and record node ID, visibility, archived state, default-branch OID, and observation time privately
    reconcile renames/deletions and re-query state immediately before every write
    advance an idempotent leased transaction only after target-repo governance and activation prerequisites pass
```

---

## Files To Change

| Action | Path/surface | Reason |
|---|---|---|
| Create | policy engine/schema/default/aggregate/tests listed above | category- and posture-aware authority without public private-topology disclosure |
| Update | `.legal-deny-list.yaml` through a tested one-to-one migration manifest | preserve every legacy rule and add category/action metadata |
| Update | legacy shell wrapper | retain compatibility; route supported entrypoints to staged/range/artifact collectors; reject positional and surface ambiguity |
| Update | SHARED_SOUL, restored legal rule, docs, skills, and generated provider runtimes | replace the universal legacy scan with the composite posture contract |
| Update | Phase D/E, cron/backfill, PR/review and readiness callers | remove broken/fail-open/bypass behavior |
| Create | reproducible dependency-vendored zipapp, checksum/SBOM, reusable workflow, and repo-relative hook template | give downstream repos a pinned local engine plus an immutable central CI authority |
| Update | security scanner registry/templates | provide same-manifest staged and CI secret evidence; missing binary/config will block activation |
| Create/update | active private repo signed policy, vendored zipapp, hook/CI, ruleset evidence via separately approved per-repo PR | enact the user decision without overriding target governance |
| Create | public aggregate and private detailed HTML/JSON reports | separate public counts from private identities/URLs |
| Create | semantic bypass inventory/checker and signed forensic-allowance schema | reject operative bypasses and classify safe historical/test literals without a blanket file exemption |
| Update | `docs/plans/README.md` | index this plan |

Archived repositories will receive private inventory dispositions only. The implementation will recheck archive state before each write and will not mutate an archived repository; an unarchived/archive-drift case will return to target-repo planning rather than inherit the baseline disposition.

The engine will be source-built into a deterministic dependency-vendored zipapp. Each activated repo will commit that zipapp, checksum, and SBOM for local use. Its CI will additionally call the workspace-hub reusable workflow at an exact commit SHA and verify the signed engine/policy digests. No hook will resolve through a sibling checkout or an unpinned branch. Without live visibility and attestation access, the local wrapper will fall back to strict legacy disclosure scanning; it will never use cached private posture to skip.

`scripts/agents/build-soul-runtime.sh` will regenerate every provider runtime after the canonical policy changes. A regression test will compare generated artifacts and verify that every loaded runtime contains the new gate.

---

## Evidence Protocol

### Staged/index evidence

- The collector will derive a raw, NUL-safe manifest from the snapshotted index and will cover A/M/D/R/C/T/U, both rename/copy paths, type changes, symlink targets, and gitlink path/OID metadata.
- A deletion-only commit will have a valid nonempty tombstone manifest even though it has no new blob. Path rules will inspect the deleted path; old blob inspection will occur only for a rule whose contract requires before-state evidence.
- Unmerged entries and intent-to-add will be `ERROR`. Binary content will require a registered extractor; oversize content will stream rather than skip. Any required content that cannot be examined will be `ERROR`.
- Pre/post index tree OIDs will have to match, closing the staged-blob/working-tree TOCTOU gap.

### CI range and public metadata evidence

- GitHub event/API data will supply repository node ID, event ID, immutable base/head SHAs, current head verification, merge base, tree OIDs, commit messages, and PR/issue title/body/comment node IDs.
- Shallow clones will fetch the exact missing objects with bounded retries; unresolved history or a force-push/head mismatch will be `ERROR`.
- The verdict will bind all fetched metadata and blobs to hashes. It will not trust free-form environment values for visibility or operation selection.

### Rendered/exported evidence

- Pages, packs, external-send, and export gates will independently enumerate a canonical resolved artifact root after generation, reconcile every directory entry, and construct a deterministic path/type/size/mode/SHA-256 manifest themselves.
- The gate will stage a read-only content-addressed archive/tree, rescan its exact bytes, and either invoke the registered transport itself or issue a one-time digest-bound transport authorization. The publisher will consume only that scanned object; an arbitrary producer manifest will never be authoritative.
- A zero-record root, omitted/extra file, changed output after scan, symlink escape, unsupported file type, unregistered transport, or digest mismatch will be `ERROR`.

### Mutable public metadata

- GitHub App/webhook checks will cover create/edit/delete events for issue and PR bodies/comments, review bodies/comments, and commit metadata where applicable. Evidence will bind normalized content hashes, node IDs, `updatedAt` values, and an event-sequence watermark.
- A final pre-merge/posting gate will refetch the complete current metadata set and compare the watermark immediately before the protected action. Later edits will invalidate the prior result and enqueue a new check; a SHA-green run with a stale metadata watermark will not satisfy the ruleset.

---

## Rollout Transaction and Rollback

The rollout will use two independent gates so a private skip can never precede its replacements:

1. **Strict installation:** a target issue and plan will be created, reviewed, and user-approved; the pinned engine, strict policy, repo-relative hook, same-manifest secret gate, immutable CI workflow, and required-check/ruleset will be installed. The legacy disclosure component will still run.
2. **Activation:** only after staged and remote CI evidence is green at the exact candidate SHA will a separately signed attestation enable `private-client/internal` disclosure `SKIP`. A final live visibility/archive/ruleset query will precede merge/activation.

The private journal will advance through `DISCOVERED -> PLANNED -> USER_APPROVED -> STRICT_INSTALLED -> CHECKS_ENFORCED -> SKIP_ACTIVATED -> VERIFIED`, with terminal `DEFERRED`, `FAILED`, and `ROLLED_BACK` states. Each step will record node ID, observation time, default/base SHA, branch, immutable candidate commit, expected remote ref, lease value, issue/plan/approval evidence, PR node ID, check runs, ruleset digest, attestation digest, and idempotency key. Every ref write will bind expected state: expected-empty lease for creation and exact expected-OID lease for update. The tool will fetch and verify the resulting remote ref/candidate SHA after each push. Before retrying a rejected push, the operator will inspect reflog and remote state for auto-sync races.

The target repo's own gates will remain authoritative. Approval of [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443) will authorize the central engine and rollout preparation, not self-approve target-repo plans. A private batch manifest may be presented for one explicit user approval covering enumerated target plans, but the evidence will be recorded on every target issue.

Rollback will first publish a signed live revocation for the affected attestation/key and verify that every target returns strict mode without relying on a cache. It will then restore/verify strict disclosure scanning on every persistent ref before reverting the target hook/workflow/policy using the journaled base and merge SHAs. Open PRs will be closed or superseded idempotently. A rollback will not be complete while any old local zipapp or SHA-pinned workflow can authorize a skip; unavailable targets will remain `ROLLBACK_BLOCKED`. Central-engine rollback will publish a new pinned release and update target attestations without mutating an existing digest.

The private governance store will be a schema-versioned, signed, append-only journal inside an allowlisted private Git repository whose immutable node ID is pinned in approved local configuration. The tool will reject a public/unknown GitHub visibility, a path inside any public worktree, a symlink/reparse-point traversal, permissive ACLs, a dirty/unleased authority ref, or a location outside the resolved approved root. Writes will use lock + temporary file + fsync + atomic rename, followed by an exact leased commit/push; recovery will replay only fully signed records. Key material will remain outside this store. Backup/restore drills and journal-write failure tests will prove state recovery.

Inventory will authenticate the enumerator's owner/viewer identity, record token scope/permission headers, GraphQL `totalCount`, every cursor/page and rate-limit record, and reconcile node IDs with the prior private registry. A lower or missing prior set will become `UNOBSERVED_ACCESS_GAP`, not successful coverage. A changed count will require an explicit added/deleted/transferred/renamed disposition.

The public report will publish aggregate state counts and a non-reversible run ID only. Exact repo identities, node IDs, workflow names, URLs, branches, and PR evidence will stay in the verified private governance store. Tests will reject private identities in public registries, migration manifests, reports, exception traces, dry-run transcripts, and logs.

---

## TDD Test List

- private-client/internal emits `skipped_private_internal` and performs zero identity/topology deny-pattern searches only with a live valid attestation and live private visibility; offline/cached state runs strict disclosure scanning;
- the same identifier blocks in public/public-egress content, metadata, and path names;
- all component-action combinations reduce to the specified `0/2/3/4` exit contract; signed finding resolution will require the right role and a complete later re-evaluation;
- self-signed, wrong-role, stale/revoked/rotated-key, duplicate-key, clock-skew, canonicalization, parser-differential, and signature-test-vector fixtures will fail closed;
- a private/internal skip will not activate with a missing/failing secret binary, config, staged gate, CI check, ruleset, privacy/IP/residency gate, or unsigned/expired/replayed attestation;
- exact workflow/check/app identity, candidate SHA, protected ref coverage, no bypass actors, active enforcement mode, direct-push closure, merge queue, and current non-stale run will be required; collisions and scope gaps will fail;
- repo-local policy cannot weaken protected floors, add an unknown category/action, or change an entrypoint binding;
- caller/env attempts to downgrade Pages, pack, export, external-send, PR metadata, or import to internal will fail;
- private-client secrets/private keys will fail the independent same-manifest security gate;
- private-client code-import third-party IP markers will fail the targeted clean-room gate;
- personal PII and raw data will use explicit privacy/residency actions rather than being silently allowed by private posture;
- private profile on public/unknown visibility, wrong node ID, missing policy/map, invalid schema, or zero required evidence will fail closed;
- staged A/M/D/R/C/T/U blobs and paths, deletion tombstones, deletion-only changes, untracked-to-staged files, type changes, symlinks, gitlinks, unmerged/index-intent entries, leading-colon/wildcard names, binary/oversize content, and index mutation will have explicit expected verdicts;
- trusted `base...head` CI will cover shallow-fetch recovery, force-push drift, commit messages, PR title/body/comments, metadata edits/deletes, event watermarks, tree OIDs, and zero-range handling;
- rendered artifact roots will cover independent enumeration, generator omission, extra files, generated/untracked output, empty roots, post-scan mutation, symlink escape, unsupported types, and digest-bound gate-owned transport;
- sibling repo resolution and nonzero repo enumeration work from arbitrary CWD;
- Phase D/E target paths invoke the supported engine contract and fail if required tooling is missing;
- disclosure-sentinel grammar will accept only an exact, reviewed, unexpired disclosure-rule line and will reject spoofed/moved/broadened markers plus every secret/PII/IP/residency exemption;
- the semantic bypass checker will classify all current tracked occurrences, distinguish documentation/checker fixtures from executable behavior, and reject operative assignments/flags, aliases/wrappers, split-token construction, fail-open tool absence, blanket directory exemptions, missing client maps, and unsupported positional calls;
- the signed forensic-allowance registry will accept only exact approved test/checker-source line hashes and reject runtime files, broad paths, stale entries, and self-approval;
- visibility change from private to public invalidates cached private decisions;
- legacy migration will map every old deny rule and exclusion exactly once; exclusions will be classified as index-irrelevant traversal, exact extractor policy, sentinel conversion, or removed bypass; golden public-profile tests will preserve or strengthen every prior public block;
- deterministic zipapp builds will match their checksum; local and immutable CI engines will produce equivalent component verdicts;
- rollout schema/validator fixtures will prove authenticated owner/scopes, pagination/total-count completion, prior-registry reconciliation, `UNOBSERVED_ACCESS_GAP`, unique node IDs, one disposition per observed repo, valid state transitions, target approval evidence, expected-empty/exact-OID leases, remote SHA verification, PR/check evidence, archive drift handling, and zero activation without mandatory gates;
- authority-store fixtures will reject public/unknown worktrees, symlink/reparse escapes, bad ACLs, dirty/unleased refs, partial writes and unsigned records, and will recover an atomic journal transaction;
- revocation/rollback fixtures will prove every target returns strict mode before rollback completion and that cached/offline evidence never authorizes a skip;
- rollout fixture will visit every enumerated active repo exactly once, classify archived repos without mutation, and report drift from the 29/26/3 baseline;
- public-boundary fixtures will reject exact private names, IDs, URLs, workflow names, reversible mappings, and exception leakage in registries, migration manifests, reports, dry runs, and logs;
- outward `llm-wiki-acma` Pages/pack fixtures continue to fail on private identifiers;
- public-repo legacy behavior remains strict and backward-compatible where the wrapper is retained.
- regenerated Claude, Codex, Gemini, and Hermes runtime fixtures will contain the new canonical gate and match generator output.

Tests will be written before implementation for each bounded slice: schema/action floors, evidence collectors, composite evaluation, legacy migration, bypass checker, distribution equivalence, inventory transaction, runtime regeneration, and caller adapters.

---

## Proposed Verification Commands

```text
uv run pytest -q tests/legal_policy -p no:cacheprovider
uv run python scripts/legal/legal_policy.py validate-policy --policy .legal-policy.json
uv run python scripts/legal/legal_policy.py scan-staged --repo . --entrypoint local-precommit
uv run python scripts/legal/legal_policy.py scan-ci-range --repo . --github-event "$GITHUB_EVENT_PATH" --entrypoint github-pr
uv run python scripts/legal/legal_policy.py scan-and-publish --repo . --artifact-root public --entrypoint pages-publish --dry-run-transport
uv run python scripts/legal/legal_policy.py inventory --owner vamseeachanta --private-store "$LEGAL_GOVERNANCE_STORE" --aggregate-out config/legal/repo-policy-aggregate.yml
uv run python scripts/legal/legal_policy.py rollout --private-store "$LEGAL_GOVERNANCE_STORE" --dry-run
uv run python scripts/legal/legal_policy.py rollout --private-store "$LEGAL_GOVERNANCE_STORE" --resume-from "$RUN_ID"
uv run python scripts/legal/legal_policy.py rollback --private-store "$LEGAL_GOVERNANCE_STORE" --run-id "$RUN_ID" --dry-run
uv run python scripts/legal/legal_policy.py verify-rollout --private-store "$LEGAL_GOVERNANCE_STORE" --public-report docs/reports/2026-07-10-3443-private-repo-rollout.json
uv run python scripts/legal/check_legal_policy_bypasses.py
uv run pytest -q tests/test_legal_phase_d_e.py tests/test_nightly_readiness.py tests/test_security_scan.py -p no:cacheprovider
uv run pytest -q -p no:cacheprovider
uv run python scripts/legal/build_policy_zipapp.py --verify-reproducible --verify-sbom
bash scripts/security/secrets-scan.sh --repo workspace-hub
bash scripts/legal/legal-sanity-scan.sh --diff-only
bash scripts/agents/build-soul-runtime.sh
git diff --exit-code -- config/agents
uv run pytest -q tests/test_agent_runtime_generation.py tests/test_legal_public_report.py -p no:cacheprovider
git diff --check
git diff --cached --check
git fsck --no-dangling
```

The focused and full pytest suites, runtime generation, staged checks, and committed-tree verification will run locally and in pinned CI. The independent secret scan and signature/ruleset integration tests will be required in pinned CI; missing local gitleaks or signing tooling will be recorded as an expected local blocker, never converted to success. The rollout tool will print exact redacted `gh issue create`, branch creation, SHA-pinned workflow, expected-empty/exact-OID leased `git push`, `gh pr create`, ruleset verification, apply/resume/recovery, and rollback commands in private dry-run output before any target write. Tests will compare that transcript with golden transaction fixtures. Credentials, exact repo identities, and private URLs will not be written to public logs.

---

## Acceptance Criteria

- [ ] Tests will be written first and fail before the policy engine exists.
- [ ] Authorized `private-client/internal` commits will run zero client-identity/topology deny-pattern searches and will record `skipped_private_internal` component evidence; cached/offline/unknown authorization will run strict disclosure scanning.
- [ ] The composite verdict will still require passing secret, privacy, provenance/IP, and raw-data residency components over the same immutable manifest/range.
- [ ] Public/public-egress and targeted code-import/privacy/residency gates will remain fail closed with staged-blob/path, CI-range/metadata, or rendered-artifact evidence as appropriate.
- [ ] No caller-controlled surface flag, repo-local action override, same-change workflow/policy downgrade, cached visibility, self-signed posture, or replayed attestation will enable the skip.
- [ ] Missing secret tooling/config, required CI/ruleset enforcement, signed posture, live private visibility, or targeted gates will block activation and leave strict scanning enabled.
- [ ] Every legacy deny rule and exclusion will receive exactly one migration disposition, and the public golden profile will preserve or strengthen legacy blocking behavior.
- [ ] All currently observed active private repos will be re-enumerated and receive a separately governed target issue/plan plus an activated, failed, or deferred disposition; archived repos will remain unmodified after a final state recheck.
- [ ] Coverage reporting will use the live execution set and prove each observed repo was visited once; it will never infer full coverage from the 2026-07-10 baseline.
- [ ] Public/unknown repos will be unable to select `private-client`; visibility drift will fail closed.
- [ ] Phase D/E, sibling resolution, readiness and current bypass paths will use the tested contract.
- [ ] The semantic bypass inventory/checker will reject operative legacy bypass behavior without blocking safe documentation/checker fixtures; exact signed forensic allowances will be line-hash scoped and expiring.
- [ ] `scripts/legal/legal-sanity-scan.sh` will remain a compatibility entry point, but the new engine/schema and closed action model will be canonical.
- [ ] Every activated repo will use a repo-relative deterministic zipapp locally and an immutable SHA-pinned reusable workflow remotely; sibling paths and moving branches will be rejected.
- [ ] Every activated repo will have readable required-check/ruleset evidence and passing staged/CI secret checks before the private/internal attestation is minted.
- [ ] Required-check evidence will bind active ruleset scope, no bypass actors, exact app/workflow/check identity, protected refs, candidate SHA, and current run; wrong-name/stale/bypass cases will fail.
- [ ] `uv run pytest -q tests/legal_policy -p no:cacheprovider` and focused pipeline/readiness/security tests will pass.
- [ ] Full workspace tests, staged diff checks, secret scan, and the profile-aware policy self-scan will pass.
- [ ] The private report will hold exact identities/PR links; the public HTML/JSON report will contain only aggregate states and a non-reversible run ID and will pass a topology-leak test.
- [ ] `scripts/agents/build-soul-runtime.sh` will regenerate all provider artifacts, and tests will prove that every loaded runtime contains the new gate.
- [ ] Rollback tests will prove strict scanning returns before an attestation/workflow/profile is withdrawn and that retries are idempotent/race-safe.
- [ ] The authority store will pass private-root/resolved-path/ACL/symlink/atomic-journal/recovery tests, and public artifacts/logs will pass private-topology leak tests.
- [ ] T3 provider-diverse plan review and code/artifact review will report no MAJOR findings.
- [ ] [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443) will receive plan and implementation evidence comments at the correct gates.
- [ ] ACMA [#214](https://github.com/vamseeachanta/llm-wiki-acma/issues/214) will retain its current gate until this policy lands; afterward its plan may replace the legacy scan with the approved private/internal and public-egress commands.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex internal — policy/security r1 | MAJOR, addressed in revision 2 | Required composite same-manifest gates, signed immutable identity, trusted operation derivation, private control store, pinned distribution, and activation ordering |
| Codex internal — transaction/coverage r1 | MAJOR, addressed in revision 2 | Required private reporting, exact evidence semantics, cross-repo governance, idempotent journal/leases, archive drift handling, distribution and rollback |
| Codex internal — TDD/enforcement r1 | MAJOR, addressed in revision 2 | Required closed action floors, security prerequisites, deletion semantics, sentinel grammar, bypass validator, legacy-rule bijection, and runtime regeneration |
| Codex internal — policy/security r2 | MAJOR, addressed in revision 3 | Required trust roots/signature format, realizable attestation carrier, exact ruleset semantics, gate-owned publishing, JSON/dependency contract, private-store residency, and semantic bypass checks |
| Codex internal — transaction/coverage r2 | MAJOR, addressed in revision 3 | Required authoritative artifact enumeration/transport, leases on every ref write, live revocation, live visibility, mutable-metadata invalidation, private journal contract, token-coverage proof, and exact verification commands |
| Codex internal — TDD/enforcement r2 | MAJOR, addressed in revision 3 | Required full reduction/exit semantics, signature authority, semantic bypass classification, remote enforcement identity, legacy-exclusion migration, and executable acceptance commands |
| Claude | PENDING | Provider-diverse review will run on the revised, pushed artifact |
| Codex | PENDING | Provider-diverse review will run on the revised, pushed artifact |
| Gemini | PENDING | Provider-diverse review will run on the revised, pushed artifact |

**Overall result:** BLOCKED pending adversarial review and user approval.

---

## Risks and Locked Decisions

- **Profile laundering:** signed immutable identity, protected action floors, trusted entrypoint derivation, and required-check evidence will be required; local declaration or arbitrary surface input will not grant private posture.
- **Security confusion:** disclosure skip and secret/privacy/IP/residency checks will be separate component evidence but one composite decision over the same manifest.
- **Private outward leakage:** operation and destination evidence, not repository visibility or caller input, will control public-egress scanning.
- **Third-party IP:** clean-room tripwires will move to targeted import/ingest gates, not disappear.
- **Private topology in public governance:** exact repository identity, workflow, and PR evidence will remain private; public artifacts will expose counts only.
- **Partial rollout:** archived, failed, unavailable and unobserved states will appear in aggregate counts; no N/N claim will be made without paginated live enumeration and one verified disposition per observed node ID.
- **Distribution drift:** local zipapp digest and SHA-pinned CI workflow will be cross-checked; sibling resolution and mutable refs will not be accepted.
- **Rollback gap:** strict disclosure scanning will be restored before revoking replacement controls.
- **Locked user decision:** private at-rest/internal commits will skip legal deny-pattern scanning after this policy is approved and implemented.
- **Out of scope:** changing repository visibility, unarchiving repos, publishing private data, or weakening secret/private-key controls.

---

## Complexity: T3

T3 - this changes a universal hard gate, introduces a policy engine, repairs multiple enforcement paths, and rolls policy across 26 active private repositories with provider-diverse review.
