# Plan for #2357: chore(seo) — backfill sitemap.xml apex-host entries to www host

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2357
> **Review artifacts:** latest plan-review artifacts under `scripts/review/results/` matching `*2357*sitemap-www-backfill*plan-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `aceengineer-website/sitemap.xml` — current source sitemap contains legacy apex-host `<loc>` entries plus 5 newer `www.` demo-detail entries; this is the primary implementation file.
- Found: `aceengineer-website/build.js` — already copies the root `sitemap.xml` into `dist/` on each build via `copySitemap()`, so #2391 removed the serving/404 blocker and this issue does not need another build-pipeline change.
- Found: `aceengineer-website/tests/js/demo-links.test.js` — currently asserts the 5 `/demos/*.html` sitemap entries exist at the `www` host, but does not yet enforce full-file host normalization.
- Gap: no existing test asserts that all `<loc>` entries in `sitemap.xml` use `https://www.aceengineer.com/`.

### Standards
Not applicable — static website SEO/canonicalization issue.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- Issue #2357 — defines the exact scope: replace apex-host sitemap `<loc>` entries with `www.` equivalents, keep metadata unchanged, avoid duplicates, validate XML.
- `docs/session-handoffs/2026-04-21-gtm-plan-review-implementation-v2.md` — elevates #2357 from low priority to critical now that `sitemap.xml` is live after #2391.
- `docs/session-handoffs/2026-04-20-gtm-plan-review-implementation.md` — earlier arc treated #2357 as a bundle/follow-up to the sitemap-serving fix.
- `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — parent GTM rollout plan that explicitly logged sitemap apex→www backfill as follow-up debt.
- Issue #2391 — confirms the serving fix already shipped in `aceengineer-website` and that the remaining problem is the crawler-visible host mismatch inside the sitemap content.

### Gaps identified
- No canonical local plan artifact existed for #2357 before this draft.
- No local review artifacts existed for #2357 before this draft.
- No local approval marker `.planning/plan-approved/2357.md` exists, so any live `status:plan-approved` label on GitHub must be treated as governance drift until reconciled.
- No regression test currently proves zero apex-host `<loc>` entries remain after the edit.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2357` — OPEN — `chore(seo): backfill sitemap.xml apex-host entries to www host (canonical redirect target)`
- `#2391` — CLOSED in handoff context / shipped to production; the remaining host-normalization work is intentionally split to #2357.

**File existence** (verified 2026-04-21):
- EXISTS: `aceengineer-website/sitemap.xml`
- EXISTS: `aceengineer-website/build.js`
- EXISTS: `aceengineer-website/tests/js/demo-links.test.js`
- EXISTS: `docs/plans/2026-04-21-issue-2357-sitemap-www-backfill.md`
- MISSING (not yet created): `.planning/plan-approved/2357.md`

**Tool availability** (verified 2026-04-21):
- `xmllint --version` exits 0 in the current implementation environment, so `xmllint` is the approved XML well-formedness gate for this issue.
- Normalized-collision preflight: current `aceengineer-website/sitemap.xml` has 39 `<loc>` entries and 0 duplicate normalized `https://www.aceengineer.com/...` values, so this host-only rewrite does not require deduplication logic.

**Line excerpts**

`aceengineer-website/sitemap.xml` (legacy apex examples + newer www demo-detail rows):
```xml
<loc>https://aceengineer.com/</loc>
<loc>https://aceengineer.com/about.html</loc>
...
<loc>https://www.aceengineer.com/demos/jumper-installation.html</loc>
<loc>https://www.aceengineer.com/demos/freespan.html</loc>
<loc>https://www.aceengineer.com/demos/wall-thickness.html</loc>
<loc>https://www.aceengineer.com/demos/mudmat.html</loc>
<loc>https://www.aceengineer.com/demos/pipelay.html</loc>
```

`aceengineer-website/tests/js/demo-links.test.js` (current test only covers 5 demo detail entries):
```js
const re = /<loc>\s*https:\/\/www\.aceengineer\.com\/demos\/([a-z-]+)\.html\s*<\/loc>/gi;
...
expect(found.sort()).toEqual([...DETAIL_SLUGS].sort());
```

**Gap proofs**
- `docs/plans/*2357*.md` search returned no prior canonical local plan file.
- `scripts/review/results/*2357*` search returned no prior review artifacts.
- `.planning/plan-approved/2357.md` does not exist.

Distinct sources consulted: 7 (`#2357` issue body, `aceengineer-website/sitemap.xml`, `aceengineer-website/build.js`, `aceengineer-website/tests/js/demo-links.test.js`, `docs/session-handoffs/2026-04-21-gtm-plan-review-implementation-v2.md`, `docs/session-handoffs/2026-04-20-gtm-plan-review-implementation.md`, `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2357-sitemap-www-backfill.md` |
| Implementation | `aceengineer-website/sitemap.xml` |
| Regression test | `aceengineer-website/tests/js/demo-links.test.js` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude | latest matching artifact under `scripts/review/results/*2357*sitemap-www-backfill*plan-claude.md` |
| Plan review — Codex | latest matching artifact under `scripts/review/results/*2357*sitemap-www-backfill*plan-codex.md` |
| Plan review — Gemini | latest matching artifact under `scripts/review/results/*2357*sitemap-www-backfill*plan-gemini.md` |

---

## Deliverable

`aceengineer-website/sitemap.xml` will use `https://www.aceengineer.com/...` for every `<loc>` entry, with unchanged non-host metadata and a regression test that fails if any apex-host `<loc>` entry reappears.

---

## Pseudocode

Trivial — see Files to Change.

Implementation shape:
```text
1. Extend or tighten Jest coverage first in aceengineer-website/tests/js/demo-links.test.js
2. Run the new sitemap assertions and confirm the apex-host check fails against the current sitemap
3. Edit aceengineer-website/sitemap.xml
4. Replace each <loc>https://aceengineer.com/... with https://www.aceengineer.com/...
5. Leave lastmod/changefreq/priority untouched row-for-row; normalized-collision preflight already proved there are no current apex→www duplicates to resolve
6. Re-run Jest and verify the durable regression checks: zero remaining apex-host <loc> entries, zero duplicate full <loc> values, and the existing 5 demo-detail entries still present at www host
7. Run one-time execution verification against the pre-edit snapshot: compare `<loc>` count before vs after and confirm per-row non-host metadata is unchanged after normalizing only the host prefix in `<loc>`
8. Run xmllint --noout aceengineer-website/sitemap.xml as a separate shell validation step after Jest and execution-time comparisons
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `aceengineer-website/sitemap.xml` | Rewrite all sitemap `<loc>` entries from apex host to canonical `www.` host |
| Modify | `aceengineer-website/tests/js/demo-links.test.js` | Add regression coverage that fails if any apex-host `<loc>` remains and that guards against accidental duplicate host variants |
| Update | `docs/plans/README.md` | Add this plan to the planning index |

---

## TDD Test List

### Durable regression tests (must remain after this issue ships)

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `sitemap_demo_detail_entries_at_www` | Existing 5 `/demos/*.html` entries remain present at `www` host | current `sitemap.xml` | same 5 detail slugs found |
| `sitemap_all_loc_values_are_www_and_nonempty` | Every parsed `<loc>` value is non-empty and matches `^https://www\.aceengineer\.com/` | updated `sitemap.xml` | all parsed locs pass the regex |
| `sitemap_each_url_has_one_loc` | Each `<url>` block contributes exactly one `<loc>` value after the rewrite | updated `sitemap.xml` | url-block count equals loc-value count |
| `sitemap_loc_values_are_unique` | The full set of `<loc>` values contains no duplicates after normalization | updated `sitemap.xml` | `Set(locValues).size === locValues.length` |

### One-time execution verification (for this migration run)

| Check name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `sitemap_metadata_is_unchanged_row_for_row` | Each row keeps the same `lastmod`, `changefreq`, and `priority`; only the host prefix in `<loc>` changes | pre-edit snapshot captured from the on-disk file before mutation + post-edit `sitemap.xml` | parsed row tuples match after normalizing only the host prefix |
| `sitemap_loc_count_preserved` | Host rewrite preserves the `<loc>` row count for the execution diff | pre-edit snapshot captured from the on-disk file before mutation + post-edit `sitemap.xml` | identical `<loc>` count before and after |
| `sitemap_xml_is_still_well_formed` | Separate shell validation step `xmllint --noout aceengineer-website/sitemap.xml` passes after the edit | updated `sitemap.xml` | exit code 0 |
| `execution_evidence_recorded` | Exact commands and before/after comparison summary are recorded in the GitHub implementation summary comment for #2357 | implementation summary comment | includes snapshot path or hash, `npm test`, `xmllint`, and before/after count+metadata results |

---

## Acceptance Criteria

### Durable merge blockers

- [ ] `aceengineer-website/sitemap.xml` contains zero apex-host or other non-`www` `<loc>` entries; every parsed `<loc>` is non-empty and matches `^https://www\.aceengineer\.com/`.
- [ ] Each `<url>` block has exactly one `<loc>` after the rewrite.
- [ ] The full set of `<loc>` values is unique after the host rewrite.
- [ ] Regression test coverage is added in `aceengineer-website/tests/js/demo-links.test.js` (or equivalent Jest file), is written before the sitemap edit, and passes via `cd aceengineer-website && npm test` after the rewrite.
- [ ] `xmllint --noout aceengineer-website/sitemap.xml` passes as a separate shell validation step after Jest.

### One-time execution verification for this migration

- [ ] `<loc>` row count is preserved before vs after the host-only rewrite.
- [ ] Non-host metadata (`<lastmod>`, `<changefreq>`, `<priority>`) is unchanged row-for-row, proven by a before/after comparison that normalizes only the host prefix in `<loc>`.
- [ ] A GitHub issue comment or implementation summary notes that the original issue body referred to `public/sitemap.xml` but the actual repo path is `aceengineer-website/sitemap.xml`, so future readers are not misled by stale path language.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet run |
| Codex | PENDING | not yet run |
| Gemini | PENDING | not yet run |

**Overall result:** PENDING — draft requires adversarial review before plan-review/user approval.

Revisions made based on review:
- None yet.

---

## Risks and Open Questions

- **Risk:** GitHub issue state appears to have drifted — live label may show `status:plan-approved` without the required local approval marker `.planning/plan-approved/2357.md`. This must not be treated as execution authorization until reconciled.
- **Risk:** The issue body still refers to `aceengineer-website/public/sitemap.xml`, while the actual tracked file is `aceengineer-website/sitemap.xml`. Implementation must follow the real repo path and record the path correction in the issue thread or implementation summary.
- **Risk:** `xmllint` is the chosen XML well-formedness gate and is already present in the current implementation environment (`xmllint --version` exits 0). If a future execution environment lacks it, stop before editing and re-run plan review with an approved fallback rather than improvising one.
- **Open:** None at plan-review time.

---

## Complexity: T1

**T1** — bounded single-artifact content rewrite plus one regression-test update, with no architecture change and no new module creation.
