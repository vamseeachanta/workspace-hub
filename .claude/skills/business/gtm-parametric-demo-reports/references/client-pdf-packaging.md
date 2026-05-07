# Client PDF Packaging for GTM Reports

Use when the user needs same-day client-facing PDFs from existing GTM HTML material.

## Pattern

1. **Package existing print-friendly HTML first.** Do not wait for a deeper report refactor when the user needs material today. Use current `examples/demos/gtm/output/*.html` reports and add a lightweight client header/caveat/footer.
2. **Brand with digitalmodel assets.** Prefer `assets/logo/digitalmodel_logo.svg`; base64-embed the SVG in generated wrapper HTML so Chrome can render it without external path issues.
3. **Add client caveats visibly.** Insert a short note near the top: representative/class-typical vessel values are GTM collateral, not final engineering; project use needs owner-approved vessel data, certified RAOs, and project-specific metocean.
4. **Add a pack index.** Generate `00_vessel_capability_gtm_pdf_pack_index.html/.pdf` listing included PDFs, routing guidance, caveats, and relevant issue URLs.
5. **Create operation-specific PDFs.** For vessel suitability packs, include at least:
   - mudmat/subsea installation vessel capability
   - shallow-water pipelay vessel capability
   - rigid jumper/subsea installation vessel capability
   - CTV/SOV/access-operability suitability if reference data exists
6. **Zip for email.** Create a ZIP containing only PDFs for client distribution.
7. **Verify before reporting.** Check non-zero sizes, run `pdfinfo`/`pdftotext` if installed, verify `git status`, and confirm `HEAD == origin/main` if committing.

## Chrome command

Use headless Chrome directly for HTML-to-PDF when report HTML is already print-friendly:

```bash
google-chrome \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --allow-file-access-from-files \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=15000 \
  --print-to-pdf-no-header \
  --no-pdf-header-footer \
  --print-background \
  --print-to-pdf="$out_pdf" \
  "file://$html_path"
```

Notes:
- `--virtual-time-budget=15000` helps Plotly/JS reports finish rendering before print.
- `--print-background` preserves digitalmodel/navy/orange branding.
- `--allow-file-access-from-files` avoids local asset/chart access issues.
- Some Chrome versions accept either `--print-to-pdf-no-header` or `--no-pdf-header-footer`; using both is safe in observed runs.

## Verification commands

```bash
out='examples/demos/gtm/output/client_pdf_pack_YYYY-MM-DD'
for f in "$out"/*.pdf "$out"/*.zip; do test -s "$f"; done
ls -lh "$out"/*.pdf "$out"/*.zip

if command -v pdfinfo >/dev/null; then
  for f in "$out"/*.pdf; do echo "--- $f"; pdfinfo "$f" | sed -n '1,12p'; done
fi

if command -v pdftotext >/dev/null; then
  for f in "$out"/*.pdf; do
    printf '%s | ' "$f"
    pdftotext "$f" - | grep -E -m 1 'digitalmodel|Vessel|Installation|Pipeline|CTV' || true
  done
fi

git status --short --branch
printf 'HEAD=' && git rev-parse --short HEAD
printf 'origin/main=' && git rev-parse --short origin/main
```

## Pitfalls

- **Do not claim a PDF was generated just because Chrome exited.** Check file existence and size for every artifact.
- **Avoid false failures from `pipefail` + preview pipes.** `pdftotext "$pdf" - | head` can exit `141` under `set -o pipefail` after successful extraction because `head` closes the pipe. For verification scripts, write `pdftotext` output to a temp file first, then run `head`/`grep` on the temp file.
- **If generating CTV/access-operability tables from JSON, inspect keys first.** In the Kincardine CTV dataset the monthly key is `with_s_landing_n_plus_s_pct`, not `with_s_landing_pct`; monthly uplift may need to be computed as `with_s_landing_n_plus_s_pct - as_built_n_only_pct`.
- **Do not disturb unrelated dirty files.** Stage only the output pack path (or leave uncommitted if user only wants local deliverables). Re-run `git status --short --branch` before and after.
- **Preserve provenance caveats.** If values are image-derived/digitized, say so in the PDF and preserve source attribution/reuse-rights caveats.
