# O&G Knowledge Management Plan

## User Requirements (Confirmed)

1. **First Task:** Consolidate codes & standards into single directory with appropriate subfolders, remove duplicates
2. **Access Methods:** All (AI Q&A + Searchable Catalog + Organized File Browser)
3. **Timeline:** Full system build (4+ weeks)

---

## Collection Overview

**Location:** `/mnt/ace/0000 O&G`
**Total Files:** ~49,401 documents
**Total Size:** Multi-GB collection

### Current Structure (Has Duplicates!)

```
/mnt/ace/0000 O&G/
├── 0000 Codes & Standards/      # Main codes (organized but has duplicates)
│   ├── AS/API/                  # Well-organized API standards
│   ├── DNV/                     # Well-organized DNV standards
│   ├── ASTM/                    # ASTM with some organization
│   ├── ISO/                     # ISO standards
│   ├── Norsok/                  # Norsok standards
│   ├── BSI/                     # British standards
│   ├── MIL/                     # Military standards
│   └── Spare/                   # DUPLICATE location (API, DNV, ASTM, etc.)
│       ├── API Standards/       # ← DUPLICATE
│       ├── API Stds/            # ← DUPLICATE
│       ├── DNV Standards/       # ← DUPLICATE
│       ├── ASTM Standards/      # ← DUPLICATE
│       └── ...
├── Oil and Gas Codes/           # ENTIRE FOLDER IS DUPLICATE
│   ├── API Standards/           # ← DUPLICATE of above
│   ├── API Stds/                # ← DUPLICATE
│   ├── DNV Standards/           # ← DUPLICATE
│   └── ...
├── 2H Projects/                 # Real project files (keep as-is)
└── Production/                  # Operations files (keep as-is)
```

### Duplication Analysis

| Standard Org | Locations Found | Best Organized |
|--------------|-----------------|----------------|
| API | 5+ locations | `0000 Codes & Standards/AS/API/` |
| DNV | 3 locations | `0000 Codes & Standards/DNV/` |
| ASTM | 3 locations | `0000 Codes & Standards/ASTM/` |
| ISO | 3 locations | `0000 Codes & Standards/ISO/` |
| Norsok | 3 locations | `0000 Codes & Standards/Norsok/` |
| BSI | 3 locations | `0000 Codes & Standards/BSI/` |
| MIL | 3 locations | `0000 Codes & Standards/MIL/` |

---

## Phase 1: Codes & Standards Consolidation (First Task)

### Target Structure

```
/mnt/ace/O&G-Standards/          # NEW consolidated location
├── API/                         # American Petroleum Institute
│   ├── Specifications/          # API Spec documents
│   ├── Recommended-Practice/    # API RP documents
│   ├── Standards/               # API STD documents
│   ├── Bulletins/               # API Bulletins
│   └── Technical-Reports/       # API TR documents
├── DNV/                         # Det Norske Veritas
│   ├── Offshore-Standards/      # DNV-OS series
│   ├── Recommended-Practices/   # DNV-RP series
│   ├── Classification-Notes/    # DNV-CN series
│   ├── Service-Specs/           # DNV-OSS series
│   └── Guidelines/              # DNV Guidelines
├── ASTM/                        # ASTM International
│   ├── A-Series/                # Metals (A131, A320, etc.)
│   ├── D-Series/                # Petroleum, etc.
│   ├── E-Series/                # Testing methods
│   └── G-Series/                # Corrosion
├── ISO/                         # International Standards
│   ├── 13xxx/                   # Offshore (13624, 13628, etc.)
│   ├── 14xxx/                   # Welding, thermal spray
│   ├── 15xxx/                   # Materials
│   └── 19xxx/                   # Arctic, drilling
├── Norsok/                      # Norwegian Standards
├── BSI/                         # British Standards
├── MIL/                         # Military Standards
├── SNAME/                       # Ship/marine
├── NEMA/                        # Electrical
├── OnePetro/                    # Technical papers
└── _catalog.json                # Metadata index
```

### Consolidation Script Approach

```python
# Pseudocode for consolidation
1. SCAN all source directories for PDF/DOC files
2. EXTRACT metadata (filename, size, hash, modified date)
3. IDENTIFY duplicates by content hash (MD5/SHA256)
4. SELECT best version (newest, largest, best quality)
5. ORGANIZE by standard organization and document type
6. COPY (not move) to new consolidated structure
7. GENERATE catalog index with metadata
8. VERIFY completeness and report
```

### Implementation Steps

1. **Build Document Inventory**
   - Scan all codes directories
   - Extract: path, filename, size, hash, modified date
   - Store in SQLite database for querying

2. **Identify Duplicates**
   - Group by content hash
   - Mark duplicates vs originals
   - Report duplicate statistics

3. **Create Target Structure**
   - Create consolidated directory tree
   - Document organization rules

