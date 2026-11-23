---
name: doc-extraction-1-constants-0-yield-not-yet-implemented
description: "Sub-skill of doc-extraction: 1. `constants` (0% yield \u2014 not yet\
  \ implemented) (+7)."
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. `constants` (0% yield — not yet implemented) (+7)

## 1. `constants` (0% yield — not yet implemented)


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


## 2. `equations` (0% yield — not yet implemented)


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


## 3. `tables`


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


## 4. `curves`


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


## 5. `procedures` (0% yield — not yet implemented)


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


## 6. `requirements`


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


## 7. `definitions`


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


## 8. `worked_examples` (0% yield — not yet implemented)


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
