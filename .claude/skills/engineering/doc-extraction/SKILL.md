---

name: doc-extraction
description: 'Classify and extract structured content from engineering documents using a 3-layer taxonomy: generic content
  types, engineering patterns, and domain sub-skills. Use when ingesting standards, reports, or technical manuals into structured
  data for downstream analysis.

  '
version: 1.0.0
updated: 2026-03-12
category: engineering
triggers:
- document extraction
- content classification
- extract constants
- extract equations
- extract tables
- parse engineering document
- ingest standard
- technical manual extraction
capabilities:
- content-type-classification
- engineering-pattern-extraction
- standards-reference-parsing
- unit-normalization
requires: []
tags: []
scripts_exempt: true
---

# Doc-Extraction Skill

Classify and extract structured content from engineering documents. The skill
operates in three layers: generic content classification, engineering-specific
pattern recognition, and domain sub-skills for specialized heuristics.

## Yield Reality (WRK-1246 Corpus Assessment)

WRK-1246 assessed deep extraction yield across 420K+ text-extractable documents.
Only two content types have proven extraction yield from the current parsers:

| Content type | Yield | Status |
|-------------|-------|--------|
| tables | 69-93% | **Production-ready** — primary extraction target |
| figure_refs | 1-52% | **Partial** — metadata only, varies by stratum |
| equations | 0% | Not yet implemented — parsers do not reliably detect |
| constants | 0% | Not yet implemented — parsers do not reliably detect |
| procedures | 0% | Not yet implemented — parsers do not reliably detect |
| worked_examples | 0% | Not yet implemented — parsers do not reliably detect |

These content types are NOT currently extractable from the corpus — they exist in the
manifest schema (documented below) but the parsers do not reliably detect them. The
schema is retained for future parser development.

## When to Use

- Ingesting a new standard or code (DNV-RP, API RP, ISO, ASME)
- Extracting constants, equations, or tables from technical reports
- Building structured datasets from engineering manuals
- Populating knowledge bases from document collections
- Pre-processing documents before analysis workflow

## Architecture

```
doc-extraction/
  SKILL.md                       # Layers 1+2: generic + engineering (this file)
  cp/SKILL.md                    # Layer 3: cathodic protection domain
  drilling-riser/SKILL.md        # Layer 3: drilling riser domain
  naval-architecture/SKILL.md    # Layer 3: naval architecture domain
```

## Layer 1: Content Type Classification

Eight content types cover the structural building blocks of engineering documents.

### 1. `constants` (0% yield — not yet implemented)

Named values with units that remain fixed within a standard or design context.

**Detection heuristics**: Named value with "=" sign, units in parentheses or
brackets, appears in tables or definition lists, often prefixed with a symbol
(Greek or Latin letter).

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `name` | Human-readable name |
| `symbol` | Mathematical symbol (e.g. `f_ci`, `ρ`) |
| `value` | Numeric value |
| `units` | SI or field units |
| `source_standard` | Standard reference (e.g. DNV-RP-B401 Sec 3.4) |

### 2. `equations` (0% yield — not yet implemented)

Mathematical relationships between variables.

**Detection heuristics**: Contains mathematical notation, Greek letters, operator
symbols (=, ×, /, ^), variable definitions follow the expression, often numbered
(Eq. 1, Equation 3.2).

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `name` | Equation name or number |
| `expression` | Mathematical expression (LaTeX or plain text) |
| `variables` | List of {symbol, name, units} |
| `source` | Standard and section reference |
| `applicability` | Conditions where equation applies |

### 3. `tables`

Tabular data — lookup values, design parameters, or comparison matrices.

**Detection heuristics**: Grid or tabular layout, header row with column labels,
numeric cells with units, often titled "Table N" or has a caption.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `title` | Table caption or identifier |
| `columns` | List of column headers with units |
| `rows` | Data rows as lists or dicts |
| `interpolation_method` | Linear, step, or none |
| `source` | Standard and table number |

### 4. `curves`

Graphical data — x-y relationships presented as figures.

