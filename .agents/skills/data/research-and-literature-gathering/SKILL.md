---
name: research-and-literature-gathering
description: "Systematic workflow for finding, downloading, and indexing engineering
  literature by domain. Covers the full lifecycle: discovery via standards ledger and
  doc index, web search for open-access PDFs, download script generation, PDF validation,
  catalogue YAML creation, and handoff to the 7-phase document-index-pipeline for
  indexing. Use when populating a new engineering domain with reference literature or
  when a WRK item requires domain-specific standards and textbooks."
type: reference
version: 1.0.0
updated: 2026-04-01
category: data
related_skills:
- doc-research-download
- research-literature
- document-index-pipeline
- dark-intelligence-workflow
tags:
- literature
- engineering-domains
- download
- indexing
- standards
- research
triggers:
- gather literature for
- download domain documents
- populate domain literature
- research engineering standards
- find standards for domain
- literature gathering workflow
- new domain setup
- domain literature download
freedom: medium
---

# Research & Literature Gathering for Engineering Domains

> Full lifecycle: Discover → Search → Download → Validate → Catalogue → Index

## When to Use This Skill

Trigger this skill when:
- A WRK item requires populating literature for an engineering domain
- A new domain is being set up and needs reference material
- An existing domain has gaps identified by Phase F of the document-index-pipeline
- A calculation implementation needs standards/textbooks not yet downloaded
- You see keywords like "gather literature", "download standards", "populate domain"

## Engineering Domains

### Active Domains (with existing literature directories)

| Domain                | Literature Path                                                         | Key Standards Bodies        |
|-----------------------|-------------------------------------------------------------------------|-----------------------------|
| cathodic_protection   | /mnt/ace-data/digitalmodel/docs/domains/cathodic_protection/literature/ | DNV, NACE, ISO              |
| geotechnical          | /mnt/ace-data/digitalmodel/docs/domains/geotechnical/literature/        | API, DNV, ISO               |
| hydrodynamics         | /mnt/ace-data/digitalmodel/docs/domains/hydrodynamics/literature/       | DNV, ITTC, SNAME            |
| naval_architecture    | /mnt/ace-data/digitalmodel/docs/domains/naval_architecture/literature/  | ABS, DNV, SNAME, IMO        |
| pipeline              | /mnt/ace-data/digitalmodel/docs/domains/pipeline/literature/            | DNV, API, ASME, BSEE        |
| structural            | /mnt/ace-data/digitalmodel/docs/domains/structural/literature/          | AISC, DNV, IIW, API         |
| structural-parachute  | /mnt/ace-data/digitalmodel/docs/domains/structural-parachute/literature/| NHRA, SFI, NASA, AISC       |
| subsea                | /mnt/ace-data/digitalmodel/docs/domains/subsea/literature/              | API, DNV, BSEE              |
| metocean              | /mnt/ace-data/digitalmodel/docs/domains/metocean/literature/            | DNV, API, ISO, WMO          |

### Additional Domains (in standards but not yet in literature tree)

| Domain     | Typical Target Repo  |
|------------|---------------------|
| catenary   | digitalmodel        |
| mooring    | digitalmodel        |
| risers     | digitalmodel        |
| drilling   | OGManufacturing     |
| bsee       | worldenergydata     |
| economics  | worldenergydata     |

### Legacy Standards Storage

The og_standards corpus lives at `/mnt/ace/docs/_standards/` organized by org:
ABS, API, ASTM, BSI, DNV, ISO, MIL, NEMA, Norsok, OnePetro, Unknown.
Inventory DB: `/mnt/ace/O&G-Standards/_inventory.db` (SQLite, 6.8 GB).

## Step-by-Step Procedure

### Step 0 — Verify Domain Directory Exists

```bash
DOMAIN="geotechnical"   # ← set your domain
LIT_DIR="/mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature"
mkdir -p "${LIT_DIR}"
ls -la "${LIT_DIR}"
```

If the domain is new, create standard subdirectories:

```bash
mkdir -p "${LIT_DIR}"/{textbooks,standards,course-notes,worked-examples}
```

