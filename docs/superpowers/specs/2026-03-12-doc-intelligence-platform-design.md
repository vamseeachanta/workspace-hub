# Doc Intelligence Platform — Design Spec
**Date:** 2026-03-12
**Status:** Approved
**WRK context:** WRK-1113 (proof-of-concept) → Feature WRK (platform)

---

## Problem Statement

The workspace has 1,033,926 documents indexed but zero content extracted. Engineers
re-read documents every time they need a constant, equation, or procedure. The goal is
a zero-look-back guarantee: once a document is absorbed, nothing in it ever needs to be
looked up again — all content lives in the codebase as queryable, reusable artifacts.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Extraction trigger | Hybrid (auto + on-demand + internet) | Scales to 1M; curated paths for high-value docs |
| Content types | All 8 (constants, tables, equations, examples, curves, procedures, requirements, definitions) | Zero-look-back requires complete extraction |
| Storage model | Dual-layer: per-doc manifests + federated indexes | Traceable AND queryable |
| Existing source integration | Federation (Option 3) | Non-breaking; existing ledger/data-sources untouched |
| GitHub exposure | Scripts + promoted artifacts only; manifests/indexes gitignored | Public repo; client doc content must not leak |
| Promoted artifact completeness | All extracted items promoted, not just WRK-relevant ones | Comprehensive = trustworthy |

---

## Pre-Conditions (before first extraction run)

**These must be applied before any `extract-document.py` run to prevent accidental commit of client content:**

1. Add to `.gitignore`:
   ```
   # Doc Intelligence Platform (WRK-1113+)
   data/doc-intelligence/
   ```
2. Confirm `data/standards/` does not exist or is empty before first promotion run.
   If it exists with existing content, restrict promoted output to `data/standards/promoted/`.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Document Corpus                     │
│  1M local files + internet URLs                     │
└──────────────────────┬──────────────────────────────┘
                       │
              extract-document.py
              extract-url.py
              (guided by doc-extraction SKILL)
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         Layer 1: Extraction Manifests               │
│  data/doc-intelligence/manifests/<domain>/<ref>.yaml│
│  — gitignored (local only, rebuilt per machine)     │
│  — all 8 content types, every item                  │
│  — confidence per item, legal_status, validated flag│
└──────────────────────┬──────────────────────────────┘
                       │
              build-doc-intelligence.py
              (delete-by-doc-ref before re-index)
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         Layer 2: Federated Indexes                  │
│  data/doc-intelligence/indexes/                     │
│    constants.jsonl  equations.jsonl  tables/        │
│    curves/  procedures.jsonl  requirements.jsonl    │
│    definitions.jsonl  worked_examples.jsonl         │
│    manifest-index.jsonl                             │
│  — gitignored (regenerated from manifests)          │
└──────────────────────┬──────────────────────────────┘
                       │
              query-doc-intelligence.py
                       │
           ┌───────────┴────────────┐
           ▼                        ▼
┌──────────────────┐    ┌───────────────────────────┐
│  Stage 2         │    │  promote-to-code.py        │
│  Resource Intel  │    │                            │
│  (every WRK)     │    │  Python constants/fns      │
│                  │    │  CSV data files            │
│  --stage2-brief  │    │  pytest verification tests │
│  merges into     │    │  YAML skills (procedures)  │
│  resource-       │    │  Glossary YAML             │
│  intelligence    │    │                            │
│  .yaml under     │    │  ← COMMITTED TO GITHUB     │
│  doc_intel key   │    │    (after legal scan)       │
└──────────────────┘    └───────────────────────────┘
```

---

## Layer 1: Extraction Manifest Schema

**Location:** `data/doc-intelligence/manifests/<domain>/<doc-ref>.yaml`
**Gitignored:** yes — entire `data/doc-intelligence/` directory

```yaml
doc_ref: "2100-RPT-4005-06"
doc_title: "Cathodic Protection Design Report"
doc_type: report               # report|standard|calculation|guideline|web
domain: cathodic-protection
ledger_id: "XXX"               # ← links to standards-transfer-ledger entry
source: local                  # local|web|standard
source_path: acma-projects/B1522/ctr-2/ref/proj/...
source_available: true         # false if path absent on current machine
extractor: claude-sonnet-4-6
extraction_date: "2026-03-12"
extraction_cost_usd: 0.042     # LLM API cost for this extraction
confidence: high               # overall: high|medium|low
legal_status: pass             # pass|pending|blocked
exhausted: false
version: "Rev 6"
superseded_by: null            # doc_ref of newer edition if exists

document_map:                  # structural scan output (Layer 1 of skill)
  sections: ["§1 Scope", "§2 Definitions", "§3 Design Basis", ...]
  tables: ["Table 4.1 Current Density", "Table 5.1 Anode Properties", ...]
  figures: ["Fig 4.1 Current Density vs Depth", ...]
  equations: ["Eq 4.1 Current Demand", "Eq 4.2 Anode Mass", ...]

