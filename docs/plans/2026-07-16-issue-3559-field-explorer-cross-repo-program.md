# Plan for #3559: Immutable Hugging Face field/well HTML drill-down program

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3559
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; approved implementation `parallel-worktree`
> **Review artifacts:** `scripts/review/results/2026-07-16-plan-3559-claude.md` | `scripts/review/results/2026-07-16-plan-3559-codex.md` | `scripts/review/results/2026-07-16-plan-3559-gemini.md`

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

**Immutable-read reproduction:** raw datasets-server requests without a revision, with the real HF SHA, and with an invalid all-zero SHA all returned HTTP 200 and identical bytes. Therefore acceptance evidence will use only raw `resolve/<exact-sha>/...` artifacts; datasets-server will not prove immutability.

**Reproduction proofs:** N/A for the parent governance implementation. The two child plans will carry the runtime/data gap proofs.

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
| Verifier tests | `tests/workflow/test_field_explorer_promotion.py` |
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
    verifier joins publisher, manifest, registry, build, route, and scan evidence.
P5: production smoke accepts the candidate and retains the prior pin.
P6: an R1→R2 update and R2→R1 revert prove stable routes and whole-snapshot rollback.
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
    require exact child URLs, owners, lifecycle states, V1 bounds and crosswalk
    reject cyclic dependencies or any edge where parent approval approves a child
    reject floating revision semantics or child implementation paths owned by parent
```

```text
verify_candidate(wed_receipt, hf_manifest, website_registry, build_receipt):
    require independently approved children
    require source SHA and manifest source identity agree
    require registry dataset/revision/manifest agree with WED receipt
    require every read used the exact raw HF SHA
    validate hashes, schemas, counts, IDs, joins, licenses and readiness
    validate parent + field + well routes, links, sitemap and visible revision
    return immutable candidate record; never mutate last_good
```

```text
accept_or_retain(candidate, last_good, production_smoke):
    if all gates and smoke pass: accept candidate and retain last_good as rollback
    else: record unpromoted candidate and retain last_good unchanged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/field-explorer-cross-repo-contract.json` | machine-readable lifecycle, crosswalk, issue DAG, V1 bounds |
| Create | `docs/governance/field-explorer-promotion-runbook.html` | human promotion, failure recovery and rollback |
| Create | `scripts/workflow/verify_field_explorer_promotion.py` | join and verify child receipts and release evidence |
| Create | `tests/workflow/test_field_explorer_promotion.py` | TDD for lifecycle, candidate, rollback and expansion bounds |
| Update | `docs/README.md` | expose the approved contract/runbook |
| Update | `docs/plans/README.md` | index this plan |
| Create at closeout | `docs/reports/<date>-3559-field-explorer-e2e.html` | actual end-to-end evidence |

The parent will not modify worldenergydata publisher code, HF data, website templates, website JavaScript, website registry entries, or Vercel configuration.

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_children_are_exact_and_independently_gated` | parent approval cannot approve children |
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
| `test_runbook_matches_machine_contract` | HTML and JSON lifecycle stay in parity |

---

## Acceptance Criteria

- [ ] This parent plan and both child plans will receive independent adversarial review and explicit user approval before their implementations begin.
- [ ] Parent approval will not authorize either child.
- [ ] Parent JSON and HTML will define the exact issue DAG, crosswalk, revisions, receipts, states, failure behavior, and rollback.
- [ ] #1045 will produce byte-identical browser outputs from one clean source revision and one atomic HF commit.
- [ ] Every immutable read will use raw `resolve/<exact-hf-sha>/...`; datasets-server and floating refs will be rejected.
- [ ] #74 production pinning will consume the verified #1045 receipt, not only fixtures.
- [ ] V1 will generate one parent, ten field, and 56 well routes with seven populated and three zero-well fields.
- [ ] Complete selection/pagination will reach records beyond 100 without legacy truncation.
- [ ] Parent/child URLs, state, breadcrumbs, canonical links, back-links, and sitemap entries will resolve.
- [ ] No-JS HTML will expose useful results, counts, provenance, revision, limitations, and links.
- [ ] Dirty source, legal ambiguity, unsafe path, embedded HTML, duplicate/orphan ID, schema/hash/count mismatch, missing shard, mixed revision, or stale pin will fail before deployment.
- [ ] Failed R2 promotion will leave R1 intact; R2→R1 revert will reproduce R1.
- [ ] Production browser, mobile, keyboard, JS-disabled, CSP, XSS, link, and revision-disclosure checks will pass.
- [ ] Both implemented child issues will receive summary comments before parent closure.
- [ ] Parent and child legal/security scans, tests, cross-reviews, cleanup audits, and completeness gates will pass.
- [ ] Closeout will not claim the 115 FDP pages or broader expansion tiers as delivered.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | review not run |
| Codex | PENDING | review not run |
| Gemini | PENDING | review not run |

**Overall result:** PENDING. The issue will remain `status:needs-plan` until no unresolved MAJOR finding remains.

---

## Risks and Open Questions

- **Non-atomic platforms:** GitHub, HF, and Vercel cannot become visible simultaneously. Acceptance will be a verified state transition, not a visibility claim.
- **License conflict:** #1045 will fail closed until source-specific redistribution and dataset-card licensing are recorded; the parent cannot waive it.
- **PR overlap:** #74 will begin only after PR #73 merges/rebases or explicit path coordination occurs.
- **Identity drift:** display names and slugs may change; stable IDs and redirects will preserve joins and URLs.
- **Cache substitution:** only a fully validated cache for the exact pinned revision may support an outage build.
- **Scale:** V1 proves generic correctness beyond 100 with synthetic fixtures; it will not claim performance for all future 1,389 fields without a later measured expansion plan.

## Complexity: T3

Systemic cross-repository work will span immutable external data, legal admission, stable relational identities, static HTML generation, deployment promotion, rollback, accessibility, security, and independently approved children.
