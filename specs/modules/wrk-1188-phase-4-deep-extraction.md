# WRK-1188 Phase 4: Deep Extraction on High-Value Standards

## Objective

Run `deep-extract.py` on 9 high-value API RP and DNV-RP documents to extract tables,
worked examples, and charts. Use each extraction as a feedback loop to enhance the
deep extraction scripts and doc-intelligence-promotion skill.

## Target Documents

| Doc | Edition | Size | Domain | Existing Code |
|-----|---------|------|--------|---------------|
| DNV-RP-B401 | 1993 | 0.8MB | cathodic-protection | `digitalmodel/cathodic_protection/dnv_rp_b401.py` |
| DNV-RP-F109 | - | 0.8MB | pipeline | `digitalmodel/geotechnical/on_bottom_stability.py` |
| DNV-RP-C203 | 2011 | 3.4MB | fatigue | `assetutilities` S-N curves |
| DNV-RP-C205 | - | 2.8MB | marine/hydrodynamics | hydrodynamics skill |
| DNV-RP-F105 | 2002 | 8.4MB | pipeline/VIV | VIV analysis skill |
| API RP 1111 | 4th 2009 | 5.2MB | pipeline | pipeline wall thickness |
| API RP 2SK | 3rd 2005 | 18.0MB | mooring | mooring-design skill |
| API RP 2A | 21st 2000 | 18.7MB | structural | structural-analysis skill |
| API 579 | 2016 | 10.4MB | asset-integrity | fitness-for-service skill |

**Execution order**: Smallest first (faster feedback loops), increasing complexity.

## Execution Plan

### Step 1: DNV-RP-B401 (pilot — 0.8MB, CP domain)

**Why first**: Smallest file, well-understood domain, existing Python module to validate against.

```bash
uv run --no-project python scripts/data/doc-intelligence/deep-extract.py \
    --input "/mnt/ace/O&G-Standards/API/..." --domain cathodic-protection \
    --report --verbose
```

**Expected extractions**:
- Tables: Anode material properties (Al-Zn-In alloy), seawater resistivity, coating breakdown factors
- Worked examples: Anode weight calculation, current demand for jacket/pipeline
- Charts: Current density vs temperature, coating breakdown vs time

**Validate against**: `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` constants

**Skill enhancement targets**:
- Does `worked_example_parser.py` handle DNV's "Example" format? (not always "Example N.N:")
- Does `table_exporter.py` handle multi-page tables with repeated headers?
- Does `extract_engineering_constants.py` catch inline constants like "ρ = 0.30 Ω·m"?

### Step 2: DNV-RP-F109 (0.8MB, pipeline stability)

**Expected**: Stability criteria tables, Morison coefficient tables, worked stability checks.
**Validate against**: `digitalmodel/geotechnical/on_bottom_stability.py`

### Step 3: DNV-RP-C203 (3.4MB, fatigue)

**Expected**: S-N curve tables (critical — 221 curves across 17 standards), SCF formulas, fatigue examples.
**Validate against**: `assetutilities` S-N curve data.

### Step 4: DNV-RP-C205 (2.8MB, environmental loads)

**Expected**: Wave spectrum parameters, drag/inertia coefficients, wind speed profiles.
**Validate against**: hydrodynamics skill constants.

### Step 5: DNV-RP-F105 (8.4MB, free span VIV)

**Expected**: VIV screening tables, modal analysis worked examples, response model parameters.

### Step 6: API RP 1111 (5.2MB, pipeline design)

**Expected**: Wall thickness formulas, collapse pressure equations, design factor tables.

### Step 7: API RP 2SK (18.0MB, mooring)

**Expected**: Mooring line property tables, catenary equations, safety factor tables.

### Step 8: API RP 2A (18.7MB, offshore platforms)

**Expected**: Pile capacity tables, wave force coefficients, member stress check procedures.

### Step 9: API 579 (10.4MB, fitness for service)

**Expected**: Assessment level decision trees, flaw acceptance tables, stress intensity factors.

## Learning Loop (after each doc)

After each extraction:

1. **Audit**: Run `scripts/data/doc_intelligence/audit_extractions.py` on manifest
2. **Compare**: Cross-check extracted constants/tables against existing Python code
3. **Identify gaps**: What did the parser miss? What format wasn't handled?
4. **Enhance script**: Fix the gap in the appropriate script:
   - `worked_example_parser.py` — new example format patterns
   - `table_exporter.py` — multi-page table handling, merged cell logic
   - `chart_extractor.py` — figure reference linking heuristics
   - `extract_engineering_constants.py` — inline constant regex patterns
   - `parse_standard_reference.py` — section reference formats
5. **Re-run**: Re-extract with improved scripts, verify fix
6. **Update skill**: Add learnings to `doc-intelligence-promotion/SKILL.md`

## Script Enhancement Targets (pre-identified)

| Script | Known Gap | Enhancement |
|--------|-----------|-------------|
| `worked_example_parser.py` | Only handles "Example N.N:" format | Add DNV "Example", API "Sample Problem" patterns |
| `table_exporter.py` | Single-page tables only | Handle multi-page tables with repeated headers |
| `extract_engineering_constants.py` | Misses Greek symbol constants | Add regex for ρ, α, σ, ε with units |
| `chart_extractor.py` | No S-N curve detection | Add log-log axis detection for S-N and fatigue charts |
| `deep_extract.py` | No extraction quality score | Add confidence scoring per extracted item |
| `normalize_units.py` | Missing offshore units | Add ksi, bar, t/m³, mA/m² |

## Acceptance Criteria

1. [ ] All 9 target docs deep-extracted with manifests + CSV + metadata
2. [ ] Extraction reports YAML for each doc in `data/doc-intelligence/reports/`
3. [ ] At least 3 script enhancements merged (from learning loop)
4. [ ] `doc-intelligence-promotion/SKILL.md` updated with new patterns
5. [ ] Extracted tables validated against existing Python module constants
6. [ ] Worked examples converted to pytest stubs (minimum 10 across all docs)
7. [ ] Extraction learnings captured in `extraction-learnings-phase4.yaml`

## Budget

- LLM cost: $0 (deep extraction is deterministic — PyMuPDF + regex)
- Compute: ~30 min total across 9 docs
- Human review: Worked example validation, chart calibration metadata