### Step 1 — Query the Standards Ledger

Find standards already tracked for this domain:

```bash
uv run --no-project python scripts/data/document-index/query-ledger.py \
  --domain ${DOMAIN} --verbose
```

Record each standard's status: `gap`, `done`, `wrk_captured`, `reference`.
Standards with `gap` or `wrk_captured` are download candidates.

### Step 2 — Query the Document Index

Search the 1M+ record index for existing documents in this domain:

```bash
uv run --no-project python -c "
import json
from collections import Counter
matches = []
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        path_lower = rec.get('path', '').lower()
        summary_lower = (rec.get('summary') or '').lower()
        if '${DOMAIN}' in path_lower or '${DOMAIN}' in summary_lower:
            matches.append(rec)
print(f'Found {len(matches)} documents')
by_source = Counter(r['source'] for r in matches)
for s, c in by_source.most_common():
    print(f'  {s}: {c}')
"
```

Prioritize `og_standards` and `ace_standards` sources — these are already local.

### Step 3 — Cross-Reference Capability Map

Check what calculations exist vs. gaps in the target repo:

```bash
uv run --no-project python -c "
import yaml
with open('specs/capability-map/digitalmodel.yaml') as f:
    data = yaml.safe_load(f)
for m in data['modules']:
    if '${DOMAIN}' in m['module'].lower():
        print(f\"Module: {m['module']} ({m.get('standards_count', '?')} standards)\")
        for s in m.get('standards', [])[:30]:
            print(f\"  {s['status']:15s} {s['org']:8s} {s['id'][:70]}\")
"
```

### Step 4 — Web Search for Open-Access Literature

Search for freely available PDFs across these source tiers:

**Tier 1 — High-value free sources:**
- DNV Veracity (rules.dnv.com/docs/pdf/) — free DNV-RP, DNV-OS PDFs
- API publications (some free after registration)
- DTIC (apps.dtic.mil) — US military/govt technical reports
- NASA Technical Reports (ntrs.nasa.gov)
- BOEM/BSEE (boem.gov, bsee.gov) — regulatory guidance
- University open repos (MIT OCW, TU Delft, deepblue.lib.umich.edu)

**Tier 2 — Conference/journal open access:**
- OnePetro open-access papers
- ISOPE proceedings (selected)
- OTC open papers
- ResearchGate/Academia.edu author copies

**Tier 3 — Textbooks and course notes:**
- Internet Archive (archive.org) — public domain texts
- University course note PDFs
- Open textbook initiatives

**WAF/paywall notes:**
| Site                 | Issue                                      | Action              |
|----------------------|--------------------------------------------|----------------------|
| eagle.org (ABS)      | Cloudflare WAF blocks wget/curl            | Add to pending_manual |
| archive.org borrow   | HTTP 403 for borrow-only items             | Add to pending_manual |
| IEEE Xplore          | Paywalled unless institutional login       | Skip or pending_manual |
| ASME Digital Collect | Paywall                                     | Check og_standards DB |

### Step 5 — Generate or Update the Download Script

**Option A: Use the research-domain.py driver** (queries all data sources, generates brief + script):

```bash
uv run --no-project python scripts/data/research-literature/research-domain.py \
  --category ${DOMAIN} --repo digitalmodel --generate-download-script
```

**Option B: Manual script creation** from template:

```bash
#!/usr/bin/env bash
# ABOUTME: Download open-access ${DOMAIN} literature
# Usage: bash download-literature.sh [--dry-run]

set -uo pipefail

DEST="/mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature"
LOG_DIR="$(git rev-parse --show-toplevel)/.claude/work-queue/assets"
LOG_FILE="${LOG_DIR}/download-${DOMAIN}.log"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "${DEST}"/{textbooks,standards,course-notes,worked-examples}
mkdir -p "${LOG_DIR}"

# shellcheck source=scripts/lib/download-helpers.sh
source "$(git rev-parse --show-toplevel)/scripts/lib/download-helpers.sh"

log "=== ${DOMAIN} Literature Download ==="
log "Destination: ${DEST}"
log "Dry run: ${DRY_RUN}"

# ─── TEXTBOOKS ────────────────────────────────
log "--- Textbooks ---"

download \
  "https://example.org/textbook.pdf" \
  "${DEST}/textbooks" \
  "Author-Year-Short-Title.pdf"

# ─── STANDARDS ────────────────────────────────
log "--- Standards ---"

download \
  "https://rules.dnv.com/docs/pdf/dnvpm/codes/docs/..." \
  "${DEST}/standards" \
  "DNV-RP-XXXX-Title-Year.pdf" || true

log "=== Download complete ==="
total=$(find "${DEST}" -name "*.pdf" | wc -l)
log "  Total PDFs: ${total}"
```

