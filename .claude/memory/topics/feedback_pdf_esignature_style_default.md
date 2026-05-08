> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-08
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_pdf_esignature_style_default.md

---
name: PDF e-signature style default
description: For PDF signing tasks (paychecks, admin docs, legal), default to typed e-signature style (cursive font + "Electronically signed" + date) rather than placing a bitmap signature image
type: feedback
originSessionId: 8f00e0db-1ba2-4167-9684-f9f468e2ae98
---
For PDF document signing in workspace-hub admin / payroll / legal contexts, default to a **typed e-signature style**: cursive font (Z003-MediumItalic chancery at `/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf` works well, dark-blue ink color) + thin underline + "Electronically signed" subscript + date stamp. Do NOT default to placing a bitmap signature image.

**Why:** On 2026-05-05 user redirected mid-task: "why not use an electronic signaure style with date i.e. PDF signature style". Two upsides over the bitmap path:
1. Sidesteps "filename ≠ contents" risk — `achantas-data/va/VA_Signature.jpg` despite the `VA_` filename actually contained "A. V. Satish" (different person), and three signed PDFs almost shipped with the wrong signature before visual verification caught it.
2. Matches industry norm for PDF signing (DocuSign-style typed signature) and is universally accepted for paystubs/admin docs.

**How to apply:**
- When user asks to sign a PDF (paycheck, NDA, admin form, etc.) in workspace-hub, propose typed e-signature style as the default. Only use a bitmap image if user explicitly requests handwritten.
- Always render a preview of the signature area to PNG and visually verify before producing the full set of signed PDFs.
- Write signed copies as `<orig>_signed.pdf` alongside originals (don't overwrite) — keeps an undo path.
- Recipe (pymupdf):
  ```python
  page.insert_font(fontname='cursive', fontfile='/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf')
  page.insert_text((x, y), 'Vamsee Achanta', fontname='cursive', fontsize=24, color=(0, 0, 0.55))
  page.draw_line(fitz.Point(x_l, y+6), fitz.Point(x_r, y+6), color=(0.4,0.4,0.4), width=0.4)
  page.insert_text((x, y+20), 'Electronically signed', fontname='helv', fontsize=8, color=(0.35,0.35,0.35))
  page.insert_text((x, y+35), f'Date: {datestr}', fontname='helv', fontsize=10, color=(0,0,0))
  ```
- Date interpretation: when user says "appropriate date stamp", look for the document's own date (Pay Date, Issue Date, Effective Date) and apply any offset they specify (e.g., "+5 days").