4. **Copy & Organize**
   - Copy unique files to new structure
   - Rename with consistent naming convention
   - Preserve original paths in metadata

5. **Generate Catalog**
   - JSON/SQLite catalog of all standards
   - Searchable by: org, number, title, keywords

6. **Verification**
   - Confirm all originals preserved
   - Validate no data loss
   - Generate consolidation report

---

## Full Implementation Plan (4+ Weeks)

### Phase 1: Codes & Standards Consolidation (Week 1)
**Goal:** Single organized directory, no duplicates

**Deliverables:**
- [ ] Python consolidation script
- [ ] SQLite document inventory database
- [ ] Duplicate detection report
- [ ] Consolidated `/mnt/ace/O&G-Standards/` directory
- [ ] Catalog JSON/SQLite with all metadata

**Tasks:**
1. Create inventory script to scan all source directories
2. Build SQLite database with file metadata + content hashes
3. Generate duplicate report (expected: 40-60% reduction)
4. Create target directory structure
5. Copy unique files with consistent naming
6. Generate searchable catalog

### Phase 2: Searchable Catalog System (Week 2)
**Goal:** Fast keyword search across all standards

**Deliverables:**
- [ ] Full-text search index (SQLite FTS5 or Elasticsearch)
- [ ] CLI search tool
- [ ] Web-based catalog browser (optional)
- [ ] Standard number parser (API RP 2RD → org: API, type: RP, num: 2RD)

**Tasks:**
1. Extract text from PDF titles/first pages
2. Parse standard numbers from filenames
3. Build full-text search index
4. Create CLI search tool
5. Generate HTML catalog for browsing

### Phase 3: AI Q&A System (Weeks 3-4)
**Goal:** Ask engineering questions, get answers with source references

**Deliverables:**
- [ ] PDF text extraction pipeline
- [ ] Vector embeddings (OpenAI or local)
- [ ] ChromaDB/Qdrant vector store
- [ ] Claude RAG integration
- [ ] Source citation system

**Tasks:**
1. Extract text from all consolidated PDFs
2. Chunk documents for embedding
3. Generate embeddings
4. Store in vector database
5. Build retrieval-augmented generation pipeline
6. Create Claude Code integration for engineering Q&A

### Phase 4: Production System (Weeks 5-6+)
**Goal:** Robust, maintainable knowledge system

**Deliverables:**
- [ ] Automated ingestion pipeline for new documents
- [ ] Web UI for search and Q&A
- [ ] Usage analytics
- [ ] Backup and sync system
- [ ] Documentation

**Optional Enhancements:**
- Multi-repository integration (connect to 2H Projects, Production)
- CAD file metadata indexing
- Project-to-standard cross-referencing

---

## Key Standards Identified in Collection

### Offshore/Subsea (High Priority)
- DNV-OS-F101 (Submarine Pipeline Systems)
- DNV-RP-F105, F106, F107, F108 (Pipeline analysis)
- API RP 2RD (Risers) - Multiple versions found
- API RP 579 (Fitness for Service)
- API RP 2A-WSD, 2A-LRFD (Platform design)
- API 16Q (Drilling riser design)
- ISO 13628 (Subsea systems)
- ISO 13624 (Drilling risers)

### Materials & Testing
- ASTM A131, A320, A350, A508 (Structural steels)
- ASTM A182, A193, A194 (Flanges, bolting)
- API 5L (Line pipe)
- API 5CT (Casing/tubing)
- ISO 15156 (NACE/SSC requirements)

### Technical Papers
- OTC papers (Offshore Technology Conference)
- BP SCR Design Guidelines
- VIV analysis procedures
- Wellhead fatigue methodologies

---

## Technical Implementation Details

### Consolidation Script Location
```
/mnt/github/workspace-hub/scripts/og-standards/
├── consolidate.py           # Main consolidation script
├── inventory.py             # Document inventory builder
├── dedup.py                 # Duplicate detection
├── catalog.py               # Catalog generator
└── config.yaml              # Configuration
```

### Source Directories to Process
```python
SOURCE_DIRS = [
    "/mnt/ace/0000 O&G/0000 Codes & Standards",
    "/mnt/ace/0000 O&G/Oil and Gas Codes",
]

# Exclude project-specific copies
EXCLUDE_PATTERNS = [
    "*/2H Projects/*",
    "*/Production/*",
]
```

### Target Directory
```
/mnt/ace/O&G-Standards/      # Consolidated standards library
```

### File Types to Process
```python
STANDARD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
```

---

## Next Steps

1. **Approve Plan** - Review this plan and confirm approach
2. **Start Phase 1** - Build consolidation scripts
3. **Run Inventory** - Generate document inventory with duplicate analysis
4. **Review Duplicates** - User reviews duplicate report before deletion
5. **Execute Consolidation** - Copy unique files to new structure
6. **Verify** - Confirm all standards accessible in new location
