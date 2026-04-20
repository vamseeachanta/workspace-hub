# Plan for #2367: Wire capability-summary-v1.pdf Download Link from Gallery CTA + 4 Methodology Pages (#2344 Follow-up)

> **Status:** draft v3 (revised 2026-04-20 after Codex round-2 REQUEST-CHANGES)
> **Complexity:** T1
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2367
> **Parent:** #2344 — capability-summary PDF render (plan-approved 2026-04-20; this follow-up carries deferred CTA-wiring scope)
> **Sequencing predecessors:**
> - #2344 implementation — will publish `aceengineer-website/assets/capability-summary-v1.pdf`. Until that asset is on disk and deployed, wiring a link here would produce a broken download. **Not yet cleared** at v2 draft time (`ls aceengineer-website/assets/ | grep -i capability` returns 0 matches).
> - #2342+#2343 Commit 2 — edits `aceengineer-website/content/demos/index.html` (gallery CTA set). **Cleared 2026-04-20** as `aceengineer-website` main commit `1b4adf1`; this plan will proceed against current `main` with no predecessor conflict on the gallery file.
> **Cross-repo note:** All edits below will land inside the nested `aceengineer-website/` git repo. Verified via `cd aceengineer-website && git remote -v` at v2 draft: `origin  https://github.com/vamseeachanta/aceengineer-website.git (push)`. Commits and `git push` will target that repo's remote, **not** `workspace-hub`. This plan file and its index row are the only artifacts that live in `workspace-hub`.
> **Review artifacts:** `scripts/review/results/2026-04-20-plan-2367-claude.md` (round 1, MINOR, 8 findings — addressed in v2) | `scripts/review/results/2026-04-20-v2-plan-2367-claude.md` (round 2, APPROVE — all 8 v1 fixes verified) | Codex round-1 silent-dropped (no artifact) | `scripts/review/results/2026-04-20-v2-plan-2367-codex.md` (round 2, REQUEST-CHANGES, 2 findings — this v3 addresses them: F1 independent 1-page gate; F2 structural placement tests) | Gemini TBD

---

## Resource Intelligence Summary

### Existing repo code

