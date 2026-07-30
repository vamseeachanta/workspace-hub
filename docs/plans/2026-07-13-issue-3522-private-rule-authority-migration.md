# Plan for #3522: Private Legal-Rule Authority Migration

> **Status:** plan-review (awaiting explicit user approval)
> **Complexity:** T3
> **Date:** 2026-07-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3522
> **Client:** N/A
> **Lane:** lane:codex
> **Execution:** two separately approved rollout phases; isolated single writer
> **Review artifacts:** `scripts/review/results/2026-07-13-plan-3522-{claude,codex,gemini}-rN.md`

---

## Resource Intelligence Summary

### Existing repo code

- `.legal-deny-list.yaml` has 23 pattern records, 14 exclusions, and nine
  reachable revisions from 2026-02-03 through 2026-07-02. Values were inspected
  only privately and will not be repeated in this public plan or reviews.
- `scripts/legal/legal-sanity-scan.sh:108-179` reads public YAML patterns and
  prints matching paths/lines. It has no opaque registry, sealed map, or history
  audit and skips errors/large inputs in legacy modes.
- `scripts/legal/check-client-pii.py` and `redact-client-pii.py` already source a
  separate untracked/gitignored client map and withhold matched values. Their 21
  synthetic tests do not cover arbitrary bytes or generic authority rollback.
- `.github/workflows/legal-client-pii-gate.yml` materializes a secret but degrades
  open if absent and publicly names a reversible private-source location.
- Live `protect-main` evidence shows deletion/non-fast-forward protection but no
  required status check; a new workflow alone cannot claim merge prevention.

### Standards and boundaries

- `docs/standards/CONTROL_PLANE_CONTRACT.md` routes schemas/policy/tools to Git;
  pattern bytes, keys, anchors, manifests, mirrors, and reports remain private.
- `.claude/rules/patterns.md` places CI at Level 2 and hooks at Level 3. #3522
  owns authority/current-tree/history assessment; #3521 owns staged attestation;
  #3398 owns later hook adoption.
- Universal legal/security rules require no secrets, hostile-input validation,
  value-withholding logs, legal scan passage, and explicit owner gates for
  irreversible or external-state transactions.

### Documents consulted

