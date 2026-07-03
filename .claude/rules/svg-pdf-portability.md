# SVG-for-PDF portability — agent rule

**When to apply:** authoring or editing any SVG that will be embedded in, or printed to, a PDF — **especially logos and brand marks** (logos get dropped into pre-reads, decks, letterheads, and reports everywhere, so they must render identically in every PDF engine). Also applies to inline-SVG in HTML artifacts that default to PDF per [`feedback_html_default_artifact`].

**Why:** PDF renderers do **not** agree on the harder SVG features. A logo that looks perfect in Chrome and Poppler can render a spurious fill/band in **Cairo** — which is what GNOME Document Viewer / Evince (the default Linux PDF viewer) uses. Live incident 2026-07-03: the digitalmodel logo's `<pattern>` (a tiled "lay-line" rope texture) applied as a `stroke` inside a `clip-path` group made **Cairo paint the tiled pattern across the entire clipped bounding box** → a translucent teal rectangle over the whole logo. Chrome's screenshot engine, `pdftoppm` (Poppler), and Ghostscript all rendered it clean, so the defect was invisible until viewed in Evince. A renderer-dependent logo is the worst kind of "silly business" — it ships looking broken to exactly the reader you're trying to impress.

**How to apply:**

1. **Avoid these constructs in PDF-bound / logo SVG:**
   - `<pattern>` tiles (Cairo mis-paints them across the fill/clip bbox). If you need texture, draw **explicit line/shape elements**, not a tiled pattern.
   - `<clipPath>` / `clip-path=` (inconsistent; and it amplifies the pattern bug). Design shapes to their final geometry instead of clipping a larger shape.
   - `<mask>`, `<filter>` (blurs/shadows), and `<foreignObject>` — all poorly/insconsistently supported in PDF.
   - Heavy reliance on `opacity` compositing for meaning (flatten to the final color where practical).
2. **Prefer:** solid `fill`, explicitly stroked `<path>`/`<line>`, plain `<text>`, `<linearGradient>`/`<radialGradient>` (these *are* portable). Self-contained, flattened primitives.
3. **Verify in Cairo, not just Chrome/Poppler.** A screenshot of the HTML, or a `pdftoppm` raster, is **not** sufficient — they use different engines than the reader's viewer. Rasterize the actual PDF with **`pdftocairo -png`** (Cairo) and eyeball the logo/artifact. If it's clean in Cairo, Poppler, and Ghostscript, it's safe:
   ```
   pdftocairo -png -r 200 out.pdf check   # the engine that catches band/fill bugs
   pdftoppm  -png -r 200 out.pdf check     # poppler cross-check
   ```
   **Font caveat for the verification raster:** the SVG's web font (e.g. Inter) is usually absent on the render box, so the PNG falls back — force `Liberation Sans` when rendering the check image so text is faithful, but **keep the real font stack (Inter, …) in the committed SVG**. Substitute only for the throwaway verification render.
4. **Fix at the canonical source, and fetch it from git — never hand-copy.** Harden the brand asset (`<repo>/assets/logo/*.svg`) so every downstream embed inherits the safe version; pull the current mark from the branch/`origin/main` (`git show <ref>:assets/logo/<x>.svg` or the raw githubusercontent URL), not from a local scratch copy — parallel sessions on other machines can't see your `/tmp`. **Canonical digitalmodel mark = the mooring-bollard + laid-rope mark** (PR [vamseeachanta/digitalmodel#1352](https://github.com/vamseeachanta/digitalmodel/pull/1352), closes #1351; branch `design/logo-moored-1351` until merged, then `origin/main`). It is portable by construction — the rope texture is explicit `<line>` elements, not a `<pattern>`. Taglines: *"Engineering moored to → Traceable codes and standards / Deterministic workflows / Single source of truth (SSOT)"* (the old *Asset Lifecycle / Offshore·Subsea·Marine / "Automation: ASCII Data to Engineering Insights"* lines are RETIRED — replace on sight). Full rationale: memory `project_digitalmodel_logo_moored_mark`. `aceengineer-website` has its OWN "AceEngineer" brand — out of scope, do not touch.

**Do NOT apply when:** the SVG is strictly screen-only and will never be printed or embedded in a PDF (patterns/clips/filters are fine on the web). Chart/dataviz `clip-path` inside on-screen HTML dashboards is out of scope — but the moment that page is a PDF-default artifact, this rule applies. **Logos are always assumed PDF-bound.**

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose (this rule) now → target Level 2 script `scripts/enforcement/check-svg-pdf-portability.sh` that greps `assets/logo/**.svg` and artifact HTML for `<pattern`/`clip-path`/`<filter`/`<mask` and warns (exit 1 on logos). Promote to a pre-commit hook once proven.

**Related:** [`feedback_html_default_artifact`] (HTML/PDF-default artifacts), [`patterns.md`](patterns.md) (enforcement gradient), [`coding-style.md`](coding-style.md) (edit safety). Memory: `feedback_svg_pdf_portability_no_patterns_clippaths`.
