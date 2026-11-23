# XLSX extraction — coverage protocol

## Pre-extraction estimate

```bash
unzip -l <source.xlsx> | grep "xl/worksheets/" | wc -l   # sheet count
unzip -p <source.xlsx> xl/workbook.xml | head -50         # sheet metadata
```

Inspect for:
- Hidden sheets (`state="hidden"` in `xl/workbook.xml`)
- VBA macros (`xl/vbaProject.bin`) — typically contain calc logic, not data
- Embedded objects (`xl/embeddings/`) — sub-files needing separate extraction
- External links (`xl/externalLinks/`) — sheets referencing other workbooks

`extraction_estimate` baseline:

| Indicator | Estimate |
|---|---|
| Standard data sheets, no macros, no hidden content | 0.98 |
| Hidden sheets with material data | (visible_count + hidden_count) / total |
| Heavy macro logic; data derived at runtime | 0.50 (need macro execution context) |
| External links to unreachable workbooks | 0.30 (broken refs) |
| Password-protected | 0.0 |

## Primary extractor: `openpyxl`

```python
import openpyxl
wb = openpyxl.load_workbook("<source.xlsx>", data_only=True)  # data_only=True returns formula values, not formulas
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(values_only=True):
        if any(cell is not None for cell in row):
            print(row)
```

`data_only=True` is critical: returns the **last-saved cached value** of
formulas, not the formula itself. For formula text, use `data_only=False`.

Limitations:
- Hidden rows / columns: `openpyxl` does not skip them by default; check
  `ws.row_dimensions[i].hidden` and `ws.column_dimensions[col].hidden`
- Conditional-format-styled cells: styling lost
- Pivot tables: extract the source data, not the pivot itself
- Charts: not extractable as data; OCR if needed

## Fallback: `pandas.read_excel`

```python
import pandas as pd
xl = pd.ExcelFile("<source.xlsx>")
for sheet_name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    print(f"{sheet_name}: {len(df)} rows")
```

Pandas is faster for large tabular sheets but less precise on
cell-by-cell metadata. Use for bulk extraction; openpyxl for
selective/structural work.

## Post-extraction yield

Count addressable cells:

```python
total_cells = sum(
    ws.max_row * ws.max_column
    for ws in wb.worksheets
    if ws.sheet_state == "visible"  # exclude hidden sheets from baseline unless they carry data
)
extracted_cells = sum(
    1 for ws in wb.worksheets if ws.sheet_state == "visible"
    for row in ws.iter_rows(values_only=True)
    for cell in row
    if cell is not None
)
yield_ = extracted_cells / total_cells
```

## Anchor format

`[[sources/<slug>]]:<sheet>!<cell-range>`

Examples:
- `[[sources/mooring-results-export]]:Lines!C12`
- `[[sources/mooring-results-export]]:Lines!C12:F12` (range)
- `[[sources/mooring-results-export]]:Summary!B5`

Sheet names with spaces: quote per Excel convention — `'Summary By Line'!C12`.

## Spot-check

Open the XLSX in Excel/LibreOffice. Verify 5–10 random cells against
extracted values. Pay special attention to:
- Formula cells: did `data_only=True` return the cached value correctly?
- Date cells: ISO format vs Excel serial number
- Cells with custom number formats: extracted as raw value, not formatted display

## Common pitfalls

- `data_only=True` returns `None` if the workbook was never opened in Excel
  after the formula was authored (no cached value). Force a recalc by
  opening in LibreOffice headless: `soffice --headless --calc --convert-to xlsx <source.xlsx>`
- Merged cells: only the top-left cell carries the value; other cells in
  the merge are empty
- Frozen panes / split views: structural metadata, not data — ignore
- Defined names: `wb.defined_names` carries them; can be cited as anchors