constants:
  - id: "2100-RPT-4005-06-const-001"
    name: current_density_bare_steel_seawater
    value: 0.025
    unit: A/m²
    section: "§4.2"
    note: "Initial current density for bare carbon steel in seawater"
    confidence: high
    validated: false
    promoted_to: null          # filled by promote-to-code.py: "module.py#L14"

tables:
  - id: "2100-RPT-4005-06-table-001"
    name: current_density_by_environment
    section: "Table 4.1"
    columns: [environment, j_initial_a_m2, j_mean_a_m2, j_final_a_m2]
    data:
      - [seawater_tropical, 0.025, 0.020, 0.010]
      - [seawater_arctic, 0.040, 0.030, 0.020]
    confidence: high
    promoted_to: null

equations:
  - id: "2100-RPT-4005-06-eq-001"
    name: current_demand
    section: "§4.3"
    formula: "I = A * j * (1 - cf)"
    variables:
      I: {description: "current demand", unit: A}
      A: {description: "surface area", unit: m²}
      j: {description: "current density", unit: A/m²}
      cf: {description: "coating factor", unit: "-"}
    python_fn: null            # filled after promotion
    confidence: high
    promoted_to: null

worked_examples:
  - id: "2100-RPT-4005-06-ex-001"
    equation_ref: "2100-RPT-4005-06-eq-001"
    section: "§4.4 Example 1"
    inputs: {area_m2: 150.0, current_density: 0.025, coating_factor: 0.05}
    expected: {value: 0.1875, unit: A, note: "doc states 0.19 A rounded"}
    test_file: null            # filled after promotion
    confidence: high
    promoted_to: null

curves:
  - id: "2100-RPT-4005-06-curve-001"
    name: current_density_vs_depth
    section: "Fig 4.1"
    x_label: depth_m
    y_label: current_density_a_m2
    data: [[0, 0.025], [50, 0.020], [100, 0.018], [200, 0.015]]
    interpolation: linear
    confidence: medium         # digitized from chart
    promoted_to: null

procedures:
  - id: "2100-RPT-4005-06-proc-001"
    name: cp_design_procedure
    section: "§3.0"
    steps:
      - "1. Determine surface area requiring CP"
      - "2. Select current density from Table 4.1 based on environment"
      - "3. Calculate current demand using Eq 4.1"
      - "4. Calculate anode mass using Eq 4.2"
    skill_file: null           # filled after promotion
    confidence: high
    promoted_to: null

requirements:
  - id: "2100-RPT-4005-06-req-001"
    section: "§5.1"
    text: "Anode spacing shall not exceed 300 mm in splash zone"
    normative: true
    keyword: anode spacing
    confidence: high
    promoted_to: null

definitions:
  - id: "2100-RPT-4005-06-def-001"
    term: coating breakdown factor
    symbol: cf
    section: "§2.1"
    definition: "Ratio of bare to total surface area accounting for coating degradation over design life"
    confidence: high
    promoted_to: null
```

---

## Layer 2: Federated Indexes

**Location:** `data/doc-intelligence/indexes/` — gitignored (part of `data/doc-intelligence/`)
**Built by:** `scripts/data/doc-intelligence/build-doc-intelligence.py`
**Re-index contract:** before inserting entries for a doc-ref, all existing entries for that
doc-ref are deleted first — prevents duplicates on re-extraction or re-indexing.
**Incremental rebuild:** `--since <date>` reprocesses only manifests modified after date;
`--doc <doc-ref>` reprocesses a single manifest (delete-then-insert).

```
indexes/
  constants.jsonl           # {id, doc_ref, domain, name, value, unit, section, confidence, validated}
  equations.jsonl           # {id, doc_ref, domain, name, formula, variables, python_fn, confidence}
  worked_examples.jsonl     # {id, doc_ref, domain, equation_ref, inputs, expected, test_file}
  procedures.jsonl          # {id, doc_ref, domain, name, steps, skill_file, confidence}
  requirements.jsonl        # {id, doc_ref, domain, text, normative, keyword}
  definitions.jsonl         # {id, doc_ref, domain, term, symbol, definition}
  tables/
    cathodic-protection/    # <table-id>.csv per table
    drilling-riser/
    structural/
  curves/
    cathodic-protection/    # <curve-id>.csv per curve
    drilling-riser/
  manifest-index.jsonl      # {doc_ref, domain, exhausted, confidence, item_counts_by_type}
```

---

## Federated Query Interface

**Script:** `scripts/data/doc-intelligence/query-doc-intelligence.py`

```bash
# Constants for a domain
query-doc-intelligence.py --type constant --domain cathodic-protection

