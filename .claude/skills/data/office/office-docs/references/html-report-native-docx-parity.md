# HTML report → native DOCX visual parity

Use this when creating or repairing a native/editable Word review document from an HTML report while preserving text and tables as Word content and embedding report visuals as static images.

## Trigger

- User asks for a DOCX to be complete or “1:1” relative to an HTML report.
- Existing DOCX has editable paragraphs/tables but may be missing HTML visuals.
- HTML report uses inline SVG or JavaScript-rendered charts rather than `<img>` tags.

## Workflow

1. Treat the HTML report as source of truth for visual inventory.
2. Count every visual channel, not just `<img>`:
   - `<img>` tags.
   - inline `<svg>` blocks.
   - Plotly charts, usually `Plotly.newPlot` calls.
   - canvas-based charts if present.
   - `data:image` embeds.
3. Prepare the DOCX work from an explicit artifact map before editing:
   - source HTML report path and canonical sibling derivative names;
   - current DOCX path, if one exists;
   - whether companion PDF regeneration is in scope or explicitly not touched;
   - expected HTML visual inventory by section/title, not only an aggregate count.
4. Inspect the current DOCX as a ZIP:
   - `word/media/*` count gives embedded raster/vector media count.
   - `word/document.xml` paragraph text can locate section insertion points.
   - `word/_rels/document.xml.rels` confirms each embedded image has a relationship target.
5. Compare `html_visuals` vs `docx_media` before modifying.
6. Capture missing HTML visuals with Playwright screenshots, selecting the smallest stable section that preserves context:
   - Prefer the chart/schematic container over raw SVG when the report section includes labels, legends, readouts, or explanatory framing.
   - Use a deterministic viewport and output PNG dimensions.
   - Name temporary captures by report section, not generic `chart.png`, so insertion mistakes are visible during review.
7. Patch the DOCX with `python-docx` rather than regenerating the whole document when the existing DOCX already has accepted editable text/tables.
8. Insert each visual near the corresponding editable section, with a concise source note.
9. Preserve native/editable Word content; do not convert the whole HTML/PDF to page images unless explicitly requested.
10. Re-verify:
   - DOCX media count equals HTML visual count.
   - Expected image dimensions are present.
   - Key note text reflects that visuals are static embeds and tables/text remain editable.
   - Every added image appears in `word/document.xml` relationships and not only as an orphaned file in `word/media/`.
   - If the companion PDF was not regenerated, state that explicitly in closeout rather than implying the whole review bundle was refreshed.

## Verification snippets

HTML visual count concept:

```python
html_visuals = html.count('<img') + html.count('<svg') + html.count('Plotly.newPlot') + html.count('<canvas') + html.count('data:image')
```

DOCX media count concept:

```python
import zipfile
with zipfile.ZipFile(docx_path) as zf:
    media = [n for n in zf.namelist() if n.startswith('word/media/')]
```

## Pitfalls

- A report with zero `<img>` tags can still contain required visuals via inline SVG and Plotly.
- Existing DOCX media count can be misleading if it only reflects chart captures; compare against all visual channels in HTML.
- `outputs/` directories may be ignored while specific generated artifacts are tracked. Confirm with `git ls-files --stage -- <path>` before force-adding.
- If `python-docx` is unavailable in the generic tool sandbox, use the repository’s project environment (for this workspace, normally `uv run python`).
- If no office renderer is installed, state that layout was structurally verified but not visually opened/rendered in Word/LibreOffice.
