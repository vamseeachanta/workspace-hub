# Resource Intelligence — Gap Closure Action Plan

> **Date:** 2026-04-02
> **Reference:** mount-drive-knowledge-map.md, dde-drive-catalog.md
> **Goal:** Close the identified gaps to maximize the value of 3.6M+ files across 4 mount points

---

## Priority Matrix

| # | Action | Priority | Effort | Value | Status |
|---|--------|----------|--------|-------|--------|
| 1 | Index conference papers (38,526 files) | P0-CRITICAL | Medium | VERY HIGH | PREP DONE — 21,346 files batched (#1608) |
| 2 | Add DDE drive to mounted-source-registry | P0-CRITICAL | Small | HIGH | DONE — #1756 closed, 11 sources |
| 3 | Migrate missing standards orgs from DDE | P1-HIGH | Medium | HIGH | DONE — #1758 closed, 525 files/6GB migrated |
| 4 | Cross-drive dedup audit | P1-HIGH | Medium | MEDIUM | SCRIPT DONE — #1757, needs full SHA run |
| 5 | Complete Phase B summarization (38% remaining) | P1-HIGH | Large | HIGH | PENDING — Claude API quota |
| 6 | Expand standards transfer ledger | P2-MEDIUM | Medium | MEDIUM | PENDING — #1612 |
| 7 | Index DDE unique project files | P2-MEDIUM | Medium | MEDIUM | PENDING — needs full dedup (#4) |
| 8 | Catalog DDE engineering literature | P2-MEDIUM | Small | MEDIUM | DONE — #1759 closed, 87 items cataloged |
| 9 | Port FreeSpanVIVFatigue MATLAB to Python | P3-LOW | Large | MEDIUM | PENDING |
| 10 | Triage va-hdd-2 engineering content | P3-LOW | Small | LOW | PENDING |

---

## P0 Actions — Do Now

### Action 1: Index Conference Papers

The 38,526 conference papers in `/mnt/ace/docs/conferences/` are the highest-value
unindexed resource. These contain directly applicable engineering knowledge for
riser, mooring, VIV, structural, and subsea domains.

**Steps:**
```bash
cd /mnt/local-analysis/workspace-hub

# 1. Ensure conferences source is in Phase A config
#    Add to scripts/data/document-index/config.yaml if not present:
#    - source_id: ace_conferences
#      mount_root: /mnt/ace/docs/conferences
#      document_intelligence_bucket: conferences

# 2. Run Phase A indexing
uv run scripts/data/document-index/phase-a-index.py

# 3. Run Phase B summarization (batch overnight)
uv run scripts/data/document-index/phase-b-extract.py --source conferences

# 4. Run Phase C classification
uv run scripts/data/document-index/phase-c-classify.py
```

**Expected yield:** 38,526 new index records, domain classification into 12 engineering domains.

### Action 2: Register DDE in Mounted Source Registry

Add these entries to `data/document-index/mounted-source-registry.yaml`:

```yaml
  - source_id: dde_standards_remote
    document_intelligence_bucket: dde_standards
    mount_root: /mnt/remote/ace-linux-2/dde/0000 O&G
    local_or_remote: remote
    canonical_storage_policy: legacy standards collection with unique orgs (ASME, AWS, NACE, etc.)
    provenance_rule: source of truth for orgs not present in /mnt/ace/O&G-Standards
    dedup_rule: check /mnt/ace/O&G-Standards first; DDE is authoritative for missing orgs only
    availability_check_ref: scripts/readiness/check-network-mounts.sh
    note: Contains 36 org dirs including 18 orgs NOT in /mnt/ace/O&G-Standards

  - source_id: dde_literature_remote
    document_intelligence_bucket: dde_literature
    mount_root: /mnt/remote/ace-linux-2/dde/Literature
    local_or_remote: remote
    canonical_storage_policy: historical literature collection (engineering, O&G, business)
    provenance_rule: reference in place; prefer domain-organized copies in digitalmodel/docs/domains
    dedup_rule: check digitalmodel/docs/domains literature first for engineering content

  - source_id: dde_engineering_remote
    document_intelligence_bucket: dde_engineering
    mount_root: /mnt/remote/ace-linux-2/dde
    local_or_remote: remote
    canonical_storage_policy: legacy engineering work (OrcaFlex models, MATLAB code, project backups)
    provenance_rule: reference only; active work migrated to /mnt/ace repos
    note: Includes FreeSpanVIVFatigue (MATLAB), o-drive/017 ODA, o-drive/018 FFS
```

---

## P1 Actions — Next Sprint

### Action 3: Migrate Missing Standards Organizations

18 standards organizations exist on DDE but NOT in `/mnt/ace/O&G-Standards/`.
The critical ones for offshore engineering are ASME, AWS, NACE, ASCE, HSE, IEC.

```bash
# Check sizes of critical missing orgs
for org in ASME ASCE AWS NACE HSE IEC ANSI; do
  echo -n "$org: "
  du -sh "/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards/$org" 2>/dev/null || echo "not found"
done

# Copy critical orgs to /mnt/ace/O&G-Standards/
for org in ASME ASCE AWS NACE HSE IEC; do
  rsync -av "/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards/$org/" "/mnt/ace/O&G-Standards/$org/"
done

# Re-run OCR pipeline for new orgs
uv run /mnt/ace/O&G-Standards/scripts/ocr_scanned_pdfs.py

# Re-index into _inventory.db
# (check if there's an indexing script for the semantic search DB)
```

### Action 4: Cross-Drive Dedup Audit

```bash
# Script concept: SHA-256 all PDFs on both drives, find overlaps
cd /mnt/local-analysis/workspace-hub

# Create dedup script
cat > /tmp/dedup-audit.py << 'EOF'
#!/usr/bin/env python3
"""Cross-drive deduplication audit."""
import hashlib, os, json
from pathlib import Path
from collections import defaultdict

DRIVES = {
    "ace_docs": "/mnt/ace/docs",
    "dde_documents": "/mnt/remote/ace-linux-2/dde/documents",
    "ace_standards": "/mnt/ace/O&G-Standards",
    "dde_standards": "/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards",
}

hashes = defaultdict(list)  # sha -> [(drive, path), ...]
for drive_name, root in DRIVES.items():
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                sha = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
                hashes[sha].append((drive_name, fp))
            except Exception:
                pass

dupes = {k: v for k, v in hashes.items() if len(v) > 1}
unique_dde = {k: v for k, v in hashes.items() 
              if len(v) == 1 and v[0][0].startswith('dde')}

print(f"Total unique files: {len(hashes)}")
print(f"Duplicated across drives: {len(dupes)}")
print(f"Unique to DDE: {len(unique_dde)}")

with open('data/document-index/cross-drive-dedup-report.json', 'w') as f:
    json.dump({"duplicates": len(dupes), "unique_dde": len(unique_dde)}, f)
EOF
```

### Action 5: Complete Phase B Summarization

639,585 of 1,033,933 documents have summaries (61.9%). Remaining: 394,348 docs.

```bash
# Run overnight batch with Claude sharding
uv run scripts/data/document-index/phase-b-claude-worker.py --shard 0 --total-shards 10
# ... repeat for shards 1-9 across multiple terminals
```

---

## P2 Actions — Backlog

### Action 6: Expand Standards Transfer Ledger
- Current: 425 entries (1.6% of 26,884 files on disk)
- Target: Add SNAME (145 files), OnePetro (94), BSI (76), Norsok (9)
- Also: bulk-add remaining API (396 unledgered) and ISO (244 unledgered)

### Action 7: Index DDE Unique Project Files
- After dedup audit, index files unique to DDE into Phase A
- Focus on projects not in /mnt/ace: 0170 AQWA, 0171 COSL, 0200 Anadarko

### Action 8: Catalog DDE Engineering Literature
- Map DDE `Literature/Engineering/` and `Literature/Oil and Gas/` to domain taxonomy
- Cross-reference with `digitalmodel/docs/domains/` to avoid duplication
- Add unique textbooks to research-literature registry

---

## P3 Actions — Future

### Action 9: Port FreeSpanVIVFatigue MATLAB to Python
- 13 MATLAB scripts implementing 2H VIV fatigue methodology
- Target: digitalmodel VIV module using dark-intelligence-workflow skill
- Covers: crossflow screening, inline fatigue, damage assessment, Weibull current fitting

### Action 10: Triage va-hdd-2 Engineering Content
- `data/va-hdd-2/2HDD Literature/` may contain engineering references
- Low priority — most value already extracted to structured locations

---

## GitHub Issue Tracker

All work items have corresponding GitHub issues:

| Action | Issue(s) | Status |
|--------|----------|--------|
| Conference indexing | #1608, #1641, #1642 | PREP DONE, ready for Phase A |
| DDE source registration | #1756 | CLOSED |
| Standards migration (6 orgs) | #1758 | CLOSED |
| Cross-drive dedup audit | #1757 | Script done, needs full run |
| Phase B summarization | #1769 | Open — needs Claude API quota |
| Standards ledger expansion | #1770, #1612 | Open |
| Index DDE unique files | #1771 | Open — blocked by #1757 |
| DDE literature catalog | #1759 | CLOSED |
| OCR + index migrated orgs | #1772 | Open |
| VIV MATLAB port | #1773 | Open — low priority |
| va-hdd-2 triage | #1774 | Open — low priority |

---

## Success Metrics

| Metric | Baseline (Apr 2) | Current (Apr 3) | Target | Timeline |
|--------|-------------------|------------------|--------|----------|
| Documents indexed | 1,033,933 | 1,033,933 | 1,072,459 (+38K conf) | 2 weeks |
| Phase B summaries | 61.9% | 61.9% | 90% | 1 month |
| Standards in ledger | 425 (1.6%) | 425 | 1,274 (+849) | 1 month |
| DDE sources registered | 0 | 3 (DONE) | 3 | DONE |
| Conference papers batched | 0% | 100% (21,346 files) | Phase A run | 2 weeks |
| Mounted sources | 8 | 11 (DONE) | 11 | DONE |
| Standards orgs on /mnt/ace | 11 | 17 (DONE) | 17 | DONE |
| Domain coverage (done) | 6.8% | 6.8% | 15% | 3 months |
