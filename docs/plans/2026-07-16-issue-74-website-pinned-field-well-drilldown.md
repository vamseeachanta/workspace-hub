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
> **Round 1 artifacts:** `scripts/review/results/issue-74-round-1/2026-07-16-plan-74-claude.md` | `...-codex.md` | `...-gemini.md`
> **Isolated adjudication:** `scripts/review/results/issue-3559-isolated-adjudication/2026-07-16-adjudication.md`

---

## Authorization Boundary

This plan will authorize only aceengineer-website changes after its own adversarial review and explicit user approval. Approval of parent #3559 or publisher #1045 will not approve this implementation. Phase A will begin only after parent #3559 and this plan receive explicit user approval and PR #73 is merged or closed with its overlapping paths reconciled. Phase A will implement only the generic parent/child registry schema, validator, renderer, controller, transactional build machinery, and synthetic fixtures. It will perform no HF network request, create no production cache, switch no live capability to relational mode, run no Vercel promotion, and change no production route behavior.

Phase B will begin only after #1045 receives its own approval, publishes one validated receipt and exact HF SHA, and the website verifies that receipt against the reviewed contract. Phase B will create the exact-revision cache, switch `field-explorer` to relational mode, generate production parent/child routes and content-addressed assets, run preview evidence and R1→R2→R1 exercises, and stop for fresh explicit production authorization. Issue #74 will remain open until both phases and production closeout complete.

Before the Phase A branch is created, the integration owner will record PR #73's final disposition and merge SHA, fetch current remote `main`, create `feature/issue-74-pinned-parent-child-drilldown` from that SHA, and prove that PR #73 capability entries/tests remain present. While PR #73 is open, no #74 lane may edit `build.js`, `config/capabilities.yaml`, or `tests/js/capabilities-registry.test.js`; those shared files will have one serialized integration owner after reconciliation.

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

The current live HF configs are 10 fields, 56 wells, and 84 countries. The page strings “Showing 50 of 56” and “Showing 50 of 84” describe wells and countries, not a 56-field/84-well baseline. V1 therefore does not silently reduce field coverage from 56 to 10. A regression test will compare every preserved config and will disclose any future count reduction before promotion.

### Standards and gaps

