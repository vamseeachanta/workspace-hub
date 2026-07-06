> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-06
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_svg_pdf_portability_no_patterns_clippaths.md

---
name: feedback_svg_pdf_portability_no_patterns_clippaths
description: SVGs bound for PDF (especially logos) must avoid <pattern>/clipPath/filter/mask — Cairo (Evince) mis-paints them; verify with pdftocairo
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2da9d909-1a47-4c6a-93ae-e7f8c6cff42c
---

Any SVG that will be embedded in / printed to a PDF — **especially a logo** — must avoid the PDF-fragile SVG features: `<pattern>` tiles, `<clipPath>`/`clip-path`, `<filter>`, `<mask>`, `<foreignObject>`. PDF renderers disagree on them.

**Why:** 2026-07-03 incident — the digitalmodel logo used a `<pattern>` (tiled "lay-line" rope texture) applied as a `stroke` inside a `clip-path` group. **Cairo** (the engine behind GNOME Document Viewer / Evince, the default Linux PDF viewer) painted the tiled teal pattern across the entire clipped bounding box → a translucent teal band over the whole logo. Chrome's screenshot engine, `pdftoppm` (Poppler), and Ghostscript ALL rendered it clean, so the defect was invisible in my usual checks and only showed in the user's Evince. The user (Vamsee) flagged it directly and asked to institutionalize the fix "especially for a logo."

**How to apply:**
- Prefer flattened primitives: solid `fill`, explicit stroked `<path>`/`<line>`, plain `<text>`, gradients (gradients ARE portable). If texture is needed, draw explicit line elements, not a tiled `<pattern>`.
- **Verify the actual PDF in Cairo**, not just a Chrome HTML screenshot or a Poppler `pdftoppm` raster: `pdftocairo -png -r 200 out.pdf check` — Cairo is the strict engine that surfaces band/fill bugs. Cross-check Poppler + Ghostscript too.
- **Fix at the canonical source asset** (`<repo>/assets/logo/*.svg`), not just the one document, so every downstream embed inherits the safe version.
- Verified fix method: strip `<defs>` (clipPath+pattern), replace `<g clip-path="url(#clip)">` → `<g>`, delete every `<path ... stroke="url(#pattern)">` overlay (keep the solid navy/teal strokes underneath).

**Verification font caveat:** the SVG's web font (Inter) is usually absent on the render box → force `Liberation Sans` for the throwaway check PNG so text is faithful, but keep the Inter stack in the committed SVG.

**Superseded / current state (2026-07-03):** my initial in-place hardening of the OLD digitalmodel mark is MOOT — the logo was redesigned to the **mooring-bollard + laid-rope mark** (PR vamseeachanta/digitalmodel#1352, closes #1351; branch `design/logo-moored-1351`), which is portable by construction (rope texture = explicit `<line>` elements, no pattern) and fixes the D-overlap. See [[project_digitalmodel_logo_moored_mark]]. **Lane A DONE:** the Subsea7 FDG pre-read (`aceengineer-strategy/pipeline/subsea7-fdg/pre-read-one-pager.html`) now embeds the new moored mark + new taglines (old ones retired); regenerated PDF verified clean in Cairo, 1 Letter page — see [[project_subsea7_fdg_deck]]. Rule added: [[svg-pdf-portability]].

**PENDING (user-gated):** (a) commit/PR the pre-read swap in aceengineer-strategy; (b) **Lane B** — 2 non-portable `<pattern>` rope SVGs in `aceengineer-strategy/strategy/deckhand/release/assets/vote/{logo-A1-rope,logo-B1-rope}.svg` still need flattening; (c) **Lane C** (Deckhand rebrand) is a USER branding decision — do NOT start unprompted; (d) digitalmodel + worldenergydata capabilities pages still embed the pre-redesign mark (fold in when #1352 propagates); (e) Level-2 `check-svg-pdf-portability.sh` still the next enforcement step. `aceengineer-website` = separate brand, out of scope.

See [[feedback_html_default_artifact]] (HTML/PDF-default artifacts) and [[reference_headless_chrome_pdf_image_gotchas]] (related Chrome print-to-PDF quirks).