# Search by keyword across all types
query-doc-intelligence.py --keyword "current density"

# Equations not yet implemented in code
query-doc-intelligence.py --type equation --status extracted

# Stage 2 resource intelligence brief
query-doc-intelligence.py --stage2-brief --domain drilling-riser

# Full federation: joins ledger + data-sources + doc-intel
query-doc-intelligence.py --domain cathodic-protection --full
```

**Stage 2 integration:** `--stage2-brief` outputs a YAML block that is **merged** into the
`doc_intelligence_brief` key of the existing `evidence/resource-intelligence.yaml` (create
key if absent, overwrite if present). Stage 2 calls this script when a domain-matched
manifest-index entry exists; silently skips (no error) when no manifests exist for the domain.

```yaml
# Merged into evidence/resource-intelligence.yaml under doc_intelligence_brief:
doc_intelligence_brief:
  domain: cathodic-protection
  queried_at: "2026-03-12T17:00:00Z"
  constants_available: 47
  equations_available: 23
  equations_implemented: 14
  procedures_available: 8
  gaps: [impressed_current_sizing, coating_breakdown_sweep]
  key_sources: [2100-RPT-4005-06, 3824-TNE-0008-2, DNV-RP-B401]
```

---

## Extraction Pipeline

### Entry Points

| Entry | Command | Use case |
|-------|---------|----------|
| On-demand | `extract-document.py <doc-ref>` | High-value curated doc |
| Queue | `queue-extraction.py add <doc-ref> [--priority high]` | Batch with priority |
| Internet | `extract-url.py <url>` | Web page or online PDF |

### Pipeline Stages

```
1. Fetch        resolve path from index.jsonl or fetch URL
                → if source_path absent on machine: set status=source_unavailable,
                  log warning, exit 0 (queue item surfaced in queue report, not silently dropped)

2. Parse        PDF→text (pdfplumber), DOCX→text, XLSX→tables

3. Structure    doc-extraction SKILL Layer 1: produces document_map

4. Extract      doc-extraction SKILL Layer 2: all 8 content types

5. QC           doc-extraction SKILL Layer 3: completeness + confidence assignment

6. Legal scan   scripts/legal/legal-sanity-scan.sh per-item pass
                → block-severity items: stripped from manifest (item removed, not just flagged)
                → warn-severity items: kept with legal_status: warn
                → if >50% of items blocked: set manifest legal_status=blocked,
                  abort pipeline, do not write manifest
                → otherwise: write manifest with blocked items removed

7. Save         write manifest to manifests/<domain>/<doc-ref>.yaml
                (atomic write: temp file → rename)

8. Index        build-doc-intelligence.py --doc <doc-ref>
                (delete existing entries for doc-ref first)

9. Validate     human reviews confidence:medium/low items → sets validated:true per item

10. Promote     promote-to-code.py <doc-ref> --all
                → legal scan runs per artifact before commit
                → blocked artifacts: skip + log (do not halt batch)
                → clean artifacts: commit immediately
                → updates manifest promoted_to field per item

11. Exhaust     mark-exhausted.py <doc-ref> <module>
```

### Extraction Queue

**Location:** `data/doc-intelligence/extraction-queue.yaml` — gitignored

```yaml
queue:
  - doc_ref: "2100-RPT-4005-06"
    priority: high
    domain: cathodic-protection
    # status: queued|extracting|draft|legal_blocked|source_unavailable|
    #         indexed|validated|exhausted
    status: validated
    added_at: "2026-03-12"
    extracted_at: "2026-03-12"
    validated_at: "2026-03-12"
    cost_usd: 0.042
```

---

## Extraction Skill

**Location:** `.claude/skills/engineering/doc-extraction/SKILL.md`
**Invocation:** called by `extract-document.py`; also `/doc-extract <doc-ref>`

Three layers:
1. **Structure Scan** — maps all sections, tables, figures, equations before extracting
2. **Content Extraction** — per-section pass for all 8 content types
3. **Quality Check** — validates completeness, assigns confidence, pre-legal-scan check

Domain sub-skills extend Layer 2 with domain-specific lookup knowledge:
```
.claude/skills/engineering/doc-extraction/domains/
  cathodic-protection.md    looks for: current density tables, anode mass formulas, coating factors
  drilling-riser.md         looks for: tension capacity, RAO data, operability envelopes
  structural.md
  pipeline.md
