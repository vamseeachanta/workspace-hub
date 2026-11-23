# WRK-5036: Doc-Extraction Skill — Implementation Plan

## Context

The workspace lacks a centralized content classification framework for engineering documents. Extraction is ad-hoc — `phase-b-extract.py` routes by file extension, `doc_to_context.py` provides format parsers, but neither classifies *what* is being extracted (constants vs equations vs tables vs procedures). This skill fills that gap with a 3-layer extraction taxonomy and domain-specific heuristics for CP and drilling-riser documents.

## Architecture: 3 Files (400-line limit)

```
.claude/skills/engineering/doc-extraction/
  SKILL.md                    # Layers 1+2: generic + engineering (~300-380 lines)
  cp/SKILL.md                 # Layer 3: CP domain sub-skill (~200-250 lines)
  drilling-riser/SKILL.md     # Layer 3: drilling-riser sub-skill (~200-250 lines)
```

**Rationale**: Single-file would hit ~700 lines. The split follows the existing pattern (`marine-offshore/cathodic-protection/` and `marine-offshore/viv-analysis/` as sibling directories).

## Layer 1: Content Type Classification (8 types)

| Type | Detection Heuristics | Key Extraction Fields |
|------|---------------------|----------------------|
| `constants` | Named values with units, "=" sign | name, symbol, value, units, source_standard |
| `equations` | Math notation, Greek letters, variables | name, expression, variables[], source |
| `tables` | Grid/tabular data, header rows, lookup values | title, columns[], rows, interpolation_method |
| `curves` | Figure refs, x-y axis labels, "Figure N" | title, x_axis, y_axis, data_points, source |
| `procedures` | Numbered steps, "shall"/"must", sequential | title, steps[], prerequisites, standard_ref |
| `requirements` | Normative language, "shall"/"required" | id, text, standard_ref, verification_method |
| `definitions` | "means", "is defined as", glossary format | term, definition, source, synonyms |
| `worked_examples` | "Example", given/find/solution pattern | title, given{}, solution_steps[], answer{} |

## Layer 2: Engineering Extraction Patterns

- Unit detection and normalization (SI/imperial/field)
- Standards reference parsing ("DNV-RP-B401 Section 3.4.6" → structured ref)
- Safety/design factor identification
- Material property recognition
- Condition/applicability tagging

## Layer 3: Domain Sub-Skills

**CP sub-skill** (aligned with `cathodic_protection.py` + DNV-RP-B401/F103):
- Anode formulae: mass, current capacity, utilisation factor, resistance
- Coating breakdown factors: f_ci, k, degradation model, category I/II/III
- Design life tables: years, temperature bands, environmental severity
- Current density values: mA/m², zonal (submerged/splash/atmospheric)

**Drilling-riser sub-skill** (aligned with `typical_riser_stack_up_calculations.py` + VIV skill):
- VIV parameters: Strouhal number, reduced velocity, lock-in, mode shapes
- Kill/choke line specs: ID/OD, pressure rating, burst/collapse, material grade
- BOP stack configurations: annular preventer, pipe/blind/shear rams, stack height

## Implementation Sequence (TDD)

### Step 1: Write tests (RED)
- **File**: `tests/skills/test_doc_extraction_skill.py`
- 11 tests covering all ACs:
  1. Main SKILL.md exists with required frontmatter
  2. All 8 content types defined
  3. Content types have detection heuristics
  4. CP sub-skill exists with keywords (anode, coating breakdown, current density, design life)
  5. Drilling-riser sub-skill exists with keywords (VIV, BOP, kill/choke)
  6. CP references DNV-RP-B401, DNV-RP-F103
  7. Drilling-riser references API RP 16Q or DNV-RP-C205
  8-10. All three files under 400 lines
  11. Main SKILL.md references both sub-skills

### Step 2: Create main SKILL.md (partial GREEN)
- Frontmatter + Layer 1 (8 content types) + Layer 2 (engineering patterns)
- Extraction workflow, output schema, sub-skill pointers

### Step 3: Create cp/SKILL.md (partial GREEN)
- CP-specific extraction heuristics aligned with `_B401_2021_*` constants

### Step 4: Create drilling-riser/SKILL.md (full GREEN)
- Drilling-riser extraction heuristics aligned with riser stack-up columns

### Step 5: Refactor + verify all tests pass

## Key Source Files

| Purpose | Path |
|---------|------|
| Skill format reference | `.claude/skills/engineering/asset-integrity/fitness-for-service/SKILL.md` |
| CP module | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py` |
| CP constants | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cp_DNV_RP_B401_2021.py` |
| Riser stack-up | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/typical_riser_stack_up_calculations.py` |
| VIV skill | `.claude/skills/engineering/marine-offshore/viv-analysis/SKILL.md` |
| Existing extraction | `scripts/utilities/doc-to-context/src/doc_to_context.py` |

## Verification

```bash
uv run --no-project python -m pytest tests/skills/test_doc_extraction_skill.py -v
```

## Scope Boundary

**In scope**: Skill files (SKILL.md) defining extraction taxonomy and heuristics.
**Out of scope**: Code changes to `doc_to_context.py`, new Python extraction functions, runtime classification engine. Those are future work.
