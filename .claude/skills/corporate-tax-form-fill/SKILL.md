---
name: corporate-tax-form-fill
version: "1.0.0"
category: business-finance
description: "Programmatically fill IRS tax form PDFs (Form 1120, etc.) using pymupdf/fitz. Covers field discovery, mapping, filling, cross-checking, and PDF generation."
tags: [tax, pdf, form-fill, irs, 1120, pymupdf, fitz]
type: reference
---

# Corporate Tax Form Fill — IRS PDF Automation

Fill IRS tax form PDFs programmatically using pymupdf (fitz).
Companion to `corporate-tax-strategic-planning` (analysis → execution).

## When to Use

- User has computed tax numbers and needs to fill an IRS PDF form
- User wants to regenerate a filled PDF after changing values
- User needs to discover field names in a new IRS form version

## Prerequisites

- `uv pip install pymupdf` (provides the `fitz` module)
- Blank fillable PDF from IRS (e.g., `f1120.pdf` from irs.gov/pub/irs-pdf/)
- Source of truth YAML with all computed values

## Step 1: Field Discovery

Extract all widget fields from the blank PDF to build a field map:

```python
import fitz
doc = fitz.open("f1120_blank.pdf")
for pg_idx, page in enumerate(doc):
    for w in page.widgets():
        print(f"Page {pg_idx+1} | {w.field_name} | type={w.field_type} | rect={w.rect}")
```

**Field naming convention (2025 Form 1120):**
- Text fields: `topmostSubform[0].PageN[0]...fN_X[0]` — match by suffix `fN_X[0]`
- Checkboxes: `...cN_X[0]` or `...cN_X[1]` — on-values typically "1", "2", "3"
- Page numbering: `f1_*` = Page 1, `f3_*` = Page 3, `f6_*` = Page 6
- **Field names change with each year's form revision** — always re-discover

## Step 2: Field-to-Line Mapping

When field names aren't self-documenting, extract text labels to correlate:

```python
page = doc[page_idx]
words = page.get_text("words")  # [(x0, y0, x1, y1, "text", ...)]
# Match field rect.y to nearest text label
```

For checkboxes, check available states:
```python
w.button_states()  # Returns dict with on/off values
```

## Step 3: Fill Script Pattern

```python
def fill(page_idx, suffix, value):
    page = doc[page_idx]
    for w in page.widgets():
        if w.field_name.endswith(suffix):
            w.field_value = str(value)
            w.update()
            return True
    print(f"  MISS: page {page_idx + 1}, suffix={suffix}")
    return False

def check(page_idx, suffix, on_value="1"):
    # Same pattern for checkboxes
```

## Step 4: Cross-Check Verification

After generating, read back and verify critical ties:

| Check | Formula |
|-------|---------|
| Schedule L balance | Total assets = Total L&E (both BOY and EOY) |
| M-1 reconciliation | Line 10 = Page 1 Line 28 |
| M-2 → Schedule L | M-2 Line 8 (EOY balance) = Schedule L Line 25 (RE EOY) |
| Tax computation | Taxable income × 21% = Tax (Schedule J) |
| Page 1 flow | Line 11 - Line 27 = Line 28 |

## Step 5: Output Structure

```
taxes/YYYY/
├── f1120_blank.pdf              # IRS blank form (input)
├── fill_f1120.py                # Fill script (regenerable)
├── YYYY-form-1120-filled.pdf    # Output PDF
├── YYYY-form-1120-filing-packet.yaml  # Source of truth
└── YYYY-form-1120-fill-guide.md      # Human-readable fill guide
```

## Pitfalls

1. **Schedule L line numbers shift between years** — the 2025 form uses Line 15 for Total Assets, Line 22a/b for stock, Line 25 for RE. Always verify against the actual PDF.

2. **Checkbox on-values aren't always "1"** — use `w.button_states()` to discover. First radio = "1", second = "2", etc.

3. **M-1/M-2 consistency** — M-2 ending balance MUST equal Schedule L retained earnings. If they don't match, the book net income calculation is wrong. Work backward from Schedule L.

4. **Negative cash** — if company cash is negative, show $0 on Schedule L Line 1 and move the overdraft to Line 18 (Other current liabilities).

5. **The `fill()` helper matches by suffix** — if multiple fields share a suffix across pages, specify `page_idx` carefully.
