# Plan for #2438: fix(aceengineer-website): resolve canonical brand identity + ship real logo asset

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2438
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2438-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- **Found — nav template with inline SVG placeholder**: `aceengineer-website/content/partials/nav.html:10-14` draws an `<svg>` rect+text "A&CE" wordmark programmatically (no file asset).
- **Found — asset directory with NO logo file**: `aceengineer-website/assets/img/` contains only `case-studies/`, `demos/`, `samples/` subdirs; root-level `logo.png` and `logo.svg` do not exist.
- **Found — favicon uses `#b84315`, not the consolidated `#c85a2a`**: `aceengineer-website/assets/favicon.svg` (line 1) — `<rect ... fill="#b84315" rx="15"/>` with white `A` letter. This is a hue drift from the locked primary accent (see "Decisions already locked" below).
- **Found — Inter variable font self-hosted**: `aceengineer-website/assets/fonts/inter/InterVariable.woff2` exists with LICENSE. Brand typography should standardize on Inter to match site chrome.
- **Found — existing "AceEngineer"-named capability brief**: `aceengineer-website/assets/Capability Brief · AceEngineer.pdf` already uses the now-canonical wordmark. Useful as a visual reference for the new logo treatment.
- **Found — build pipeline is `content/` → (posthtml+include+expressions) → root + `dist/`**: `aceengineer-website/build.js` uses `srcDir='./content'`, `distDir='./dist'` and processes `content/**/*.html` excluding `partials/`. Implication: source edits must be in `content/`, but the root-level served files are also committed and currently contain the broken references — so a clean rebuild is mandatory.
- **Gap — no `aceengineer-website/brand/` directory**: confirmed missing. The brand sheet must be created from scratch.
- **Gap — no real raster or vector logo file exists in the `aceengineer-website` repo**: must be designed from scratch. For reference template, `digitalmodel/assets/logo/` has `digitalmodel_logo.svg` + `digitalmodel_logo_1280x640.png` + `digitalmodel_logo_preview.png` — same file-count pattern to mirror.

### Standards

Not applicable (brand-identity / frontend-design issue; no marine-engineering standard applies). The relevant external specs are:
- `schema.org/Organization` and `schema.org/BlogPosting` — JSON-LD `publisher.logo`, `image` fields must resolve to real images for Google Rich Results.
- Open Graph protocol + Twitter Card — `og:image`, `twitter:image` cascade from JSON-LD `image` when not set explicitly.

### LLM Wiki pages consulted

No relevant wiki pages — this is a brand/frontend issue, not engineering knowledge.

### Documents consulted

- `docs/reports/2026-04-21-claude-design-trial-2435-design-system.md` — trial report. Documents the palette-divergence finding (`#b84315` favicon vs `#d35400`/`#e67e22` Bootstrap alerts → consolidation on `#c85a2a`), confirms Inter + Ubuntu typography stack, records the 4 design decisions that were held open pending this issue. Also logs the seed blurb error ("A&CE (AceEngineer)" — wrong primary) that motivated resolution.
- `memory/project_claude_design_adoption.md` (user auto-memory, project-level) — records the locked brand hierarchy (AceEngineer primary / A&CE retired) and the **locked visual-DNA decision on #2440 Option B (do NOT inherit digitalmodel's navy+teal; keep `#c85a2a`)**. This removes the palette ambiguity.
- **Issue #2438 comment 2026-04-21T15:42:15Z** — scope consolidation: broken JSON-LD `logo.png` folded into this issue; `aceengineer-admin`/`aceengineer-strategy` brand use is downstream consumer, not a separate issue.
- **Issue #2438 comment 2026-04-21T18:49:55Z** — brand hierarchy locked (AceEngineer / Analytical & Computational Engineering for SEO / Achanta AceEngineer Inc. legal / A&CE retired). Sets the acceptance criteria for wordmark + copy.
- **Issue #2440 comment 2026-04-21T18:49:44Z** — Option B decision locked (deliberate differentiation from digitalmodel; keep `#c85a2a`).
- **Issue #2435 comment 2026-04-21T15:33:31Z** — design-system trial is HOLDING for this issue to land. Palette A (`#c85a2a`) is the pre-agreed primary once wordmark lands. No further decisions expected from #2435 before #2438 closes.
- **Issue #2434 (state OPEN)** — aceengineer-website Claude Design adoption umbrella; this issue is a direct blocker.

### Gaps identified