Save script to: `/mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature/download-literature.sh`

**Key script patterns:**
- Always `source scripts/lib/download-helpers.sh` for the `download` and `log` functions
- Use `set -uo pipefail` (NOT `set -e`) — download failures should log, not abort
- Guard fallible downloads with `|| true` or `|| log "NOTE: ..."`
- Use descriptive filenames: `Author-Year-Short-Title.pdf`
- The `download` function auto-skips existing files (resume-safe)
- Always run `--dry-run` first to preview

### Step 6 — Execute Downloads and Validate

```bash
# Dry run first
bash download-literature.sh --dry-run

# Execute
bash download-literature.sh

# Validate all PDFs are real PDFs (not HTML/WAF responses)
find "${LIT_DIR}" -name "*.pdf" -exec file {} \; | grep -v "PDF document"
```

Any file that shows "HTML document" or "ASCII text" instead of "PDF document"
is a WAF response. Move it to a `_failed/` directory and add to `pending_manual`.

### Step 7 — Create Catalogue YAML

Write `knowledge/seeds/${DOMAIN}-resources.yaml`:

```yaml
category: ${DOMAIN}
subcategory: references
created_at: "YYYY-MM-DD"

textbooks:
  - title: "Full Book Title"
    author: "Author Name"
    year: YYYY
    local_path: "/mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature/textbooks/file.pdf"
    source_url: "https://..."
    size_mb: N
    topics: [topic1, topic2]

standards:
  - title: "Standard Title"
    id: "DNV-RP-XXXX"
    org: "DNV"
    local_path: "/mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature/standards/file.pdf"
    source_url: "https://..."
    key_sections: ["Sec X.Y — relevant"]

online_portals:
  - title: "Portal Name"
    url: "https://..."
    notes: "What is available"

pending_manual:
  - title: "Blocked Resource"
    url: "https://..."
    notes: "WAF blocked / borrow-only / paywalled"
```

Validate against `knowledge/seeds/schema.md`.

### Step 8 — Produce Research Brief

Save to `specs/capability-map/research-briefs/${DOMAIN}.yaml`:

```bash
uv run --no-project python scripts/data/research-literature/research-domain.py \
  --category ${DOMAIN} --repo digitalmodel
```

Or produce manually following the template in the research-literature skill's
`references/templates.md`.

### Step 9 — Trigger Document Index Pipeline

Hand off to the document-index-pipeline for indexing newly downloaded literature:

```bash
# Phase A — re-index to pick up new files
uv run --no-project python scripts/data/document-index/phase-a-index.py

# If full pipeline takes >5 min, queue it instead:
echo "uv run --no-project python scripts/data/document-index/phase-a-index.py" \
  > .claude/work-queue/assets/${WRK_ID}/index-regen-queued.txt
```

The pipeline phases that follow:
- Phase A: scan filesystem → index.jsonl
- Phase B: LLM extraction + classification
- Phase C: domain classification
- Phase E: backpopulate index

See `document-index-pipeline` skill for full phase details.

### Step 10 — Archive Dark Intelligence

For university coursework, worked examples, and methodology extractions:

```bash
mkdir -p knowledge/dark-intelligence/${DOMAIN}/
```

Save worked examples (problem statements + known answers) here for TDD test
generation. These are private resources — see `dark-intelligence-workflow` skill.

## Pitfalls and Warnings

### Download Pitfalls

