# Plan for #2344: Complete #2090 — Render Branded 1-Page Capability-Summary PDF Leave-Behind

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2344
> **Parent (closed, unfinished):** #2090 — shipped markdown + HTML but omitted the PDF deliverable
> **Review artifacts (pending):** `scripts/review/results/2026-04-19-plan-2344-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- **Found:** `docs/gtm/capability-summary.md` (41 lines) — markdown source delivered by #2090 commit `9e2ca90b3`. Two-section layout: What We Do (5 service domains with standards codes) + How We Work (tier table, standards tags, software tags). Contact footer line 41 already reads `info@aceengineer.com | aceengineer.com | Licensed P.E. --- Houston, TX` — satisfies the issue's credentials-line acceptance verbatim.
- **Found:** `docs/gtm/website-pages/capability-summary.html` (456 lines) — fully hand-crafted branded HTML with inline `<style>` block. Includes `@media print { @page { size: letter; margin: 0 } }` with `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` overrides for `.header`, `.proof`, `.eng-table thead th`. Design is **print-ready by construction** — a 1-page letter-size layout with two-column body grid (`1fr 0.7fr`), navy/orange brand gradient header, footer at lines 443-450 with the exact credentials string. **Internet dependency at render time:** uses Google Fonts `fonts.googleapis.com` Inter (lines 7-9).
- **Found:** `docs/gtm/capability-summary.pdf` — **absent** (`ls docs/gtm/*.pdf` → 0 hits). This is the gap #2344 targets.
- **Found:** `aceengineer-website/assets/` (not `content/assets/` — that dir is empty). Committed site assets live here: `css/`, `data/`, `favicon.svg`, `fonts/`, `img/`, `js/`. Posthtml build copies this dir wholesale to `dist/assets/`. **`dist/` is gitignored** (`aceengineer-website/.gitignore` line 2: `dist/`). Therefore the PDF must be committed at `aceengineer-website/assets/capability-summary.pdf` so Vercel picks it up on next build.
- **Found:** `aceengineer-website/content/` top-level pages (`about.html`, `index.html`, `engineering.html`, `contact.html`, etc.) but no current `capability-summary.html` page and no download link to a PDF. This PR creates the PDF only — wiring download links from website pages is out of scope (the issue body decomposition lists wiring as a secondary scope item; the plan defers it to a follow-up to avoid colliding with in-flight #2342/#2343 gallery work).
- **Found:** `.claude/skills/data/documents/md-to-pdf/SKILL.md` + `md_to_pdf.py` — Chrome-headless markdown-to-PDF skill. **Key property:** it injects the markdown body into its own `templates/base.html` + `components.css` (bespoke cover page + section headers + card + tier-header + score-chip + priority-badge styling). It does **not** pass through custom HTML/CSS. Using this skill would **replace** the hand-crafted branded design in `capability-summary.html` with the skill's generic corporate template — a regression vs. the work already shipped by #2090. The correct rendering path is **direct Chrome headless `--print-to-pdf`** on the existing HTML file, reusing the flag set that `md_to_pdf.py` already uses at lines 149-161 (`--no-sandbox --disable-gpu --print-to-pdf --no-pdf-header-footer --print-background`).
- **Confirmed:** `/usr/bin/google-chrome` installed (v147.0.7727.101), sufficient for Chrome headless `--print-to-pdf`. No install needed on this machine.

### Standards
Not applicable — this is a GTM/marketing deliverable, not an engineering calculation.

### LLM Wiki pages consulted
No relevant wiki pages — GTM content, not domain knowledge.

### Documents consulted
- **Closed parent #2090 body** (fetched via `gh issue view 2090`) — acceptance originally required "**Fits on 1 printed page** (or 2 half-pages)" and "**HTML version matches GTM report branding**" and "**PDF via Chrome headless print (or /data:md-to-pdf skill)**". The HTML and markdown were delivered; PDF was silently dropped. #2344 body cites the closure overclaim explicitly: "2026-04-15 exit summary: 'still needs PDF/rendered leave-behind'".
- **Issue #2344 body** — scope: render → 1-page constraint check → dual placement → CTA wiring. Acceptance: 1-page PDF, public URL returns 200, credentials line "Licensed P.E. — Houston, TX" (already in the HTML footer verbatim), matches branding.
- **Related plan:** `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — established pattern for aceengineer-website changes: Vercel auto-deploys from `main` push; `dist/` gitignored so assets commit to `content/` or `assets/` source; `vercel.json` has no CSP blocker. This plan reuses that deploy model.
- **Commit `9e2ca90b3`** (2026-04-10) — "feat(gtm): capability summary, capability map, expert profiles, LinkedIn calendar (#2090, #2095, #2098, #2099)". Confirms the HTML + MD were committed together; PDF was indeed never produced.
- **Memory:** `feedback_adversarial_review_stance.md` — every review prompt must force defect-hunting, not charitable reading. Applied in this plan's self-review before commit.

### Gaps identified
- No PDF artifact exists at `docs/gtm/capability-summary.pdf` (internal canonical copy) or `aceengineer-website/assets/capability-summary.pdf` (public asset copy).
- No rendering script or Makefile target automates regeneration; plan adds an inline one-shot command documented in the commit body — no permanent script because the source rarely changes (annual-or-less refresh cadence).
- Google Fonts dependency at render time is not offline-safe. Chrome headless with network access will fetch Inter from `fonts.googleapis.com` during `--print-to-pdf`. On a disconnected host this would silently fall back to system sans-serif and degrade branding. **Not a blocker on this machine** (internet available) but flagged as a risk.
- No CTA wiring from website pages to the PDF (out of scope per issue body decomposition — filed as follow-up at PR time to avoid colliding with #2342/#2343 gallery work).

### Source count
Distinct sources consulted: 6 (issue body + closed #2090 body + `capability-summary.md` + `capability-summary.html` + md-to-pdf SKILL.md + related demo-detail-pages plan). Exceeds minimum 3 required.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` |
| PDF — internal canonical copy | `docs/gtm/capability-summary.pdf` |
| PDF — public asset (Vercel-served) | `aceengineer-website/assets/capability-summary.pdf` |
| HTML source (existing, unchanged) | `docs/gtm/website-pages/capability-summary.html` |
| Markdown source (existing, unchanged) | `docs/gtm/capability-summary.md` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-19-plan-2344-claude.md` (not dispatched in this task) |
| Plan review — Codex | `scripts/review/results/2026-04-19-plan-2344-codex.md` (not dispatched in this task) |
| Plan review — Gemini | `scripts/review/results/2026-04-19-plan-2344-gemini.md` (not dispatched in this task) |

**No `dist/*` entries** — gitignored; Vercel rebuilds from `content/` + `assets/` on push.

---

## Deliverable

A committed 1-page Letter-size PDF at `docs/gtm/capability-summary.pdf` (internal) and `aceengineer-website/assets/capability-summary.pdf` (public), rendered via Chrome headless `--print-to-pdf` from the existing `docs/gtm/website-pages/capability-summary.html`, preserving the hand-crafted navy/orange branded layout, the 1,292-cases proof point, the 3-tier pricing table, and the exact credentials line "Licensed P.E. — Houston, TX" in the footer. Public URL `https://www.aceengineer.com/assets/capability-summary.pdf` returns HTTP 200 after Vercel deploy.

---

## Pseudocode

T1 — trivial. Rendering is a single Chrome headless invocation, not a new script. Commands documented in the commit body:

```bash
# From repo root. Chrome at /usr/bin/google-chrome (verified v147).
cd /mnt/local-analysis/workspace-hub

/usr/bin/google-chrome \
    --headless \
    --no-sandbox \
    --disable-gpu \
    --print-to-pdf=docs/gtm/capability-summary.pdf \
    --no-pdf-header-footer \
    --print-background \
    "file://$(pwd)/docs/gtm/website-pages/capability-summary.html"

# Verify 1-page constraint with pdfinfo (poppler-utils)
pdfinfo docs/gtm/capability-summary.pdf | grep "^Pages:"
# Expected: Pages:          1

# Copy to public asset path (identical binary)
cp docs/gtm/capability-summary.pdf aceengineer-website/assets/capability-summary.pdf

# Commit both (no push — user reviews)
git add docs/gtm/capability-summary.pdf aceengineer-website/assets/capability-summary.pdf
```

Flag rationale (same as md-to-pdf skill at `md_to_pdf.py:149-161`):
- `--no-sandbox`: required for container/CI; harmless on this host.
- `--disable-gpu`: Chrome headless quirk — prevents GPU-init error spam.
- `--no-pdf-header-footer`: suppresses Chrome's default "Page 1 / URL / timestamp" print headers.
- `--print-background`: **critical** — without it the navy/orange gradient header and proof-point dark-background render as blank white.

**If pdfinfo reports >1 page:** the CSS `@media print { @page { size: letter; margin: 0 } }` is not tightening enough. Mitigation before re-render: tighten `.body` padding or header padding in `capability-summary.html` — but measure first via `--window-size=816,1056` screenshot (letter @ 96dpi). This plan accepts that if the render produces 2 pages a follow-up CSS tweak is required; see Risks below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/gtm/capability-summary.pdf` | Internal canonical 1-page PDF rendered from existing HTML source |
| Create | `aceengineer-website/assets/capability-summary.pdf` | Public-facing asset copy; Vercel serves at `/assets/capability-summary.pdf` after push-triggered rebuild |
| Update | `docs/plans/README.md` | Register this plan in the index with status `draft` |

**No edits to:**
- `docs/gtm/capability-summary.md` — #2090 already finalized content, no copy changes.
- `docs/gtm/website-pages/capability-summary.html` — existing print CSS is sufficient; design unchanged.
- `aceengineer-website/content/*.html` — CTA wiring deferred to a separate follow-up issue to avoid conflict with #2342/#2343 gallery work already in flight.
- `aceengineer-website/sitemap.xml` — PDFs are not typically sitemap'd; skip unless SEO explicitly asks.

---

## TDD Test List

T1 — verification is manual + bash assertions rather than a Jest/pytest suite. Run before commit:

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| pdf_created_internal | bash | `docs/gtm/capability-summary.pdf` exists, non-empty | `test -s docs/gtm/capability-summary.pdf` → exit 0 |
| pdf_created_public | bash | `aceengineer-website/assets/capability-summary.pdf` exists, non-empty | `test -s aceengineer-website/assets/capability-summary.pdf` → exit 0 |
| pdf_is_one_page | pdfinfo | Rendered PDF is exactly 1 page (Letter) | `pdfinfo docs/gtm/capability-summary.pdf \| grep -c '^Pages:[[:space:]]*1$'` → 1 |
| pdf_has_credentials_line | pdftotext | PDF contains "Licensed P.E." near "Houston, TX" (em-dash tolerance: either `—` or `--`) | `pdftotext docs/gtm/capability-summary.pdf - \| grep -E 'Licensed P\.E\..*Houston'` → exit 0 |
| pdf_has_proof_point | pdftotext | PDF contains "1,292" (proof-point number must survive render) | `pdftotext docs/gtm/capability-summary.pdf - \| grep '1,292'` → exit 0 |
| pdf_has_tier_table | pdftotext | PDF contains "Screening", "Detailed", "Operations" (3 tier rows) | all 3 grep matches |
| dual_copies_identical | bash | Internal and public copies are bit-identical (same render, not two separate renders) | `diff -q docs/gtm/capability-summary.pdf aceengineer-website/assets/capability-summary.pdf` → no output |

**Post-deploy (after user pushes commit):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| public_url_200 | curl | `https://www.aceengineer.com/assets/capability-summary.pdf` returns 200 with `Content-Type: application/pdf` | `curl -sI https://www.aceengineer.com/assets/capability-summary.pdf \| grep -E 'HTTP/.*200\|application/pdf'` → 2 matches |

---

## Acceptance Criteria

- [ ] `docs/gtm/capability-summary.pdf` committed, non-empty
- [ ] `aceengineer-website/assets/capability-summary.pdf` committed, byte-identical to internal copy
- [ ] `pdfinfo` reports exactly 1 page (Letter size)
- [ ] `pdftotext` extraction contains: "Licensed P.E." co-occurring with "Houston", "1,292", "Screening", "Detailed", "Operations"
- [ ] Visual QA: brand header gradient renders (not blank white — `--print-background` worked)
- [ ] Visual QA: navy/orange color palette preserved (no greyscale fallback)
- [ ] Plan registered in `docs/plans/README.md` with status `draft`
- [ ] **Post-deploy (user, after push):** `curl -sI https://www.aceengineer.com/assets/capability-summary.pdf` returns 200 + `application/pdf`
- [ ] **Follow-up filed at PR time:** "Wire capability-summary.pdf download CTA from aceengineer-website gallery and 4 methodology pages" (deferred from #2344 scope)

---

## Rollback Plan

Trivial. Single commit introduces two new binary files and one index row. No live-site regression because:
- The PDF is a **new asset** — no existing URL currently 404s, no existing link currently points at it (CTA wiring is deferred). If the render is bad, nothing on the live site breaks; the PDF simply becomes a new orphan asset.
- `docs/plans/README.md` gains one additive row — revert is a one-line diff.

**Rollback command:** `git revert <this-commit-sha>` → push. Vercel redeploys ≤5 min, removing the asset from `/assets/capability-summary.pdf`. No cache-purge needed because no caller currently references the URL.

**Failure modes and responses:**
- **pdfinfo reports 2 pages:** do NOT commit. Tighten `.body` padding in `capability-summary.html` (not in this PR's scope — file a blocker follow-up). Alternative: accept 2 pages temporarily if the issue owner agrees, but relabel acceptance.
- **Fonts rendered as system sans-serif (network offline during render):** re-run with network access; the render is non-deterministic by construction due to the Google Fonts fetch. Long-term mitigation: vendor Inter via the same approach as #2342/#2343 Plotly vendoring — flagged as follow-up risk, not a v1 blocker.
- **Vercel serves PDF with `Content-Type: application/octet-stream` rather than `application/pdf`:** `vercel.json` headers for `/assets/(.*)` are already `immutable 1yr`; add an explicit `Content-Type: application/pdf` header for `/assets/*.pdf` in a follow-up. Browsers sniff PDFs regardless, so this is a correctness-not-function issue.

---

## Adversarial Review Summary

**Not dispatched in this task** (plan-drafting only per task instructions). Will be filled when the plan is routed through `scripts/cross-review/` before status change to `plan-review`.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending adversarial review.

---

## Risks and Open Questions

- **Risk (medium): 1-page overflow.** The HTML's print CSS was never actually rendered to PDF before (closed-#2090 skipped the PDF step). If the two-column body grid plus proof-point card plus 3-row tier table spills past one Letter page at 14px root font, the render will be 2 pages and acceptance fails. **Mitigation:** pdfinfo check is the first gate. If fail, tighten `.service { margin-bottom }` from 10px to 6px, or reduce `.header { padding: 28px 36px 22px }` before re-render. Max 2 iterations acceptable; if still >1 page, escalate to issue owner — likely a content-trim call not a CSS call.
- **Risk (medium): Google Fonts network dependency.** Chrome headless fetches `fonts.googleapis.com/css2?family=Inter` at render time. On an offline host or behind a strict firewall the render falls back to system sans-serif and the branded typography is lost silently (no error, just wrong font). **Mitigation for v1:** accept — this machine has internet. **Long-term follow-up:** vendor Inter WOFF2 to `docs/gtm/website-pages/fonts/` and rewrite the `<link>` to a relative path. Filed at PR time.
- **Risk (low): font-rendering drift across Chrome versions.** Same HTML rendered under Chrome 145 vs 147 may produce subtly different glyph metrics and push a border-case 1-page layout to 2. **Mitigation:** record the rendering Chrome version in the commit body; if Chrome auto-updates and a future re-render fails 1-page, the fix is a CSS tweak not a blocker.
- **Risk (low): `-webkit-print-color-adjust: exact` browser-engine coverage.** Chromium-family honors it. If we ever switch renderers (Firefox headless, WeasyPrint), colors may flatten. N/A for Chrome-only pipeline.
- **Open question: should the PDF be embedded-fonts-only (Inter subset embedded) for PDF/A compliance?** Likely no — leave-behinds are not archival artifacts. Flagged for issue owner if they push back.
- **Open question: does the cold-email outreach workflow expect the PDF at a specific filename matching Template A/B/C text?** Issue body says filename is `capability-summary.pdf` — matches. Templates in `docs/gtm/gtm-plan-30day.md` not rechecked here; if a template hard-codes a different filename, a rename + symlink is a follow-up.

---

## Complexity: T1

T1 justified:
- **No new code** — single Chrome invocation documented in the commit body, no script file added.
- **No tests beyond bash assertions** — pdfinfo + pdftotext checks are inline verification, not a pytest/Jest suite.
- **Two new binary files** — PDF rendered once, copied once. Zero logic.
- **Trivial rollback** — no live-site regression, single `git revert`.
- **Deferred scope** — CTA wiring to website pages is filed as a follow-up, not bundled here, precisely to keep this T1.

**Why not T2:** a T2 would be appropriate if the plan added a reusable `scripts/gtm/render-capability-summary.sh`, Jest link-check for the public URL, or sitemap.xml integration. None of those are needed for the narrow #2344 ask. If a script is later wanted for annual refresh cadence, it is a separate T1 follow-up.
