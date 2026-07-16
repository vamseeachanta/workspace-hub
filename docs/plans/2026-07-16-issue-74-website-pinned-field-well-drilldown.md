# Plan for aceengineer-website #74: Registry-driven pinned field/well HTML drill-down

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/aceengineer-website/issues/74
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/3559
> **Producer:** https://github.com/vamseeachanta/worldenergydata/issues/1045
> **Client:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; approved implementation `parallel-worktree`
> **Review artifacts:** `scripts/review/results/2026-07-16-plan-74-claude.md` | `scripts/review/results/2026-07-16-plan-74-codex.md` | `scripts/review/results/2026-07-16-plan-74-gemini.md`

---

## Authorization Boundary

This plan will authorize only aceengineer-website changes after its own adversarial review and explicit user approval. Approval of parent #3559 or publisher #1045 will not approve this implementation. Production pinning will also wait for a verified #1045 publication receipt. Draft [PR #73](https://github.com/vamseeachanta/aceengineer-website/pull/73) overlaps the registry, build, and registry-test paths; implementation will start only after merge/rebase or explicit path coordination.

## Resource Intelligence Summary

### Existing repo code

- `config/capabilities.yaml` currently describes independent field, well, and country tables. It has no exact revision, manifest, relationship, selector keys, child templates, or route contract.
- `scripts/hf-fetch.js` currently reads floating datasets-server rows with a default maximum of 100 and caches tables independently.
- `scripts/render-capabilities.js` currently renders at most 50 table rows and will not express a relational field-to-well view.
- `assets/js/capabilities-refresh.js` currently refreshes floating tables independently and can expose a mixed snapshot.
- `build.js` currently removes `dist` before validation and catches capability rendering errors. A failed relational build could therefore destroy the last good local output or hide an incomplete capability.
- The production capability page returned HTTP 200 on 2026-07-16, contained no `<select>`, and displayed only “Showing 50 of 56 rows” and “Showing 50 of 84 rows.”
- `vercel.json` does not need a browser Hugging Face CSP allowance under the approved build-time design.

### Immutable-read evidence

Hugging Face datasets-server returned identical successful bodies when called with no revision, the observed real revision, and an invalid all-zero revision. It will not be used as immutable evidence. Browser artifacts will be fetched only through raw `resolve/<exact-sha>/<path>` URLs.

Raw regular Git blobs may redirect once to a same-origin Hugging Face `/api/resolve-cache/.../<exact-sha>/...` path. The fetcher will allow that one bounded same-origin form only when the exact revision remains present. Off-origin redirects for browser JSON, floating refs, omitted revisions, and LFS/Xet browser shards will fail. Publisher #1045 will keep browser JSON as bounded regular Git blobs.

### Documents and related work

