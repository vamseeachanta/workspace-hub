# HTML → PDF rendering (reference)

The repeatable way to turn a branded HTML asset into a clean, shareable PDF without heavy
dependencies. Works wherever a Chromium/Chrome binary exists.

## Render command (headless Chrome)
```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="output.pdf" "file://$(pwd)/input.html"
```
- `--no-pdf-header-footer` drops the default URL/date chrome around the page.
- Use an absolute `file://` path.
- `chromium`/`chromium-browser` work the same way if `google-chrome` isn't present.
- Fallbacks if no browser: `weasyprint input.html output.pdf` or `wkhtmltopdf`.

## Print-friendly HTML conventions
- `@page { size:A4; margin:14mm 0; }` and `html { -webkit-print-color-adjust:exact; print-color-adjust:exact; }` so colors/gradients render.
- `break-before:page` on a section to force it onto a new page (e.g. keep page 1 a short summary; push detail to following pages).
- `break-inside:avoid` on cards/tables/diagram blocks so they don't split across pages.
- Keep it self-contained (inline `<style>`, no external CSS/JS/CDN) so it renders offline.

## House style starting palette
```
--navy:#0d2438; --teal:#0e7c7b; --ink:#1c2730; --soft:#5d6b76; --bg:#f5f7f8;
font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
```
A teal→navy gradient header, teal section rules, cards with a colored top border, and a
gold accent for the "outcome/decision" callouts reads as a clean engineering-firm brand.

## Verify
- Read back the PDF (page count + page 1) to confirm the summary-first layout and that no
  card/table split awkwardly across a page break.
