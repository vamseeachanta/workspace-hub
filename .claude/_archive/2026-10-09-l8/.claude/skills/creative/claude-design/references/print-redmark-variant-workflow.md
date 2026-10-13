# Print / Redmark Variant Workflow

Use when converting a client-facing dark or presentation-style artifact into a markup-ready copy for printing.

## Goal

Produce a practical review artifact, not a cosmetic clone:

- white background
- dark, high-contrast text
- simplified color fills and outlines
- no decorative glow/gradients that waste toner or reduce legibility
- enough whitespace for handwritten client redmarks
- export formats suitable for client circulation: PNG and PDF, with SVG/HTML source preserved when possible

## Workflow

1. **Locate and confirm the source**
   - If the user says “same image” without a path, inspect recent screenshots/images and use vision to identify the intended artifact.
   - Search repo references for title text, brand marks, or distinctive labels to recover data/provenance.

2. **Rebuild as source-first vector/HTML**
   - Prefer SVG embedded in a simple HTML wrapper.
   - Preserve the original structure, labels, metrics, and chart story.
   - Rework the palette for print rather than inverting colors.

3. **Export client formats**
   - PNG screenshot:
     ```bash
     google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
       --screenshot=out.png --window-size=850,1100 file:///absolute/path/to/artifact.html
     ```
   - PDF print copy:
     ```bash
     google-chrome --headless=new --no-sandbox --disable-gpu \
       --print-to-pdf=out.pdf file:///absolute/path/to/artifact.html
     ```

4. **Verify visually**
   - Confirm no scrollbars in the screenshot.
   - Confirm no clipped text or cramped labels.
   - Confirm white background and dark readable text.
   - Confirm the chart/data relationship still matches the source artifact.

## Common Pitfalls

- Do not only invert colors; dark-theme effects usually print poorly.
- Do not output only a raster file if future edits are likely; preserve SVG/HTML source.
- Do not claim “same image” if data labels or layout hierarchy changed materially; call it a print/redmark variant.
- Browser screenshots may include scrollbars unless `--hide-scrollbars` is used and the viewport matches the artifact size.
