# Plan for #2344: Complete #2090 — Render Branded 1-Page Capability-Summary PDF Leave-Behind

> **Status:** draft v2 (revised after 2026-04-19 adversarial review)
> **Complexity:** T2 (reclassified from T1 — v2 adds a committed render script + version-pinning + sidecar metadata + post-render assertions)
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2344
> **Parent (closed, unfinished):** #2090 — shipped markdown + HTML but omitted the PDF deliverable
> **Review artifacts:** `scripts/review/results/2026-04-19-plan-2344-claude.md` (MINOR) | Codex review (REQUEST-CHANGES / effective MAJOR — 4 MAJORs + 1 MINOR, captured in Adversarial Review Summary) | Gemini (not dispatched)

## Revision history

- **v1 (2026-04-19, commit `e348e76b1`):** initial draft. T1. Single inline Chrome headless command in commit body, no render script, Google Fonts fetched live, no font-embedding assertion, no Chrome-version pin, no cache-bust strategy. Scope explicitly deferred CTA wiring.
- **v2 (2026-04-19, this revision):** absorbs round-1 adversarial review. Reclassified T1→T2. Adds committed render script (`scripts/gtm/render-capability-summary-pdf.sh`) with pinned Chrome flags, version assert, fail-fast 1-page gate, `pdffonts` Inter-embedded assertion, `sha256sum` check, and sidecar `assets/capability-summary.pdf.meta` recording the renderer version. Vendors Inter WOFF2 locally under `aceengineer-website/assets/fonts/inter/` and rewrites the HTML `<link>` to a relative path to eliminate the Google Fonts network race and satisfy portability. Versioned public filename `capability-summary-v1.pdf` to work with Vercel's `/assets/(.*)` immutable 1-year cache (no vercel.json change needed). Rollback section corrected — removes the incorrect "browsers sniff" claim; vercel.json sets `X-Content-Type-Options: nosniff`. Scope reconcile: CTA wiring remains deferred but is now explicitly tracked as a filed follow-up referenced in this plan; see Scope Deviations From Issue Body.

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
- No PDF artifact exists at `docs/gtm/capability-summary.pdf` (internal canonical copy) or `aceengineer-website/assets/capability-summary-v1.pdf` (public asset copy — versioned filename per v2 revision; see Rollback Plan).
- **v1 gap addressed in v2:** Rendering was a throw-away inline command. v2 adds a committed `scripts/gtm/render-capability-summary-pdf.sh` that enforces reproducibility: asserts Chrome version, writes sidecar metadata, runs `pdfinfo`/`pdffonts`/`sha256sum` post-render gates, fail-fasts on !=1 page, fail-fasts if Inter is not embedded.
- **v1 gap addressed in v2:** Google Fonts network race. v2 vendors Inter WOFF2 locally under `aceengineer-website/assets/fonts/inter/` and rewrites the HTML `<link>` to relative paths so the render is offline-safe AND no longer silently falls back to system sans-serif. Additionally, the render script passes `--virtual-time-budget=5000` as a belt-and-braces mitigation for any remaining async stylesheet load.
- **v1 gap addressed in v2:** Chrome version drift. v2 asserts `google-chrome --version` major == `147` (documented approved) and hard-fails otherwise. Exact patch version is recorded in the sidecar `capability-summary.pdf.meta` file so a future regeneration can diff-check.

### Scope deviations from issue body

Issue #2344 body scope section lists four items. This plan explicitly:
- **Delivers 3 of 4:** render PDF, 1-page constraint gate, dual-placement commit.
- **Defers 1 of 4:** "Wire download link from gallery CTA and 4 methodology pages." Deferred because (a) the gallery CTA target HTML is being actively modified in in-flight #2342/#2343, (b) the four methodology pages do not all exist yet in `aceengineer-website/content/`, and (c) wiring requires its own 1-page PDF URL which cannot exist until this plan lands first. **v2 scope reconcile:** this deferral is tracked by filing issue `#2344-followup-cta-wiring` at PR time; the follow-up issue number is recorded in the commit body of this PR and referenced in `docs/plans/README.md` for this plan's row. No wiring happens in this PR.

