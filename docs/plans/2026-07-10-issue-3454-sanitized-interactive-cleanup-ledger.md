# Plan for #3454: Publish a sanitized interactive cleanup ledger and prune stale local permission residue

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3454
> **Private child:** https://github.com/vamseeachanta/aceengineer-admin/issues/37
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** planning/review `parallel-readonly`; implementation `single-lane`
> **Schema:** `local-analysis-cleanup/public-projection/v1`
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3454-{claude,codex,gemini,disagreement}.md`; `...-codex-inline-r1.md`

---

## Resource Intelligence Summary

### Existing repo code

- `docs/reports/2026-07-10-local-analysis-cleanup-flow-design.html` defines the user-approved local/public/private boundary, five dispositions, artifact locations, and fail-closed behavior. Its approved blob SHA-256 is `5fe4cb2ad532024f9983e2027744b7b577f3155a4467cf40f1aae199edc2cf01`.
- `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md` defines origin/residue/archive checks, per-action approval, race checks, a cleanup lock, trash stage, verification, and the public Markdown handoff. Its TSV/checksum examples are not arbitrary-name-safe and are tracked separately by [#3458](https://github.com/vamseeachanta/workspace-hub/issues/3458).
- `docs/sessions/2026-05-19-mnt-analysis-cleanup.md` and `docs/sessions/2026-05-24-mnt-local-analysis-conservative-cleanup.md` provide transaction precedents but publish exact paths, so they cannot be copied into this public run.
- `scripts/legal/check-client-pii.py --strict`, `scripts/workflow/render_completeness_html.py`, `tests/workflow/test_render_completeness_html.py`, `docs/reports/sessions/manifest.json`, and `scripts/build_pages.py` provide value-withholding, canonical round-trip, and Pages patterns.
- The machine-local settings JSON is valid, with eight allow entries and exactly two stale candidates. Raw values remain withheld. The root is `fuseblk`; chmod does not change its reported `0777` modes, so mount/ACL hardening belongs to [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456).
- No #3454 plan, public cleanup schemas, sanitized-bundle validator/renderer, guarded permission editor, or approval marker exists on live `origin/main`.

### Standards and wiki

Not applicable. This issue will not touch engineering calculations, standards-derived constants, data pipelines, or wiki content.

### Documents and issues consulted

- [#3454](https://github.com/vamseeachanta/workspace-hub/issues/3454) defines the public outcome and local permission edit.
- Private [aceengineer-admin #37](https://github.com/vamseeachanta/aceengineer-admin/issues/37) owns exact ledger instances, exact sidecars, and every live mutation.
- [#2572](https://github.com/vamseeachanta/workspace-hub/issues/2572) is the persistent sanitized milestone sink.
- [#3453](https://github.com/vamseeachanta/workspace-hub/issues/3453), [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456), and [#3458](https://github.com/vamseeachanta/workspace-hub/issues/3458) own scheduled cleanup, mount permissions, and arbitrary-name manifests respectively.
- `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, `docs/architecture/report-publication-gates.md`, and `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md` require control-plane ownership, durable ledgers, publication gates, empirical sibling coverage, and private-to-public promotion.
- The mandatory drive-index query for `local-analysis cleanup ledger permissions` timed out twice before returning usable JSON. Drive coverage is **UNAVAILABLE**, not “no relevant files”; no ad-hoc drive crawl substitutes for it.

### Gaps identified

- A versioned public projection schema and bounded public modules will need to be built.
- The private child will need its own exact schema, validator/tests, write-ahead events, legal/residency policy, and pinned dependency on the reviewed public tool commit.
- Permission editing will need optimistic concurrency, same-mount durability probes, value-withholding authority input, and an explicit residual TOCTOU boundary.
- Cross-repo push/comments will need non-self-referential A→B→C receipts and reconciliation.
- The original 124-directory observation has no immutable manifest. It will remain `historical_observation`; only a fresh `baseline_v1` will be authoritative.

### Evidence (embedded verification)

**Resource-intel base snapshot** (remote refs verified 2026-07-10T21:58:26-05:00):