- [workspace-hub #3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) will own the cross-repository lifecycle and rollback contract.
- [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) will own the manifest, browser shards, identities, provenance, license admission, HF commit, exact-SHA readback, and receipt.
- [workspace-hub #3485](https://github.com/vamseeachanta/workspace-hub/issues/3485) will remain the broader capability-registry program; its floating refresh path will not govern this relational capability.
- Drive-index search for `Hugging Face field explorer HTML templates dropdown worldenergydata` returned no relevant governing document. No LLM-wiki page will be modified.

### Verified baseline

Planning inspected website `origin/main` at `efde01a32a8507768804649afedf06190ec618bf`. The proposed V1 producer fixture contains 10 fields and 56 wells, including seven populated fields and three explicit zero-well fields. Production code will discover counts from the validated manifest rather than hardcoding them.

---

## Deliverable

A scalable registry-driven build pipeline will fetch one exact Hugging Face browser snapshot, validate it completely, stage it locally, and generate:

- one accessible parent Explorer page with dependent field/well selectors;
- one static child page per field;
- one nested static child page per well;
- reusable HTML child-panel partials for summary, economics, well list, well detail, and generic tables;
- local immutable browser assets, pagination, and shareable deep-link state;
- transactional build/promotion evidence that preserves the prior complete output on failure.

No browser request will depend on Hugging Face at runtime.

## Registry Contract

The relational capability entry will declare, at minimum:

```yaml
id: field-explorer
mode: relational-snapshot
dataset: aceengineer/worldenergydata-explorer
snapshot:
  revision: <exact-40-character-hf-sha>
  manifest_path: browser/manifest.json
relationships:
  field_key: field_id
  well_key: well_id
  well_parent_key: parent_field_id
selectors:
  primary: field
  dependent: well
templates:
  page: capabilities/relational/page.html
  field_panels:
    - field-summary.html
    - production-economics.html
    - well-list.html
  well_panels:
    - well-detail.html
routes:
  parent: /capabilities/field-explorer.html
  field: /capabilities/field-explorer/fields/{field_slug}.html
  well: /capabilities/field-explorer/fields/{field_slug}/wells/{well_slug}.html
```

The validator will reject unknown schema majors, floating revisions, unsafe paths, duplicate template/route ownership, missing relationship keys, selector cycles, and relational capabilities wired to legacy floating refresh.

## Template and Route Architecture

Markup will live in real HTML partial files rather than JavaScript string templates:

```text
content/partials/capabilities/relational/page.html
content/partials/capabilities/relational/field-summary.html
content/partials/capabilities/relational/production-economics.html
content/partials/capabilities/relational/well-list.html
content/partials/capabilities/relational/well-detail.html
content/partials/capabilities/relational/generic-table.html
```

The renderer will construct escaped, data-only view models and pass them to the existing PostHTML pipeline. It will not concatenate record values into markup, execute data-provided HTML, or embed executable inline JSON.

Generated canonical routes will be:

```text
/capabilities/field-explorer.html
/capabilities/field-explorer/fields/<field-slug>.html
/capabilities/field-explorer/fields/<field-slug>/wells/<well-slug>.html
```

The no-JavaScript parent will expose the complete field index. Every field page will expose all child well links or an explicit zero-well state. Breadcrumbs, canonical links, back-links, and sitemap entries will be generated for every route.

## Snapshot, Cache, and Promotion Contract

```text
validate registry before network access
derive cache key from dataset + exact HF SHA
fetch manifest via raw exact-revision URL
permit at most one same-origin exact-SHA resolve-cache redirect
validate manifest schema, safe paths and producer identity
fetch every declared browser shard from the same exact SHA
rehash and validate bytes, counts, schemas, ordering, IDs and joins
write only a fully validated revision cache
construct one relational model from that cache
render the whole site into a sibling staging directory
run route/link/security/accessibility/build-receipt checks
atomically promote staging to dist only after every gate passes
retain the prior complete dist and exact-revision cache on failure
```

The committed V1 exact-revision cache fixture will make deterministic offline builds possible. A build may use only a complete cache for the configured revision. A different revision will never substitute silently. A failed R2 candidate will leave deployed R1 unchanged.

## Files to Change

| Action | Path | Purpose |
|---|---|---|
| Update | `config/capabilities.yaml` | register exact relational snapshot, relationships, templates and routes |
| Update | `docs/capabilities-registry.md` | document relational schema and migration rules |
| Update | `scripts/validate-capabilities.js` | fail closed on relational registry defects |
| Create | `scripts/hf-pinned-snapshot.js` | exact-SHA fetch, redirect policy, manifest/shard validation and cache |
| Create | `scripts/refresh-pinned-capability-data.js` | explicit reviewed refresh command; no floating refresh |
| Create | `scripts/render-relational-capability.js` | safe view models and parent/child route generation |
| Create | `scripts/promote-build-output.js` | atomic staging-to-dist promotion and retention |
| Create | `scripts/write-field-explorer-build-receipt.js` | closed-schema build/route/input/tool evidence with artifact hashes |
| Create | `scripts/collect-field-explorer-browser-evidence.js` | Playwright assertion results and raw evidence hashes for preview/production smoke |
| Update | `build.js` | orchestrate validated relational rendering transactionally |
| Create | `content/partials/capabilities/relational/page.html` | standard parent page shell |
| Create | `content/partials/capabilities/relational/field-summary.html` | reusable field summary panel |
| Create | `content/partials/capabilities/relational/production-economics.html` | reusable analysis/economics panel |
| Create | `content/partials/capabilities/relational/well-list.html` | reusable complete/paginated well list |
| Create | `content/partials/capabilities/relational/well-detail.html` | reusable well drill-down panel |
| Create | `content/partials/capabilities/relational/generic-table.html` | bounded generic fallback panel |
| Create | `assets/js/capability-drilldown.js` | local selector, pagination, history and deep-link controller |
| Update/Create | `assets/css/` relational styles | accessible responsive presentation |
| Create | `data/hf-cache/pinned/<dataset>/<sha>/` | exact V1 manifest/shard fixture and metadata |
| Create per build | `dist/.build-receipts/field-explorer.json` | website commit, pinned SHA, manifest, template/data hashes, route/link counts and commands |
| Create per acceptance | `artifacts/field-explorer/<release-id>/browser-receipt.json` | tool/browser versions, deployment URL/ID, assertions and screenshot/report hashes |
| Create/Update | `tests/` focused registry/snapshot/render/browser/build tests | TDD and regressions |

New implementation modules will remain at or below 400 lines and functions at or below 50 lines. The work will not enlarge `scripts/render-capabilities.js` into a second relational renderer.

## Pseudocode

```text
load_relational_registry(entry):
    require exact dataset, 40-char revision and safe manifest path
    require stable field/well/parent keys and acyclic dependent selectors
    require real page and child-panel template paths
    require collision-free parent/field/well route patterns
    reject legacy floating refresh for this capability
```

```text
load_pinned_snapshot(entry, cache):
    if cache has complete validated entry.revision: candidate = cache
    else: fetch raw exact-revision manifest and every declared shard
    enforce redirect policy and same revision for every response
    verify hashes, bytes, rows, schemas, ordering, primary/foreign keys
    reject unsafe or executable data and mixed/missing artifacts
    atomically persist only complete validated cache
    return immutable relational model
```

```text
render_relational(model, templates, staging):
    build escaped view models
    render parent page and complete field index
    for each field: render child panels and all well links or empty state
    for each well: render nested well page and parent context
    emit local browser data, revision disclosure, canonical links and sitemap
    verify route inventory and internal links before promotion
    write closed-schema build receipt containing command/tool/input/output hashes
```

```text
reduce_browser_state(state, action):
    field change resets well and page, then filters wells locally
    well change selects only a child of the active field
    page change remains bounded and preserves field/well/panel query state
    history updates a shareable URL without network data access
    invalid deep links recover visibly to a valid state
```

## Failing-First TDD Sequence

### Registry and pinned fetch

- Reject missing, floating, short, or nonhex revisions.
- Reject unsafe manifest/template/route paths and selector cycles.
- Reject relational capability wired to `capabilities-refresh.js`.
- Prove datasets-server and `main` are never used.
- Permit only the bounded same-origin exact-SHA resolve-cache redirect.
- Reject off-origin, multi-hop, revision-losing, and LFS/Xet browser JSON redirects.
- Reject unknown manifest major, wrong dataset/source identity, missing shard, bad hash/byte/count/schema/order, duplicate ID, orphan well, embedded markup, unsafe URL/path, and R1/R2 mixing.
- Accept only a complete cache for the configured revision; reject incomplete or different-revision fallback.
- Prove a >100-record fixture loads and remains complete.

### Templates and routes

- Assert every registry template path exists and is an HTML partial.
- Render a parent, a populated field, a zero-well field, and a well page from the same component family.
- Assert record values are escaped and cannot create script, event-handler, URL, or markup execution.
- Assert no executable inline JSON is emitted.
- Assert V1 route counts are discovered as 1 parent + 10 fields + 56 wells.
- Assert every breadcrumb, canonical link, back-link, field/well link, and sitemap entry resolves.
- Assert no-JS parent and field pages expose complete navigation and revision/provenance context.
- Assert stable IDs remain independent of display labels and route slugs.
- Assert duplicate slugs fail rather than overwrite output.

### Browser controller

- Populate the field selector from local validated data.
- Filter the well selector by `parent_field_id` and expose the zero-well state.
- Reach every well and every record beyond 100 through pagination.
- Reset invalid dependent state when the field changes.
- Parse and serialize field, well, panel, and page deep-link state.
- Preserve Back/Forward behavior and recover visibly from unknown IDs/pages.
- Pass keyboard, label, focus, live-region, and reduced-motion checks.
- Make no runtime request to Hugging Face or datasets-server.

### Build and promotion

- Fail before deleting or replacing current `dist` when registry/snapshot/render/link checks fail.
- Render the whole site in a sibling staging directory.
- Promote only after route, link, CSP, accessibility, legal and receipt checks pass.
- Reject any receipt with an unknown schema major, missing command/tool/deployment identity, unreferenced raw result, or hash mismatch.
- Collect browser evidence against preview first; production collection will be read-only and separately authorized.
- Prove a failed R2 leaves R1 output and cache intact.
- Prove a registry-pin revert R2→R1 reproduces R1 content and stable URLs.
- Preserve legacy non-relational capability behavior through focused regression tests.

## Acceptance Criteria

- [ ] This issue plan will receive T3 adversarial review and explicit user approval before implementation.
- [ ] PR #73 overlap will be merged/rebased or explicitly coordinated before shared files change.
- [ ] The registry will bind dataset ID, exact HF SHA, manifest path, relationships, selector keys, template paths, and route patterns.
- [ ] Production pinning will use the verified #1045 receipt and exact returned HF SHA.
- [ ] Every browser artifact will be fetched from the same raw exact revision and fully validated before rendering.
- [ ] No runtime browser request will target Hugging Face or datasets-server.
- [ ] Only a complete validated same-revision cache may support offline/outage builds; a different revision will never substitute.
- [ ] Actual HTML partials will define the page shell and reusable child panels; JavaScript will not own the markup contract.
- [ ] One parent, every field, and every well will receive a canonical static route with complete links and sitemap coverage.
- [ ] The parent field dropdown and dependent well dropdown will reach all validated records, including records beyond 100.
- [ ] Shareable field/well/panel/page deep links and browser Back/Forward behavior will work without data refetch.
- [ ] No-JS output will provide useful field and well navigation, counts, provenance, revision, limitations, and zero-well states.
- [ ] Data values will remain inert through escaping, safe URL/path validation, and CSP-compatible rendering.
- [ ] The full website build will stage and validate before atomic promotion; a failed candidate will preserve the prior complete output.
- [ ] Build and browser receipts will conform to the parent contract, bind exact commands/tool versions/inputs/routes/deployment IDs, and hash every referenced raw artifact.
- [ ] An R1→R2→R1 rollback exercise will run on preview only; a fresh explicit user authorization will be required before production promotion.
- [ ] Pin rollback will restore the earlier whole snapshot without changing canonical field/well URLs.
- [ ] Focused tests, full tests, link/accessibility/browser checks, legal/security scans, and T3 code/artifact review will have no unresolved MAJOR finding.
- [ ] The issue will receive a closeout comment linking the website commit, pinned HF SHA, build/deployment evidence, route/count report, rollback target, and named residual gaps.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Review not yet run |
| Codex | PENDING | Review not yet run |
| Gemini | PENDING | Review not yet run |

**Overall result:** PENDING. The plan will remain draft until no unresolved MAJOR finding remains.

## Risks and Fixed Decisions

- **Upstream overlap:** PR #73 is a real implementation blocker for shared paths, not a reason to weaken or bypass the plan.
- **HF redirect behavior:** browser JSON will remain regular Git blobs. Only a bounded same-origin exact-SHA resolve-cache redirect will be accepted.
- **Static-output size:** all field/well pages are intentional for accessibility, search, and no-JS drill-down. Pagination will bound individual panels without truncating the route inventory.
- **Template drift:** registry validation and render tests will bind actual partial files and required panel inputs.
- **Cache staleness:** cache identity is the exact SHA. A cached latest snapshot or different SHA is invalid.
- **Mixed snapshot:** tables will not hydrate independently. One manifest and one relational model will govern all pages.
- **No open owner decision:** build-time pinned ingestion, local browser assets, actual child HTML partials, exact-revision cache, static nested routes, and transactional promotion are fixed by the approved architecture.

## Complexity: T3

T3 is required because this implementation changes registry schema, external immutable-fetch semantics, data validation, reusable template architecture, static route generation, browser state, accessibility, security, build promotion, rollback, and cross-repository release evidence.