1. **No canonical logo asset** (svg + png variants) exists in `aceengineer-website/`.
2. **No brand sheet** documenting hierarchy, palette, typography, usage rules, forbidden treatments.
3. **Nav template** renders a placeholder SVG (`A&CE` text in a rect) rather than a real logo file.
4. **JSON-LD `logo` / `image` fields point to a non-existent file** in 14 HTML files (root + content/ duplicates).
5. **Wordmark `A&CE` contamination** extends far beyond nav into JSON-LD `publisher.name`, page `<title>` suffixes, `og:site_name`, `collection.name` — 185 occurrences across 20 HTML files (mix of "A&CE" literal and "Analytical & Computational Engineering" long-form).
6. **Favicon hue drift** (`#b84315`) vs. locked primary (`#c85a2a`) — may or may not be in-scope; flag as open question.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2438` — OPEN — "fix(aceengineer-website): resolve canonical brand identity + ship real logo asset"
- `#2434` — OPEN — "epic(aceengineer-website): Claude Design adoption — site-wide visual refresh"
- `#2435` — OPEN — "feat(aceengineer-website): establish design system in Claude Design — one-time compounding unlock" (HOLDING on #2438)
- `#2440` — OPEN — "decision: visual DNA coherence across aceengineer.com + digitalmodel" (decision locked in comment 2026-04-21T18:49:44Z; Option B; close-pending)

**File existence** (`ls` 2026-04-23):
- EXISTS: `aceengineer-website/content/partials/nav.html` (inline SVG placeholder)
- EXISTS: `aceengineer-website/assets/favicon.svg` (color `#b84315`)
- EXISTS: `aceengineer-website/assets/fonts/inter/InterVariable.woff2`
- EXISTS: `aceengineer-website/assets/Capability Brief · AceEngineer.pdf`
- EXISTS: `aceengineer-website/build.js` (posthtml pipeline `content/` → `dist/`)
- EXISTS: `digitalmodel/assets/logo/digitalmodel_logo.svg` (reference template)
- MISSING (this plan creates): `aceengineer-website/assets/img/logo.svg`
- MISSING (this plan creates): `aceengineer-website/assets/img/logo.png`
- MISSING (this plan creates): `aceengineer-website/assets/img/logo-1280x640.png` (social/og variant)
- MISSING (this plan creates): `aceengineer-website/brand/BRAND.md`

**Line excerpts** — nav placeholder (`sed -n 9,15p aceengineer-website/content/partials/nav.html`):
```
            <a href="{{ rootPath }}index.html" class="navbar-brand-link">
                <svg viewBox="0 0 120 50" xmlns="http://www.w3.org/2000/svg" class="navbar-logo" aria-labelledby="logoTitle">
                    <title id="logoTitle">Analytical & Computational Engineering</title>
                    <rect x="0" y="0" width="120" height="50" fill="#f0f0f0" rx="4"/>
                    <text x="60" y="28" text-anchor="middle" font-weight="bold" fill="#333" font-family="sans-serif" font-size="26">A&amp;CE</text>
                </svg>
            </a>
```

**Line excerpts** — representative broken JSON-LD (`sed -n 55,72p aceengineer-website/blog/ai-native-structural-analysis.html`):
```
    "@type": "BlogPosting",
    "headline": "AI-Native Structural Analysis: Why Traditional FEA is Changing",
    "image": "https://aceengineer.com/assets/img/logo.png",
    "datePublished": "2025-01-12T00:00:00Z",
    ...
    "publisher": {
        "@type": "Organization",
        "name": "Analytical & Computational Engineering",
        "logo": {
            "@type": "ImageObject",
            "url": "https://aceengineer.com/assets/img/logo.png"
        }
    }
```

**Gap proofs**:
- `ls aceengineer-website/assets/img/logo.*` → "No such file or directory" — confirms 14 HTML files reference a non-existent asset.
- `ls aceengineer-website/brand/` → "No such file or directory" — confirms brand sheet does not yet exist.
- `grep -rc "logo\.png" aceengineer-website --include="*.html"` → 14 files with broken reference.
- `grep -rc -E "A&CE|A&amp;CE|Analytical & Computational|Analytical &amp; Computational" aceengineer-website --include="*.html"` → 185 occurrences across 20 files (full scope of the wordmark/long-form sweep).
- Case-studies directory count: `find aceengineer-website/case-studies -maxdepth 2 -name "*.html"` → 7 files; each has `publisher.name = "Analytical & Computational Engineering"` per grep.

<!-- Source count: issue body + 5 related issues + 2 docs/memory artifacts + 12 code-file inspections = 20 distinct sources. Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2438-brand-identity-and-canonical-logo.md |
| Logo — vector | `aceengineer-website/assets/img/logo.svg` |
| Logo — raster (primary) | `aceengineer-website/assets/img/logo.png` |
| Logo — social/og variant | `aceengineer-website/assets/img/logo-1280x640.png` |
| Brand sheet | `aceengineer-website/brand/BRAND.md` |
| Nav template (modified) | `aceengineer-website/content/partials/nav.html` |
| JSON-LD / title / og sweep | `aceengineer-website/content/**/*.html` (source) + rebuild |
| Built output | `aceengineer-website/*.html`, `aceengineer-website/dist/` |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2438-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2438-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2438-gemini.md |

---

## Deliverable

One sentence: `aceengineer-website` ships a canonical **AceEngineer** logo asset (svg + png variants at `/assets/img/`), a brand sheet at `/brand/BRAND.md` documenting the locked naming hierarchy + palette + typography, a nav template that renders the real logo file instead of an inline SVG placeholder, and a JSON-LD / title / og-meta sweep that purges the retired `A&CE` wordmark from all served pages — unblocking #2435 and restoring SEO/social-preview integrity.

---

## Pseudocode

This is a **T3 bundle** of four loosely-coupled workstreams. Most of the work is asset creation, doc authoring, and template/text edits — not algorithm. Pseudocode captures only the non-trivial bits.

### A — Logo asset production

```
given wordmark = "AceEngineer" (single word per locked hierarchy)
      palette = { primary: "#c85a2a",               # consolidated from trial #2435
                   surface: "#3A404C",               # current hero slate
                   ink: "#1A1D23",                   # body text
                   paper: "#FFFFFF" }
      font = Inter Variable, weight 700 for wordmark

construct logo.svg:
    viewBox 0 0 W H    # design decision: W≈320, H≈80 for wordmark-only
    <text> at center, fill=primary, font-family=Inter, font-weight=700
    kerning tuned so "Ace" + "Engineer" read as one word (per brand hierarchy)
    optional: minimal mark (e.g. stylized hex or nothing) — decide during asset sprint

construct logo.png: rasterize logo.svg at 800x200 (retina 4x) → export PNG, sRGB, no alpha jagginess
construct logo-1280x640.png: square/landscape lockup for og:image, centered wordmark on paper background

acceptance for assets:
    svg validates with no embedded raster
    png files load without alpha artifacts at Twitter/LinkedIn card dimensions
    color picker on wordmark reads #c85a2a (± 1 LSB)
```

### B — Nav template rewire

```
in content/partials/nav.html:
    locate the <svg viewBox="0 0 120 50" ...> ... </svg> block at lines 10-14
    replace with:
        <img src="{{ rootPath }}assets/img/logo.svg"
             alt="AceEngineer"
             class="navbar-logo"
             width="..." height="..."
             loading="eager" fetchpriority="high">
    preserve {{ rootPath }} template variable (posthtml-expressions resolves it per page depth)
    preserve "navbar-logo" class (CSS in assets/css/styles.css sizes it)

verify: rebuild with `node build.js` (or `npm run build` if scripted) — all pages get the new nav
```

### C — JSON-LD / title / og sweep (mass audit)

```
for each html_file in content/**/*.html (and root-level *.html if build doesn't regenerate them):
    # Fix logo references (14 files affected)
    replace '"logo": "https://aceengineer.com/assets/img/logo.png"'       → keep (asset now exists)
    replace '"image": "https://aceengineer.com/assets/img/logo.png"'      → keep (asset now exists)
    replace publisher.logo.url reference                                   → keep (asset now exists)

    # Fix wordmark per locked hierarchy (185 occurrences across 20 files)
    replace '"A&CE Engineering Blog"'      in <title> → 'AceEngineer Blog'
    replace '"A&CE Engineering Case Studies"' in JSON-LD name → 'AceEngineer Case Studies'
    replace '"A&CE Energy Data Samples"'   in JSON-LD name → 'AceEngineer Energy Data Samples'
    replace any '"A&CE"' literal wordmark reference → 'AceEngineer'

    # og:site_name policy (per brand hierarchy comment):
    # - Keep "Analytical & Computational Engineering" ONLY where SEO-long-form is warranted
    #   (publisher.name in blog/case-study JSON-LD — these are archived semantic-search signals)
    # - Switch consumer-facing surfaces (og:site_name, og:title company suffix, <title> suffix)
    #   to "AceEngineer"

    # Nav SVG <title id="logoTitle"> stays as "Analytical & Computational Engineering"
    #   (SEO/a11y long-form per locked hierarchy)

verify: grep shows zero "A&CE" or "A&amp;CE" outside documented historical callouts (BRAND.md may cite as retired)
verify: grep shows no orphan "logo.png" references to paths that 404
verify: schema.org Structured Data Testing Tool passes for at least 1 blog + 1 case-study + index.html
```

### D — Brand sheet authoring

```
write aceengineer-website/brand/BRAND.md with sections:
    # AceEngineer — Brand Sheet

    ## Naming hierarchy (locked 2026-04-21)
    | Context | Treatment | Use in |
    | Consumer-facing | AceEngineer | site, social, marketing, design system, code comments |
    | SEO / a11y long-form | Analytical & Computational Engineering | SVG <title>, meta-description, JSON-LD publisher.name where semantic-search value exists |
    | Legal | Achanta AceEngineer Inc. | tax, banking, contracts, invoicing |
    | Retired — DO NOT USE | A&CE | (historical only; grep should return 0 outside this doc) |

    ## Wordmark
    - Font: Inter Variable, weight 700
    - Primary color: #c85a2a on paper; paper (#FFFFFF) on #c85a2a or #3A404C for inverse
    - Clearspace: minimum 0.5× cap-height on all sides
    - Forbidden: drop shadows, gradients, rotations, replacement fonts, recoloring outside locked palette

    ## Palette (locked from trial #2435 / #2440 Option B)
    | Role | Hex | Notes |
    | Primary accent | #c85a2a | consolidated from #b84315/#d35400/#e67e22; rust orange |
    | Surface dark | #3A404C | hero BG, nav |
    | Ink | #1A1D23 | body text |
    | Paper | #FFFFFF | body BG |

    ## Typography
    - Primary: Inter Variable, self-hosted at `/assets/fonts/inter/`
    - Fallback: Ubuntu (loaded from Google Fonts CDN)
    - Heading weight: 600–700 | body weight: 400

    ## Relationship to digitalmodel (#2440 Option B — deliberate differentiation)
    - AceEngineer retains `#c85a2a` orange + plum/slate chrome.
    - Does NOT inherit digitalmodel's navy+teal database-cylinder identity.
    - Rationale: different audiences (consulting prospects vs open-source engineers downloading a library).

    ## Forbidden treatments
    - Do not use "A&CE" in new work.
    - Do not use "Analytical & Computational Engineering" in consumer-facing headline copy (reserved for SEO/a11y surfaces only).
    - Do not mix legal form "Achanta AceEngineer Inc." into marketing copy.
```

---

## Files to Change

### Create

| Path | Purpose |
|---|---|
| `aceengineer-website/assets/img/logo.svg` | canonical vector wordmark |
| `aceengineer-website/assets/img/logo.png` | canonical raster (800×200 or equivalent aspect; retina density) |
| `aceengineer-website/assets/img/logo-1280x640.png` | og:image / social-preview variant |
| `aceengineer-website/brand/BRAND.md` | brand sheet (see Phase D pseudocode for section list) |

### Modify — nav template

| Path | Reason |
|---|---|
| `aceengineer-website/content/partials/nav.html` | replace inline SVG placeholder at lines 10-14 with `<img src="{{ rootPath }}assets/img/logo.svg" alt="AceEngineer" class="navbar-logo" ...>` |

### Modify — content sources (SEO / wordmark sweep)

14 files with broken `logo.png` (both `content/` source + root-level built — verify build covers both):
- `aceengineer-website/content/index.html` | `aceengineer-website/index.html`
- `aceengineer-website/content/about.html` | `aceengineer-website/about.html`
- `aceengineer-website/content/energy.html` | `aceengineer-website/energy.html`
- `aceengineer-website/content/contact.html` | `aceengineer-website/contact.html`
- `aceengineer-website/content/faq.html` | `aceengineer-website/faq.html`
- `aceengineer-website/content/blog/ai-native-structural-analysis.html` | `aceengineer-website/blog/ai-native-structural-analysis.html`
- `aceengineer-website/content/blog/offshore-engineering-standards.html` | `aceengineer-website/blog/offshore-engineering-standards.html`

Additional files with `A&CE` / long-form wordmark to sweep (20 files total; enumerated from grep):
- `aceengineer-website/engineering.html`, `404.html`, `samples/index.html`
- `aceengineer-website/case-studies/index.html` + 6 case-study pages (`subsea-fea-automation`, `wind-turbine-foundation-analysis`, `offshore-platform-fatigue-optimization`, `marine-safety-correlation`, `orcaflex-riser-sensitivity-automation`, `bsee-field-economics`, `pipeline-on-bottom-stability-assessment`)
- `aceengineer-website/blog/` — 7 additional posts (`risk-based-inspection-planning`, `gulf-of-mexico-production-data-access`, `python-engineering-automation`, `cfd-offshore-engineering`, `drilling-technology-evolution-mpd-adoption`, `open-source-engineering-tools`, and others per grep)
- `aceengineer-website/calculators/` — 4 pages (`index`, `fatigue-sn-curve`, `fatigue-life-calculator`, `npv-field-development`)
- Mirror each in `content/` where the `content/` copy exists; for files with no `content/` counterpart, edit in place and document the build-pipeline exception in a one-line comment at top of the sweep script.

### Modify — optional (flag as open question, not committed in this plan)

| Path | Reason |
|---|---|
| `aceengineer-website/assets/favicon.svg` | favicon hue is `#b84315` — locked primary is `#c85a2a`. Harmonize or keep as documented drift? Flag to user. |

### Do NOT modify (forbidden by worker's write boundary; belongs to a separate index pass)

| Path | Reason |
|---|---|
| `docs/plans/README.md` | plan index; updated by human or separate pass outside this worker's write boundary |

---

## TDD Test List

Frontend/brand issue — test harness is primarily grep invariants + schema validation + visual QA, not pytest. Each row below is an acceptance assertion the implementer must confirm before declaring done.

| Check | What it verifies | How to run | Expected |
|---|---|---|---|
| logo_svg_exists | vector asset present | `ls aceengineer-website/assets/img/logo.svg` | file exists, non-empty |
| logo_png_exists | raster asset present | `ls aceengineer-website/assets/img/logo.png` | file exists, non-empty |
| logo_social_exists | social variant present | `ls aceengineer-website/assets/img/logo-1280x640.png` | file exists, non-empty |
| brand_sheet_exists | brand doc present | `ls aceengineer-website/brand/BRAND.md` | file exists, ≥120 lines |
| no_broken_logo_png | zero references to paths that 404 | `grep -rl "logo\.png" aceengineer-website --include="*.html"` → then `for f; do curl -I ... ; done` (staging) | all referenced `logo.png` paths return 200 |
| nav_uses_real_logo | nav.html references the new file, not inline SVG | `grep -c '<svg.*navbar-logo' aceengineer-website/content/partials/nav.html` + `grep -c 'assets/img/logo.svg' aceengineer-website/content/partials/nav.html` | inline-SVG hit count 0; img-src hit count 1 |
| no_ampersand_ce_in_built | retired wordmark purged from served HTML | `grep -rE "A&amp;CE\|A&CE" aceengineer-website --include="*.html" --exclude-dir=brand` | 0 matches (or explicitly documented historical callouts only) |
| title_uses_ace | consumer-facing `<title>` suffix uses AceEngineer | `grep -rE "<title>.*A&amp;CE" aceengineer-website --include="*.html"` | 0 matches |
| seo_longform_preserved_where_warranted | JSON-LD `publisher.name` intentionally kept as long-form only where documented | `grep -rE '"name": "Analytical & Computational Engineering"' aceengineer-website --include="*.html"` + cross-reference with BRAND.md policy | only in JSON-LD publisher.name; zero in `<title>` / `og:site_name` / visible copy |
| json_ld_validates | schema.org validator passes | https://validator.schema.org/ on index.html, 1 blog post, 1 case study | no errors |
| social_preview_valid | og:image resolves and is rendered | Twitter Card Validator + Facebook Sharing Debugger | image loads; preview renders |
| build_clean | `node build.js` / `npm run build` completes without warnings | rebuild | zero warnings about missing assets or template expansion errors |
| visual_qa_live_staging | nav renders the logo without layout shift | browser inspection of staging deploy | logo visible at expected size, no CLS regression, no console 404s |

---

## Acceptance Criteria

- [ ] All four canonical assets created: `logo.svg`, `logo.png`, `logo-1280x640.png`, `brand/BRAND.md`.
- [ ] `nav.html` renders `<img src=".../logo.svg" ...>`; inline-SVG placeholder removed.
- [ ] `grep -rE "A&amp;CE|A&CE" aceengineer-website --include="*.html" --exclude-dir=brand` returns zero matches across built pages.
- [ ] All 14 files referencing `logo.png` resolve to a live asset (no 404).
- [ ] `<title>` and `og:site_name` on every built page use "AceEngineer" (or a documented AceEngineer-prefixed form).
- [ ] JSON-LD `publisher.name` may retain "Analytical & Computational Engineering" ONLY where BRAND.md documents SEO/a11y long-form warrant.
- [ ] `node build.js` completes with zero warnings; `dist/` output is consistent with root-level served files.
- [ ] Schema.org validator passes on index.html + 1 blog post + 1 case study.
- [ ] Twitter Card + Facebook Open Graph debuggers render the logo image correctly for index.html and 1 blog post.
- [ ] Brand sheet at `aceengineer-website/brand/BRAND.md` documents the locked hierarchy, palette, typography, wordmark rules, forbidden treatments, and relationship-to-digitalmodel stance (Option B from #2440).
- [ ] #2435 can proceed with its palette + wordmark regeneration on top of this plan's outputs — no further brand decision needed from that issue.
- [ ] Review artifacts posted to `scripts/review/results/2026-04-23-plan-2438-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

<!-- Populated after Step 4. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** TBD

Revisions made based on review:
- TBD

---

## Risks and Open Questions

### Risks

- **Asset creation is creative work**, not mechanical. The implementer must either commission a wordmark or render one programmatically (SVG `<text>` with Inter tuned kerning). Plan does not prescribe an artist — if one is not available, defer to an Inter-only wordmark render and document the choice in BRAND.md as "baseline treatment, may be refreshed later."
- **`content/` vs. root duality**: editing only `content/` without confirming `build.js` writes the built HTML back to root-level committed files (not just `dist/`) would leave stale live pages. The implementer must either (a) run the build and commit the regenerated root-level files, or (b) confirm root-level files are no longer the served path (e.g. Vercel routes from `dist/` now). If (b) is true, root-level files should be deleted in a separate issue — out of scope here.
- **185 occurrence sweep** risks introducing regressions in blog/case-study copy if a regex is overly broad. Mitigation: produce a pre-change grep manifest, apply edits, produce a post-change grep manifest, diff; any site-visible copy change beyond the wordmark swap must be flagged as a separate copy-edit decision.
- **Build pipeline rewrites relative paths**: `{{ rootPath }}` in `nav.html` currently resolves per page depth; confirm the same template expansion works for `<img src>` (it should, since posthtml-expressions is string-level). Smoke-test by rebuilding and spot-checking rendered paths on a nested page (e.g. `blog/ai-native-structural-analysis.html`).
- **Favicon hue drift**: `#b84315` vs locked `#c85a2a` — if not harmonized here, BRAND.md must document the drift as a known follow-up (or a separate issue must be filed). Not doing either leaves a contradiction between brand sheet and favicon.

### Open questions (flag to user during approval)

1. **Wordmark production**: acceptable to ship an Inter-only text-based wordmark (no custom mark) as baseline, with a refresh issue filed later for an optional mark/monogram?
2. **Favicon**: in-scope to update to `#c85a2a` here, or leave as `#b84315` and document the drift for a future pass?
3. **Copy-edit policy during sweep**: when replacing `<title>foo | A&CE Engineering Blog</title>` with `<title>foo | AceEngineer Blog</title>`, is "AceEngineer Blog" the preferred suffix, or does the user want a different variant (e.g. "AceEngineer — Engineering Blog")?
4. **JSON-LD `publisher.name`**: keep as "Analytical & Computational Engineering" (SEO long-form) across all blog/case-study pages, or switch to "AceEngineer"? The brand-hierarchy comment suggested "keep long-form only where SEO-long-form is warranted" — the implementer reads this as "keep in JSON-LD publisher.name, switch everywhere else" — confirm.
5. **Root-level committed HTML**: is Vercel serving `/` from root files or from `dist/`? Answer determines whether this plan's sweep edits root files or relies entirely on a rebuild.

---

## Complexity: T3

**T3** — spans four loosely-coupled workstreams (asset creation, doc authoring, template change, mass HTML sweep), touches ~20 files, requires a working build, requires schema + social-preview + visual validation, and is the critical-path unblocker for #2435. No single piece is hard; the coordination cost and the cross-surface verification (grep + schema.org + OG + visual) makes this a T3 rather than T2.