```text
workspace-hub origin/main = 83eba19e7c445597208660acf6abe814371fe00e
aceengineer-admin origin/main = 1b14a3fae186362acf6a2364e84754e7d404ba74
```

Immediately before review dispatch and push, a separate attestation will require the plan branch parent and fetched `origin/main` to equal the then-live remote SHA. Later unrelated `main` movement will be reported as drift rather than rewriting this historical snapshot silently.

**Issue state** (verified 2026-07-10): #3454 is OPEN at `status:needs-plan`; #37 is OPEN without plan-lifecycle labels; #2572 remains OPEN; #3453, #3456, and #3458 are OPEN at `status:needs-plan`.

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

---

## Parent/Child Ownership and Dependency Lock

| Owner | Exclusive responsibility |
|---|---|
| Public #3454 | Public projection and permission-authority schemas; reusable synthetic-tested permission editor; sanitized-bundle validation; public Markdown/HTML rendering; public leakage/legal/Pages checks; pure/stateless publication-reconciliation library. |
| Private #37 | Exact ledger schema/instances; fresh baseline; exact evidence and WAL; private projection export; persistent publication state and external-action wrapper; every live `--apply` invocation; every manual folder transaction; private pre/post-action commits and pushes. |

Private execution will remain blocked until the public plan is pushed/approved, Phase A tooling passes code review, and a public implementation commit is pushed. #37 will pin that commit, tool blob hashes, both public schema blob hashes/versions, and its wrapper will refuse any mismatch. Workspace-hub will consume only a sanitized runtime bundle and will never read the private ledger. The public library will calculate deterministic reconciliation observations/actions without persisting state or calling GitHub; the private wrapper alone will read/write receipts and perform authorized remote/comment actions.

Public approval requires user-created `status:plan-approved` plus `.planning/plan-approved/3454.md`. Private approval requires provisioned canonical lifecycle labels plus user-created `.planning/plan-approved/37.md`, each binding the reviewed plan commit. No agent will create or self-apply approval.

---

## Versioned Public Contracts

Public #3454 will own `local-analysis-cleanup/public-projection/v1` and `local-analysis-cleanup/permission-edit-authority/v1`. Their schema blobs and implementing tool blobs will be independently pinned by private #37.

Canonical bytes will be UTF-8/NFC JSON with sorted keys, separators `,`/`:`, no NaN, and one trailing newline. Digests will use SHA-256 with domain prefix `local-analysis-cleanup-v1\0`.

| Field | Contract |
|---|---|
| `run_id` | UUIDv4; immutable |
| `alias` | `la1_` + 20 random base32 chars; run-scoped, collision-checked, tombstoned, never reused |
| `class` | `canonical_repo|linked_worktree|standalone_clone|runtime_config|system_managed|preservation|data|cache|scratch|unknown` |
| `disposition` | `keep|delete|relocate|archive|defer`; independent of transaction outcome |
| `transaction_state` | `discovered|evidence_ready|decision_recorded|preflight_verified|wal_pushed|executing|verified|deferred|failed|rollback_pending|rolled_back` |
| `reason_code` | `canonical_active|active_worktree|system_managed|machine_runtime|unique_evidence|redundant_verified|reconstructible|relocate_by_contract|insufficient_evidence|user_directive|other_private` |
| `size_bucket` | `empty|lt_1m|m1_99|m100_999|g1_9|gte_10g|unknown` |
| `age_bucket` | `lt_1d|d1_7|d8_30|d31_90|gt_90d|unknown` |
| `repo_state` | `not_git|clean_synced|clean_diverged|dirty|unmerged|unverified` |

The permission-authority schema will require its schema ID/version, algorithm version, raw before-file SHA-256, exactly two domain-separated target commitments, unchanged non-allow-subtree digest, ordered retained-allow-sequence digest, target-set digest, user approval reference, exact issuance/expiry timestamps, and expected target absence/registration state. It will forbid raw target values and unknown fields.