**Detection heuristics**: Figure references ("Figure N", "Fig."), x-y axis labels,
data series legends, often accompanied by a caption describing the relationship.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `title` | Figure caption |
| `x_axis` | {label, units, range} |
| `y_axis` | {label, units, range} |
| `data_points` | Digitized x-y pairs |
| `source` | Standard and figure number |

### 5. `procedures` (0% yield — not yet implemented)

Sequential steps for performing an operation or assessment.

**Detection heuristics**: Numbered or lettered steps with sequential dependencies,
prerequisites section, action-oriented language. The distinguishing feature vs
`requirements` is sequential execution order — procedures describe *how* to do
something step-by-step, requirements state *what* must be true.

**Disambiguation rule**: If a clause contains both normative language ("shall")
and sequential steps, classify as `procedures` when the steps have execution
order, or `requirements` when each statement stands independently. Multi-label
output is allowed when both types genuinely co-exist in the same passage.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `title` | Procedure name |
| `steps` | Ordered list of step descriptions |
| `prerequisites` | Required inputs or conditions |
| `standard_ref` | Source standard and section |
| `decision_points` | Steps with branching logic |

### 6. `requirements`

Normative statements that define mandatory or recommended practice.

**Detection heuristics**: Contains "shall", "required", "must", "is to be";
often numbered with a requirement ID; may reference verification methods.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `id` | Requirement identifier |
| `text` | Full requirement statement |
| `standard_ref` | Source standard and clause |
| `verification_method` | How compliance is verified |
| `normative_strength` | shall / should / may |

### 7. `definitions`

Terms and their meanings as used within a standard or domain.

**Detection heuristics**: "means", "is defined as", "refers to"; glossary or
definitions section; term followed by colon or em-dash and explanation.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `term` | The defined term |
| `definition` | Full definition text |
| `source` | Standard and section |
| `synonyms` | Alternative terms |
| `domain` | Engineering sub-domain |

### 8. `worked_examples` (0% yield — not yet implemented)

Step-by-step calculations demonstrating application of equations or procedures.

**Detection heuristics**: "Example", "Sample calculation"; given/find/solution
pattern; specific numeric values substituted into equations; final answer with
units.

**Key extraction fields**:
| Field | Description |
|-------|-------------|
| `title` | Example identifier or description |
| `given` | Input parameters {name, value, units} |
| `solution_steps` | Ordered calculation steps |
| `answer` | Final result {name, value, units} |
| `source` | Standard and section/appendix |

## Layer 2: Engineering Extraction Patterns

Cross-cutting patterns that apply regardless of content type.

### Unit Detection and Normalization

Recognize units in parentheses, brackets, or inline: `(m/s²)`, `[ksi]`,
`N/mm²`. Normalize to a canonical form:

| Input variants | Canonical |
|---------------|-----------|
| `ksi`, `KSI` | `ksi` |
| `N/mm²`, `MPa` | `MPa` |
| `mA/m²`, `mA/m2` | `mA/m²` |
| `°C`, `deg C` | `°C` |
| `lb/ft`, `lbs/ft` | `lb/ft` |

Flag SI vs imperial vs field units. Prefer SI in output; keep original as
`units_original`.

### Standards Reference Parsing

Parse references like `DNV-RP-B401 Section 3.4.6` into structured form:

```yaml
standard_ref:
  body: DNV
  document: RP-B401
  edition: null         # null unless explicitly stated in source text
  edition_inferred: 2021  # set only when edition can be inferred; null otherwise
  section: 3.4.6
  table: null
  figure: null
  raw: "DNV-RP-B401 Section 3.4.6"
```

**Inference rule**: `edition` must be null unless the source text explicitly
states the year. Use `edition_inferred` only when surrounding context (title
page, header, or adjacent reference) provides strong evidence; never guess.

Common patterns:
- `DNV-RP-XXXX Sec N.N.N` / `Section N.N` / `Table N-N` / `Figure N-N`
- `API RP NNX Section N` / `API 579-1 Part N`
- `ASME BPVC Section VIII Div 2`
- `ISO NNNNN-N:YYYY Clause N.N`

