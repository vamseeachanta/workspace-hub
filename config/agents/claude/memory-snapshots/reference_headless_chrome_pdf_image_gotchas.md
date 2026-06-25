---
name: reference_headless_chrome_pdf_image_gotchas
description: "Headless Chrome --print-to-pdf drops images unless they're base64 <img>; how to render self-contained HTML→PDF reliably"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d89a3b9e-1e0e-46a6-9d61-ad3aacafce51
---

Rendering self-contained HTML → PDF with `google-chrome --headless=new --print-to-pdf` (Chrome 148, this box) has three stacked traps that all silently produce a blank/imageless PDF:

1. **`file://` → `file://` subresource loads are BLOCKED** in headless. Relative `<img src="images/x.jpg">` on a `file://` page won't load. Workaround: render via an HTTP URL (a `python3 -m http.server` already runs in scratchpad), OR base64-inline the images.
2. **`--print-to-pdf` does NOT paint CSS `background-image`** even with `-webkit-print-color-adjust:exact` / `print-color-adjust:exact`. Background tiles render on screen but vanish in the PDF.
3. **The fix that works: foreground `<img>` with inline base64 data-URIs.** Guaranteed load (no subresource fetch), foreground element prints fine, `object-fit:cover` is OK once the src is a data-URI. File becomes truly self-contained.

Diagnostic tells: byte-identical PDF size across CSS edits looks like caching but is really "images never embedded + text compresses to ~same size" — confirm by `about:blank` (renders ~7KB, proves URL IS honored) and by the PDF size JUMPING when images actually embed (e.g. 532KB → 2.1MB for 7 photos). Use a fresh `--user-data-dir=$(mktemp -d)` per render to rule out profile reuse. Verify pages with the Read tool on the PDF (`pages:` param) — don't trust byte size alone.

Pattern used: keep the repo `index.html` with relative `images/` refs (clean, browsable when opened normally), and generate a throwaway base64-embedded copy ONLY for the PDF render (small Python: regex-replace `src="(images/[^"]+)"` → data-URI, render, delete temp). Photos: pull CC0/CC-BY/CC-BY-SA from Wikimedia Commons (use 960px thumbnail URLs — arbitrary widths like 1000px return HTTP 400; nearest valid is 960px), print attribution in the doc.