| Contract | Status | Source |
|---|---|---|
| parent approval before child implementation | binding | [workspace-hub #3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) |
| deterministic publisher/receipt before real pin | binding | [worldenergydata #1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) |
| issue → plan → approval → TDD → review | binding | `AGENTS.md`, workspace plan workflow |
| security/legal/link/accessibility release checks | binding | website CI plus parent receipt schemas |

Gaps: the legacy renderer currently owns the parent route; local browser-data URLs are undefined; nested pages lack depth-aware roots; sitemap copying is static; `dist` replacement is not atomic over a populated directory; Playwright/axe dependencies and production deployment intent/reconciliation do not exist; and `field-economics-sensitivity` shares the same HF dataset.

### Embedded retrieval and reproduction evidence

```bash
git -C aceengineer-website show origin/main:scripts/hf-fetch.js | nl -ba
git -C aceengineer-website show origin/main:scripts/render-capabilities.js | nl -ba
git -C aceengineer-website show origin/main:build.js | nl -ba
gh pr view 73 -R vamseeachanta/aceengineer-website --json isDraft,files
curl -fsSL https://aceengineer.com/capabilities/field-explorer.html
```

Captured 2026-07-16: `DEFAULT_MAX_ROWS=100`, `MAX_TABLE_ROWS=50`; the legacy renderer owned `/capabilities/${id}.html`; build removed `dist` before later work; PR #73 was draft and overlapped registry/build/tests; production returned 200, no `<select>`, and the 56/84 well/country caps. A Node 24 probe confirmed renaming a candidate directory over populated `dist` returns `ENOTEMPTY`, so this plan now specifies a journaled two-rename recovery protocol rather than claiming one-step atomic replacement.

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-16-issue-74-website-pinned-field-well-drilldown.md` |
| Registry contract | `config/capabilities.yaml`, `docs/capabilities-registry.md` |
| HTML template family | `content/partials/capabilities/relational/` |
| Pinned ingestion/cache | `scripts/hf-pinned-snapshot.js`, `data/hf-cache/pinned/` |
| Release-coupled browser assets | `<staging>/assets/generated/capabilities/field-explorer/<release-hash>/` |
| Public deployed build identity | `<staging>/.well-known/field-explorer-build-receipt.json` |
| Protected release evidence workspace | runner-temporary `<RUNNER_TEMP>/field-explorer/<release-id>/` |
| Durable protected evidence | Actions artifact `field-explorer-release-<release-id>` with separate receipts and hashed index |
| Release workflows | `.github/workflows/verify-field-explorer-release.yml`, `.github/workflows/promote-field-explorer.yml` |

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
  parent:
    config: fields
    value_column: field_id
    label_column: display_name
    route_key_column: field_route_key
    url_parameter: field
  child:
    config: wells
    value_column: well_id
    label_column: display_name
    route_key_column: well_route_key
    parent_column: parent_field_id
    url_parameter: well
  duplicate_label_policy: append_stable_id_suffix
selectors:
  parent_label: Field
  child_label: Well
templates:
  page: capabilities/relational/page.html
  parent_panels:
    - field-summary.html
    - production-economics.html
    - well-list.html
  child_panels:
    - well-detail.html
routes:
  root: /capabilities/field-explorer.html
  parent_record: /capabilities/field-explorer/fields/{parent_route_key}.html
  child_record: /capabilities/field-explorer/fields/{parent_route_key}/wells/{child_route_key}.html
```

The validator will reject unknown schema majors, floating revisions, unsafe paths, duplicate template/route ownership, missing config/value/label/route/URL/parent keys, ambiguous duplicate labels without the declared policy, selector cycles, and relational capabilities wired to legacy floating refresh. A second synthetic hierarchy with different config/column names will prove that renderer logic is registry-generic rather than field/well hardcoded.

Core renderer/controller state will be named `parentKey`, `childKey`, `panelKey`, and `pageIndex`; DOM hooks will use `data-parent-*` and `data-child-*`. Field/well words will exist only in registry labels, config/column mappings, route literals, and field-specific panel filenames. The second hierarchy fixture will fail if core modules inspect `fields`, `wells`, `field_id`, or `well_id` directly.

The validator will require each declared route key to equal the single canonical safe encoding of its stable value ID. Producer route-key columns will be verification sidecars, not independent route authority; a mismatch will fail. Mutable labels/slugs will never change canonical routes.

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
/capabilities/field-explorer/fields/<stable-field-route-key>.html
/capabilities/field-explorer/fields/<stable-field-route-key>/wells/<stable-well-route-key>.html
```

Route keys will be deterministic safe encodings derived from stable IDs, not mutable display slugs. Mutable slugs will remain labels/aliases and may generate reviewed redirects, but will not define canonical identity. The no-JavaScript parent will expose the complete field index. Every field page will expose all child well links or an explicit zero-well state. Depth-aware `rootPath` values, breadcrumbs, canonical links, back-links, and generated sitemap entries will be produced for every route.

`page.html` will be the inherited shell for root, parent-record, and child-record pages. The renderer will supply a generic page-kind view model and ordered allowlisted panel partials; partials will not include or extend arbitrary data-provided paths. Required locals and panel outputs will be validated before render. The root-path calculator will derive depth from the generated output path and will be fixture-asserted as `../` for the root page, `../../../` for a parent-record page, and `../../../../../` for a nested child-record page. Full rendered-link tests will verify head, nav, CSS, JavaScript, images, breadcrumbs, canonical links, and back-links at each depth.

## Snapshot, Cache, and Promotion Contract

```text
validate registry before network access
derive cache key from dataset + exact HF SHA
fetch manifest via raw exact-revision URL
permit at most one same-origin exact-SHA resolve-cache redirect
validate manifest schema, safe paths and producer identity
fetch every declared browser shard from the same exact SHA
rehash and validate bytes, counts, schemas, ordering, IDs and joins
write only a fully validated revision cache under data/hf-cache/pinned
construct one relational model from that cache
render the whole site into a sibling staging directory
write deployable JSON only to <staging>/assets/generated/capabilities/<id>/<release-hash>/
fingerprint controller JavaScript and relational CSS into that release directory
bind exact fingerprinted JSON/JavaScript/CSS URLs in HTML and build receipt
never mutate tracked source assets during npm run build
run route/link/security/accessibility/build-receipt checks
journal promotion; rename dist to retained backup, then staging to dist
on any error/crash recover from journal/backup before another build
retain the prior deployed Vercel release and exact-revision cache on failure
```

The reviewed synthetic contract fixture will support Phase A without pretending to be a published revision. The real committed cache will enter only in Phase B from the verified #1045 receipt. A build may use only a complete cache for the configured revision. A different revision will never substitute silently. All release-coupled resources—JSON, controller JavaScript, and relational CSS—will use the release-hash URL; generated pages will not reference stable controller/style URLs under the existing year-long immutable `/assets/*` policy. An R1 page will therefore bind only R1 client/data/style bytes and an R2 page only R2 bytes. A failed build or deployment candidate will leave deployed R1 unchanged; local directory promotion will be crash-recoverable, not falsely described as single-operation atomic.

Every root, parent-record, and child-record page will visibly disclose the HF revision, producer source revision, materialization source (`exact-raw` or `exact-revision-cache`), and bounded fallback reason (`none`, `offline-build`, `network-unavailable`, or `raw-validation-failed`). Raw errors, local paths, hosts and secrets will not render. The same disclosure will remain present without JavaScript.

Promotion will support first build with no current `dist` and replacement builds. The durable checksummed journal will carry schema version, destination, staging, backup, expected tree digests, and phase; files and affected parent directories will be fsynced before the next phase. Recovery will define deterministic outcomes for no journal/no dist, prepared, old moved, new moved, committed, missing staging, missing backup, both trees present, orphan staging/backup, and malformed/truncated/checksum-invalid journals. Ambiguous or corrupt state will fail closed without deleting candidates and will emit an operator inventory. Automated recovery will select a tree only when its recorded digest validates, never by mtime.

## Files to Change

| Action | Path | Purpose |
|---|---|---|
| Update | `config/capabilities.yaml` | register exact relational snapshot, relationships, templates and routes |
| Update | `docs/capabilities-registry.md` | document relational schema and migration rules |
| Update | `scripts/validate-capabilities.js` | fail closed on relational registry defects |
| Update | `scripts/render-capabilities.js`, `scripts/hf-fetch.js` | explicitly yield relational entries to the new renderer; preserve legacy capabilities |
| Update | `scripts/verify-capabilities-online.js` | dispatch exact-revision relational verification instead of PASS-on-undefined/floating fallback |
| Create | `scripts/hf-pinned-snapshot.js` | exact-SHA fetch, redirect policy, manifest/shard validation and cache |
| Create | `scripts/refresh-pinned-capability-data.js` | explicit reviewed refresh command; no floating refresh |
| Create | `scripts/render-relational-capability.js` | safe view models and parent/child route generation |
| Create | `scripts/promote-build-output.js` | journaled backup/staging swap and crash recovery |
| Create | `scripts/write-field-explorer-build-receipt.js` | closed-schema build/route/input/tool evidence with artifact hashes |
| Create | `scripts/collect-field-explorer-browser-evidence.js` | Playwright assertion results and raw evidence hashes for preview/production smoke |
| Create | `.github/workflows/verify-field-explorer-release.yml` | protected build/browser/legal evidence with durable run and artifact provenance |
| Create | `.github/workflows/promote-field-explorer.yml` | protected candidate-bound Vercel intent/create/query/reconcile/rollback workflow |
| Create | `scripts/vercel-field-explorer-release.js` | intent metadata, zero/one/many reconciliation, deployment/rollback receipts |
| Update | `build.js` | orchestrate validated relational rendering transactionally |
| Update | `sitemap.xml` generation and `tests/js/build.test.js` | generate nested routes in staging and prevent later static-copy overwrite |
| Update | `content/partials/head-common.html`, `content/partials/nav.html` | consume validated depth-aware root paths for nested pages |
| Create | `content/partials/capabilities/relational/page.html` | standard parent page shell |
| Create | `content/partials/capabilities/relational/field-summary.html` | reusable field summary panel |
| Create | `content/partials/capabilities/relational/production-economics.html` | reusable analysis/economics panel |
| Create | `content/partials/capabilities/relational/well-list.html` | reusable complete/paginated well list |
| Create | `content/partials/capabilities/relational/well-detail.html` | reusable well drill-down panel |
| Create | `content/partials/capabilities/relational/generic-table.html` | bounded generic fallback panel |
| Create source | `assets/js/capability-drilldown.js` | local controller build input, fingerprinted into staging |
| Update/Create source | `assets/css/` relational styles | accessible style build inputs, fingerprinted into staging |
| Create Phase A | `tests/fixtures/relational-capability/` | reviewed synthetic generic hierarchy; never labeled as a real HF cache |
| Create Phase B | `data/hf-cache/pinned/<dataset>/<sha>/` | exact receipt-derived manifest/shards and metadata |
| Generate per build in staging | `.well-known/field-explorer-build-receipt.json` | bounded public commit/pin/template/data/route/tool identities and hashes |
| Generate in runner temp | separate build/browser/deployment receipts and evidence index | protected workflow artifacts, never tracked or served from `dist` |
| Update | `package.json`, `package-lock.json` | run all new Jest suites and pin Playwright/axe/link/evidence tooling |
| Update | `vercel.json` | content-addressed data caching and release workflow/output contract |
| Create/Update | `tests/` focused registry/snapshot/render/browser/build tests | TDD and regressions |

New implementation modules will remain at or below 400 lines and functions at or below 50 lines. The work will not enlarge `scripts/render-capabilities.js` into a second relational renderer.

No receipt will be written to tracked `artifacts/`, source `assets/`, or an unversioned local-only path. The public build receipt will contain only bounded public identities/hashes/counts. Preview-browser and deployment receipts will remain protected workflow artifacts and will not be served from `dist`; the deployment receipt will reference build/browser digests rather than copy their fields.

## Pseudocode

```text
load_relational_registry(entry):
    require exact dataset, 40-char revision and safe manifest path
    require stable parent/child keys and acyclic dependent selectors
    require real page and child-panel template paths
    require collision-free parent/field/well route patterns
    reject legacy floating refresh for this capability
    require generic config/value/label/route/url/parent mapping
    require legacy renderer/fetch/online verifier dispatch away from this mode
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
    render root page and complete parent-record index
    for each parent record: render allowlisted panels and all child links or empty state
    for each child record: render nested child page and parent context
    emit content-addressed JSON/controller/style bytes only inside staging
    bind exact fingerprinted URLs and visible revision/cache/fallback disclosures
    compute depth-aware root paths and stable-ID-derived canonical routes
    generate sitemap after all nested pages; never overwrite it by static copy
    verify route inventory and internal links before promotion
    write closed-schema build receipt containing command/tool/input/output hashes
```

```text
reduce_browser_state(state, action):
    parent change resets child and page, then filters children locally
    child change selects only a child of the active parent
    page change remains bounded and preserves parent/child/panel query state
    history updates a shareable URL without network data access
    invalid deep links recover visibly to a valid state
```

```text
promote_local(staging, dist, journal):
    validate optional current dist, complete staging and checksummed journal inputs
    fsync files, journal and affected parent directories at each durable phase
    if current dist exists rename it to unique retained backup
    rename staging to dist; on failure restore backup
    on startup recover by validated tree digest for every declared state
    corrupt or ambiguous state fails closed without deletion
```

```text
deploy_release(intent):
    require parent/child approvals, #1045 receipt and protected environment
    acquire non-cancelling concurrency keyed by Vercel project+target
    capture current production deployment and registry pin
    list bounded candidates by project/target/git SHA/creation window
    fetch details and match exact intent/run/HF metadata locally
    zero => create once and durably persist returned ID; one => resume; many/timeout => fail unknown
    before promotion require current production still equals captured expected current
    record deployment ID, run read-only smoke, and emit separate receipt
    before rollback require current production equals failed candidate
    failure => restore exact authorized prior deployment/pin or fail stale, then prove rollback
```

## Failing-First TDD Sequence

### Registry and pinned fetch

- Reject missing, floating, short, or nonhex revisions.
- Reject unsafe manifest/template/route paths and selector cycles.
- Reject relational capability wired to `capabilities-refresh.js`.
- Prove a second synthetic hierarchy with different config/column names renders without code changes.
- Prove core reducer/renderer state is parent/child generic and contains no field/well branches for that second hierarchy.
- Reject any producer route key that differs from the canonical encoding of its stable value ID.
- Prove Phase A performs no network, cache, live-registry, route-behavior, or deployment mutation.
- Prove Phase B rejects a missing/mismatched producer receipt or HF SHA.
- Rebase from PR #73's recorded merge SHA and prove its registry entries/tests survive before shared-file edits.
- Prove legacy renderer/fetch/online verification skips relational mode and exactly one writer owns the parent dist path.
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
- Assert route inventory equals `1 + manifest field_count + manifest well_count`; no website test hardcodes 10/56.
- Assert every breadcrumb, canonical link, back-link, field/well link, and sitemap entry resolves.
- Assert no-JS parent and field pages expose complete navigation and revision/provenance context.
- Assert stable-ID-derived route keys remain unchanged when labels/display slugs change; reviewed legacy slug redirects resolve.
- Assert duplicate labels use the declared stable-ID suffix policy and duplicate route keys fail.
- Assert nested page root paths resolve all shared head/nav/assets.
- Assert root/parent/child `rootPath` equals `../`, `../../../`, and `../../../../../` and every rendered asset resolves.
- Assert generated sitemap contains every nested route and is not overwritten by static copying.

### Browser controller

- Populate the registry-labeled parent selector from local validated data.
- Filter the child selector by the configured parent column and expose the empty-child state.
- Reach every well and every record beyond 100 through pagination.
- Reset invalid dependent state when the field changes.
- Parse and serialize field, well, panel, and page deep-link state.
- Preserve Back/Forward behavior and recover visibly from unknown IDs/pages.
- Pass keyboard, label, focus, live-region, and reduced-motion checks.
- Make no runtime request to Hugging Face or datasets-server.
- Load only the HTML-bound content-addressed data URL; stale R2 client plus rolled-back R1 page cannot mix bytes.
- Prove R1/R2 HTML cannot load the other release's fingerprinted controller, style, or data from cache.
- Prove root/parent/child pages disclose revision, source, raw/cache materialization and fallback reason without JavaScript.

### Build and promotion

- Fail before deleting or replacing current `dist` when registry/snapshot/render/link checks fail.
- Render the whole site in a sibling staging directory.
- Prove generated JSON/JavaScript/CSS exist only under staging and success/failure leave tracked source bytes unchanged.
- Prove first build without `dist` promotes complete staging.
- Exercise crash/failure at every journal phase; recovery restores a complete old or new `dist`, never a partial tree.
- Prove malformed/truncated journals and ambiguous trees fail closed without deletion.
- Promote only after route, link, CSP, accessibility, legal and build-receipt checks pass.
- Keep build, preview-browser and deployment receipts separate; reject schema/trust-boundary mixing.
- Collect browser evidence against preview first; production collection will be read-only and separately authorized.
- Bind each receipt to the exact allowlisted `.github/workflows/verify-field-explorer-release.yml` workflow_dispatch, protected target ref, reviewed head SHA, configured automation actor, run attempt 1, full-commit-pinned actions, named environment approval, attested artifact digest, and live Vercel deployment ID/environment/git SHA; fork/PR events, reruns, alternative workflows, or self-authored local PASS receipts will fail parent verification.
- Prove a failed R2 leaves R1 output and cache intact.
- Prove a registry-pin revert R2→R1 reproduces R1 content and stable URLs.
- Preserve legacy non-relational capability behavior through focused regression tests.
- Preserve `field-economics-sensitivity` parametric config/schema/row policy across the shared-dataset publish.
- Preflight exact protected environments, reviewers, prevent-self-review, actor allowlists and required secrets without mutating settings.
- Test Vercel intent reconciliation for zero/one/many deployments, timeout, crash and rollback.
- Prove two different intents for the same project/target serialize, stale expected-current blocks promotion/rollback, and reconciliation locally matches enumerated deployment metadata without a native intent filter.
- Prove `npm ci` installs pinned Playwright/axe tooling and the declared scripts discover/run every new suite.

## Acceptance Criteria

- [ ] This issue plan will receive T3 adversarial review and explicit user approval before implementation.
- [ ] Parent #3559 will be reviewed and explicitly approved before Phase A; real cache/pinning Phase B will wait for independently approved/published #1045 receipt artifacts.
- [ ] Phase A will be provably offline/non-production; Phase B will reject any pin not bound to the approved #1045 receipt.
- [ ] PR #73 will be merged/closed first; its final merge SHA and surviving registry behavior will be recorded before serialized shared-file edits.
- [ ] The generic registry will bind dataset/revision/manifest plus parent/child config, value, label, stable route key, URL parameter, parent column, duplicate-label policy, templates and route patterns.
- [ ] Core code/state will remain parent/child generic; a differently named hierarchy will pass without field/well branches.
- [ ] Production pinning will use the verified #1045 receipt and exact returned HF SHA.
- [ ] Every browser artifact will be fetched from the same raw exact revision and fully validated before rendering.
- [ ] No runtime browser request will target Hugging Face or datasets-server.
- [ ] Only a complete validated same-revision cache may support offline/outage builds; a different revision will never substitute.
- [ ] Actual HTML partials will define the page shell and reusable child panels; JavaScript will not own the markup contract.
- [ ] One parent, every field, and every well will receive a canonical static route with complete links and sitemap coverage.
- [ ] Legacy renderer/fetch/online verification will yield relational entries so the parent route has exactly one writer and no undefined-dataset soft PASS.
- [ ] The parent field dropdown and dependent well dropdown will reach all validated records, including records beyond 100.
- [ ] Shareable field/well/panel/page deep links and browser Back/Forward behavior will work without data refetch.
- [ ] No-JS output will provide useful field and well navigation, counts, provenance, revision, limitations, and zero-well states.
- [ ] Data values will remain inert through escaping, safe URL/path validation, and CSP-compatible rendering.
- [ ] Generated JSON, controller JavaScript and relational CSS will be written only inside the staged release-hash tree and HTML-bound by fingerprinted URLs; `npm run build` will leave tracked source byte-identical.
- [ ] Every generated page, including no-JS output, will visibly disclose exact revisions, raw/cache source and a bounded fallback reason.
- [ ] The full build will handle absent `dist`, every durable journal phase and corrupt/ambiguous journals without deleting the only valid tree.
- [ ] Public and protected receipts will use the single declared locations/lifecycle, remain separate, and cross-reference digests without trust-boundary mixing.
- [ ] Parent #3559 will be able to live-fetch the protected Actions run/artifact and Vercel deployment metadata and prove that the deployed website registry blob pins the receipt HF SHA.
- [ ] An R1→R2→R1 rollback exercise will run on preview only; a fresh explicit user authorization will be required before production promotion.
- [ ] Repository-admin protected environments/reviewers/actors/secrets will be explicit prerequisites with read-only preflight; plan approval will not authorize provisioning them.
- [ ] Production operations will serialize by project+target, reconcile candidates by local metadata inspection rather than an assumed native intent filter, enforce expected-current guards before promotion/rollback, and prove rollback to the prior deployment/pin.
- [ ] Nested route roots and generated sitemap will pass focused regressions; static sitemap copying will not overwrite generated entries.
- [ ] Pinned Playwright/axe/link tooling and test discovery will be declared in package files and pass from clean `npm ci`.
- [ ] Stable canonical route keys will derive from stable IDs, not mutable slugs; cross-revision label/slug changes will preserve canonical URLs.
- [ ] Shared `field-economics-sensitivity` config/schema compatibility and current 10-field/56-well/84-country counts will be checked; any real coverage reduction will require explicit disclosure before promotion.
- [ ] Pin rollback will restore the earlier whole snapshot without changing canonical field/well URLs.
- [ ] Focused tests, full tests, link/accessibility/browser checks, legal/security scans, and T3 code/artifact review will have no unresolved MAJOR finding.
- [ ] The issue will receive a closeout comment linking the website commit, pinned HF SHA, build/deployment evidence, route/count report, rollback target, and named residual gaps.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | shared dataset, route collision, count interpretation, producer dependency |
| Codex | MAJOR | evidence contract, generic registry, dispatch, content-addressing, promotion recovery, receipts, routes/tooling/URLs, parent dependency |
| Gemini | UNAVAILABLE | no non-interactive authentication configured |

**Round 1 result:** MAJOR consensus from both working providers. A user-authorized isolated adjudication of commit `7f1f3f0...` confirmed substantive client/style cache mixing, cross-intent production races, generated-output transaction, fallback disclosure, recovery-state, genericity and receipt-location gaps. Those findings are incorporated in this draft; this issue remains `status:needs-plan` until the corrected artifact receives a no-MAJOR disposition.

## Risks and Fixed Decisions

- **Upstream overlap:** PR #73 is a real implementation blocker for shared paths, not a reason to weaken or bypass the plan.
- **HF redirect behavior:** browser JSON will remain regular Git blobs. Only a bounded same-origin exact-SHA resolve-cache redirect will be accepted.
- **Static-output size:** all field/well pages are intentional for accessibility, search, and no-JS drill-down. Pagination will bound individual panels without truncating the route inventory.
- **Template drift:** registry validation and render tests will bind actual partial files and required panel inputs.
- **Cache staleness:** cache identity is the exact SHA. A cached latest snapshot or different SHA is invalid.
- **Mixed snapshot:** tables will not hydrate independently. One manifest and one relational model will govern all pages.
- **Shared dataset:** #1045 must preserve or explicitly migrate `field-economics-sensitivity`; website promotion will test that live sibling.
- **Count interpretation:** current configs are 10 fields, 56 wells and 84 countries; the 56/84 page caps are not a 56-field/84-well baseline.
- **Admin prerequisites:** protected environment/reviewer/actor/secret setup is not yet verified and remains an explicit owner-controlled blocker for live release.
- **No open architecture decision:** build-time pinned ingestion, content-addressed local browser assets, actual child HTML partials, stable-ID routes, static nested pages, and crash-recoverable promotion are fixed; implementation correctness remains gated by tests/review.

## Complexity: T3

T3 is required because this implementation changes registry schema, external immutable-fetch semantics, data validation, reusable template architecture, static route generation, browser state, accessibility, security, build promotion, rollback, and cross-repository release evidence.