```

---

## Code Artifact Promotion

**Script:** `scripts/data/doc-intelligence/promote-to-code.py`

| Manifest type | Promoted artifact | Location | Committed | TDD requirement |
|---------------|------------------|----------|-----------|-----------------|
| constants | Python SCREAMING_SNAKE_CASE with §ref comment | `digitalmodel/src/…/<module>.py` | ✅ | sanity-range test (value within physically plausible bounds) |
| tables | CSV + Python dict/DataFrame loader | `data/standards/promoted/<domain>/<name>.csv` | ✅ | schema-validation test (columns present, no nulls in key columns) |
| equations | Typed Python function with §ref docstring | `digitalmodel/src/…/<module>.py` | ✅ | worked_example test (covered by worked_examples row below) |
| worked_examples | pytest verification test | `digitalmodel/tests/…/test_*_doc_verified.py` | ✅ | is the test itself (asserts equation against doc example) |
| curves | CSV + scipy interpolation wrapper | `data/standards/promoted/<domain>/<name>-curve.csv` | ✅ | interpolation smoke test (endpoint values match source data) |
| procedures | YAML skill file | `.claude/skills/engineering/<domain>/` | ✅ | YAML schema-valid test |
| requirements | Checklist in module docstring or YAML skill | module docstring | ✅ | presence test (grep for requirement keyword in module) |
| definitions | Domain glossary YAML | `data/standards/promoted/<domain>/glossary.yaml` | ✅ | schema-valid + term uniqueness test |

All promotion is comprehensive — every extracted item is promoted, not just WRK-relevant ones.
Legal scan runs per artifact before commit. Blocked artifacts are skipped and logged; clean
artifacts are committed immediately (partial promotion is valid — blocked items are retried
after the root cause is fixed).

---

## Versioning + Conflict Resolution

**Versioning:** manifests are versioned by `doc_ref` + `version` field. When a new edition
is published, a new manifest is created; old manifest gets `superseded_by: <new-doc-ref>`.
Code artifacts carry a `# source: <doc-ref> <version> §ref` comment.

**Conflict resolution for constants:** when two docs give different values, both are kept
in the index. The higher-confidence / newer-edition value wins in the promoted Python
constant. The losing value is preserved as a commented-out line:
```python
CURRENT_DENSITY_BARE_STEEL = 0.025  # A/m² — 2100-RPT-4005-06 Rev6 §4.2
# superseded: DNV-RP-B401-2011 §6.2 gave 0.020 A/m² (older edition)
```

**Conflict resolution for tables/curves:** conflicting rows are both kept in the index with
their source refs. The promoted CSV uses the winning source; the losing rows are written to
a `<name>-alt-sources.csv` alongside it for reference.

---

## WRK Scope Mapping

```
Feature WRK: Doc Intelligence Platform
  ├── WRK-1113 (current, working)
  │   Proof-of-concept: 24 docs (CP + Drilling Riser)
  │   Validates full pipeline end-to-end before scaling
  │   Phase 0 infra: ledger schema, mark-exhausted, coverage report ✅
  │
  ├── WRK-XXXX  .gitignore update + data/standards/promoted/ scaffold (pre-condition)
  ├── WRK-XXXX  doc-extraction SKILL + domain sub-skills (CP, drilling-riser)
  ├── WRK-XXXX  extract-document.py + parse layer (pdfplumber, DOCX, XLSX)
  ├── WRK-XXXX  build-doc-intelligence.py + federated indexes
  ├── WRK-XXXX  query-doc-intelligence.py + Stage 2 resource-intelligence integration
  ├── WRK-XXXX  promote-to-code.py (all 8 types + TDD per type)
  ├── WRK-XXXX  extract-url.py (internet docs)
  └── WRK-XXXX  batch pipeline (1M doc queue + cost tracking)
```

---

## Gitignore Policy

```
# gitignored (entire directory — local runtime, rebuilt from source documents)
data/doc-intelligence/

# committed to GitHub (scripts + promoted artifacts, after legal scan)
scripts/data/doc-intelligence/
.claude/skills/engineering/doc-extraction/
data/standards/promoted/           # promoted tabular data (CSV, glossary YAML)
digitalmodel/src/…/                # promoted Python constants + functions
digitalmodel/tests/…/              # promoted verification tests
.claude/skills/engineering/*/      # promoted procedure skills
```

---

## Success Criteria

- [ ] `.gitignore` updated: `data/doc-intelligence/` excluded before first extraction run
- [ ] Any engineer can run `query-doc-intelligence.py --keyword X` and get all known values
- [ ] Stage 2 of every WRK merges a doc-intelligence brief for its domain (silently skips if none)
- [ ] `promote-to-code.py` produces committed, tested, legal-clean artifacts for all 8 types
- [ ] `extract-url.py <url>` produces a validated manifest within one session
- [ ] WRK-1113 (24 docs) validates the full pipeline end-to-end before scaling to 1M
- [ ] zero-look-back: once `exhausted: true`, the source document is never consulted again
- [ ] Re-extraction of an existing doc-ref produces no duplicate index entries
