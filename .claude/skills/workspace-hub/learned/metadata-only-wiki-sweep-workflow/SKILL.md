---
name: metadata-only-wiki-sweep-workflow
description: Disciplined inventory process for cataloging documents by filename/path without content claims, using parent-centric grouping to prevent stub proliferation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["documentation", "wiki-management", "metadata-extraction", "inventory-process"]
---

# Metadata-Only Wiki Sweep Workflow

Use this when creating stub documentation for large document collections without making content claims. (1) Verify plan approval before execution. (2) Inventory all target directories and extract PDF metadata using `pdfinfo` for safe header-only reading when feasible. (3) Apply parent-centric grouping: merge fragment documents (page scans, figures, sections) into parent document entries rather than creating proliferating stubs. (4) Generate stubs with explicit "do not claim" sections listing what content verification hasn't occurred. (5) Validate stubs with regex checks for prohibited claim language ("normative", "shall", "must", "requires that") in actual content areas, excluding constraint headers.

## Large mixed-directory fallback (learned in Wave 4)

When the collection is very large or noisy (thousands of files with viewer binaries, image bundles, caches, or legacy app payloads), use a conservative fallback instead of forcing a long interactive agent run:

1. Prefer deterministic scripted generation (`execute_code` / Python) over prolonged interactive agent editing.
2. Keep writes inside the approved reporting surface only (for example `docs/reports/**`) if the issue does not require canonical registry/wiki updates.
3. Use conservative file-action classification:
   - `stub`: `.pdf`
   - `defer`: office/archive/text formats such as `.zip`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.txt`, `.rtf`
   - `reject`: viewer binaries, caches, images, shortcuts, and app payloads such as `.dll`, `.fnt`, `.tif`, `.tiff`, `.db`, `.lnk`, `.gif`, `.png`, `.jpg`, `.jpeg`, `.exe`, `.ocx`, `.dat`, `.ini`, `.sys`
4. If PDF header extraction is too expensive for the volume, fall back to filename/path/extension-only metadata and state that explicitly in the artifact header.
5. For high-noise directories, surface the noise in the family map rather than trying to normalize everything into meaningful standards content.

## Interactive-agent recovery rule

If an interactive Claude run drifts into forbidden paths during a metadata-only sweep:
- stop it immediately,
- revert the forbidden path externally,
- narrow the agent back to report-only outputs,
- and if it still stalls, finish the artifact generation programmatically outside the agent session.

Treat the external git state as authoritative; do not trust the agent's verbal claim that cleanup is complete without verifying `git status`.