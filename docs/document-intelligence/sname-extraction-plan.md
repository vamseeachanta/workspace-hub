# SNAME Naval Architecture Knowledge Extraction Plan

> **Issue:** #1291
> **Date:** 2026-04-05
> **Status:** Plan

## 1. Collection Scope

The SNAME (Society of Naval Architects and Marine Engineers) collection contains technical papers, transaction records, and design guides covering naval architecture and marine engineering fundamentals. This represents the primary academic knowledge base for the ACE engineering digitalmodel repository's naval_architecture module.

**Estimated volume:** ~145 files identified in `/mnt/ace/O&G-Standards/` and related directories, plus conference proceedings and transaction archives.

## 2. Key Topics and Domain Mapping

### 2.1 Hull Forms and Geometry
- Hull series parametrics (Wigley, Series 60, DTMB)
- Hull resistance decomposition (frictional, residual, wave-making)
- Block coefficient, waterplane coefficient, prismatic coefficient relationships
- Bulbous bow optimization studies
- Trimaran and multihull form analysis

**digitalmodel target:** `digitalmodel/naval_architecture/hull_forms/`

### 2.2 Resistance and Propulsion
- ITTC 1978 performance prediction method
- Holtrop-Mennen resistance estimation series
- Propeller design series (B-series, high-skew designs)
- Wake fraction and thrust deduction coefficients
- Self-propulsion point determination

**digitalmodel target:** `digitalmodel/naval_architecture/resistance/`

### 2.3 Stability and Seakeeping
- Intact stability criteria (IMO, regulatory)
- Damage stability assessment methodologies
- Righting arm (GZ) curve analysis
- Parametric rolling and pure loss of stability in waves
- Seakeeping RAO-based motion prediction

**digitalmodel target:** `digitalmodel/naval_architecture/stability/`

### 2.4 Structural Design
- Ship girder longitudinal strength assessment
- Plate buckling and stiffener panel design
- Fatigue assessment of ship structural details
- Classification society rule-based scantling
- Finite element modeling of hull girders

**digitalmodel target:** `digitalmodel/naval_architecture/structural/`, `digitalmodel/structural/`

### 2.5 Specialized Naval Architecture
- Maneuvering prediction (MMG model, captive model testing)
- Vibration analysis and resonance avoidance
- Lightweight and weight estimation methods
- Powering margin and speed trial analysis

## 3. Extraction Pipeline Design

### Phase 1: Document Classification (Week 1)
1. Scan SNAME PDFs for digital vs scanned content
2. Run OCR on scanned documents (Tesseract, 300 DPI minimum)
3. Classify by sub-topic using keyword heuristics and keyword-matching patterns
4. Produce extraction manifest: SNAME doc -> target digitalmodel module

### Phase 2: Methodology Extraction (Week 2-3)
1. For each classified document, extract:
   - Mathematical formulas and equations
   - Empirical coefficients and correction factors
   - Design procedure steps
   - Reference data tables and curves
   - Validation case studies with numerical data

2. Structure output as:
   ```yaml
   source: SNAME_Transaction_XXXX.pdf
   domain: naval_architecture
   subdomain: resistance
   topic: Holtrop-Mennen
   formulas: [...]
   coefficients: {...}
   procedure_steps: [...]
   validation_data: [...]
   ```

### Phase 3: Code Integration Planning (Week 4)
1. Map extracted methods to existing digitalmodel modules
2. Identify gaps where new modules need to be created
3. Prioritize extraction-to-code pipeline by:
   - Frequency of method reference in job market (high-demand skills)
   - Reusability across client projects
   - Complexity/effort ratio

## 4. Integration with digitalmodel/naval_architecture

### Current State
The `digitalmodel` repository has placeholder or partial implementations in naval architecture. This extraction will provide:
- Validation data for existing models (comparing computed vs published values)
- New algorithm implementations from established literature
- Reference datasets for unit tests

### Integration Path
1. **Extraction output** -> `data/naval_architecture/sname/` (raw extracted data)
2. **Method validation** -> `digitalmodel/tests/naval_architecture/` (pytest fixtures)
3. **Algorithm implementation** -> `digitalmodel/naval_architecture/` (production code)
4. **Documentation** -> `digitalmodel/docs/naval_architecture/` (user guides)

## 5. Priority Ordering

### Tier 1 (Immediate - Highest GTM Value)
1. Resistance estimation (Holtrop-Mennen, ITTC) — directly billable
2. Stability calculations (GZ curves, damage stability) — regulatory compliance
3. Structural scantling — classification society submissions

### Tier 2 (Near-term)
4. Propulsion calculations — vessel performance studies
5. Hull form optimization — early-phase design studies
6. Maneuvering prediction — mooring and operations planning

### Tier 3 (Long-term)
7. Seakeeping and motion analysis — coupled with OrcaFlex workflows
8. Vibration analysis — structural integrity studies
9. Weight estimation — project scoping tools

## 6. Quality Gates

Each extracted method must pass:
1. **Completeness:** All formulas, coefficients, and procedure steps captured
2. **Verification:** Computed results against published validation cases match within tolerance
3. **Traceability:** Source document, page number, and section reference maintained
4. **Testability:** At least one worked example converted to automated test fixture
5. **Reproducibility:** Another engineer can independently reproduce results from extracted data