The folder audit predicate will be immediate entries for which `is_dir(follow_symlinks=False)` is true. Files, symlinks, broken symlinks, permission errors, and timeouts will be recorded as root anomalies but excluded from the folder count. Inode data on FUSE will be advisory; mount identity/remount ambiguity will defer private remapping.

Public timestamps will be date-level or milestone ordinals. Public hashes will cover projection/prepared/verification bytes only—never names or paths. Exact sizes, timestamps, branches, remotes, and free text stay private.

Private token policy will classify values as `confidential|approved_public|common_nonidentifying`. Confidential values will fail in boundary, case-folded, HTML/JSON escaped, URL-encoded, filename, comment, and attribute forms. Common tokens will fail only in path-aware combinations. Any allow decision will bind one token/encoding/artifact instance; no directory-wide exemption.

---

## Transaction and Publication States

Folder actions will remain manual, one-at-a-time commands under the cleanup skill; no automatic delete/relocate executor will be added. Private tooling will prepare/push a write-ahead event, verify freshness, and reconcile incomplete events before another action.

Publication will use:

`draft → validated_local → private_committed(A) → private_pushed(A) → public_committed(B) → public_pushed(B) → comments_partial → comments_complete → private_receipt(C) → published`.

Commit A binds `run_id` and projection digest. B references A/run/digest. Additive receipt C references B and comment URLs. Hidden comment marker `<!-- cleanup:<run_id>:<revision>:<sink> -->` plus body digest, ASCP serialization, read-before-create, and post-create reconciliation will make retries observable without claiming native GitHub idempotency.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan/design | `docs/plans/2026-07-10-issue-3454-sanitized-interactive-cleanup-ledger.md`; `docs/reports/2026-07-10-local-analysis-cleanup-flow-design.html` |
| User approval marker | `.planning/plan-approved/3454.md` (user-created after review) |
| Public schemas | `schemas/local-analysis-cleanup/public-projection-v1.schema.json`; `schemas/local-analysis-cleanup/permission-edit-authority-v1.schema.json` |
| Public package | `scripts/operations/local_analysis_cleanup/{schema.py,projection.py,privacy.py,render.py,publication.py,cli.py}` |
| Permission editor | `scripts/operations/prune_local_claude_permissions.py` |
| Public tests | `tests/operations/test_local_analysis_cleanup_public.py`; `tests/operations/test_prune_local_claude_permissions.py` |
| Skill routing test/update | `tests/skills/test_mnt_analysis_cleanup_visibility_routing.py`; `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md` |
| Public outputs | `docs/sessions/2026-07-10-mnt-analysis-cleanup.md`; `docs/reports/sessions/2026-07-10-mnt-analysis-cleanup.html`; `docs/reports/sessions/manifest.json` |
| Private plan/schema | `aceengineer-admin:docs/plans/2026-07-10-issue-37-local-analysis-cleanup-ledger.md`; `aceengineer-admin:schemas/local-analysis-cleanup/issue-37-ledger-v1.schema.json` |
| Reviews/completeness | `scripts/review/results/2026-07-10-plan-3454-*.md`; `docs/reports/2026-07-10-3454-completeness.html` |

---

## Deliverable and Pseudocode

A reviewed public toolkit will validate/render only sanitized bundles, guard the two-rule local edit, and publish a recoverable public record while private #37 exclusively records and executes the interactive run.

```text
validate_bundle(bundle):
    validate public-projection/v1 and canonical digest
    reject unknown fields and private-detail shapes
    verify alias uniqueness, tombstones, counts, buckets, and state enums

render_public(bundle):
    embed identical canonical projection in Markdown and escaped self-contained HTML
    emit deterministic comment bodies with marker/body digest
    round-trip both artifacts before publication

guarded_permission_replace(settings, authority_fd, runtime_dir):
    require authority schema/version, user approval, before digest, and two target commitments
    verify quiescence, target absent/unregistered, O_NOFOLLOW fd/path identity, and digest
    probe same-fuse mount rename, file fsync, directory fsync, and cleanup on synthetic bytes
    create O_EXCL randomized adjacent temp; validate/fsync; inject final race hook; recheck
    os.replace, fsync parent, verify after digest and retained sequence; clean every residue
    call this optimistic guarded replacement, document residual non-cooperating-writer TOCTOU
    fail to user-performed edit if the same-mount durability probe is not fully green

plan_publication_reconciliation(observation):
    compare expected and observed remote OIDs without force
    validate supplied remote/reflog evidence after rejection
    return one deterministic next action from supplied comment-marker observations
    never persist receipts, call GitHub, or mutate private/public state
```

