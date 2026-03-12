---
name: doc-research-download
description: >
  Repeatable workflow for domain documentation research WRKs: search for freely-available
  references, download PDFs via shared bash lib, catalogue into knowledge/seeds/<domain>-resources.yaml.
  Use when starting any WRK that collects and indexes domain reference documents.
version: 1.0.0
category: data
related_skills: [workspace-hub/work-queue-workflow]
---

# Doc Research Download Skill

## Overview

Use this skill for any WRK that collects domain reference documents:
naval architecture, electrical engineering, structural analysis, etc.
It establishes where files live, how the download script is structured,
and what the catalogue YAML must contain.

## 6-Step Workflow

1. **Fetch seed URLs** — load each seed URL, extract all linked PDFs and sub-pages;
   produce an explicit list of direct download URLs (this is the discovery phase —
   output feeds the download script, not the template directly)
2. **Web search for extras** — search OCW, archive.org, standards bodies (IEC, ISO, IEEE,
   NFPA, ABS, DNV) for freely-available PDFs; add direct URLs to the list from step 1
3. **Create domain download script** — copy the template below; populate `download` calls
   with the URL list from steps 1–2; source `scripts/lib/download-helpers.sh`
4. **Catalogue** — write `knowledge/seeds/<domain>-resources.yaml` per `knowledge/seeds/schema.md`;
   validate each saved file is a real PDF (`file <path>` must report `PDF document`);
   move HTML/WAF responses to `pending_manual:` with `notes: "WAF — saved HTML, not PDF"`
5. **Regenerate document index** — run `scripts/data/document-index/` pipeline; if the full
   run takes >5 min, write `.claude/work-queue/assets/<WRK-ID>/index-regen-queued.txt`
   with the command to run — that file is the verifiable evidence for AC completion
6. **Record WAF-blocked / borrow-only** — add to `pending_manual:` in the YAML;
   never silently skip — every attempted resource must appear somewhere

## Script Template

Copy and adapt for each new domain:

```bash
#!/usr/bin/env bash
# ABOUTME: Download open-access <DOMAIN> documents to /mnt/ace/docs/_standards/<DIR>/
# Usage: bash scripts/data/<domain>/download-<domain>-docs.sh [--dry-run]

set -euo pipefail

DEST="/mnt/ace/docs/_standards/<DIR>"
LOG_DIR="$(git rev-parse --show-toplevel)/.claude/work-queue/assets/<WRK-ID>"
LOG_FILE="${LOG_DIR}/download.log"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "${DEST}/textbooks"
mkdir -p "${LOG_DIR}"

# shellcheck source=scripts/lib/download-helpers.sh
source "$(git rev-parse --show-toplevel)/scripts/lib/download-helpers.sh"

log "=== <DOMAIN> Download — <WRK-ID> ==="
log "Destination: ${DEST}"
log "Dry run: ${DRY_RUN}"

# ─────────────────────────────────
# TEXTBOOKS — direct PDF links
# ─────────────────────────────────
log "--- Textbooks ---"

download \
  "https://example.org/book.pdf" \
  "${DEST}/textbooks" \
  "Descriptive-Filename.pdf"

log "=== Download complete ==="
total=$(find "${DEST}" -name "*.pdf" | wc -l)
log "  Total PDFs: ${total}"
```

## Catalogue YAML Template

```yaml
category: <domain-slug>
subcategory: references
created_at: "YYYY-MM-DD"

textbooks:
  - title: "Full Book Title"
    author: "Author or Organisation"
    year: YYYY
    local_path: "/mnt/ace/docs/_standards/<DIR>/textbooks/filename.pdf"
    source_url: "https://..."
    size_mb: N
    topics: [topic1, topic2]

online_portals:
  - title: "Portal Name"
    url: "https://..."
    notes: "What is available here"

pending_manual:
  - title: "Blocked Book"
    url: "https://..."
    notes: "Reason: archive.org borrow-only"
```

## AC Checklist

- [ ] All seed URLs fetched and linked PDFs extracted
- [ ] Web search performed for additional freely-available resources
- [ ] All downloadable PDFs saved to `/mnt/ace/docs/_standards/<DOMAIN>/`
- [ ] Catalogue YAML written at `knowledge/seeds/<domain>-resources.yaml`
- [ ] Document index regenerated, or `assets/<WRK-ID>/index-regen-queued.txt` written
- [ ] No paywalled or DRM-protected content downloaded; WAF-blocked items in `pending_manual:`

## Known WAF Patterns

| Site | Behaviour | Workaround |
|------|-----------|------------|
| eagle.org (ABS) | Cloudflare WAF — 403 for wget/curl | Download manually via browser |
| archive.org borrow-only | HTTP 403 — "This item is not available for download" | Add to `pending_manual:`; note borrow URL |
| IEEE Xplore full-text | Paywalled unless institution login | Only download confirmed open-access items |

These patterns were identified during WRK-1151 (naval architecture).
