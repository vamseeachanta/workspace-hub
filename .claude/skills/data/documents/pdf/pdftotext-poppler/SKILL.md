---
name: pdf-pdftotext-poppler
description: 'Sub-skill of pdf: pdftotext (Poppler) (+2).'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# pdftotext (Poppler) (+2)

## pdftotext (Poppler)

**Preferred tool for batch PDF text extraction** (WRK-1277 finding).

```bash
# Single file
pdftotext document.pdf output.txt
pdftotext -layout document.pdf output.txt  # Preserve layout
```

### Batch Processing Pattern (Proven at 297K scale)

Use `subprocess.run(timeout=N)` for reliable timeout handling in parallel workers:

```python
import subprocess
from concurrent.futures import ProcessPoolExecutor

def extract_text(pdf_path: str, timeout: int = 30) -> str | None:
    """Extract text via pdftotext subprocess — killable on timeout."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None  # Process killed cleanly by OS

# 8 workers, chunksize=50 — sustained ~49 files/second
with ProcessPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(extract_text, pdf_paths, chunksize=50))
```

> **Why subprocess, not pdfplumber?** pdfplumber runs in-process and can enter kernel
> D-state (uninterruptible disk sleep) on NTFS/NFS mounts. SIGALRM cannot interrupt
> kernel I/O — the process hangs forever. `subprocess.run(timeout=N)` runs pdftotext
> in a separate process that the OS can kill reliably via SIGTERM.

### Performance (WRK-1277 Benchmarks)

| Metric | pdftotext (subprocess) | pdfplumber (in-process) |
|--------|----------------------|------------------------|
| Speed | ~49 files/sec (8 workers) | ~1.3 files/sec |
| Timeout reliability | Reliable (OS-level kill) | Unreliable (D-state hangs) |
| NFS/NTFS safety | Safe (subprocess isolation) | Hangs on D-state I/O |
| Multiprocessing | Works with ProcessPoolExecutor | Serialization failures |

## qpdf

```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf document.pdf --pages . 1-5 -- first_five.pdf

# Decrypt
qpdf --decrypt encrypted.pdf decrypted.pdf
```


## pdftk

```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk document.pdf burst output page_%02d.pdf

# Rotate
pdftk document.pdf cat 1-endeast output rotated.pdf
```
