# Plan for #3559: Immutable Hugging Face field/well HTML drill-down program

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3559
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; approved implementation `parallel-worktree`
> **Round 1 input commit:** `06216c5c7d48b217ae7b1f92ad184d6eeb4ab2c5`
> **Round 2 input commit:** `a703e619c14fde5aea003010e3479b80f15e1d19`
> **Round 3 input commit / plan blob:** `8aeb690c7f6e1aa96f4c84accb78e734516d0a67` / `14b6cdda9782dbbad174a098a8567af9aa351231`
> **Round 1 artifacts:** `scripts/review/results/issue-3559-round-1/2026-07-16-plan-3559-claude.md` | `...-codex.md` | `...-gemini.md`
> **Round 2 artifacts:** `scripts/review/results/issue-3559-round-2/2026-07-16-plan-3559-claude.md` | `...-codex.md` | `...-gemini.md`
> **Round 3 artifacts:** `scripts/review/results/issue-3559-round-3/2026-07-16-plan-3559-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `worldenergydata/scripts/hf_export/build_explorer_results_bundle.py` currently emits strict JSON and source-file hashes, but it will not provide the proposed relational browser manifest, exact source Git revision, legal admission, or publish receipt.
- `worldenergydata/scripts/hf_export/publish_explorer_refresh_to_hf.py` currently patches floating live Parquet and uploads only selected files. It will be replaced as an authoritative publication path by [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045).
- `worldenergydata/config/fields.yml` currently contains stable canonical identities for ten rich Lower Tertiary fields plus Buckskin. The separate 115-page FDP portfolio will not yet be identity- and well-complete.
- `worldenergydata/reports/lower_tertiary/lifecycle/_explorer.json` currently contains ten rich fields and 56 unique API-12 wells: seven fields have wells and three have none.
- `aceengineer-website/config/capabilities.yaml` currently registers independent tables without a pinned revision, manifest, relationship, selector keys, child templates, or nested routes.
- `aceengineer-website/scripts/hf-fetch.js` currently materializes at most 100 floating datasets-server rows, and `scripts/render-capabilities.js` currently displays at most 50.
- `aceengineer-website/build.js` currently deletes `dist` before validation and catches rendering failures. It will not provide transactional relational output promotion until [aceengineer-website #74](https://github.com/vamseeachanta/aceengineer-website/issues/74).

### Standards

| Contract | Status | Source |
|---|---|---|
| Issue → plan → adversarial review → user approval → TDD → code review → close | binding | `AGENTS.md`, `docs/plans/README.md` |
| Parent/child layered ownership | binding | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Parallel execution classification | binding | `docs/standards/PARALLEL_FIRST_EXECUTION.md` |
| Legal/public-egress validation | binding | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| Exact HF revision and staged acceptance precedent | reusable, not the same dataset | `docs/plans/2026-07-10-issue-3427-repository-linked-algorithm-run-datasets.md` |
| Engineering calculation standards | N/A | This parent will govern publication/rendering lifecycle, not calculations. |

### Documents consulted

- [#3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) will own the cross-layer lifecycle, terminology, V1 boundary, promotion, and rollback.
- [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) will own data identities, deterministic construction, schema, provenance, licenses, HF publication, readback, and receipt.
- [aceengineer-website #74](https://github.com/vamseeachanta/aceengineer-website/issues/74) will own pinned consumption, registry validation, parent/child templates, selectors, routes, accessibility, and deployment.
- [#3485](https://github.com/vamseeachanta/workspace-hub/issues/3485) supplies the general registry-driven capability program. Its floating datasets-server behavior will remain a compatibility path only.
- [worldenergydata #939](https://github.com/vamseeachanta/worldenergydata/issues/939) supplies the longer-term Explorer program; it will not expand V1 by implication.
- [#3560](https://github.com/vamseeachanta/workspace-hub/issues/3560) now owns the general review-harness defect where providers can inspect their own empty in-progress sinks; this plan will not claim those transient observations are final artifact state.
- Drive-index query `Hugging Face field explorer HTML templates dropdown worldenergydata` ran on 2026-07-16. It returned unrelated engineering/CAD documents and one stale missing workspace-spec path; no external drive file will govern this plan.
- No relevant LLM-wiki page was found or will be modified.

### Gaps identified

- No durable parent contract will currently bind source Git SHA, HF SHA, website pin, generated routes, deployment identity, and rollback target.
- No cross-repository state machine will currently prevent an unverified HF candidate from becoming a deployed website revision.
- No verifier will currently join the publisher receipt, HF manifest, website registry/build receipt, route counts, and production evidence.
- No parent closeout rule will currently prevent broad field-coverage claims from exceeding the manifest-ready set.

### Evidence

**Live issue state verified 2026-07-16:**

- [#3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) — OPEN, `status:needs-plan`, `lane:codex`.
- [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) — OPEN, `status:needs-plan`, `lane:codex`.
- [aceengineer-website #74](https://github.com/vamseeachanta/aceengineer-website/issues/74) — OPEN, `status:needs-plan`, `lane:codex`.
- Draft [aceengineer-website PR #73](https://github.com/vamseeachanta/aceengineer-website/pull/73) overlaps `build.js`, `config/capabilities.yaml`, and registry tests.

**Verified revisions:**

```text
worldenergydata inspected baseline: a26881d49d064ea6ae6c8200ae1a874bf944e1bb
worldenergydata live main:          090228fb4a1193e4190fc4da90644d9f40a20b5a
website origin/main:      efde01a32a8507768804649afedf06190ec618bf
live HF snapshot observed: aa94a449b5bad834f36dcac253f1aedc3a976a4c
```

### Embedded retrieval and reproduction evidence

Commands ran from the workspace root at `2026-07-16T17:20-05:00`:

```bash
gh issue view 3559 -R vamseeachanta/workspace-hub --json number,title,state,labels
gh issue view 1045 -R vamseeachanta/worldenergydata --json number,title,state,labels
gh issue view 74 -R vamseeachanta/aceengineer-website --json number,title,state,labels
```

Captured result: all three issues were `OPEN`, carried `status:needs-plan` and exactly one `lane:codex` label. Their abbreviated subjects were immutable field/well HTML program, deterministic HF browser snapshot, and pinned field-to-well website drill-down; the exact live titles retained their `feat(...)` prefixes and program suffixes.

The WED baseline used for the data inventory is now behind live `main` by 21 commits. Round 2 verified that none of those commits changed the inspected Explorer inputs. Child #1045 will nevertheless fetch and reconcile fresh `main` before its implementation starts; the baseline SHA will not be described as current authorization.

```bash
git -C aceengineer-website show origin/main:scripts/hf-fetch.js | nl -ba
git -C aceengineer-website show origin/main:scripts/render-capabilities.js | nl -ba
git -C aceengineer-website show origin/main:assets/js/capabilities-refresh.js | nl -ba
git -C aceengineer-website show origin/main:build.js | nl -ba
```

Captured excerpts: `hf-fetch.js:24-25` declared page/default caps of 100; `render-capabilities.js:113,203` declared 50 and sliced to it; `capabilities-refresh.js:17-19,193,213` used floating datasets-server with fetch/display caps 100/50; `build.js:205-209` removed and recreated `dist` before later caught build operations at lines 220 and 236.

```bash
repo=aceengineer/worldenergydata-explorer
sha=aa94a449b5bad834f36dcac253f1aedc3a976a4c
curl 'https://datasets-server.huggingface.co/rows?dataset=aceengineer/worldenergydata-explorer&config=fields&split=train&offset=0&length=1'
curl 'https://datasets-server.huggingface.co/rows?dataset=aceengineer/worldenergydata-explorer&config=fields&split=train&offset=0&length=1&revision=aa94a449b5bad834f36dcac253f1aedc3a976a4c'
curl 'https://datasets-server.huggingface.co/rows?dataset=aceengineer/worldenergydata-explorer&config=fields&split=train&offset=0&length=1&revision=0000000000000000000000000000000000000000'
```

Captured output for omitted/real/fake revisions was identical: `status=200 bytes=3928 sha256=f414935f36e1f31255c60237c3db93ff40456729c44b2fac168437fbca8f3772`. Raw README resolution returned `307` for the real SHA and `404` for the fabricated SHA. Therefore datasets-server will not prove immutability; acceptance will use raw exact-SHA artifacts with the bounded redirect contract defined by the website child.

Distinct sources: three new issues, two parent programs, one overlapping PR, three repositories, one prior architecture plan, live website/HF probes, and the drive-index search.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-16-issue-3559-field-explorer-cross-repo-program.md` |
| Human approval packet | `docs/plans/2026-07-16-field-explorer-plan-approval-packet.html` |
| Parent machine contract | `docs/architecture/field-explorer-cross-repo-contract.json` |
| Promotion/rollback runbook | `docs/governance/field-explorer-promotion-runbook.html` |
| Promotion verifier | `scripts/workflow/verify_field_explorer_promotion.py` |
| Promotion state writer | `scripts/workflow/promote_field_explorer_release.py` |
| Verifier tests | `tests/workflow/test_field_explorer_promotion.py` |
| Receipt schemas | `$defs` in `docs/architecture/field-explorer-cross-repo-contract.json` |
| Authoritative release state | `docs/reports/field-explorer/release-state.json` |
| Per-release evidence | `docs/reports/field-explorer/releases/<release-id>/` |
| Final E2E report | `docs/reports/<date>-3559-field-explorer-e2e.html` |
| Publisher implementation | owned only by [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) |
| Website implementation | owned only by [aceengineer-website #74](https://github.com/vamseeachanta/aceengineer-website/issues/74) |

---

## Deliverable

A JSON parent contract, HTML promotion/rollback runbook, and tested cross-repository verifier will enforce the lifecycle from a clean worldenergydata revision through one immutable HF snapshot, one website registry pin, generated parent/field/well HTML, production acceptance, and pin-based rollback without implementing either child repository's code.

## Lifecycle and Crosswalk

```text
P0: #3559 parent contract is reviewed and user-approved.
P1: #1045 and #74 are independently reviewed and user-approved.
P2: #1045 builds from one clean Git SHA, passes legal/schema/join gates,
    publishes one expected-parent HF commit, raw-reads it by returned SHA,
    and emits a verified receipt.
P3: #74 may build against the reviewed contract fixture; production pinning
    waits for the real #1045 receipt and for PR #73 coordination.
P4: the website registry binds dataset + HF SHA + manifest path; the parent
    verifier live-checks approval comments/labels and joins schema-valid publisher,
    manifest, registry, build, browser, deployment, route, and scan evidence.
P5: an R1→R2→R1 preview-deployment drill proves whole-snapshot rollback.
P6: a candidate-bound protected-environment approval records deploy_pending;
    production deploy and read-only smoke then record accepted or failure/rollback.
P7: both children close their own gates before parent completeness/closure.
```

| Boundary | Producer identity | Consumer binding | Evidence |
|---|---|---|---|
| Source | clean worldenergydata Git SHA | HF manifest `source_git_sha` | clean-tree attestation + source hashes |
| HF snapshot | returned immutable HF SHA | website registry `snapshot.revision` | expected-parent commit + raw readback receipt |
| Browser artifacts | safe paths + hashes/counts/schema | website staged local assets | full manifest validation |
| Field | stable `field_id` | selector, static route, panels | unique ID, separate label/slug/aliases |
| Well | stable `well_id` + `parent_field_id` | filtered selector and nested route | unique API-derived ID, exactly one parent |
| Website | website Git SHA + pinned HF SHA | Vercel deployment | build receipt, route inventory, smoke |
| Rollback | previous accepted pin | rebuilt/redeployed release | stable URLs + prior hashes/counts |

The HF manifest will not self-reference its containing HF SHA. The external publisher receipt and website registry will bind that SHA.

## V1 Coverage Boundary

V1 acceptance will discover and verify:

- 10 manifest-ready fields;
- 56 wells;
- 7 fields with wells and 3 explicit zero-well fields;
- 1 parent route + 10 field routes + 56 well routes = 67 Explorer HTML routes.

Production logic will not hardcode these values; the parent acceptance fixture and release receipt will pin them. The following will remain explicitly outside V1: 115 FDP pages without equivalent well drill-down, 131 additional named/material fields, 201 named/producing fields, 1,256 producing field codes, the 1,055 code-only members needing enrichment, and all 1,389 BSEE codes.

---

## Pseudocode

```text
load_contract(path):
    require exact child URLs, owners, lifecycle states, receipt schemas, V1 bounds and crosswalk
    reject cyclic dependencies or any edge where parent approval approves a child
    reject floating revision semantics or child implementation paths owned by parent
```

```text
verify_approvals(github_api, contract):
    for parent and each child issue:
        fetch issue, timeline events and plan-review evidence comment from GitHub
        require status:plan-approved and owner-applied approval-label event
        require repository marker .planning/plan-approved/<issue>.md
        bind evidence comment's reviewed commit/blob and no-MAJOR artifact paths
        require approval event and marker follow that exact review evidence
    return exact account-authority evidence or fail closed
```

```text
verify_trusted_receipts(github_api, vercel_api, hf_raw, receipts):
    require exact allowlisted repository + workflow path/ID + workflow blob SHA
    require workflow_dispatch, protected target ref, allowlisted automation actor,
        run_attempt=1, conclusion=success and exact reviewed child head SHA
    require every action reference is pinned to a full reviewed commit SHA
    require named protected environment and live deployment-approval record
    reject fork/PR events and rehash/attestation-verify downloaded evidence
    live-fetch Vercel deployment ID/environment/git SHA and raw exact HF bytes
    require deployed website registry blob pins receipt HF SHA
```

```text
verify_candidate(approval_evidence, wed_receipt, hf_manifest, website_registry,
                 build_receipt, browser_receipt, deployment_receipt, scan_receipts):
    validate every input against closed contract $defs and rehash referenced evidence
    require live-verified independent approvals
    require live-verified trusted CI/deployment/HF provenance
    require source SHA and manifest source identity agree
    require registry dataset/revision/manifest agree with WED receipt
    require every read used the exact raw HF SHA
    validate hashes, schemas, counts, IDs, joins, licenses and readiness
    validate staged/preview parent + field + well routes, links, sitemap, browser,
            accessibility, security and visible revision evidence
    return immutable candidate record with evidence-root hash; never mutate accepted state
```

```text
transition_release(expected_state_ref_oid, expected_state_version, event, evidence):
    fetch protected refs/heads/field-explorer-release-state; require expected OID/version
    require all prior canonical event hashes remain an exact ordered prefix
    require every evidence/sha256/<digest>.json path is create-only and matches digest
    create one commit whose sole parent is expected_state_ref_oid
    non-force push commit to the same protected ref; Git receive-pack is the CAS
    on non-fast-forward rejection refetch; never auto-rebase or overwrite history

authorize_and_deploy(candidate, github_api):
    dispatch allowlisted production workflow as automation principal with release ID,
        evidence root, HF SHA, website SHA, target and unique deployment_intent_id
    require distinct configured reviewer approves protected environment with
        prevent_self_review; live-fetch approval and bind it to pending deployment
    transition preview_verified -> promotion_authorized -> deploy_pending with
        lease expiry, intent ID and exact rollback deployment
    before create/retry query Vercel by project/target/git SHA/intent metadata
    if one match resume it; if none create once; if multiple/timeout enter unknown
    after API returns transition -> deployed_pending_smoke with deployment ID
    run read-only production smoke
    on pass transition -> accepted and retain prior release as rollback target
    on failure transition -> production_failed -> rollback_pending -> rolled_back
    after crash/lease expiry reconciliation must query by intent before any retry
    if state cannot be proven transition -> unknown and block all promotion
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/field-explorer-cross-repo-contract.json` | machine-readable lifecycle, crosswalk, issue DAG, V1 bounds |
| Create | `docs/governance/field-explorer-promotion-runbook.html` | human promotion, failure recovery and rollback |
| Update | `docs/plans/2026-07-16-field-explorer-plan-approval-packet.html` | keep human approval lifecycle and authority in parity |
| Create | `scripts/workflow/verify_field_explorer_promotion.py` | join and verify child receipts and release evidence |
| Create | `scripts/workflow/promote_field_explorer_release.py` | remote-SHA/state-version CAS and legal release transitions |
| Create | `tests/workflow/test_field_explorer_promotion.py` | TDD for lifecycle, candidate, rollback and expansion bounds |
| Create on protected state ref | `docs/reports/field-explorer/release-state.json` | single authoritative state/event history/current accepted/rollback object |
| Create per release | `docs/reports/field-explorer/releases/<release-id>/` | immutable copies of publisher, build, browser, scan and deployment receipts |
| Update | `docs/README.md` | expose the approved contract/runbook |
| Update | `docs/plans/README.md` | index this plan |
| Create at closeout | `docs/reports/<date>-3559-field-explorer-e2e.html` | actual end-to-end evidence |

The parent will not modify worldenergydata publisher code, HF data, website templates, website JavaScript, website registry entries, or Vercel configuration.

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_children_are_exact_and_independently_gated` | parent approval cannot approve children |
| `test_approval_requires_live_owner_label_event_marker_review_comment_and_plan_blob` | canonical account-authority evidence binds the exact review |
| `test_receipt_schemas_are_closed_and_versioned` | unknown/missing fields and schema majors fail |
| `test_referenced_evidence_is_rehashed` | structurally convenient arbitrary JSON cannot pass |
| `test_dependency_graph_is_acyclic_and_publisher_first` | production pin cannot precede verified receipt |
| `test_crosswalk_covers_source_hf_registry_build_deploy` | every boundary has one owner/binding/evidence |
| `test_state_machine_has_no_acceptance_bypass` | legal/hash/schema/build/smoke gates are mandatory |
| `test_manifest_does_not_self_reference_hf_sha` | external receipt/registry own HF SHA |
| `test_exact_raw_revision_only` | datasets-server, `main`, tag and omitted SHA fail |
| `test_v1_bounds_and_expansion_exclusions` | 10/56/7/3/67 accepted; broader tiers excluded |
| `test_mixed_or_tampered_snapshot_fails` | R1/R2 mixing and corruption cannot promote |
| `test_duplicate_or_orphan_identity_fails` | identity graph is closed |
| `test_route_inventory_is_complete` | fixture produces parent + every field/well route |
| `test_more_than_100_records_are_not_truncated` | synthetic expansion reaches all records |
| `test_data_only_xss_and_safe_path_contract` | markup/path payloads fail or remain inert |
| `test_failed_candidate_preserves_last_good` | failed R2 leaves R1 intact |
| `test_registry_revert_restores_r1` | R2→R1 preserves stable routes and data |
| `test_single_state_object_nonforce_ref_push_is_actual_remote_cas` | same-parent concurrent writers: exactly one succeeds |
| `test_history_is_prefix_only_and_evidence_is_content_addressed_create_only` | prior events/evidence cannot be truncated or rewritten |
| `test_production_pending_failure_rollback_and_unknown_transitions` | external state never contradicts silent R1 acceptance |
| `test_protected_environment_approval_is_distinct_candidate_bound_and_single_use` | workflow actor cannot self-approve or replay another candidate |
| `test_deployment_intent_reconciles_crash_timeout_zero_one_or_many_matches` | retry never creates an ambiguous second production deployment |
| `test_exact_trusted_workflow_policy_and_live_provenance` | wrong event/path/ref/actor/attempt/action/environment/fork fails |
| `test_rollback_drill_is_preview_only_without_fresh_authorization` | planning approval cannot mutate production |
| `test_runbook_matches_machine_contract` | HTML and JSON lifecycle stay in parity |
| `test_approval_packet_matches_contract_states_and_authority` | approval surface cannot omit pending/failure/rollback gates |

---

## Acceptance Criteria

- [ ] This parent plan and both child plans will receive independent adversarial review and explicit user approval before their implementations begin.
- [ ] Parent approval will not authorize either child.
- [ ] Parent JSON and HTML will define the exact issue DAG, crosswalk, revisions, receipts, states, failure behavior, and rollback.
- [ ] Plan approval verification will bind the live account-authority `status:plan-approved` event, canonical marker, plan-review evidence comment, exact reviewed plan blob, and final review artifacts; it will not claim cryptographic proof of human intent.
- [ ] Closed versioned schemas will cover publisher, build, browser, scan, deployment, authorization, candidate, pending, acceptance, rejection, failure, rollback, and unknown receipts/states.
- [ ] One authoritative release-state object plus content-addressed create-only evidence will update on a protected state ref through a one-parent non-force push; concurrent stale writers will receive non-fast-forward failure.
- [ ] Every transition will preserve prior canonical event hashes as an exact prefix and validate state-ref ancestry to genesis.
- [ ] #1045 will produce byte-identical browser outputs from one clean source revision and one atomic HF commit.
- [ ] Every immutable read will use raw `resolve/<exact-hf-sha>/...`; datasets-server and floating refs will be rejected.
- [ ] #74 production pinning will consume the verified #1045 receipt, not only fixtures.
- [ ] V1 will generate one parent, ten field, and 56 well routes with seven populated and three zero-well fields.
- [ ] Complete selection/pagination will reach records beyond 100 without legacy truncation.
- [ ] Parent/child URLs, state, breadcrumbs, canonical links, back-links, and sitemap entries will resolve.
- [ ] No-JS HTML will expose useful results, counts, provenance, revision, limitations, and links.
- [ ] Dirty source, legal ambiguity, unsafe path, embedded HTML, duplicate/orphan ID, schema/hash/count mismatch, missing shard, mixed revision, or stale pin will fail before deployment.
- [ ] Failed R2 promotion will leave R1 intact; R2→R1 revert will reproduce R1.
- [ ] Website-generated build/browser receipts will bind commands, tools, routes, assertions, hashes and preview deployment to an exact allowlisted workflow_dispatch policy; the parent will live-fetch run/approval/artifact and Vercel provenance and verify attestations/hashes.
- [ ] Preview browser, mobile, keyboard, JS-disabled, CSP, XSS, link, and revision-disclosure checks will pass before any production mutation.
- [ ] Production promotion will require protected-environment approval by a configured reviewer distinct from the automation actor, with prevent-self-review and exact candidate inputs.
- [ ] Production will enter `deploy_pending` with a lease, intent ID and rollback target before mutation; retries will reconcile Vercel intent metadata before creation; smoke success will accept, failure will record and roll back, and ambiguity will enter blocking `unknown`.
- [ ] Both implemented child issues will receive summary comments before parent closure.
- [ ] Parent and child legal/security scans, tests, cross-reviews, cleanup audits, and completeness gates will pass.
- [ ] Closeout will not claim the 115 FDP pages or broader expansion tiers as delivered.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | final-input binding/harness self-observation; deployment-state latency residual |
| Codex | MAJOR | authorization trust boundary, exact remote CAS, crash reconciliation, workflow allowlist, append-only evidence |
| Gemini | UNAVAILABLE | no non-interactive authentication configured |

**Round 3 result:** MAJOR from two independent providers. The exact input was remotely committed at `8aeb690c...` with plan blob `14b6cdda...`; both final artifacts became non-empty after provider exit, while both reviewers also exposed the in-progress-sink race now filed as [#3560](https://github.com/vamseeachanta/workspace-hub/issues/3560). The remaining findings will be absorbed inline through the three-round cap. No fourth automatic review will run; the issue will remain `status:needs-plan` and the user will receive the final evidence plus the unresolved consensus risk for disposition.

---

## Risks and Open Questions

- **Non-atomic platforms:** GitHub, HF, and Vercel cannot become visible simultaneously. The state machine will expose `deploy_pending`, failure, rollback, and unknown states instead of claiming cross-platform atomicity.
- **License conflict:** #1045 will fail closed until source-specific redistribution and dataset-card licensing are recorded; the parent cannot waive it.
- **PR overlap:** #74 will begin only after PR #73 merges/rebases or explicit path coordination occurs.
- **Identity drift:** display names and slugs may change; stable IDs and redirects will preserve joins and URLs.
- **Cache substitution:** only a fully validated cache for the exact pinned revision may support an outage build.
- **Scale:** V1 proves generic correctness beyond 100 with synthetic fixtures; it will not claim performance for all future 1,389 fields without a later measured expansion plan.
- **External-action authority:** the rollback exercise will use a preview deployment. Planning approval will not authorize production deployment; promotion will stop for candidate-bound protected-environment approval by a reviewer distinct from the workflow actor.
- **Implementation proof burden:** approval will authorize building the state/CAS/provenance machinery, not assert that it is already correct. Remote-race, crash-point, protected-environment, Vercel reconciliation, and attestation tests plus T3 code review will remain mandatory before any production promotion.

## Complexity: T3

Systemic cross-repository work will span immutable external data, legal admission, stable relational identities, static HTML generation, deployment promotion, rollback, accessibility, security, and independently approved children.