- **Found:** `aceengineer-website/content/demos/index.html` (472 lines, post Commit-2 merge). Gallery page with `rootPath: "../"` frontmatter. Hero section `<section class="demo-hero">` at lines 252–279 ("Overnight Parametric Engineering" + 4 KPIs). Demo cards follow. Closing CTA section `<section class="demo-cta-section">` at lines 456–467 (existing heading "Ready to Automate Your Analysis?", primary button "Get a Free Assessment" → `{{ rootPath }}contact.html` at line 462). **Placement decision (v2, see Finding 5 defence below):** place the new Download-Capability-Summary button in the **hero section** (`.demo-hero` / `.hero-kpis` adjacency, around line 275–277, inside the `col-md-10 col-md-offset-1 text-center` div after the KPIs block). Rationale: cold-email landings scroll-depth-decay on the gallery is steep; the hero gets the most attention; the closing `demo-cta-section` is secondary fallback. (v1 had silently picked the footer `demo-cta-section`; v2 reverses this per issue body "hero or footer" and defends hero as higher-conversion.)
- **Found:** `aceengineer-website/content/methodology/compound-engineering/index.html` (78 lines by `wc -l` — note the plan-drafter ran `wc -l` on trailing-newline-less file which reports 78; an earlier round-1 review claim of 80 used a different counting convention. The file body ends with `</html>` followed by no trailing newline; this line-count jitter is immaterial). Template used across all 4 methodology pages: `rootPath: "../../"` frontmatter; inline `<style>` block; `<article class="method-shell">` body with `method-toc`, section H2s, `method-cta` block embedded at the **end of line 79** (the file is one-line-minified HTML body: lines 1–4 are frontmatter, line 5 is `<!DOCTYPE html>`, line 6 is the `<style>` block, and line 79 contains the full article + `method-cta` + `<include src="partials/footer.html"></include></body></html>` on a single unbroken line). The `method-cta` block contains: `<div class="method-cta text-center"><h2>Apply this methodology to your project</h2><p>We use these delivery patterns...</p><a class="btn btn-primary btn-lg" href="../../contact.html">Talk to ACE Engineering</a></div>`. **The `method-cta` block is the correct insertion point** — the new Download-PDF button sits alongside the existing "Talk to ACE Engineering" primary CTA inside the same `method-cta` div. (v2 default resolution of open question Q2; see Open Questions section.)
- **Found:** `aceengineer-website/content/methodology/enforcement/index.html` (112 lines), `.../orchestrator-worker/index.html` (142 lines), `.../multi-agent-parity/index.html` (150 lines). All three use the identical `method-cta` block pattern at the end of their `article.method-shell` (verified via grep — same `Talk to ACE Engineering` button, same `href="../../contact.html"`, same heading copy). All 4 methodology files are **one-line-minified HTML bodies** (body content is on a single long line, not multi-line readable layout — the implementation agent will use **string-based Edit landmarks** (e.g., the literal `Talk to ACE Engineering</a>` closing tag) rather than line-based navigation to insert the new anchor). One insertion pattern applies across all 4 methodology pages.
- **Templating-consistency note (v2, Finding 1 from round 1):** The 4 methodology pages' **bodies currently contain zero `{{ rootPath }}` expressions** (verified `grep -c 'rootPath' content/methodology/*/index.html` → `1` per file, the frontmatter only). Existing body links use raw relative paths (e.g., `href="../../contact.html"`). Partials like `head-common.html` and `nav.html` do use `{{ rootPath }}` — but body content in these 4 pages does not. **Decision (v2):** prescribe the raw relative path `../../assets/capability-summary-v1.pdf` in methodology-page bodies (match surrounding code style), and the templated `{{ rootPath }}assets/capability-summary-v1.pdf` in the gallery body (the gallery body at line 462 already uses `{{ rootPath }}contact.html`, so this is consistent with surrounding code). This removes the templating-inconsistency finding: each file gets the pattern the rest of its body already uses. `build.js` posthtml-expressions will pass both through correctly.
- **Found:** `aceengineer-website/vercel.json` (57 lines) — no CSP header present; `X-Content-Type-Options: nosniff` set site-wide at lines 43–44 (v1 plan said lines 33–35 — corrected in v2). Browsers honour Vercel's `Content-Type: application/pdf` (auto-derived from `.pdf` extension); `<a href="…pdf" download>` resolves cleanly. No vercel.json edits required for this PR.
- **Not yet existing (will be produced by #2344 implementation):** `aceengineer-website/assets/capability-summary-v1.pdf`. The parent-plan Artifact Map explicitly marks this as `PRESCRIBED` — it is not in git at the time this plan file is drafted. This is a load-bearing sequencing constraint (see Risks).

### Standards
Not applicable — website-publishing + GTM deliverable, not an engineering calculation.

### LLM Wiki pages consulted
No relevant wiki pages — GTM content, not domain knowledge.

### Documents consulted

- **Issue #2367 body** (fetched via `gh issue view 2367`) — scope: CTA on gallery page + 4 methodology pages, all pointing at `/assets/capability-summary-v1.pdf`. Acceptance: CTA visible on all 5 pages; click downloads PDF (or opens in-browser viewer); live URL 200 on `www.aceengineer.com`; no collision with #2342/#2343 gallery edits.
- **Approved plan:** `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` — confirms the public filename decision `capability-summary-v1.pdf` (versioned to coexist with Vercel's `/assets/(.*)` immutable 1-year cache). Confirms #2367 is the filed follow-up for deferred CTA wiring (parent-plan line 13 and Artifact-Map residual). Confirms no vercel.json edits are needed for the PDF path.
- **Approved plan:** `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — Commit 2 of that plan modified `content/demos/index.html` to add 3 detail-report CTAs + 1 calculator adjacency CTA. **Commit 2 merged 2026-04-20 as `aceengineer-website` main commit `1b4adf1`**; this plan will proceed against the current post-Commit-2 `main`. Commit 2's Download-PDF-adjacent edits are to detail-report buttons using class `btn-info` (informational tone); v2 adopts the same `btn-info` class for our Download-Capability-Summary anchor for visual consistency (see Finding 7 / v1 Risks update).
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

T1 — see Files to Change. One additional anchor per page, placed inside the **hero** of the gallery and inside the **`.method-cta`** block on each methodology page. Per-file templating matches the surrounding code style of that specific file (v2 Finding 1 resolution).

**Gallery (`content/demos/index.html`, `rootPath: "../"`):** inside the existing `<section class="demo-hero">` block, after the `.hero-kpis` div closes (around line 275) and before the closing `</div></div></div></section>` of the hero, will add:

```html
<p style="margin-top: 30px;"><a href="{{ rootPath }}assets/capability-summary-v1.pdf" class="btn btn-info btn-lg" download>Download Capability Summary (PDF, 1 page)</a></p>
```

Gallery body already uses `{{ rootPath }}` (e.g., `contact.html` at line 462), so the templated expression matches surrounding style. Class `btn-info` matches the detail-report button class used in Commit 2.

**Each of 4 methodology pages (`content/methodology/<slug>/index.html`, `rootPath: "../../"`):** the HTML body is minified onto a single line; the implementation agent will use a **string-based Edit**, not a line-based one. The landmark is the literal string `href="../../contact.html">Talk to ACE Engineering</a>` (present in all 4 files). Insert immediately after the closing `</a>` of that anchor, still inside the surrounding `<div class="method-cta text-center">`:

```html
<a href="../../assets/capability-summary-v1.pdf" class="btn btn-info btn-lg" style="margin-left: 10px;" download>Download Capability Summary (PDF, 1 page)</a>
```

Raw relative path (not `{{ rootPath }}`) matches surrounding body-content style in methodology files (their bodies currently use raw relative paths with zero `{{ rootPath }}` body usage; templating is not in scope for methodology bodies). Class `btn-info` is consistent with #2342+#2343 Commit 2's detail-report buttons. Copy default `"Download Capability Summary (PDF, 1 page)"` includes file-size/page-count hint for accessibility (WCAG 2.1 best practice for download anchors).

The `download` attribute signals a save dialog; with Vercel returning `Content-Type: application/pdf` and `X-Content-Type-Options: nosniff` set, browsers that ignore the attribute (notably iOS Safari) will render the PDF inline in their built-in viewer. This is **acceptable by the issue's acceptance criterion** ("downloads ... or opens in-browser PDF viewer") — not a claim that "both behaviours satisfy" (v1's phrasing was too strong; v2 corrects per Finding 6).

---

## Files to Change

All rows are prescribed work performed during implementation (not by this plan-drafting commit). Single commit on the `aceengineer-website` repo; 5 files touched, each with a 1-line additive HTML edit.

| Action | Path | Reason |
|---|---|---|
| Modify | `aceengineer-website/content/demos/index.html` | Add Download-PDF anchor inside the `.demo-hero` block (after the `.hero-kpis` div). `{{ rootPath }}` prefix = `"../"`. Class `btn-info btn-lg` + `download`. |
| Modify | `aceengineer-website/content/methodology/compound-engineering/index.html` | Add Download-PDF anchor inside `.method-cta` block (immediately after the `Talk to ACE Engineering` anchor). Raw relative path `../../assets/capability-summary-v1.pdf` (body-style consistent). Minified file — use string-landmark Edit. Class `btn-info btn-lg` + `download`. |
| Modify | `aceengineer-website/content/methodology/enforcement/index.html` | Same pattern (minified; string-landmark Edit). |
| Modify | `aceengineer-website/content/methodology/orchestrator-worker/index.html` | Same pattern (minified; string-landmark Edit). |
| Modify | `aceengineer-website/content/methodology/multi-agent-parity/index.html` | Same pattern (minified; string-landmark Edit). |
| Update | `docs/plans/README.md` | Update row for this plan (performed by v2-revision drafting commit, not implementation). |

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
| cta_anchor_in_4_methodology_pages | grep | each of 4 methodology pages contains exactly one anchor to the PDF (raw relative path `../../assets/…`) | for each `<slug>` in {compound-engineering, enforcement, orchestrator-worker, multi-agent-parity}: `grep -c 'capability-summary-v1\.pdf' aceengineer-website/content/methodology/<slug>/index.html` == `1` |
| gallery_uses_rootpath | grep | gallery anchor uses `{{ rootPath }}assets/…` (body-style consistent with line 462 `{{ rootPath }}contact.html`) | `grep -E '\{\{\s*rootPath\s*\}\}assets/capability-summary-v1\.pdf' content/demos/index.html` returns 1 match |
| methodology_uses_relative | grep | each methodology-page anchor uses raw `../../assets/…` (body-style consistent with the 0-rootPath-in-body convention) | `grep -E '\.\./\.\./assets/capability-summary-v1\.pdf' <each methodology file>` returns 1 match each |
| download_attribute_present | grep | each anchor carries the `download` attribute | `grep 'capability-summary-v1.pdf.*download' <each file>` returns 1 match each |
| pdf_asset_exists_at_target | bash | `aceengineer-website/assets/capability-summary-v1.pdf` exists and is a non-trivial PDF before commit (sequencing gate for #2344 predecessor) | `test -s aceengineer-website/assets/capability-summary-v1.pdf && file aceengineer-website/assets/capability-summary-v1.pdf \| grep -q 'PDF document' && [ $(stat -c %s aceengineer-website/assets/capability-summary-v1.pdf) -gt 10000 ]` → exit 0. Upgraded from plain `-s` (v1) to size>10KB + magic-bytes check (Finding 2: `-s` passes on a 1-byte file). |
| pdf_is_one_page | bash + `pdfinfo` | CTAs hardcode the copy `"(PDF, 1 page)"` in all 5 anchors — the asset must actually be 1 page or every CTA mislabels (Codex v2 F1: independent re-verification of #2344's 1-page render claim, so drift in #2344 cannot silently produce a 2-page PDF that passes this plan's other gates) | `pdfinfo aceengineer-website/assets/capability-summary-v1.pdf \| awk '/^Pages:/{print $2}'` will equal `1` exactly. Exit non-zero on any other value. Runs BEFORE the CTA-wiring Edits are accepted as a pre-commit gate; if the asset is not 1 page, implementation will either (a) swap the copy to "(PDF, N pages)" and open a corrective issue against #2344, or (b) abort the commit and escalate. |
| npm_build_succeeds | bash + `npm run build` | posthtml-expressions renders all 5 pages without error | exit 0; `dist/demos/index.html` contains `../assets/capability-summary-v1.pdf` (rootPath=`../`); `dist/methodology/<slug>/index.html` each contain `../../assets/capability-summary-v1.pdf` anchor |
| cta_in_gallery_hero | bash + regex-scoped grep | gallery CTA anchor will sit inside the `.demo-hero` block, not in the footer `.demo-cta-section` (Codex v2 F2: placement-defaults are structurally tested, not just counted) | Extract the span between `<section class="demo-hero">` and its matching `</section>` from `content/demos/index.html` (via `awk '/<section class="demo-hero">/,/<\/section>/'` or equivalent). The extracted block will contain exactly 1 match for `capability-summary-v1\.pdf`. |
| cta_in_methodology_method_cta | bash + regex-scoped grep | for each of 4 methodology pages, the CTA anchor will sit inside the `.method-cta` block, not in `.method-toc` or any other container (Codex v2 F2: parameterized per-page structural gate) | For each `<slug>` in {compound-engineering, enforcement, orchestrator-worker, multi-agent-parity}: extract the span from `<div class="method-cta text-center">` up to (and including) its matching closing `</div>` on the minified body line, then `grep -c 'capability-summary-v1\.pdf'` on that extracted span. Pass: 1 per page. |
| cta_NOT_in_gallery_footer | bash + regex-scoped grep | negative assertion: no Download-PDF anchor will appear in the gallery footer `.demo-cta-section` block (Codex v2 F2: prevents accidental dual-placement if the implementation agent mis-edits both hero and footer) | Extract the span between `<section class="demo-cta-section">` and its matching `</section>` from `content/demos/index.html`. The extracted block will contain exactly 0 matches for `capability-summary-v1\.pdf`. |

**Post-deploy (live, after Vercel finishes building from `aceengineer-website` main push):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| prod_5_pages_200 | curl | Each of 5 pages returns HTTP 200 | `curl -sI https://www.aceengineer.com/demos/` and `…/methodology/<slug>/` for each of 4 slugs — all 200 |
| prod_cta_in_rendered_html | curl + grep | Each of 5 rendered pages' HTML body contains the basename `capability-summary-v1.pdf` (Finding 4: test grep basename, NOT `/assets/…`, because posthtml renders `../assets/…` from gallery and `../../assets/…` from methodology — a literal `/assets/…` grep would fail) | `curl -s https://www.aceengineer.com/<page>/ \| grep -c 'capability-summary-v1\.pdf'` ≥ 1 for each of 5 pages. Browsers resolve the relative URLs against the page URL and reach `https://www.aceengineer.com/assets/capability-summary-v1.pdf` at runtime — which is validated separately below. |
| prod_pdf_url_200_pdf_content_type | curl | `https://www.aceengineer.com/assets/capability-summary-v1.pdf` returns 200 with `Content-Type: application/pdf` | 2 header matches |
| spot_check_download | browser | Manually click one methodology-page CTA; browser either downloads the file or opens it in its PDF viewer | 1 successful download (or inline render — both in-spec per issue acceptance) |

Manual visual QA (explicitly out-of-automation): confirm the two buttons inside each `method-cta` block wrap gracefully on mobile and do not collide with the existing "Talk to ACE Engineering" button. Flagged as manual check, not an automated test.

---

## Acceptance Criteria

- [ ] `aceengineer-website/content/demos/index.html` will gain one anchor to `{{ rootPath }}assets/capability-summary-v1.pdf` inside the `.demo-hero` block (after `.hero-kpis`)
- [ ] Each of the 4 methodology pages (`compound-engineering`, `enforcement`, `orchestrator-worker`, `multi-agent-parity`) will gain one anchor to `../../assets/capability-summary-v1.pdf` (raw relative path, body-style consistent) inside its `.method-cta` block
- [ ] All 5 anchors will carry the `download` attribute, class `btn-info btn-lg`, copy `"Download Capability Summary (PDF, 1 page)"`, and link to the versioned basename `capability-summary-v1.pdf`
- [ ] **Pre-commit independent 1-page gate (v3 F1):** `pdfinfo aceengineer-website/assets/capability-summary-v1.pdf \| awk '/^Pages:/{print $2}'` will equal `1` exactly before CTA wiring is accepted; this plan independently re-verifies the 1-page claim rather than relying solely on #2344's render-side gate
- [ ] **Structural placement (v3 F2):** gallery CTA anchor will appear inside the `.demo-hero` section block and NOT inside the footer `.demo-cta-section` (regex-scoped grep both ways); each of 4 methodology-page CTA anchors will appear inside its `.method-cta` block (regex-scoped grep, one assertion per page)
- [ ] `npm run build` in `aceengineer-website/` will complete; `dist/demos/index.html` will contain `../assets/capability-summary-v1.pdf`; `dist/methodology/<slug>/index.html` will each contain `../../assets/capability-summary-v1.pdf`
- [ ] Post-deploy: all 5 pages will return HTTP 200; all 5 pages' rendered HTML will contain the basename `capability-summary-v1.pdf`; the absolute PDF URL `https://www.aceengineer.com/assets/capability-summary-v1.pdf` will return 200 with `Content-Type: application/pdf`
- [ ] Spot-check: clicking the CTA on one methodology page will download the PDF (or open it in the browser's PDF viewer — both in-spec per issue acceptance)
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

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (round 1) | MINOR | 8 findings: templating inconsistency (body-level `{{ rootPath }}` use); line-number drift; `/assets/...` literal-grep test would fail vs. relative rendered URLs; hero-vs-footer placement silently chosen; 3 open questions pushed to user without defaults; `btn-default` subordination logic likely backwards on dark gradient; `-s` pre-commit gate passes on 1-byte file; iOS Safari `download` claim too strong. All 8 addressed in v2. |
| Claude (round 2, v2) | APPROVE | All 8 v1 fixes verified against HEAD file-state; no new blocking findings. LOW observation A ("(PDF, 1 page)" copy couples to #2344's 1-page gate) was hardening-only; v3 F1 promotes it to an independent plan-level gate. |
| Codex (round 1) | silent-dropped | No artifact produced (ops context, not a plan issue — per `feedback_codex_sandbox_no_execution.md`). Retried at round-2 on v2 text. |
| Codex (round 2, v2) | REQUEST-CHANGES | 2 findings: (F1) CTAs hardcode `"1 page"` but v2 TDD only checks asset existence/type/size — drift in #2344 would mislabel CTAs undetected; (F2) placement tests grep only basename/counts, so an implementation that placed the CTA in `.method-toc` or gallery footer would still pass. Both addressed in v3: F1 → new TDD row `pdf_is_one_page` + matching acceptance; F2 → new TDD rows `cta_in_gallery_hero`, `cta_in_methodology_method_cta`, `cta_NOT_in_gallery_footer` + matching acceptance. |
| Gemini | TBD | pending |

**Overall result:** v2 addressed all 8 Claude round-1 findings (Claude round 2: APPROVE). v3 addresses both Codex round-2 REQUEST-CHANGES findings; round-3 review not dispatched by this revision turn.

---

## Risks and Open Questions

- **Risk (HIGH, mitigated by sequencing):** PDF not yet published at target path when CTA wires in → 404 on click. **Mitigation:** implementation gate test `pdf_asset_exists_at_target` (upgraded in v2 to size>10KB + PDF magic-bytes check, not plain `-s`) hard-fails before commit; plan explicitly sequences AFTER #2344 implementation lands the asset.
- **Risk (MEDIUM, cleared):** merge conflict on `aceengineer-website/content/demos/index.html` if this lands concurrently with #2342+#2343 Commit 2. **Status:** **cleared 2026-04-20** — Commit 2 merged as `1b4adf1`. v2 reads against post-Commit-2 main. The hero-insertion slot this plan targets (after `.hero-kpis`, around line 275) is not touched by Commit 2.
- **Risk (LOW, v2 update per Finding 7):** CTA button class rendering on dark gradient. The `.method-cta` CSS applies `background: linear-gradient(135deg, #2d3436 0%, #4a5568 100%); color: #fff;` — a white button (`btn-default`, v1's proposal) would visually dominate the primary CTA rather than subordinate it. **v2 decision:** use `btn-info btn-lg` (cyan/teal on dark gradient) — matches the detail-report button class used in #2342+#2343 Commit 2, is visually coordinate-not-dominant with the existing `btn-primary` "Talk to ACE Engineering", and harmonises across the 5 pages. Flag for manual visual QA on desktop + mobile during implementation.
- **Risk (LOW):** versioned filename drift — if #2344 publishes `-v2.pdf` before this PR lands (unlikely in the same-day window, but possible), the 5 anchors will point at a dead `-v1.pdf`. **Mitigation:** implementation-time sanity check: `ls aceengineer-website/assets/capability-summary-v*.pdf` and align the anchor literal to the actual current filename. Parent plan's version-bump policy (Codex MAJOR 4 in the #2344 Rollback section) already states the CTA-updater owns cross-updates on version bumps; this follow-up inherits that policy.
- **Risk (LOW, v2 Finding 5):** final PDF size not measured yet — copy `"(PDF, 1 page)"` uses page-count (known from #2344 plan) rather than KB size. If #2344 publishes a PDF >1 MB, the implementation agent may swap copy to `"(PDF, ~N MB, 1 page)"` at Edit time. Non-blocking.

### Open questions — v2 defaults (T1 discipline: approver objects; otherwise accept)

Per Finding 7 of Claude round 1, v2 promotes each open question from "please decide" to "default; flag for objection":

- **Q1 (CTA copy) — default:** `"Download Capability Summary (PDF, 1 page)"`. Includes file-scope hint for accessibility (WCAG 2.1 best practice for download anchors). Alternatives considered but rejected: `"Get our 1-page capability summary"` (GTM-flavoured but ambiguous on action); `"Download PDF (1 page)"` (too terse, no artifact name).
- **Q2 (methodology-page placement) — default:** inside the existing `.method-cta` block, immediately after the `Talk to ACE Engineering</a>` anchor. Rationale: `method-cta` is the bottom-of-page contextual CTA container — users who read the methodology all the way through are the warmest download-leads; placing the PDF adjacent to the existing primary CTA groups both actions naturally. Rejected alternative: `.method-toc` sidebar (redesigns the TOC block, higher visibility but at the cost of design coherence).
- **Q3 (demo detail-page scope) — default:** **separate follow-up issue**, not bundled into this plan. Rationale: issue #2367's body scopes to "gallery page + 4 methodology pages" verbatim; expanding to detail pages (`freespan.html`, `jumper-installation.html`, `mudmat.html`, `pipelay.html`, `wall-thickness.html` — note the 5th page `jumper-installation.html` Claude round 1 flagged as easily-forgotten) is worth the marginal GTM value but crosses the T1 scope-discipline line. **v2 will not expand scope here**; implementation agent will file a follow-up issue "Extend capability-summary CTA to 5 demo detail pages" after this plan deploys green, referencing this plan for the anchor pattern.
- **Q4 (gallery placement) — default:** **hero section** (inside `<section class="demo-hero">`, after `.hero-kpis`). v1 silently picked the footer `.demo-cta-section`; v2 reverses per Finding 3 (issue body says "hero or footer"). Rationale: cold-email landings typically have steep scroll-depth decay; the hero gets the most attention; `.demo-cta-section` at line 456 is secondary fallback. (The footer already hosts a strong "Get a Free Assessment" primary CTA — adding a Download-PDF alongside dilutes the footer's single-action clarity.)

**Approver action:** if any of Q1–Q4 defaults are wrong for you, object in your approval comment — otherwise `status:plan-approved` accepts all 4.

---

## Complexity: T1

**T1 justified.**
- 5 files × 1-line additive HTML edit each = ~5 diff hunks, no new code paths, no new config, no new CI or test infrastructure.
- No new directories, no new dependencies, no new build steps.
- One commit, one push, Vercel rebuild. Rollback is a single `git revert`.
- Sequencing discipline (waits for #2344 + #2342/#2343 Commit 2) is a workflow constraint, not a T2 code complexity driver — it is operationally managed via the `status:plan-approved` + merge-order gate, not by the code.

**Not T2** despite touching 5 files: each file gets the identical 1-line edit, there is no new tested module, no pseudocode beyond a single anchor literal, and the rollback surface is trivial. T2 is reserved for new code + multiple assertions + non-trivial rollback (see #2344's T1→T2 reclassification for the contrast).

**T2 upgrade trigger (document for reviewer):** if adversarial review surfaces a need for custom per-page button styling (colour overrides, icon, separate CSS block per page to avoid wrap collision), reclassify to T2 and add a styling section. Current plan assumes the Bootstrap `btn-info btn-lg` default (matching Commit 2's detail-report button class) is sufficient.

---

## Revision history

- **v1 (2026-04-20, commit `3a2f6b695`):** initial draft — see prior Risks/Open Questions for v1 defaults (footer placement, `btn-default`, `{{ rootPath }}` in methodology bodies, 3 open questions pushed to user).
- **v2 (2026-04-20, this revision):** addresses all 8 findings from Claude round-1 MINOR review (`scripts/review/results/2026-04-20-plan-2367-claude.md`):
  1. Templating consistency: methodology bodies use raw `../../assets/…` (body-style consistent, zero `{{ rootPath }}` body usage); gallery uses `{{ rootPath }}assets/…` (matches line 462 `{{ rootPath }}contact.html`).
  2. Pre-commit gate upgraded from `-s` to size>10KB + PDF magic-bytes check.
  3. Line numbers corrected: `content/demos/index.html` 472 lines (was 468); `demo-cta-section` at 456 (was 451–463); `vercel.json` nosniff at 43–44 (was 33–35); `compound-engineering/index.html` 78 lines per wc -l. Acknowledged 4 methodology pages are one-line-minified bodies; implementation uses string-landmark Edits.
  4. Acceptance test `prod_cta_in_rendered_html` greps basename `capability-summary-v1.pdf`, not `/assets/…` absolute (which would fail against `../assets/…` / `../../assets/…` rendered relatives).
  5. Gallery placement: hero (defended per issue body "hero or footer"); footer noted as secondary fallback.
  6. Open questions: 3 defaults promoted (`"Download Capability Summary (PDF, 1 page)"`; `.method-cta` placement; detail-pages as separate follow-up). Q4 added for gallery placement.
  7. Class changed from `btn-default` to `btn-info` (consistent with #2342+#2343 Commit 2's detail-report buttons; avoids white-on-dark-gradient dominance).
  8. Resource Intelligence updated: Commit 2 cleared as `1b4adf1`; sequencing text acknowledges merged predecessor.

  Also: git-remote quoted (Finding audit); iOS-Safari download-attribute claim softened per Finding 6.
- **v3 (2026-04-20, this revision):** addresses Codex round-2 REQUEST-CHANGES (2 findings) after Claude round-2 APPROVE of v2 (`scripts/review/results/2026-04-20-v2-plan-2367-codex.md`, `...-v2-plan-2367-claude.md`):
  1. **F1 — independent 1-page PDF gate.** v2 hardcoded `"Download Capability Summary (PDF, 1 page)"` in all 5 CTAs but only checked asset existence/type/size. If #2344 drifted to a 2-page render, every CTA would mislabel undetected. v3 adds a new pre-commit TDD row `pdf_is_one_page` that runs `pdfinfo | awk '/^Pages:/{print $2}'` and hard-fails unless exactly `1`. This plan now independently re-verifies #2344's 1-page render claim. Acceptance gains a matching criterion. Rationale: cross-plan gates are independent of each other's drift; cheap insurance.
  2. **F2 — structural placement tests.** v2 tests greped basename/counts only; an implementation that placed the gallery CTA in the footer `.demo-cta-section` or the methodology CTA in `.method-toc` would still pass. v3 adds three new TDD rows — `cta_in_gallery_hero` (regex-scoped grep inside the `.demo-hero` span, positive), `cta_in_methodology_method_cta` (regex-scoped per-slug grep inside the `.method-cta` span, 4 positive assertions), and `cta_NOT_in_gallery_footer` (regex-scoped grep inside the `.demo-cta-section` span, negative — prevents accidental dual-placement). Acceptance gains a matching criterion summarising both directions.

  Also: Adversarial Review Summary table updated with Claude round-2 APPROVE and Codex round-2 REQUEST-CHANGES rows.
