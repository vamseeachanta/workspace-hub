# Plan for #2367: Wire capability-summary-v1.pdf Download Link from Gallery CTA + 4 Methodology Pages (#2344 Follow-up)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2367
> **Parent:** #2344 — capability-summary PDF render (plan-approved 2026-04-20; this follow-up carries deferred CTA-wiring scope)
> **Sequencing predecessors (both must be merged before this lands):**
> - #2344 implementation — publishes `aceengineer-website/assets/capability-summary-v1.pdf`. Until that asset is on disk and deployed, wiring a link here produces a broken download.
> - #2342+#2343 Commit 2 — edits `aceengineer-website/content/demos/index.html` (gallery CTA set). Merging before Commit 2 lands risks a file-level conflict on the same HTML; merging after is trivial.
> **Cross-repo note:** All edits below land inside the nested `aceengineer-website/` git repo (confirmed as a separate repo by the #2342/#2343 Commit 1 agent). Commits and `git push` target that repo's remote, **not** `workspace-hub`. This plan file and its index row are the only artifacts that live in `workspace-hub`.
> **Review artifacts:** `scripts/review/results/2026-04-20-plan-2367-claude.md` (to be written when adversarial review dispatches) | Codex / Gemini TBD

---

## Resource Intelligence Summary

### Existing repo code

- **Found:** `aceengineer-website/content/demos/index.html` (468 lines). Gallery page with `rootPath: "../"` frontmatter. Hero section at lines 252–279 ("Overnight Parametric Engineering" + KPIs). Demo cards at lines 289–393. Closing CTA section `<section class="demo-cta-section">` at lines 451–463 (existing heading "Ready to Automate Your Analysis?", primary button "Get a Free Assessment" → `contact.html`). This final CTA section is the natural placement slot for the new Download-Capability-Summary button — placed alongside the existing "Get a Free Assessment" CTA keeps the two actions visually grouped at the close of the gallery.
- **Found:** `aceengineer-website/content/methodology/compound-engineering/index.html` (78 lines). Template used across all 4 methodology pages: `rootPath: "../../"` frontmatter; inline `<style>` block; `<article class="method-shell">` body with `method-toc`, section H2s, `method-cta` block at the end (line 78: `<div class="method-cta text-center"><h2>Apply this methodology to your project</h2><p>We use these delivery patterns...</p><a class="btn btn-primary btn-lg" href="../../contact.html">Talk to ACE Engineering</a></div>`). Ends with `<include src="partials/footer.html"></include>`. The `method-cta` block is the correct insertion point — the new Download-PDF button sits alongside the existing "Talk to ACE Engineering" primary CTA inside the same `method-cta` div.
- **Found:** `aceengineer-website/content/methodology/enforcement/index.html` (112 lines), `.../orchestrator-worker/index.html` (142 lines), `.../multi-agent-parity/index.html` (150 lines). All three use the identical `method-cta` block pattern at the end of their `article.method-shell` (verified via grep — same `Talk to ACE Engineering` button, same `href="../../contact.html"`, same heading copy). One insertion pattern applies across all 4 methodology pages.
- **Found:** `aceengineer-website/vercel.json` — no CSP header present; `X-Content-Type-Options: nosniff` set site-wide (line 33–35). Browsers honour Vercel's `Content-Type: application/pdf` (auto-derived from `.pdf` extension); `<a href="…pdf" download>` resolves cleanly. No vercel.json edits required for this PR.
- **Not yet existing (will be produced by #2344 implementation):** `aceengineer-website/assets/capability-summary-v1.pdf`. The parent-plan Artifact Map explicitly marks this as `PRESCRIBED` — it is not in git at the time this plan file is drafted. This is a load-bearing sequencing constraint (see Risks).

### Standards
Not applicable — website-publishing + GTM deliverable, not an engineering calculation.

### LLM Wiki pages consulted
No relevant wiki pages — GTM content, not domain knowledge.

### Documents consulted

- **Issue #2367 body** (fetched via `gh issue view 2367`) — scope: CTA on gallery page + 4 methodology pages, all pointing at `/assets/capability-summary-v1.pdf`. Acceptance: CTA visible on all 5 pages; click downloads PDF (or opens in-browser viewer); live URL 200 on `www.aceengineer.com`; no collision with #2342/#2343 gallery edits.
- **Approved plan:** `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` — confirms the public filename decision `capability-summary-v1.pdf` (versioned to coexist with Vercel's `/assets/(.*)` immutable 1-year cache). Confirms #2367 is the filed follow-up for deferred CTA wiring (parent-plan line 13 and Artifact-Map residual). Confirms no vercel.json edits are needed for the PDF path.
- **Approved plan:** `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — Commit 2 of that plan (per its Files-to-Change table) modifies `content/demos/index.html` to add 3 detail-report CTAs + 1 calculator adjacency CTA. Merging this #2367 plan before Commit 2 would produce a conflict on the same gallery file; merging after is trivial (new CTA section is below the demo cards Commit 2 touches).
- **Feedback:** `feedback_plan_past_tense_artifact_claims.md` — all artifact references in this plan are written as future/prescribed work, not as accomplished fact. The PDF does not yet exist in `aceengineer-website/assets/`; this plan describes work that `#2344 implementation` will unblock.

### Gaps identified

- No existing capability-summary download CTA anywhere in `aceengineer-website/content/` — verified by grepping for `capability-summary` across the content tree (0 hits at plan-draft time).
- No implementation of capability-summary-v1.pdf asset on disk yet — produced by #2344 implementation, not by this plan.

### Source count
Distinct sources consulted: 6 (issue #2367 body + #2344 approved plan + #2342/#2343 approved plan + gallery HTML + one methodology HTML + three sibling methodology HTMLs via grep + vercel.json = ≥5 distinct). Exceeds minimum 3 required.

---

## Artifact Map

| Artifact | Path | Status |
|---|---|---|
| This plan | `docs/plans/2026-04-20-issue-2367-pdf-cta-wiring.md` | PRESCRIBED (created by this drafting commit) |
| Gallery CTA edit | `aceengineer-website/content/demos/index.html` | PRESCRIBED (edit in implementation) |
| Methodology page CTA — compound-engineering | `aceengineer-website/content/methodology/compound-engineering/index.html` | PRESCRIBED (edit in implementation) |
| Methodology page CTA — enforcement | `aceengineer-website/content/methodology/enforcement/index.html` | PRESCRIBED (edit in implementation) |
| Methodology page CTA — orchestrator-worker | `aceengineer-website/content/methodology/orchestrator-worker/index.html` | PRESCRIBED (edit in implementation) |
| Methodology page CTA — multi-agent-parity | `aceengineer-website/content/methodology/multi-agent-parity/index.html` | PRESCRIBED (edit in implementation) |
| Public PDF (served, NOT produced here) | `aceengineer-website/assets/capability-summary-v1.pdf` | DEPENDENCY (produced by #2344 implementation; this plan only links to it) |
| Plan index row | `docs/plans/README.md` | PRESCRIBED (update in this drafting commit) |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2367-claude.md` | TBD (adversarial-review step, not dispatched here) |
| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2367-codex.md` | TBD |
| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2367-gemini.md` | TBD |

**No `dist/*` entries** — gitignored in aceengineer-website; Vercel rebuilds from `content/` + `assets/` on push.

---

## Deliverable

After implementation lands: a single "Download capability summary (PDF)" anchor visible on each of 5 pages — the demos gallery (`/demos/`) and the 4 methodology pages (`/methodology/compound-engineering/`, `/methodology/enforcement/`, `/methodology/orchestrator-worker/`, `/methodology/multi-agent-parity/`) — each pointing to `/assets/capability-summary-v1.pdf`. Click resolves to an HTTP 200 with `Content-Type: application/pdf`, downloading the file (or opening it in the browser's built-in PDF viewer).

---

## Pseudocode

T1 — see Files to Change. One additional anchor per page, placed inside each page's existing closing CTA container, using template-correct `{{ rootPath }}` prefixing for the `assets/…` path.

**Gallery (`content/demos/index.html`, `rootPath: "../"`):** inside the existing `<section class="demo-cta-section">` block, below the "Get a Free Assessment" button, add:

```html
<a href="{{ rootPath }}assets/capability-summary-v1.pdf" class="btn btn-default btn-lg" style="margin-left: 10px;" download>Download capability summary (PDF)</a>
```

**Each of 4 methodology pages (`content/methodology/<slug>/index.html`, `rootPath: "../../"`):** inside each page's existing `<div class="method-cta text-center">` block, after the "Talk to ACE Engineering" anchor, add:

```html
<a href="{{ rootPath }}assets/capability-summary-v1.pdf" class="btn btn-default btn-lg" style="margin-left: 10px;" download>Download capability summary (PDF)</a>
```

The `download` attribute is a signal to the browser to offer a save dialog; with Vercel returning `Content-Type: application/pdf` and `X-Content-Type-Options: nosniff` set, browsers that ignore the attribute will still render the PDF inline in their built-in viewer — both behaviours satisfy the issue's acceptance criterion.

---

## Files to Change

All rows are prescribed work performed during implementation (not by this plan-drafting commit). Single commit on the `aceengineer-website` repo; 5 files touched, each with a 1-line additive HTML edit.

| Action | Path | Reason |
|---|---|---|
| Modify | `aceengineer-website/content/demos/index.html` | Add Download-PDF anchor inside the closing `.demo-cta-section` block (alongside "Get a Free Assessment"). `{{ rootPath }}` prefix = `"../"`. |
| Modify | `aceengineer-website/content/methodology/compound-engineering/index.html` | Add Download-PDF anchor inside `.method-cta` block (alongside "Talk to ACE Engineering"). `{{ rootPath }}` prefix = `"../../"`. |
| Modify | `aceengineer-website/content/methodology/enforcement/index.html` | Same pattern. |
| Modify | `aceengineer-website/content/methodology/orchestrator-worker/index.html` | Same pattern. |
| Modify | `aceengineer-website/content/methodology/multi-agent-parity/index.html` | Same pattern. |
| Update | `docs/plans/README.md` | Add row for this plan (performed by drafting commit, not implementation). |

**No edits to:**
- `aceengineer-website/vercel.json` — Vercel auto-derives `Content-Type: application/pdf` from the `.pdf` extension; no header override needed.
- `aceengineer-website/sitemap.xml` — PDFs are not sitemapped on this site (the capability summary is a leave-behind, not a crawl target).
- `aceengineer-website/assets/capability-summary-v1.pdf` — produced by #2344 implementation; this plan is a downstream consumer.

---

## TDD Test List

**Pre-deploy (local, before commit on `aceengineer-website`):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| cta_anchor_in_gallery | grep | gallery HTML contains exactly one anchor to `{{ rootPath }}assets/capability-summary-v1.pdf` | `grep -c 'capability-summary-v1\.pdf' aceengineer-website/content/demos/index.html` == `1` |
| cta_anchor_in_4_methodology_pages | grep | each of 4 methodology pages contains exactly one anchor to the PDF | for each `<slug>` in {compound-engineering, enforcement, orchestrator-worker, multi-agent-parity}: `grep -c 'capability-summary-v1\.pdf' aceengineer-website/content/methodology/<slug>/index.html` == `1` |
| rootpath_prefix_correct | grep | each anchor uses `{{ rootPath }}assets/…` (not a hardcoded absolute path that would break the posthtml templating) | `grep -E '\{\{\s*rootPath\s*\}\}assets/capability-summary-v1\.pdf' <each file>` returns 1 match each |
| download_attribute_present | grep | each anchor carries the `download` attribute | `grep 'capability-summary-v1.pdf.*download' <each file>` returns 1 match each |
| pdf_asset_exists_at_target | bash | `aceengineer-website/assets/capability-summary-v1.pdf` exists before commit (sequencing gate for #2344 predecessor) | `test -s aceengineer-website/assets/capability-summary-v1.pdf` → exit 0 |
| npm_build_succeeds | bash + `npm run build` | posthtml-expressions renders all 5 pages without error | exit 0; `dist/demos/index.html` + `dist/methodology/<slug>/index.html` each contain a literal `/assets/capability-summary-v1.pdf` anchor |

**Post-deploy (live, after Vercel finishes building from `aceengineer-website` main push):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| prod_5_pages_200 | curl | Each of 5 pages returns HTTP 200 | `curl -sI https://www.aceengineer.com/demos/` and `…/methodology/<slug>/` for each of 4 slugs — all 200 |
| prod_cta_in_rendered_html | curl + grep | Each of 5 rendered pages' HTML body contains `/assets/capability-summary-v1.pdf` | 5/5 match |
| prod_pdf_url_200_pdf_content_type | curl | `https://www.aceengineer.com/assets/capability-summary-v1.pdf` returns 200 with `Content-Type: application/pdf` | 2 header matches |
| spot_check_download | browser | Manually click one methodology-page CTA; browser either downloads the file or opens it in its PDF viewer | 1 successful download |

Manual visual QA (explicitly out-of-automation): confirm the two buttons inside each `method-cta` block wrap gracefully on mobile and do not collide with the existing "Talk to ACE Engineering" button. Flagged as manual check, not an automated test.

---

## Acceptance Criteria

- [ ] `aceengineer-website/content/demos/index.html` gains one anchor to `{{ rootPath }}assets/capability-summary-v1.pdf` inside the closing `.demo-cta-section` block
- [ ] Each of the 4 methodology pages (`compound-engineering`, `enforcement`, `orchestrator-worker`, `multi-agent-parity`) gains the same anchor inside its `.method-cta` block with the correct `{{ rootPath }}` prefix (`../../`)
- [ ] All 5 anchors carry the `download` attribute and link to the versioned filename `capability-summary-v1.pdf`
- [ ] `npm run build` in `aceengineer-website/` completes; `dist/` renders the literal `/assets/capability-summary-v1.pdf` URL in all 5 pages
- [ ] Post-deploy: all 5 pages return HTTP 200; all 5 pages' rendered HTML contains `/assets/capability-summary-v1.pdf`; the PDF URL itself returns 200 with `Content-Type: application/pdf`
- [ ] Spot-check: clicking the CTA on one methodology page downloads the PDF (or opens it in the browser's PDF viewer)
- [ ] Review artifacts posted to `scripts/review/results/` after adversarial review completes
- [ ] **Sequencing acceptance:** implementation does not start until (a) #2344 implementation commit has published `aceengineer-website/assets/capability-summary-v1.pdf` on `main`, and (b) #2342+#2343 Commit 2 has merged to `aceengineer-website` main

---

## Rollback Plan

Single-commit change in the `aceengineer-website` repo. If any post-deploy check fails or the CTA breaks layout:

- **Rollback command:** `cd aceengineer-website && git revert <this-commit-sha> && git push` — Vercel rebuilds ≤5 min, removing the 5 anchors.
- **Blast radius:** 5 additive HTML edits; revert is clean. No config files, no assets, no build-chain files touched. No follow-up cache purge required (the underlying pages and the PDF asset are unaffected).
- **Partial rollback (if only one page has a visual bug):** revert only the one offending file with a follow-up commit, leaving the other 4 live.

---

## Adversarial Review Summary

<!-- Filled in after adversarial review step. Not dispatched as part of this drafting turn. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | pending |
| Codex | TBD | pending |
| Gemini | TBD | pending |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk (HIGH, mitigated by sequencing):** PDF not yet published at target path when CTA wires in → 404 on click. **Mitigation:** implementation gate test `pdf_asset_exists_at_target` hard-fails before commit; plan explicitly sequences AFTER #2344 implementation lands the asset.
- **Risk (MEDIUM, mitigated by sequencing):** merge conflict on `aceengineer-website/content/demos/index.html` if this lands concurrently with #2342+#2343 Commit 2 (which also edits the same file). **Mitigation:** plan explicitly sequences AFTER Commit 2 merges. The two edits target different sections (Commit 2 edits demo cards in the middle of the file; this plan edits the closing `demo-cta-section`), so even if the sequence slips, the conflict is small and resolvable.
- **Risk (LOW):** CTA placement collides visually with existing primary button on each methodology page — `method-cta` currently holds a single full-width `btn-primary btn-lg`. Adding a second `btn-lg` alongside may wrap on narrow viewports. **Mitigation:** use `btn-default` (not `btn-primary`) for the new button to visually subordinate it to "Talk to ACE Engineering"; rely on Bootstrap's default inline-block flow; flag for manual visual QA on desktop + mobile during implementation.
- **Risk (LOW):** versioned filename drift — if #2344 publishes `-v2.pdf` before this PR lands (unlikely in the same-day window, but possible), the 5 anchors will point at a dead `-v1.pdf`. **Mitigation:** implementation-time sanity check: `ls aceengineer-website/assets/capability-summary-v*.pdf` and align the anchor literal to the actual current filename. Parent plan's version-bump policy (Codex MAJOR 4 in the #2344 Rollback section) already states the CTA-updater owns cross-updates on version bumps; this follow-up inherits that policy.
- **Open question (FOR USER):** CTA button copy. This plan uses `"Download capability summary (PDF)"` as a neutral, descriptive label. Alternatives: `"Get our 1-page capability summary"` (more GTM-flavoured), or `"Download PDF (1 page)"` (more terse). **Flagged for user decision during plan approval.**
- **Open question (FOR USER):** Methodology-page CTA placement. This plan places the PDF button inside the existing `.method-cta` block alongside "Talk to ACE Engineering". An alternative is placing the PDF button inside the `.method-toc` sidebar at the top of each page (higher visibility, but redesigns the TOC block). **Flagged for user decision during plan approval.**
- **Open question (nice-to-have, not blocking):** should Demo-1–4 detail pages (shipped by #2342+#2343 Commit 2 — `freespan.html`, `wall-thickness.html`, `mudmat.html`, `pipelay.html`) also carry the Download-PDF CTA? Issue #2367's scope is gallery + 4 methodology pages only; adding the 4 detail pages would be scope creep. **Recommended:** file a follow-up issue after this one deploys if GTM asks; do not expand scope here.

---

## Complexity: T1

**T1 justified.**
- 5 files × 1-line additive HTML edit each = ~5 diff hunks, no new code paths, no new config, no new CI or test infrastructure.
- No new directories, no new dependencies, no new build steps.
- One commit, one push, Vercel rebuild. Rollback is a single `git revert`.
- Sequencing discipline (waits for #2344 + #2342/#2343 Commit 2) is a workflow constraint, not a T2 code complexity driver — it is operationally managed via the `status:plan-approved` + merge-order gate, not by the code.

**Not T2** despite touching 5 files: each file gets the identical 1-line edit, there is no new tested module, no pseudocode beyond a single anchor literal, and the rollback surface is trivial. T2 is reserved for new code + multiple assertions + non-trivial rollback (see #2344's T1→T2 reclassification for the contrast).

**T2 upgrade trigger (document for reviewer):** if adversarial review surfaces a need for custom per-page button styling (colour overrides, icon, separate CSS block per page to avoid wrap collision), reclassify to T2 and add a styling section. Current plan assumes the Bootstrap `btn-default btn-lg` default is sufficient.