### Source count
Distinct sources consulted: 6 (issue body + closed #2090 body + `capability-summary.md` + `capability-summary.html` + md-to-pdf SKILL.md + related demo-detail-pages plan). Exceeds minimum 3 required.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` |
| Render script (new, committed) | `scripts/gtm/render-capability-summary-pdf.sh` |
| PDF — internal canonical copy | `docs/gtm/capability-summary.pdf` |
| PDF — public asset (Vercel-served, versioned filename) | `aceengineer-website/assets/capability-summary-v1.pdf` |
| Sidecar metadata (renderer version, sha256) | `aceengineer-website/assets/capability-summary.pdf.meta` |
| Vendored fonts (new) | `aceengineer-website/assets/fonts/inter/Inter-Regular.woff2`, `Inter-SemiBold.woff2`, `Inter-Bold.woff2` (subset — exact family files picked during implementation to match HTML weight usage) |
| HTML source (edited — vendor-font `<link>` rewrite only) | `docs/gtm/website-pages/capability-summary.html` |
| Markdown source (existing, unchanged) | `docs/gtm/capability-summary.md` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude (round 1, MINOR) | `scripts/review/results/2026-04-19-plan-2344-claude.md` |
| Plan review — Codex (round 1, REQUEST-CHANGES) | recorded in Adversarial Review Summary below (review artifact not written to `scripts/review/results/` — findings reproduced inline in this plan) |
| Plan review — Gemini | not dispatched |

**No `dist/*` entries** — gitignored; Vercel rebuilds from `content/` + `assets/` on push.

---

## Deliverable

A committed 1-page Letter-size PDF at `docs/gtm/capability-summary.pdf` (internal) and `aceengineer-website/assets/capability-summary-v1.pdf` (public, versioned filename), rendered via Chrome headless `--print-to-pdf` from the existing `docs/gtm/website-pages/capability-summary.html` (with vendored-Inter `<link>` rewrite), preserving the hand-crafted navy/orange branded layout, the 1,292-cases proof point, the 3-tier pricing table, and the exact credentials line "Licensed P.E. — Houston, TX" (em-dash U+2014) in the footer. Render is produced by a committed, reproducible script (`scripts/gtm/render-capability-summary-pdf.sh`) that asserts Chrome version, verifies 1-page output, verifies Inter is embedded via `pdffonts`, and writes sidecar `capability-summary.pdf.meta` (renderer version + sha256). Public URL `https://www.aceengineer.com/assets/capability-summary-v1.pdf` returns HTTP 200 after Vercel deploy; versioned filename works correctly with Vercel's existing immutable 1-year cache rule on `/assets/(.*)`.

---

## Pseudocode

T2 — a committed bash script enforces reproducibility. The script is the sole render path; operators do not invoke Chrome by hand. Run from repo root:

```bash
bash scripts/gtm/render-capability-summary-pdf.sh
```

### `scripts/gtm/render-capability-summary-pdf.sh` — structure

```bash
#!/usr/bin/env bash
# Render capability-summary HTML -> 1-page PDF. Reproducible, fail-fast.
# Must be run from workspace-hub repo root.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

HTML_SRC="docs/gtm/website-pages/capability-summary.html"
PDF_INTERNAL="docs/gtm/capability-summary.pdf"
PDF_PUBLIC="aceengineer-website/assets/capability-summary-v1.pdf"
SIDECAR="aceengineer-website/assets/capability-summary.pdf.meta"
APPROVED_CHROME_MAJOR="147"

# --- 0. Precondition checks --------------------------------------------------
command -v google-chrome >/dev/null || { echo "FAIL: google-chrome not installed"; exit 1; }
command -v pdfinfo       >/dev/null || { echo "FAIL: pdfinfo (poppler-utils) not installed"; exit 1; }
command -v pdffonts      >/dev/null || { echo "FAIL: pdffonts (poppler-utils) not installed"; exit 1; }
command -v pdftotext     >/dev/null || { echo "FAIL: pdftotext (poppler-utils) not installed"; exit 1; }
command -v sha256sum     >/dev/null || { echo "FAIL: sha256sum not installed"; exit 1; }
test -f "$HTML_SRC"                 || { echo "FAIL: missing $HTML_SRC"; exit 1; }

# --- 1. Chrome version pin ---------------------------------------------------
CHROME_VERSION="$(google-chrome --version | awk '{print $NF}')"
CHROME_MAJOR="${CHROME_VERSION%%.*}"
if [ "$CHROME_MAJOR" != "$APPROVED_CHROME_MAJOR" ]; then
  echo "FAIL: Chrome major $CHROME_MAJOR != approved $APPROVED_CHROME_MAJOR"
  echo "Update APPROVED_CHROME_MAJOR in this script after re-verifying 1-page layout with the new Chrome."
  exit 1
fi
echo "Chrome version: $CHROME_VERSION (approved)"

# --- 2. Render ---------------------------------------------------------------
# Pinned flags; see flag-rationale comment block below this script body.
google-chrome \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --print-to-pdf="$PDF_INTERNAL" \
  --no-pdf-header-footer \
  --print-background \
  --virtual-time-budget=5000 \
  "file://$REPO_ROOT/$HTML_SRC"

# --- 3. Post-render assertions (fail-fast gates) -----------------------------
# 3a. Exactly 1 page
PAGES="$(pdfinfo "$PDF_INTERNAL" | awk '/^Pages:/{print $2}')"
if [ "$PAGES" != "1" ]; then
  echo "FAIL: rendered PDF is $PAGES pages; must be exactly 1. NOT staging. NOT copying to public asset path."
  echo "Investigate CSS overflow in $HTML_SRC (@media print / .body padding / .service margin) before retry."
  exit 1
fi

# 3b. Letter page size (612 x 792 pts)
if ! pdfinfo "$PDF_INTERNAL" | grep -qE "Page size:[[:space:]]+612 x 792 pts"; then
  echo "FAIL: page size is not Letter (612 x 792 pts)"
  pdfinfo "$PDF_INTERNAL" | grep "Page size"
  exit 1
fi

# 3c. Inter font embedded (font-portability gate)
if ! pdffonts "$PDF_INTERNAL" | awk 'NR>2 {print $1}' | grep -qi Inter; then
  echo "FAIL: Inter font not embedded in PDF (pdffonts)."
  echo "Check that aceengineer-website/assets/fonts/inter/*.woff2 files exist AND capability-summary.html <link> points at the vendored path."
  pdffonts "$PDF_INTERNAL"
  exit 1
fi

# 3d. Credentials line present with U+2014 em-dash
if ! pdftotext "$PDF_INTERNAL" - | grep -qE 'Licensed P\.E\. — Houston'; then
  echo "FAIL: credentials line 'Licensed P.E. — Houston, TX' (em-dash U+2014) not found in extracted text."
  exit 1
fi

# 3e. Proof-point survives render
if ! pdftotext "$PDF_INTERNAL" - | grep -q '1,292'; then
  echo "FAIL: '1,292' proof-point not found in extracted text"
  exit 1
fi

# --- 4. Copy to public asset path (versioned filename) ---------------------
cp "$PDF_INTERNAL" "$PDF_PUBLIC"

# --- 5. Write sidecar metadata --------------------------------------------
SHA="$(sha256sum "$PDF_INTERNAL" | awk '{print $1}')"
cat > "$SIDECAR" <<EOF
# capability-summary.pdf sidecar metadata
# Written by scripts/gtm/render-capability-summary-pdf.sh
renderer: google-chrome
renderer_version: $CHROME_VERSION
html_source: $HTML_SRC
rendered_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)
sha256_internal: $SHA
internal_path: $PDF_INTERNAL
public_path: $PDF_PUBLIC
public_url: https://www.aceengineer.com/assets/capability-summary-v1.pdf
EOF

echo "OK: rendered $PDF_INTERNAL ($PAGES page, Inter embedded, sha256=$SHA)"
echo "OK: copied to $PDF_PUBLIC"
echo "OK: sidecar written to $SIDECAR"
echo "Next: git add the three new/updated files, review diff, commit (DO NOT push)."
```

**Flag rationale:**
- `--no-sandbox`: required for container/CI; harmless on this host.
- `--disable-gpu`: Chrome headless quirk — prevents GPU-init error spam.
- `--no-pdf-header-footer`: suppresses Chrome's default "Page 1 / URL / timestamp" print headers.
- `--print-background`: **critical** — without it the navy/orange gradient header and proof-point dark-background render as blank white.
- `--virtual-time-budget=5000`: advances the virtual clock up to 5 s so any remaining async stylesheet/font load (even with vendored-local fonts there is still a `<link rel="stylesheet">` load cycle) completes before rasterization. Belt-and-braces because the primary mitigation is vendoring Inter locally.

**On gate failure:** the script exits non-zero before any `cp` or `git add`. Operator fixes the underlying cause (CSS for 1-page overflow, missing font file for embed failure, etc.) and re-runs. There is no code path where a 2-page or missing-Inter PDF reaches the public asset directory.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/gtm/render-capability-summary-pdf.sh` | Committed, reproducible render script (T2 reclassification). Pinned Chrome flags + version assert + post-render gates. |
| Create | `aceengineer-website/assets/fonts/inter/Inter-Regular.woff2` | Vendor Inter locally to remove Google Fonts network race; matches weights used in HTML (regular / semi-bold / bold — exact file set picked in implementation). |
| Create | `aceengineer-website/assets/fonts/inter/Inter-SemiBold.woff2` | Same — matches existing HTML weight usage. |
| Create | `aceengineer-website/assets/fonts/inter/Inter-Bold.woff2` | Same — matches existing HTML weight usage. |
| Edit | `docs/gtm/website-pages/capability-summary.html` | Rewrite Google Fonts `<link>` (lines 7–9) to local `@font-face` block pointing at vendored woff2 under `../../aceengineer-website/assets/fonts/inter/…` (relative-path from HTML location). No other changes. |
| Create | `docs/gtm/capability-summary.pdf` | Internal canonical 1-page PDF rendered from HTML source by the new script. |
| Create | `aceengineer-website/assets/capability-summary-v1.pdf` | Public-facing asset copy (versioned filename — future updates land as `-v2.pdf`, `-v3.pdf` etc., sidestepping Vercel's `/assets/(.*)` immutable 1-year cache). |
| Create | `aceengineer-website/assets/capability-summary.pdf.meta` | Sidecar metadata: renderer version, sha256, render timestamp. Replaces the v1-plan's "record version in commit body" approach — commit bodies are not machine-readable from the deployed site. |
| Update | `docs/plans/README.md` | Update plan index row: status `draft (v2)`, T2. |

**No edits to:**
- `docs/gtm/capability-summary.md` — #2090 already finalized content, no copy changes.
- `aceengineer-website/vercel.json` — **NOT edited.** v1 plan toyed with adding a `/assets/*.pdf` Content-Type override; v2 drops that because (a) the existing `X-Content-Type-Options: nosniff` header means browsers must trust the extension-inferred `application/pdf`, which Vercel auto-sets correctly for `.pdf`, (b) changing immutable-cache to skip PDFs would regress cache behavior for every asset and is not needed once we use versioned filenames.
- `aceengineer-website/content/*.html` — CTA wiring deferred; tracked as a filed follow-up (see Scope Deviations From Issue Body). Conflict with in-flight #2342/#2343 gallery work is the operational reason; the issue body's 4th scope item is explicitly acknowledged as deferred, not silently dropped.
- `aceengineer-website/sitemap.xml` — PDFs are not typically sitemap'd; skip unless SEO explicitly asks.

---

## TDD Test List

T2 — most gates are enforced **inside** `scripts/gtm/render-capability-summary-pdf.sh` (fail-fast; blocks `cp` + `git add`). The tests below are the same checks re-run manually for audit confidence before commit, plus the post-deploy public-URL check.

**In-script gates (the script exits non-zero if any fails — nothing reaches the public asset directory):**

| Gate | Tool | Claim | Pass criterion |
|---|---|---|---|
| chrome_version_pin | bash | Chrome major == 147 | `google-chrome --version \| awk '{print $NF}' \| cut -d. -f1` == `147` |
| pdf_is_one_page | pdfinfo | Rendered PDF is exactly 1 page | `pdfinfo … \| awk '/^Pages:/{print $2}'` == `1` |
| pdf_is_letter | pdfinfo | Page size is Letter (612 × 792 pts) | `pdfinfo … \| grep -qE 'Page size:[[:space:]]+612 x 792 pts'` |
| pdf_inter_embedded | pdffonts | Inter font is embedded (font portability) | `pdffonts … \| awk 'NR>2 {print $1}' \| grep -qi Inter` |
| pdf_has_credentials_line | pdftotext | Exact em-dash (U+2014) credentials line | `pdftotext … - \| grep -qE 'Licensed P\.E\. — Houston'` |
| pdf_has_proof_point | pdftotext | Proof-point "1,292" survives render | `pdftotext … - \| grep -q '1,292'` |

**Audit checks, run after the script succeeds and before `git commit`:**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| pdf_created_internal | bash | `docs/gtm/capability-summary.pdf` exists, non-empty | `test -s docs/gtm/capability-summary.pdf` → exit 0 |
| pdf_created_public | bash | `aceengineer-website/assets/capability-summary-v1.pdf` exists, non-empty | `test -s aceengineer-website/assets/capability-summary-v1.pdf` → exit 0 |
| dual_copies_identical | bash | Internal and public copies are bit-identical | `diff -q docs/gtm/capability-summary.pdf aceengineer-website/assets/capability-summary-v1.pdf` → no output |
| sidecar_written | bash | Sidecar has renderer version + sha256 | `grep -E '^renderer_version:' aceengineer-website/assets/capability-summary.pdf.meta` AND `grep -E '^sha256_internal:' …` → both exit 0 |
| pdf_has_tier_table | pdftotext | PDF contains "Screening", "Detailed", "Operations" (3 tier rows) | all 3 grep matches |
| script_is_executable | bash | Render script has +x bit | `test -x scripts/gtm/render-capability-summary-pdf.sh` → exit 0 |

**Post-deploy (after user pushes commit):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| public_url_200 | curl | `https://www.aceengineer.com/assets/capability-summary-v1.pdf` returns 200 with `Content-Type: application/pdf` | `curl -sI https://www.aceengineer.com/assets/capability-summary-v1.pdf \| grep -E 'HTTP/.*200\|application/pdf'` → 2 matches |

---

## Acceptance Criteria

- [ ] `scripts/gtm/render-capability-summary-pdf.sh` committed, executable, runs green end-to-end on this host
- [ ] `aceengineer-website/assets/fonts/inter/*.woff2` committed; `capability-summary.html` `<link>` rewritten to local paths
- [ ] `docs/gtm/capability-summary.pdf` committed, non-empty
- [ ] `aceengineer-website/assets/capability-summary-v1.pdf` committed, byte-identical to internal copy
- [ ] `aceengineer-website/assets/capability-summary.pdf.meta` committed; contains renderer version + sha256
- [ ] `pdfinfo` reports exactly 1 page (Letter, 612 × 792 pts) — gate enforced in script
- [ ] `pdffonts` shows Inter embedded — gate enforced in script
- [ ] `pdftotext` extraction contains: "Licensed P.E. — Houston" (U+2014 em-dash exact), "1,292", "Screening", "Detailed", "Operations"
- [ ] Chrome version at render time matches pinned major (147); recorded in sidecar
- [ ] Visual QA: brand header gradient renders (not blank white — `--print-background` worked)
- [ ] Visual QA: navy/orange color palette preserved (no greyscale fallback)
- [ ] Plan registered in `docs/plans/README.md` with status `draft (v2)`, complexity `T2`
- [ ] **Post-deploy (user, after push):** `curl -sI https://www.aceengineer.com/assets/capability-summary-v1.pdf` returns 200 + `application/pdf`
- [ ] **Follow-up filed at PR time:** "Wire capability-summary-v1.pdf download CTA from aceengineer-website gallery and 4 methodology pages" (deferred from #2344 scope; tracked per Scope Deviations From Issue Body)

---

## Rollback Plan

**Initial deploy (this PR).** Commit introduces a render script + vendored fonts + HTML `<link>` rewrite + two PDFs + a sidecar + one index row. No live-site regression because the PDF is a new asset; nothing on the live site currently links to `/assets/capability-summary-v1.pdf`. `docs/plans/README.md` gains one additive row.

**Rollback command (initial deploy):** `git revert <this-commit-sha>` → push. Vercel redeploys ≤5 min, removing the asset from `/assets/capability-summary-v1.pdf`. No cache-purge needed because no caller currently references the URL.

**Vercel immutable-cache strategy (addresses Codex MAJOR 4).** `vercel.json` line 22–28 sets `Cache-Control: public, max-age=31536000, immutable` for `/assets/(.*)`. This means: **a PDF published at a given URL is cached at edge + browser for 1 year and cannot be updated in place.** To handle future refreshes without fighting the cache:

- **Chosen strategy:** **versioned filenames.** Initial deploy is `capability-summary-v1.pdf`. A future content refresh publishes `capability-summary-v2.pdf` (new URL → new cache entry). Cold-email templates reference the current-version URL; templates get updated together with the new PDF. **Not chosen (alternatives considered and rejected):**
  - (b) Edit vercel.json to exempt `*.pdf` from immutable cache. Rejected — regresses cache behavior for every other asset that happens to be a PDF; low benefit because versioned filenames solve the same problem without vercel.json churn.
  - (c) Rely on Vercel dashboard cache purge. Rejected — manual step, not reproducible from repo state.

**Content-Type on Vercel.** Vercel auto-derives `Content-Type: application/pdf` from the `.pdf` extension. `vercel.json` line 32–36 sets `X-Content-Type-Options: nosniff` site-wide, so browsers **must** trust that header — there is no sniff fallback. Acceptance criterion `public_url_200` expects `application/pdf` and will catch any Vercel misconfiguration.

**Failure modes and responses:**
- **In-script gate fails (1-page, Inter-embedded, credentials line, Chrome version):** script exits non-zero before any file is staged. Operator fixes the root cause (CSS tweak, missing font file, Chrome update) and re-runs. There is no "commit anyway" bypass in the script — by design.
- **PDF is live but needs a content update (post-deploy):** rendered output = `capability-summary-v2.pdf`. Update the versioned filename in the render script constant + the sidecar + any cold-email template references (at that time). Old `-v1.pdf` URL continues to serve — no 404 for any in-flight email already sent. **Cache-bust runbook:** none needed — the new URL is cache-miss by construction. If, in an emergency, an old versioned URL must be invalidated, use the Vercel dashboard "Purge Cache" action (manual, out-of-repo).
- **Rollback wanted after CTA wiring has landed (future):** at that future point a `git revert` must revert **both** this PR's commit **and** the CTA-wiring commit, else the wired links 404. The CTA-wiring follow-up issue is expected to document this in its own rollback section.

---

## Adversarial Review Summary

### Round 1 (v1 plan, commit `e348e76b1`)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | F1 Google Fonts async race unmitigated (no `--virtual-time-budget`); F2 1-page claim untested in PDF form, pseudocode lets operator stage a 2-page PDF; F3 Letter-size assertion missing; F4 Content-Type rollback contradicts acceptance; F5 plan silently corrected issue body path without noting deviation; F6 em-dash tolerance masks render defect; F7 flag name note (low). |
| Codex | REQUEST-CHANGES (effective MAJOR) | MAJOR 1 — non-reproducible regeneration (no committed render script). MAJOR 2 — Chrome version drift not controlled. MAJOR 3 — font portability not asserted (no `pdffonts` check; Google Fonts remote). MAJOR 4 — rollback + cache assumptions contradicted by vercel.json immutable 1-year cache + `X-Content-Type-Options: nosniff`. MINOR — scope narrowed (CTA wiring punted) without reconciling issue body. |
| Gemini | not dispatched | — |

### v2 revisions applied

| Finding | Resolution |
|---|---|
| Codex MAJOR 1 (reproducibility) | Added `scripts/gtm/render-capability-summary-pdf.sh` — committed, pinned flags, post-render gates. Reclassified plan T1 → T2. |
| Codex MAJOR 2 (Chrome version drift) | Script asserts `google-chrome --version` major equals `APPROVED_CHROME_MAJOR=147` and hard-fails otherwise. Exact version recorded in sidecar `capability-summary.pdf.meta` (not just commit body — commit bodies are not machine-readable from the site). |
| Codex MAJOR 3 (font portability) | **Both mitigations applied:** (a) vendor Inter WOFF2 locally under `aceengineer-website/assets/fonts/inter/` and rewrite the HTML `<link>` to relative paths (removes Google Fonts network dependency entirely); (b) post-render `pdffonts` assertion that Inter is embedded — gate in render script. Chose vendoring (not pure-assert) because it also satisfies Claude F1 async-race risk. |
| Codex MAJOR 4 (rollback/vercel cache) | Rollback section rewritten. Strategy: **versioned public filename** `capability-summary-v1.pdf` (future refresh → `-v2.pdf`). vercel.json immutable-cache rule is preserved and correctly respected. Removed the incorrect "browsers sniff" claim — `X-Content-Type-Options: nosniff` means browsers must trust Vercel's declared Content-Type; Vercel correctly sets `application/pdf` from the extension; `vercel.json` is NOT edited. |
| Codex MINOR (scope reconcile) | Added "Scope deviations from issue body" subsection in Resource Intelligence. Deferral of CTA wiring is explicit, justified (in-flight #2342/#2343 collision + not-yet-existing methodology pages + chicken-and-egg on PDF URL), and tracked as a filed follow-up issue (issue number recorded at PR time). |
| Claude F1 (Google Fonts async race) | Primary: vendor Inter locally (see MAJOR 3). Secondary: `--virtual-time-budget=5000` added to Chrome flags as belt-and-braces. |
| Claude F2 (1-page fail-fast) | Render script fails with non-zero exit before `cp` or `git add` if `pdfinfo` reports pages != 1. |
| Claude F3 (Letter-size assert) | Additional gate: `pdfinfo \| grep -qE 'Page size:[[:space:]]+612 x 792 pts'`. |
| Claude F4 (Content-Type rollback contradiction) | Rollback rewritten — no follow-up kicked down the road. Vercel auto-sets `application/pdf` from extension; nosniff header forces browsers to respect it; accept criterion is honest. |
| Claude F5 (`dist/` path deviation) | Added explicit note that issue body's `dist/assets/` path was corrected to `assets/` because `dist/` is gitignored. |
| Claude F6 (em-dash tolerance) | Credentials grep tightened to require U+2014: `grep -qE 'Licensed P\.E\. — Houston'`. |
| Claude F7 (flag name) | No change — advisory only, Chrome 147 is pinned so current flag name is correct. |

**Overall result (v2):** all round-1 MAJOR findings resolved in-plan. Ready for round-2 adversarial review after user re-approves the plan scope.

---

## Risks and Open Questions

- **Risk (medium): 1-page overflow.** The HTML's print CSS was never actually rendered to PDF before (closed-#2090 skipped the PDF step). If the two-column body grid plus proof-point card plus 3-row tier table spills past one Letter page at 14px root font, the render will be 2 pages and the script exits non-zero before staging. **Mitigation:** in-script `pdfinfo` gate. If fail, tighten `.service { margin-bottom }` from 10px to 6px, or reduce `.header { padding: 28px 36px 22px }` before re-render. Max 2 iterations acceptable; if still >1 page, escalate to issue owner — likely a content-trim call not a CSS call.
- **Risk (low, was medium): font-rendering drift across Chrome versions.** v2 pins `APPROVED_CHROME_MAJOR=147` and hard-fails the script if Chrome is updated. Sidecar records exact patch version. A future Chrome update forces an intentional script bump + re-verify step, not a silent regression.
- **Risk (low, was medium): font network dependency.** v2 vendors Inter WOFF2 locally. Render is offline-safe. `--virtual-time-budget=5000` is kept as defence-in-depth for any remaining async stylesheet cycle. `pdffonts` gate asserts Inter is actually embedded in the output, catching any future regression.
- **Risk (low): `-webkit-print-color-adjust: exact` browser-engine coverage.** Chromium-family honors it. If we ever switch renderers (Firefox headless, WeasyPrint), colors may flatten. N/A for Chrome-only pipeline; not worth mitigating until pipeline changes.
- **Risk (low): versioned filename churn in cold-email templates.** When `-v2.pdf` ships, cold-email templates in `docs/gtm/gtm-plan-30day.md` must be updated in the same PR. **Mitigation:** include a grep check in the v2-refresh PR template: `grep -rn 'capability-summary-v[0-9]' docs/gtm/` must match expected template locations before merge.
- **Open question: Inter WOFF2 file provenance.** The vendored Inter files should come from rsms/inter upstream (OFL-1.1 licensed). Needs a one-line license attribution in `aceengineer-website/assets/fonts/inter/LICENSE` or equivalent — added during implementation; flagged here for reviewer awareness.
- **Open question: should the PDF be embedded-fonts-only (Inter subset) for PDF/A compliance?** Likely no — leave-behinds are not archival artifacts. Inter is still embedded per `pdffonts` assertion, which is enough for font-portability. Flagged for issue owner only if they push back.
- **Open question: does the cold-email outreach workflow expect the PDF at a specific filename matching Template A/B/C text?** v2 uses `capability-summary-v1.pdf` (versioned). Templates in `docs/gtm/gtm-plan-30day.md` reference `capability-summary.pdf` without a version suffix. Decision required before implementation: (a) update templates to include `-v1`, or (b) keep an unversioned redirect in `vercel.json`. Recommend (a) — less moving parts; flagged to issue owner.

---

## Complexity: T2 (reclassified from v1 T1 after adversarial review)

T2 justified in v2:
- **New committed code** — `scripts/gtm/render-capability-summary-pdf.sh` with pinned flags, version assertion, and six post-render gates. Non-trivial bash with explicit fail-fast behaviour.
- **Content edit** — HTML `<link>` rewrite to vendored fonts; requires the font files to exist before the HTML renders correctly.
- **Multiple new committed files** — render script, three WOFF2 font files, two PDFs, one sidecar, one HTML edit, one README index update. 8-ish files across two source trees (`docs/` + `aceengineer-website/`).
- **Non-trivial rollback** — versioned-filename strategy interacts with Vercel's immutable cache; future content refreshes require a script-constant bump + template sync, documented in Rollback Plan.

**Why v1 was T1 and v2 is T2:** v1 assumed "one inline Chrome command, two binary files, done." Codex round-1 review showed the reproducibility / Chrome-drift / font-portability / cache-handling obligations are large enough that treating them as informal steps is a defect path. The work to do them correctly is a committed script with real preconditions and real post-conditions, which crosses the T1/T2 line by the plan-complexity ladder (T2 = new code + multiple assertions + non-trivial rollback; still no new runtime service, no new dependency, no new CI job — so not T3).