### Safety and Design Factor Identification

Flag values tagged as safety factors, design factors, or usage factors:
- Keywords: "safety factor", "design factor", "utilisation factor", "usage factor"
- Often dimensionless ratios between 0 and 10
- Extract: {name, value, standard_ref, applicability}

### Material Property Recognition

Detect material properties in text or tables:
- Yield strength (SMYS), tensile strength (SMTS), Young's modulus
- Density, thermal expansion coefficient, Poisson's ratio
- Fatigue S-N curve parameters
- Extract: {property, value, units, material_grade, temperature, standard_ref}

### Condition and Applicability Tagging

Many values have applicability constraints. Tag extracted items with:
- Temperature range
- Depth/pressure range
- Material grade or category
- Environmental condition (seawater, air, buried)
- Service life assumptions

## Extraction Workflow

```
1. Identify document type (standard, report, manual, datasheet)
2. Segment into sections using headings and structure
3. For each section:
   a. Classify content type(s) from Layer 1
   b. Apply Layer 2 engineering patterns
   c. If domain sub-skill applies, delegate to Layer 3
4. Produce structured output (YAML or JSON)
5. Cross-reference extracted items (e.g. equations reference constants)
```

## Output Schema

Each extracted item follows this structure:

```yaml
- content_type: constants     # one of the 8 types
  source:
    document: "DNV-RP-B401"
    section: "3.4.6"
    page: 42
  data:
    name: "Initial coating breakdown factor"
    symbol: "f_ci"
    value: 0.05
    units: dimensionless
    applicability:
      coating_category: "I"
      description: "High quality >= 300 um epoxy"
  confidence: high            # high / medium / low
  extraction_notes: null
```

## Domain Sub-Skills

For domain-specific extraction heuristics, delegate to Layer 3 sub-skills:

| Domain | Sub-skill | When to use |
|--------|-----------|-------------|
| Cathodic protection | [cp/SKILL.md](cp/SKILL.md) | DNV-RP-B401, F103, CP design documents |
| Drilling riser | [drilling-riser/SKILL.md](drilling-riser/SKILL.md) | API RP 16Q, riser analysis reports |
| Naval architecture | [naval-architecture/SKILL.md](naval-architecture/SKILL.md) | SNAME PNA, IMO stability, classification rules |

## Hybrid Classification Strategy (WRK-1188 Learning)

For large homogeneous collections, prefer deterministic classifiers over LLM:

| Collection | Strategy | Cost | Accuracy |
|-----------|----------|------|----------|
| ASTM (25,537 docs) | Designation prefix → discipline | $0 | 86% vs LLM |
| API/DNV/ISO (1,062) | LLM (Claude Haiku CLI) | ~$2 | Baseline |
| Unknown org (484) | LLM (Claude Haiku CLI) | ~$1 | Baseline |

**Rule**: If org has predictable title/designation patterns, write a deterministic
classifier first. Validate with 100-doc LLM sample. Accept if >85%.

See `data/document-index-pipeline` skill for full pipeline orchestration.

## Related Skills

- [document-index-pipeline](../../data/document-index-pipeline/SKILL.md) — 7-phase A→G pipeline
- [doc-intelligence-promotion](../../data/doc-intelligence-promotion/SKILL.md) — Deep extraction post-processing
- [cathodic-protection](../marine-offshore/cathodic-protection/SKILL.md) — CP system design
- [viv-analysis](../marine-offshore/viv-analysis/SKILL.md) — VIV assessment for risers
- [fitness-for-service](../asset-integrity/fitness-for-service/SKILL.md) — FFS assessment
- [structural-analysis](../marine-offshore/structural-analysis/SKILL.md) — Structural checks

## References

- DNV-RP-B401: Cathodic Protection Design
- DNV-RP-C205: Environmental Conditions and Environmental Loads
- API 579-1/ASME FFS-1: Fitness-for-Service
- API RP 16Q: Design, Selection, Operation, and Maintenance of Marine Drilling Riser Systems
