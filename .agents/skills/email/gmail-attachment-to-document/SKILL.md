---
name: gmail-attachment-to-document
description: Download attachments from Gmail threads, parse their content (Excel, PDF), extract structured data, and save to target repos with proper legal scanning.
version: 1.0.0
author: vamsee
tags: [email, gmail, attachments, excel, pdf, data-extraction]
related_skills: [gmail-multi-account, gmail-extract-and-act, excel-workbook-to-python-cowork]
metadata:
  hermes:
    tags: [email, gmail, attachments, excel, pdf]
    related_skills: [gmail-multi-account]
---

# Gmail Attachment to Document Pipeline

Download attachments from email threads, extract data, save to repos.

## Use Cases

1. **Payment analysis Excel** from tenants/landlords → save to real estate repo
2. **1099-MISC PDFs** from payers → save to tax docs
3. **CRE listing brochures** from brokers → extract → data table → delete
4. **Engineering reports** from clients → extract → code/analysis repo

## Workflow

### Step 1: Find the attachment in the thread

```python
# 1. Refresh OAuth token
# 2. Search for thread: gmail_search('subject:"1099-MISC" has:attachment', token)
# 3. Get full message: gmail_full(message_id, token)
# 4. Find attachment: parse payload.parts recursively for filename + attachmentId
# 5. Download: GET /messages/{id}/attachments/{attachmentId}
# 6. Decode: base64.urlsafe_b64decode(data["data"])
```

### Step 2: Parse the attachment

**Excel files (.xlsx)**:
```bash
# From /tmp directory to avoid repo pyproject.toml conflicts
cd /tmp && uv run python3 -c "
import openpyxl
wb = openpyxl.load_workbook('path/to/file.xlsx', data_only=True)
print(wb.sheetnames)
for name in wb.sheetnames:
    ws = wb[name]
    print(f'Sheet: {name} (rows={ws.max_row}, cols={ws.max_column})')
    for row in ws.iter_rows(min_row=1, max_row=30, values_only=True):
        print([v for v in row[:10] if v is not None])
"
```

**PDF files**:
```python
from pypdf import PdfReader
reader = PdfReader("path/to/file.pdf")
for page in reader.pages:
    print(page.extract_text())
```

**Images (.png, .jpg)**:
```python
from PIL import Image
import io
img = Image.open(io.BytesIO(image_data))
print(f"Image: {img.size}, {img.mode}, {img.format}")
```

### Step 3: Extract key data

For payment analysis spreadsheets:
```python
# Common structures in payment analysis files:
# - Year tabs (2024, 2025, 2026)
# - Columns: Date, Amount, Payment Type, Vendor Number
# - Rows: individual payment records

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    # Header row
    headers = [cell.value for cell in ws[1] if cell.value]
    # Data rows
    for row in ws.iter_rows(min_row=2, values_only=True):
        date = row[0]  # Payment date
        amount = row[1]  # Payment amount
        pmt_type = row[2]  # Rent, Insurance, Tax, etc.
        total += amount if amount else 0
```

### Step 4: Save to repo

```python
import os
from pathlib import Path

# For tax documents:
save_dir = Path("/mnt/local-analysis/workspace-hub/sabithaandkrishnaestates/docs/tax")
save_dir.mkdir(parents=True, exist_ok=True)
save_path = save_dir / f"2024-2026-fd30150-payment-analysis.xlsx"
with open(save_path, "wb") as f:
    f.write(attachment_data)

# For extracted data (CSV/JSON):
save_dir = Path("/mnt/local-analysis/workspace-hub/sabithaandkrishnaestates/data/payments")
save_dir.mkdir(parents=True, exist_ok=True)
```

### Step 5: Commit

```bash
cd /mnt/local-analysis/workspace-hub/sabithaandkrishnaestates
git add docs/tax/ data/payments/
git commit -m "docs(tax): add FD 2024-2026 payment analysis from Family Dollar response
Ref: #1992, 1099-MISC discrepancy thread"
git push origin main
```

## Key Findings from 1099 Thread

1. **Attachments are often in the latest email, not in the original inquiry**
   - The payment analysis was attached by Ebony Ham, not in the first email
   - Search must include all messages in thread: `gmail_search('subject:"..." has:attachment')`

2. **Excel files from corporate systems often have multiple year tabs**
   - One workbook can contain 2024, 2025, 2026 data on separate tabs
   - Use `openpyxl` with `data_only=True` to read calculated values

3. **Don't read from repo directory with `uv run`**
   - Repo pyproject.toml may conflict with uv settings
   - Use `cd /tmp` before running `uv run python3`

4. **Attachment IDs are long and unique**
   - They can be 100+ chars, don't truncate them
   - They're stable across refreshes (same message, same attachment ID)

5. **Some attachments are actually inline images**
   - Corporate emails often have logo images (image001.png, image002.png)
   - Filter by checking if filename is generic + mimeType is image/* + size < 20KB

## Pitfalls

1. **`uv run` must be from /tmp**, not from the repo directory (pyproject.toml conflicts)
2. **openpyxl not always installed** in current venv — use `uv run` which auto-installs
3. **Base64 data can be very large** — use `base64.urlsafe_b64decode`, not `.b64decode`
4. **PDF extraction can fail on scanned docs** — use OCR fallback if text extraction returns empty
5. **Corporate XLSX files may have merged cells** — use `openpyxl` carefully
6. **Always save before parsing** — don't rely on in-memory data for long operations
7. **Legal scan before committing attachments** — run `legal-sanity-scan.sh` on any extracted text