- [#3522](https://github.com/vamseeachanta/workspace-hub/issues/3522) owns private
  migration/history disposition; [#3521](https://github.com/vamseeachanta/workspace-hub/issues/3521)
  is blocked on the exact codec and anti-rollback authority.
- Closed [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095),
  [#3099](https://github.com/vamseeachanta/workspace-hub/issues/3099), and
  [#3169](https://github.com/vamseeachanta/workspace-hub/issues/3169) establish
  external client maps and metadata scans but not generic raw-byte authority.
- `docs/plans/2026-06-16-issue-3169-pii-guard-commit-msg-pr-body.md` supplies the
  synthetic/value-withholding precedent.
- Drive query `legal scanner private rule map` returned five unrelated results
  across six indexes; two indexes were unreachable and three stale.

No wiki or engineering standard applies. Required reproduction is intentionally
non-content-bearing: tracked pattern/revision counts prove the storage class
without republishing values. Verified 2026-07-13: #3521/#3522 OPEN
`status:needs-plan`; #3095/#3099/#3169 CLOSED; private local client map untracked
and ignored; related legal/enforcement baseline 47 passed. Source count is 10+.

### Gaps

- No canonical registry/map/policy/manifest codecs or anti-rollback anchor.
- No strict tree/history/GitHub-surface assessment or private coverage manifest.
- No structural protection against force-adding encoded authority secrets.
- No safe CI bootstrap, fork-oracle boundary, or enforced required check.
- No owner transaction for deletion-diff exposure or history disposition.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan / normative contract | this file; `docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md` |
| Schemas | `schemas/legal-rule-{registry,map,policy,authority-manifest,active-anchor,generation-ledger,complete}.schema.json` |
| Public authority | `config/legal-rule-{registry,authority-policy}.json` |
| CLI/package | `scripts/legal/manage_rule_authority.py`; `scripts/legal/rule_authority/*.py` |
| Tests | `scripts/legal/tests/test_rule_authority_{codec,seal,audit,workflow}.py` |
| Trusted workflow | `.github/workflows/legal-rule-authority-gate.yml` |
| Legacy policy | `.legal-deny-list.yaml` |
| Docs | `.claude/docs/legal-rule-authority.md`; `.claude/docs/client-pii-prevention.md` |
| Private-only | map, manifest, key, anchor, mirror, reports, generation ledger |
| Index/reviews | `docs/plans/README.md`; `scripts/review/results/...3522...` |

## Deliverable

Phase A will establish reviewed canonical authority tooling, a protected trusted
workflow, and verified enforcement without migrating values. A separate owner-
approved Phase B will seal/migrate the private rules, prove the proposed tree and
public metadata clean, and create an owner-only reachable-exposure assessment.

## Normative Design

`docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md` freezes:

- canonical JSON byte codecs and synthetic golden HMAC vectors;
- authenticated generation ledger, fresh UUID/generation, active anchor, and
  dual CURRENT/PENDING slots that reject rollback and isolate migration cutover;
- structural scanning for encoded map/manifest/key/anchor artifacts;
- retained-dirfd private mirror/report contracts and rc0/1/2/3/4;
- exact Git ref/raw-object and paginated GitHub-surface coverage with reverse
  reachability and explicit unknown/provider residuals;
- fork constant-response/no-secret behavior and immutable trusted tooling;
- two-phase bootstrap, protected environment/CODEOWNERS/ruleset readback, and
  the separate owner acceptance of unavoidable deletion-diff re-exposure.

Actual history rewriting, force-pushing, cache/provider requests, ref deletion,
credential rotation, or collaborator coordination require a separate issue,
transaction preview, and explicit owner approval. #3522 will remain open until
the owner records an approved follow-on or residual-history decision.

## Files to Change

| Phase | Action | Path |
|---|---|---|
| A | Create | four schemas; public registry/policy; CLI/package; synthetic tests |
| A | Create | trusted workflow and authority operator documentation |
| A | Modify | `docs/plans/README.md`; CODEOWNERS/ruleset transaction preview |
| B | Modify | `.legal-deny-list.yaml` only after replacement enforcement is live |
| B | Modify | existing workflow/docs to remove reversible private-source references |
| B | External | seal/provision bundle, key, anchor; private mirror/API audit/report |

Phase A will not remove legacy protection, handle real private values, provision
secrets, or claim prevention. Phase B will be a separately reviewed branch/PR
based on the live Phase A tool SHA.

## TDD Test List

| Test | Verification |
|---|---|
| `test_complete_codec_golden_vectors` | Exact registry/policy/map/manifest/MAC bytes interoperate. |
| `test_codec_rejects_hostile_inputs` | Duplicate/unknown/bad UUID/base64/order/ASCII/size inputs reject silently. |
| `test_valid_bundle_rollback_rejects` | Old valid bundle fails against anchor and authenticated ledger. |
| `test_reseal_and_revision_reuse_reject` | Genesis/append/rotation require exact ledger tip+1 and new UUID. |
| `test_structural_secret_artifacts_reject` | Force-added map/manifest/key/anchor under arbitrary names blocks. |
| `test_private_filesystem_contract` | Executable Git modes, credential-free stable-dirfd fetch, report COMPLETE integrity. |
| `test_tree_raw_object_metadata` | Paths/blobs/raw commit/tag/ref bytes scan without checkout. |
| `test_history_ref_snapshot_and_edges` | All advertised/PR refs, drift, and every reverse reachability edge. |
| `test_github_surface_coverage_matrix` | Accessible bytes, archives, drift/pagination/caps and residual statuses. |
| `test_public_output_allowlist` | Errors, stdout/stderr/job summary leak no locators or sensitive fragments. |
| `test_fork_constant_result_no_oracle` | Fork exits before secret access/data scan with constant result. |
| `test_same_repo_trusted_object_scan` | Immutable base tool scans inert full-OID PR objects only. |
| `test_ci_promotion_boundary` | Pinned reusable workflow owns Environment; caller gets no secrets. |
| `test_ruleset_readback` | Required check and direct-update/bypass restrictions match preview. |
| `test_dual_slot_cutover` | Concurrent CURRENT/PENDING, exact-head selection, CAS promotion/rollback. |
| `test_fork_maintainer_promotion` | Fork never scans/merges; independent privately cleaned same-repo PR can pass. |
| `test_legacy_enforcement_until_cutover` | Legacy private rules remain until active replacement passes. |
| `test_existing_pii_regression` | Existing 21 tests and behavior remain green. |

## Implementation Sequence

1. Add RED canonical codec, golden-vector, anti-rollback, structural-secret, and
   hostile private-filesystem tests; implement schema/model/seal/verify modules.
2. Add RED raw Git/GitHub coverage, reverse-edge, output-withholding, and cap
   tests; implement tree/history/API audit and private COMPLETE transactions.
3. Add RED pinned-reusable/fork/dual-slot/promotion/ruleset workflow tests;
   implement Phase A secret-free caller/workflow, docs, and synthetic authority.
4. Run exact acceptance, T3 code review, and present Phase A branch/PR plus
   protected-environment/CODEOWNERS/ruleset preview for owner approval.
5. After Phase A merges, verify the immutable live tool SHA and external-state
   readback, then prepare a private Phase B preview. Stop for distinct owner
   approval of secrets, active anchor, deletion-diff exposure, and migration PR.
6. Under that approval, seal/provision, run strict base-tool proposed-tree audit,
   migrate current policy, and retain all legacy enforcement until replacement
   required check passes.
7. Run fresh private mirror/GitHub-surface audit; deliver private COMPLETE report
   and generic public status. Route rewrite/rotation/provider work to a separately
   approved follow-on.
8. Run T3 artifact review for each phase. Any authority-byte change reseals,
   increments generation/revision, and reruns review/owner gate.

## Acceptance Criteria

- [ ] RED evidence precedes each Phase A implementation slice.
- [ ] Normative exact commands and hermetic rc0/1/2/3/4 fixtures pass.
- [ ] Canonical codecs, complete golden vectors, active-anchor rollback, revision
      reuse, structural forced-add, and filesystem failure tests pass.
- [ ] Private inputs/outputs remain external 0600 under retained 0700 parents;
      public output satisfies the strict allowlist under every error class.
- [ ] Phase A code review has no MAJOR; no legacy value/protection is removed.
- [ ] Owner separately approves and live API verifies the environment,
      CODEOWNERS, required check, direct-update/bypass restrictions, and tool SHA.
- [ ] Forks are constant-fail/nonmergeable and receive no secret/data scan;
      maintainer candidates are privately cleaned into independent same-repo PRs.
- [ ] CURRENT/PENDING concurrency, exact-head routing, and owner CAS promotion/
      rollback pass without disrupting ordinary old-base checks.
- [ ] Owner separately accepts the exact Phase B deletion-diff visibility and
      sealed migration preview before a migration branch/PR is created.
- [ ] Proposed tree/raw metadata audit returns zero findings under the live base
      tool before legacy values are removed.
- [ ] Private history/API coverage manifest records every surface as scanned,
      no-access, provider-follow-up, or unknown-residual—never unsupported clean.
- [ ] Existing 21 tests and 47-test baseline plus focused/Ruff/compileall/schema/
      function/file/no-abs/legal/workflow checks pass.
- [ ] Each implemented phase receives a non-sensitive issue comment and T3
      artifact review. No self-approval, merge, close, force-push, or rewrite.

## Adversarial Review Summary

| Provider | Verdict | Findings |
|---|---|---|
| Claude r1 | MAJOR | rollback, codecs, CI bootstrap/trust, unenforced gate, history, forced secrets, filesystem, commands |
| Codex r1 | MAJOR | same consensus plus fork oracle, promotion boundary, reverse edges, diff re-exposure, interim gap |
| Gemini r1 | UNAVAILABLE | noninteractive OAuth rc41 |
| Claude r2 | MAJOR | immutable workflow/fork path, CLI, downloadable coverage, artifact classes, Git modes, protection readback, anchor/ledger |
| Codex r2 | MAJOR | same consensus plus dual-slot cutover, COMPLETE integrity, secret size, exit precedence |
| Gemini r2 | UNAVAILABLE | noninteractive OAuth rc41 |
| Main session r3 | RESOLVED | every r2 finding is mapped in the inline-resolution artifact; no r3 dispatch per routing rule |

**Overall:** plan-review. R1/r2 defects are incorporated through the mandatory
inline r3 resolution. Explicit user approval is required before Phase A only;
Phase B and every external-state/irreversible transaction retain separate gates.
No agent may apply `status:plan-approved` or create an approval marker.

## Risks and Open Decisions

- Deleting an already-public value necessarily exposes it again in a public diff;
  the owner must choose Phase B migration versus prior history remediation.
- Provider caches, deleted refs, inaccessible forks, and expired artifacts remain
  residual/unknown even after Git rewrite.
- Secret-bearing environment approval creates deliberate per-run owner friction.
- #3521 remains draft until Phase B authority artifacts merge and are pinned.

## Complexity: T3

This spans public security, private authority, Git/GitHub exposure inventory,
CI secret boundaries, live branch protection, and irreversible follow-on risk.
