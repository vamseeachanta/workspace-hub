# Data Intelligence Reference

## Purpose

Surface domain-specific data assets during /work session startup, planning, and
research phases. This enables grounded, evidence-based execution by connecting
WRK items to the corpus of standards, worked examples, and document intelligence.

Issue: #1321 (WRK-5126)

## Available Data Assets

| Asset | Location | Records | Description |
|-------|----------|---------|-------------|
| Standards Ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 | Industry standards by domain with implementation status |
| Worked Examples | `data/doc-intelligence/worked_examples.jsonl` | 423 | Calculation examples extracted from reference texts |
| Test Vectors | `tests/fixtures/test_vectors/` | 255 curated | Gold/silver/bronze quality-tiered test fixtures |
| Document Index | `data/document-index/index.jsonl` | 1M+ pages | Full-text page-level records with summaries |
| Registry | `data/document-index/registry.yaml` | stats | Aggregate stats by domain and source |

## Domains

The standards ledger covers these domains:
- **materials** (122) — material specifications, testing standards
- **structural** (72) — structural analysis, platform design codes
- **pipeline** (55) — pipeline design, operations, inspection
- **process** (55) — process engineering, equipment sizing
- **marine** (33) — marine operations, vessel design, mooring
- **cad** (23) — drawing standards, CAD conventions
- **installation** (22) — offshore installation procedures
- **cathodic-protection** (19) — CP system design standards
- **regulatory** (15) — regulatory compliance, HSE
- **drilling** (9) — drilling operations and equipment

## How to Query

### From Shell (session scripts)

```bash
# Direct domain query
bash scripts/session/data-intelligence-context.sh --domain marine

# From WRK file (auto-extracts category/subcategory → domain)
bash scripts/session/data-intelligence-context.sh --wrk-file .claude/work-queue/working/WRK-123.md

# From WRK subcategory
bash scripts/session/data-intelligence-context.sh --subcategory cathodic-protection

# JSON output for machine consumption
bash scripts/session/data-intelligence-context.sh --domain pipeline --format json
```

### From Python (GSD agents / subagents)

```bash
uv run --no-project python scripts/session/data-intelligence-context.py \
    --domain marine --format json
```

## Integration Points

### Session Briefing (automatic)
The `session-briefing.sh` script calls `data-intelligence-context.sh` automatically
when an active WRK item is in the working/ queue. The briefing shows:
- Standards count and status breakdown for the WRK's domain
- Gap count (standards not yet captured — potential new WRK items)
- Worked examples count and source documents
- Test vector availability and quality tiers
- Document index page count

### Research Phase
When `/gsd:research-phase` or `/gsd:plan-phase` runs discovery, the researcher
can query the data intelligence to:
1. Find which industry standards are relevant to the phase domain
2. Locate worked examples that could serve as test vectors
3. Identify existing document summaries for reference

### Plan Phase
When `/gsd:plan-phase` creates PLAN.md files, the planner can reference:
1. Standards that the implementation should comply with
2. Test vectors available for validation
3. Gap standards that suggest future WRK items

## Domain Resolution

WRK items use `category` and `subcategory` in frontmatter. The data intelligence
script maps these to ledger domains:

| WRK subcategory | Ledger domain |
|-----------------|---------------|
| cathodic-protection | cathodic-protection |
| pipeline, subsea, riser | pipeline |
| marine, naval-architecture, mooring | marine |
| structural | structural |
| materials | materials |
| process, energy-economics | process |
| cad | cad |
| installation | installation |
| regulatory | regulatory |
| drilling | drilling |