1. **WAF responses saved as PDF** — Always validate with `file *.pdf`. Sites like
   eagle.org (ABS) return HTML through Cloudflare WAF. The `download` helper saves
   whatever it gets — you must check.

2. **`set -e` kills download scripts** — Use `set -uo pipefail` without `-e`.
   The `download` function returns 1 on failure; with `-e` the script aborts on
   the first 404. Guard individual downloads with `|| true`.

3. **Archive.org borrow-only** — Some books show a download button but return 403.
   Check the item page for "Borrow" vs "Download" before scripting.

4. **Duplicate downloads across domains** — Check if a standard already exists in
   `/mnt/ace/docs/_standards/` or another domain's literature before downloading.
   Use the og_standards SQLite to search:
   ```bash
   sqlite3 /mnt/ace/O&G-Standards/_inventory.db \
     "SELECT path FROM documents WHERE path LIKE '%keyword%' LIMIT 20"
   ```

5. **Large file timeouts** — The `download` helper uses `wget --timeout=60`.
   For large textbooks (>50 MB), increase timeout or download manually.

### Indexing Pitfalls

6. **pdfplumber hangs on NTFS/NFS** — For batch PDF processing, use `pdftotext`
   via subprocess, NOT pdfplumber. See WRK-1277 warning in document-index-pipeline.

7. **Phase A must run before Phase B** — New files won't be extracted/classified
   until Phase A adds them to index.jsonl.

8. **Budget awareness for Phase B** — LLM extraction costs ~$0.002/doc (Haiku).
   Large domain additions (100+ docs) should be batched and budget-tracked.

### Catalogue Pitfalls

9. **Every attempted resource must appear** — Never silently skip a failed download.
   It goes in `pending_manual:` with a reason (WAF, paywall, borrow-only, 404).

10. **Validate local_path in YAML** — Every `local_path` in the catalogue YAML
    must point to an actually existing file. Script this check:
    ```bash
    uv run --no-project python -c "
    import yaml
    from pathlib import Path
    data = yaml.safe_load(open('knowledge/seeds/${DOMAIN}-resources.yaml'))
    for section in ['textbooks', 'standards']:
        for item in data.get(section, []):
            p = Path(item.get('local_path', ''))
            status = 'OK' if p.exists() else 'MISSING'
            print(f'  {status}: {p}')
    "
    ```

## AC Checklist

- [ ] Domain literature directory exists with standard subdirectories
- [ ] Standards ledger queried — gap standards identified
- [ ] Document index searched — existing docs catalogued
- [ ] Capability map cross-referenced — implementation gaps noted
- [ ] Web search performed for open-access PDFs (Tiers 1-3)
- [ ] Download script created, sourcing `scripts/lib/download-helpers.sh`
- [ ] Download script run with `--dry-run` then executed
- [ ] All downloaded PDFs validated with `file` (no HTML/WAF fakes)
- [ ] Catalogue YAML written at `knowledge/seeds/<domain>-resources.yaml`
- [ ] Research brief saved to `specs/capability-map/research-briefs/`
- [ ] Failed/blocked resources recorded in `pending_manual:` (none silently skipped)
- [ ] Document index pipeline triggered (Phase A) or queued
- [ ] Worked examples archived in `knowledge/dark-intelligence/<domain>/`

## Quick Command Reference

```bash
# Query ledger for a domain
uv run --no-project python scripts/data/document-index/query-ledger.py --domain ${DOMAIN} --verbose

# Run the research driver (generates brief + optional download script)
uv run --no-project python scripts/data/research-literature/research-domain.py \
  --category ${DOMAIN} --repo digitalmodel --generate-download-script

# Validate PDFs after download
find /mnt/ace-data/digitalmodel/docs/domains/${DOMAIN}/literature -name "*.pdf" \
  -exec file {} \; | grep -v "PDF document"

# Check og_standards for existing copies
sqlite3 /mnt/ace/O&G-Standards/_inventory.db \
  "SELECT path FROM documents WHERE path LIKE '%keyword%' AND is_duplicate=0 LIMIT 20"

# Re-index after adding literature
uv run --no-project python scripts/data/document-index/phase-a-index.py
```
