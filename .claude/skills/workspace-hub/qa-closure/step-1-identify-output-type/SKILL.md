---
name: qa-closure-step-1-identify-output-type
description: "Sub-skill of qa-closure: Step 1 \u2014 Identify Output Type."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 1 — Identify Output Type

## Step 1 — Identify Output Type


Classify the work item's primary output to select the correct QA checks and
SME skill.

```bash
REPO="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?WRK item ID required}"
WRK_FILE="$REPO/.claude/work-queue/pending/$WRK_ID.md"
[ -f "$WRK_FILE" ] || WRK_FILE="$REPO/.claude/work-queue/working/$WRK_ID.md"

# Read area and title from frontmatter
AREA=$(grep "^area:" "$WRK_FILE" | awk '{print $2}')
TITLE=$(grep "^title:" "$WRK_FILE" | sed 's/^title: //')

# Classify output type
OUTPUT_TYPE="generic"
case "$AREA" in
  marine-offshore|hydrodynamics|mooring)  OUTPUT_TYPE="rao-diffraction" ;;
  meshing|cad)                             OUTPUT_TYPE="mesh" ;;
  data-pipeline|data-science)             OUTPUT_TYPE="data-pipeline" ;;
  analysis|calculation|engineering)       OUTPUT_TYPE="calculation" ;;
  code|development|testing)               OUTPUT_TYPE="code" ;;
esac

echo "  [INFO] WRK=$WRK_ID  AREA=$AREA  TYPE=$OUTPUT_TYPE"
```

Output type → SME skill mapping:

| Type | SME Skill | QA Checks |
|------|-----------|-----------|
| `rao-diffraction` | `orcaflex-specialist`, `hydrodynamic-analysis` | unit check, RAO range, symmetry |
| `mooring-analysis` | `mooring-analysis`, `mooring-design` | pretension, MBL %, offsets |
| `mesh` | `gmsh-meshing` | element count, aspect ratio, watertight |
| `data-pipeline` | `polars` / `pandas` skill | null count, schema, row count |
| `calculation` | `hydrodynamic-analysis` | unit consistency, value range |
| `code` | none (run tests) | test coverage, lint score |
| `generic` | none | artefact existence, size > 0 |

---
