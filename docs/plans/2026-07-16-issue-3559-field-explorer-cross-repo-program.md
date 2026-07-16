# Plan for #3559: Immutable Hugging Face field/well HTML drill-down program

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3559
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; approved implementation `parallel-worktree`
> **Reviewed draft:** `06216c5c7d48b217ae7b1f92ad184d6eeb4ab2c5`
> **Round 1 artifacts:** `scripts/review/results/issue-3559-round-1/2026-07-16-plan-3559-claude.md` | `...-codex.md` | `...-gemini.md`
> **Round 2 artifacts:** `scripts/review/results/issue-3559-round-2/2026-07-16-plan-3559-claude.md` | `...-codex.md` | `...-gemini.md`

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
worldenergydata main:     a26881d49d064ea6ae6c8200ae1a874bf944e1bb
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

Captured result: all three issues were `OPEN`, carried `status:needs-plan` and exactly one `lane:codex` label. Titles were respectively “immutable Hugging Face field/well HTML drill-down program,” “deterministic exact-revision HF browser snapshot manifest,” and “registry-driven pinned field → well HTML drill-down.”

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
| Append-only release ledger | `docs/reports/field-explorer/release-ledger.jsonl` |
| Accepted-release pointer | `docs/reports/field-explorer/accepted-release.json` |
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
P6: a separately user-authorized production promotion receives read-only smoke;
    accepted state advances atomically and retains the prior pin/deployment.
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
        fetch the issue and approval comment from GitHub, never caller JSON alone
        require status:plan-approved, approved plan commit/blob and approval marker
        require comment author is the configured owner and predates implementation
    return hash-bound approval evidence or fail closed
```

```text
verify_candidate(approval_evidence, wed_receipt, hf_manifest, website_registry,
                 build_receipt, browser_receipt, deployment_receipt, scan_receipts):
    validate every input against closed contract $defs and rehash referenced evidence
    require live-verified independent approvals
    require source SHA and manifest source identity agree
    require registry dataset/revision/manifest agree with WED receipt
    require every read used the exact raw HF SHA
    validate hashes, schemas, counts, IDs, joins, licenses and readiness
    validate staged/preview parent + field + well routes, links, sitemap, browser,
            accessibility, security and visible revision evidence
    return immutable candidate record with evidence-root hash; never mutate accepted state
```

```text
record_candidate(candidate, ledger, expected_accepted_hash):
    acquire repository-local lock; reject concurrent or stale expected state
    write per-release evidence to temporary sibling; fsync and atomically rename
    append hash-chained candidate event; leave accepted-release unchanged