Rollback in `/run/user/<uid>` will cover process failure only. Crash safety will rely on validated temp + atomic rename + successful file/parent fsync; interruption tests will cover before replace, after replace, and before verification. No persistent adjacent rollback will be retained on fuseblk.

**Decision D1 — adjacent raw-temp exposure.** Recommended/default: **REJECT** adjacent raw-temp exposure and use a user-performed edit or defer the permission change until [#3456](https://github.com/vamseeachanta/workspace-hub/issues/3456) resolves the mount posture. Alternative: **ACCEPT** the documented minimum-lifetime exposure and residual race only after the same-mount probes pass. Plan approval must explicitly select D1; silence means REJECT and cannot authorize the guarded editor.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `schemas/local-analysis-cleanup/{public-projection-v1,permission-edit-authority-v1}.schema.json` | Freeze both public interfaces. |
| Create | `scripts/operations/local_analysis_cleanup/*.py` | Keep schema/projection/privacy/render/publication/CLI responsibilities bounded. |
| Create | `scripts/operations/prune_local_claude_permissions.py` | Supply the reusable guarded editor; private #37 alone will invoke live apply. |
| Create | `tests/operations/test_local_analysis_cleanup_public.py`; `tests/operations/test_prune_local_claude_permissions.py` | Drive public behavior test-first. |
| Update | `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md`; `tests/skills/test_mnt_analysis_cleanup_visibility_routing.py` | Route exact evidence away from public repos. |
| Create/update | Public plan/design/session/report/manifest/review/completeness paths in the Artifact Map, including `docs/reports/2026-07-10-local-analysis-cleanup-verification.json` | Preserve reviewed public artifacts and a non-self-referential validation attestation. |
| Update | `docs/plans/README.md` | Index the draft/review state. |

No public code will read the private ledger. No automatic folder executor, raw archive, raw settings copy, root-settings generator, mount change, scheduled-cleanup fix, or #3458 manifest redesign will be added.

---

## TDD Test List

Tests will be written first with synthetic-only private values:

| Test | Verification |
|---|---|
| `test_public_schema_contract` | Both schema IDs/versions, missing/unknown fields, enums, duplicate/reused aliases, count drift, authority shape, and blob mismatch reject. |
| `test_public_round_trip` | Bundle/Markdown/HTML share canonical bytes/digest; markup escapes; no network assets. |
| `test_token_policy` | Confidential/common/public tokens, boundaries, substrings, comments, attributes, filenames, Unicode, and encodings behave without value logs. |
| `test_permission_authority` | Missing/duplicate/third targets, stale authority, reappeared/registered targets, symlinks, fd/path mismatch, and non-quiescence reject. |
| `test_fuse_guarded_replace` | Rename, file/parent fsync, residue cleanup, pre-replace race, and interruption boundaries verify on the same mount. |
| `test_permission_value_withholding` | Six unrelated values/non-allow subtree remain; stdout/stderr/attestations/repo/comments contain no raw value. |
| `test_publication_recovery` | A→B→C, remote mismatch, push failures, state crashes, partial comments, concurrent retry, and reconciliation recover. |
| `test_visibility_routing` | Exact sidecars require a private sink; #3458 retains arbitrary-name format ownership. |
| `test_pages_output` | Pages builds/scans only the sanitized report. |
| `test_private_pin_gate` | Private schema/commit/blob mismatch blocks rendering. |
| `test_validation_attestation` | Nonzero subject-file blobs verify; the attestation excludes itself, and private C records public B's pushed identity. |

---

## Implementation Sequence

1. Both plans will be rebased on the authoritative bases, pushed, re-attested, reviewed, and user-approved. Private lifecycle labels/marker will be provisioned before implementation.
2. Phase A will land public schemas/modules/tests and complete code review. The private plan will pin the landed commit/blob digests.
3. #37 will create `baseline_v1`; the 124 and 128 counts will remain incomplete historical observations, not reconstructed deltas.
4. For the permission edit and every later mutation, #37 will validate approval/preflight JSON, commit/push pre-action WAL, verify remote OID, reacquire an execution ASCP claim, rerun freshness checks, apply manually or via the pinned permission editor, then commit/push result evidence.
5. Private export will write a sanitized-only runtime bundle under the verified user-private runtime directory. Public code will consume only that bundle; private validation will rescan final public bytes.
6. Private A will push before public B. Scanned comments will post last. Private C will record B/comment receipts.
7. The interactive folder audit will resume one folder at a time. Any unknown Git/process/residue/destination state will defer.
8. Code/artifact review, completeness evidence, temporary-worktree removal, and the pre-completion cleanup audit will precede closeout.

---

## Verification Commands

```bash
set -euo pipefail
: "${LEGAL_CLIENT_MAP:?must point to a readable private client map}"
test -f pyproject.toml
test -f scripts/legal/check-client-pii.py
test -f scripts/build_pages.py
test -f scripts/enforcement/check-no-abs-paths.sh
test -r "$LEGAL_CLIENT_MAP"
timeout 600 uv run pytest tests/operations/test_local_analysis_cleanup_public.py \
  tests/operations/test_prune_local_claude_permissions.py \
  tests/skills/test_mnt_analysis_cleanup_visibility_routing.py -q

RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
test -d "$RUNTIME_DIR"
EXPECTED_PUBLIC_SUBJECT_MANIFEST="$RUNTIME_DIR/issue-3454-expected-subject.nul"
EXPECTED_PUBLIC_FINAL_MANIFEST="$RUNTIME_DIR/issue-3454-expected-final.nul"
ACTUAL_PUBLIC_MANIFEST="$RUNTIME_DIR/issue-3454-actual.nul"
timeout 180 uv run python -m scripts.operations.local_analysis_cleanup.cli expected-files \
  --run-date 2026-07-10 --package public-b --subject-only \
  --output "$EXPECTED_PUBLIC_SUBJECT_MANIFEST"
timeout 180 uv run python -m scripts.operations.local_analysis_cleanup.cli expected-files \
  --run-date 2026-07-10 --package public-b \
  --output "$EXPECTED_PUBLIC_FINAL_MANIFEST"
timeout 180 uv run python -m scripts.operations.local_analysis_cleanup.cli write-validation-attestation \
  --subject-manifest "$EXPECTED_PUBLIC_SUBJECT_MANIFEST" \
  --output docs/reports/2026-07-10-local-analysis-cleanup-verification.json
timeout 180 git add -- docs/reports/2026-07-10-local-analysis-cleanup-verification.json
timeout 180 git diff --cached --name-only --diff-filter=ACMR -z | sort -z > "$ACTUAL_PUBLIC_MANIFEST"
cmp "$EXPECTED_PUBLIC_FINAL_MANIFEST" "$ACTUAL_PUBLIC_MANIFEST"
timeout 180 uv run python -m scripts.operations.local_analysis_cleanup.cli verify-validation-attestation \
  --index docs/reports/2026-07-10-local-analysis-cleanup-verification.json \
  --subject-manifest "$EXPECTED_PUBLIC_SUBJECT_MANIFEST"
test -s "$EXPECTED_PUBLIC_SUBJECT_MANIFEST"
mapfile -d '' -t public_files < "$EXPECTED_PUBLIC_FINAL_MANIFEST"
timeout 300 uv run python scripts/legal/check-client-pii.py --strict --map "$LEGAL_CLIENT_MAP" "${public_files[@]}"
timeout 300 bash scripts/legal/legal-sanity-scan.sh --diff-only
timeout 600 uv run python scripts/build_pages.py
timeout 300 uv run python -m scripts.operations.local_analysis_cleanup.cli verify-public public/
timeout 300 bash scripts/enforcement/check-no-abs-paths.sh \
  scripts/operations/local_analysis_cleanup/*.py \
  scripts/operations/prune_local_claude_permissions.py
timeout 180 git diff --cached --check
```

Verification will run only from a current-base full checkout containing every named path. Every bounded command will fail closed, including timeout exit 124. The validation attestation will record only the nonzero subject-file path/blob map and digest, base SHA, scanner script blob hashes, generated-output scan result, and exit codes. It will exclude itself and will not claim its own blob/tree/commit identity. The final manifest will include the staged attestation, and the read-only index verifier will reject a stale or self-referential attestation. Private receipt C will record public package B's commit/tree/verified remote OIDs. The legal scanner will be described accurately as scanning all tracked `git diff HEAD` changes; final-manifest equality will reject extra/missing files.

---

## Acceptance Criteria

- [ ] Public/private plans, both public schema revisions, ownership, dependency pins, approval labels/markers, and reviewed commits will match exactly.
- [ ] Public code will never read the private ledger; only private code will export the sanitized runtime bundle and invoke live mutation.
- [ ] A fresh folder-only `baseline_v1` and root anomalies will replace any claim of reconstructing the 124→128 history.
- [ ] Plan approval, disposition, permission authority, and destructive-action authority will remain separate.
- [ ] The permission edit will use domain-separated commitments through a private FD, repeat target checks, pass same-fuse durability probes, preserve unrelated data, and disclose residual TOCTOU.
- [ ] Every live mutation will have a validated, pushed pre-action WAL and a pushed post-action result; push failure will block mutation.
- [ ] Private A → public B → private C and partial-comment recovery will verify without circular hashes or force push.
- [ ] Public reconciliation code will remain pure/stateless; private #37 alone will persist state and perform authorized remote/comment actions.
- [ ] Public projection/HTML/Markdown/comments/generated Pages will contain only allowed fields/buckets/digests and will pass non-vacuous scans.
- [ ] Public validation will bind a nonzero subject-file map without self-reference; private receipt C will bind the pushed public package identity.
- [ ] Folder actions will remain manual, explicit, no-overwrite transactions under #37 and the cleanup skill.
- [ ] #2572 will receive sanitized milestones and remain open; #3453/#3456/#3458 will remain separate.
- [ ] T3 code/artifact review, completeness, cleanup audit, and temporary-worktree removal will pass before closure.

---

## Adversarial Review Summary

| Provider | Verdict | Result |
|---|---|---|
| Claude CLI | UNAVAILABLE | rc=137 timeout/no stderr |
| Codex CLI | UNAVAILABLE | rc=124 stdin regression on 0.144.1 |
| Gemini CLI | UNAVAILABLE | no non-interactive auth |
| Codex inline r1 | MAJOR | 10 blockers; ownership/schema/CAS/WAL/publication/scan defects revised in v2 |

**Overall result:** FAIL — draft remains blocked pending fresh adversarial review on a pushed, current-base commit. Provider unavailability is not consensus.

---

## Risks and Open Questions

- **Residual settings race:** advisory quiescence cannot stop a non-cooperating writer. Failure to obtain green same-mount probes/quiescence will require user-performed edit or defer.
- **Decision D1 — mount exposure:** fuseblk chmod is ineffective and #3456 owns durable hardening. Recommended/default REJECT will select user-performed edit or defer; explicit ACCEPT will authorize the guarded-editor route only after same-mount probes pass.
- **Provider outage:** fresh T3 review cannot complete until provider capacity/auth works; no label will advance on unavailable artifacts alone.
- **Root drift:** a new execution claim, fresh baseline, per-action remote checkpoint, and preflight will fence concurrent work.
- **Open:** D1 must be selected explicitly with plan approval; no selection defaults to REJECT.

---

## Complexity: T3

**T3** — public/private/machine-local state, a versioned security boundary, guarded configuration mutation, manually executed irreversible actions, cross-repo receipts, and provider/code review require T3 treatment.