accept_candidate(candidate, user_authorization, production_smoke):
    require preview R1→R2→R1 drill and separate production-promotion authorization
    require read-only production smoke binds deployment + website + HF revision
    atomically append accepted event and replace accepted-release pointer
    retain previous accepted release as explicit rollback target
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/field-explorer-cross-repo-contract.json` | machine-readable lifecycle, crosswalk, issue DAG, V1 bounds |
| Create | `docs/governance/field-explorer-promotion-runbook.html` | human promotion, failure recovery and rollback |
| Create | `scripts/workflow/verify_field_explorer_promotion.py` | join and verify child receipts and release evidence |
| Create | `scripts/workflow/promote_field_explorer_release.py` | locked, hash-chained candidate/accept state transitions |
| Create | `tests/workflow/test_field_explorer_promotion.py` | TDD for lifecycle, candidate, rollback and expansion bounds |
| Create | `docs/reports/field-explorer/release-ledger.jsonl` | append-only candidate/accepted/rejected/rollback history |
| Create | `docs/reports/field-explorer/accepted-release.json` | atomic pointer to accepted evidence root and rollback target |
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
| `test_approval_requires_live_issue_label_owner_comment_and_plan_blob` | caller JSON cannot forge authorization |
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
| `test_ledger_is_hash_chained_locked_and_append_only` | concurrent/stale/tampered transitions fail |
| `test_accepted_pointer_updates_atomically_after_authorized_smoke` | no partial accepted state |
| `test_browser_build_deployment_and_scan_receipts_are_required` | synthetic parent fixture cannot satisfy production evidence |
| `test_rollback_drill_is_preview_only_without_fresh_authorization` | planning approval cannot mutate production |
| `test_runbook_matches_machine_contract` | HTML and JSON lifecycle stay in parity |

---

## Acceptance Criteria

- [ ] This parent plan and both child plans will receive independent adversarial review and explicit user approval before their implementations begin.
- [ ] Parent approval will not authorize either child.
- [ ] Parent JSON and HTML will define the exact issue DAG, crosswalk, revisions, receipts, states, failure behavior, and rollback.
- [ ] Promotion will live-fetch each issue label and owner approval comment, bind the approved plan commit/blob, and reject caller-authored approval claims.
- [ ] Closed versioned schemas will cover publisher, build, browser, scan, deployment, candidate, acceptance, rejection, and rollback receipts.
- [ ] A locked hash-chained ledger, per-release evidence directory, and atomic accepted pointer will preserve durable last-good state and recovery history.
- [ ] #1045 will produce byte-identical browser outputs from one clean source revision and one atomic HF commit.
- [ ] Every immutable read will use raw `resolve/<exact-hf-sha>/...`; datasets-server and floating refs will be rejected.
- [ ] #74 production pinning will consume the verified #1045 receipt, not only fixtures.
- [ ] V1 will generate one parent, ten field, and 56 well routes with seven populated and three zero-well fields.
- [ ] Complete selection/pagination will reach records beyond 100 without legacy truncation.
- [ ] Parent/child URLs, state, breadcrumbs, canonical links, back-links, and sitemap entries will resolve.
- [ ] No-JS HTML will expose useful results, counts, provenance, revision, limitations, and links.
- [ ] Dirty source, legal ambiguity, unsafe path, embedded HTML, duplicate/orphan ID, schema/hash/count mismatch, missing shard, mixed revision, or stale pin will fail before deployment.
- [ ] Failed R2 promotion will leave R1 intact; R2→R1 revert will reproduce R1.
- [ ] Website-generated build/browser receipts will bind commands, tool versions, routes, assertions, hashes, preview deployment, and raw artifacts; the parent will schema-check and rehash them.
- [ ] Preview browser, mobile, keyboard, JS-disabled, CSP, XSS, link, and revision-disclosure checks will pass before any production mutation.
- [ ] Production promotion will require a fresh explicit authorization after preview evidence; production smoke will be read-only.
- [ ] Both implemented child issues will receive summary comments before parent closure.
- [ ] Parent and child legal/security scans, tests, cross-reviews, cleanup audits, and completeness gates will pass.
- [ ] Closeout will not claim the 115 FDP pages or broader expansion tiers as delivered.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | timed out after 600 seconds without usable output |
| Codex | MAJOR | approval authenticity, receipt/state schemas, evidence interfaces, rollback authority, embedded reproduction |
| Gemini | UNAVAILABLE | no non-interactive authentication configured |

**Round 1 result:** MAJOR. Findings will be resolved in this revision and independently rerun under the Round 2 namespace. The issue will remain `status:needs-plan` until the fresh round has no unresolved MAJOR finding.

---

## Risks and Open Questions

- **Non-atomic platforms:** GitHub, HF, and Vercel cannot become visible simultaneously. Acceptance will be a locked, hash-chained verified state transition, not a visibility claim.
- **License conflict:** #1045 will fail closed until source-specific redistribution and dataset-card licensing are recorded; the parent cannot waive it.
- **PR overlap:** #74 will begin only after PR #73 merges/rebases or explicit path coordination occurs.
- **Identity drift:** display names and slugs may change; stable IDs and redirects will preserve joins and URLs.
- **Cache substitution:** only a fully validated cache for the exact pinned revision may support an outage build.
- **Scale:** V1 proves generic correctness beyond 100 with synthetic fixtures; it will not claim performance for all future 1,389 fields without a later measured expansion plan.
- **External-action authority:** the rollback exercise will use a preview deployment. Planning approval will not authorize production deployment or a production rollback drill; promotion will stop for a fresh user authorization after preview evidence.

## Complexity: T3

Systemic cross-repository work will span immutable external data, legal admission, stable relational identities, static HTML generation, deployment promotion, rollback, accessibility, security, and independently approved children.
