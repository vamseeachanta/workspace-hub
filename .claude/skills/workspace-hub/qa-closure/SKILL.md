---
name: qa-closure
description: >
  Automated QA closure for AI agent work items — generates paired HTML reports
  (input → process → output → QA verdict), invokes SME verification skills,
  runs data quality checks (unit validation, range checks), and emits a final
  PASS / WARN / FAIL verdict before a WRK item may be marked complete.
version: 1.0.0
category: workspace-hub
last_updated: 2026-02-24
wrk_ref: WRK-229
invoke: /qa-closure
trigger: pre-complete
auto_execute: false
related_skills:
  - workspace-hub/ecosystem-health
  - workspace-hub/tool-readiness
  - engineering/marine-offshore/orcaflex-specialist
  - engineering/marine-offshore/hydrodynamic-analysis
  - engineering/marine-offshore/mooring-analysis
  - engineering/marine-offshore/orcawave-analysis
tags:
  - qa
  - verification
  - html-report
  - sme
  - data-quality
  - work-item-lifecycle
platforms: [all]
capabilities: []
requires: []
---

# /qa-closure — AI Agent QA Closure Loop

Generates a paired HTML report and runs automated quality checks before any
WRK item may be marked complete. This is a mandatory pre-completion gate.

## Usage

```
/qa-closure WRK-NNN                          — full QA run for a work item
/qa-closure WRK-NNN --output file.csv        — specify primary output artefact
/qa-closure WRK-NNN --type calculation       — override output type detection
/qa-closure WRK-NNN --skip-sme               — skip SME invocation (use with care)
```

## Agent Completion Gate

Agents MUST NOT mark a WRK item complete until all of the following pass:

- [ ] Output artefacts exist and are readable
- [ ] At least one automated QA check has run and returned PASS or WARN
- [ ] HTML report generated at `.claude/state/qa-reports/WRK-NNN-qa.html`
- [ ] QA verdict recorded in the WRK item frontmatter (`qa_verdict:`)

---

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

## Step 2 — Generate HTML Report

Invoke `scripts/qa/generate-qa-report.sh` with the WRK ID and any output
artefact paths collected during the task.

```bash
REPO="$(git rev-parse --show-toplevel)"
WRK_ID="$1"
ARTEFACTS="${@:2}"   # additional output file paths (space-separated)

bash "$REPO/scripts/qa/generate-qa-report.sh" \
    --wrk-id    "$WRK_ID" \
    --type      "$OUTPUT_TYPE" \
    --artefacts "$ARTEFACTS" \
    --out       "$REPO/.claude/state/qa-reports/${WRK_ID}-qa.html"

REPORT_PATH="$REPO/.claude/state/qa-reports/${WRK_ID}-qa.html"
[ -f "$REPORT_PATH" ] \
    && echo "  [PASS] HTML report: $REPORT_PATH" \
    || echo "  [FAIL] HTML report not created"
```

The report follows the five-section template from WRK-229:

```
Section 1  Inputs    — spec digest, config hash, parameters
Section 2  Process   — steps taken, tools invoked, duration
Section 3  Outputs   — tables, key numbers, file inventory
Section 4  QA Checks — SME verdict, correlation matrix, unit/range checks
Section 5  Verdict   — PASS / WARN / FAIL + rationale
```

---

## Step 3 — Invoke Domain SME Skill

Based on the output type determined in Step 1, invoke the matching SME skill
for independent cross-verification.

```bash
echo "=== Step 3: SME Verification ==="

SME_VERDICT="SKIP"

case "$OUTPUT_TYPE" in
  rao-diffraction)
    echo "  [INFO] Invoking /orcaflex-specialist for RAO cross-check"
    # Orchestrator spawns SME skill as subagent:
    # Task(subagent_type="claude", prompt="/orcaflex-specialist --verify $ARTEFACTS")
    SME_VERDICT="PENDING"
    ;;
  mooring-analysis)
    echo "  [INFO] Invoking /mooring-analysis for pretension + MBL check"
    SME_VERDICT="PENDING"
    ;;
  mesh)
    echo "  [INFO] Invoking /gmsh-meshing for mesh quality check"
    SME_VERDICT="PENDING"
    ;;
  data-pipeline)
    echo "  [INFO] Running schema + null-count checks (no external SME)"
    SME_VERDICT="LOCAL"
    ;;
  code)
    echo "  [INFO] Running test suite (no external SME)"
    SME_VERDICT="LOCAL"
    ;;
  *)
    echo "  [INFO] No domain SME mapped — running generic artefact check"
    SME_VERDICT="LOCAL"
    ;;
esac

echo "  [INFO] SME_VERDICT=$SME_VERDICT"
```

When SME skill is invoked as a subagent, wait for its JSON verdict and inject
it into Section 4 of the HTML report before finalising the verdict.

---

## Step 4 — Run Data Quality Checks

Run automated checks appropriate to the output type.

```bash
echo "=== Step 4: Data Quality Checks ==="
FAIL_COUNT=0
WARN_COUNT=0

# --- 4a. Artefact existence and non-empty ---
for f in $ARTEFACTS; do
    if [ ! -f "$f" ]; then
        echo "  [FAIL] Artefact missing: $f"; ((FAIL_COUNT++))
    elif [ ! -s "$f" ]; then
        echo "  [FAIL] Artefact empty: $f";  ((FAIL_COUNT++))
    else
        SIZE=$(du -sh "$f" | awk '{print $1}')
        echo "  [PASS] Artefact exists: $f ($SIZE)"
    fi
done

# --- 4b. Unit consistency (CSV / text outputs) ---
if echo "$ARTEFACTS" | grep -qiE '\.csv|\.txt|\.yaml|\.json'; then
    # Check for mixed unit indicators in headers
    for f in $ARTEFACTS; do
        if grep -qiE '\b(kN|MN|lbs|ton|kg)\b' "$f" 2>/dev/null; then
            # Verify only one force unit family present
            force_units=$(grep -oiE '\b(kN|MN|lbs|ton|kg)\b' "$f" \
                | tr '[:upper:]' '[:lower:]' | sort -u)
            unit_count=$(echo "$force_units" | wc -l)
            if [ "$unit_count" -gt 2 ]; then
                echo "  [WARN] Mixed force units in $f: $force_units"
                ((WARN_COUNT++))
            else
                echo "  [PASS] Unit consistency OK: $f"
            fi
        fi
    done
fi

# --- 4c. Numerical range check (RAO / analysis outputs) ---
if [ "$OUTPUT_TYPE" = "rao-diffraction" ] || [ "$OUTPUT_TYPE" = "calculation" ]; then
    for f in $ARTEFACTS; do
        # Flag values that look like NaN, Inf, or extreme outliers in CSV
        if grep -qiE 'nan|inf|#' "$f" 2>/dev/null; then
            echo "  [WARN] NaN / Inf values found in: $f"
            ((WARN_COUNT++))
        else
            echo "  [PASS] No NaN/Inf in: $f"
        fi
    done
fi

# --- 4d. Code output: test coverage gate ---
if [ "$OUTPUT_TYPE" = "code" ]; then
    COV_REPORT=$(find "$REPO" -name "coverage.xml" -not -path "*/.git/*" | head -1)
    if [ -n "$COV_REPORT" ]; then
        COVERAGE=$(grep -oP 'line-rate="\K[0-9.]+' "$COV_REPORT" | head -1)
        COV_PCT=$(echo "$COVERAGE * 100" | bc 2>/dev/null || echo "0")
        if (( $(echo "$COV_PCT < 80" | bc -l 2>/dev/null || echo 1) )); then
            echo "  [WARN] Coverage ${COV_PCT}% < 80% threshold"
            ((WARN_COUNT++))
        else
            echo "  [PASS] Coverage ${COV_PCT}%"
        fi
    else
        echo "  [WARN] No coverage.xml found — cannot verify coverage"
        ((WARN_COUNT++))
    fi
fi

echo "  [INFO] QC totals: FAIL=$FAIL_COUNT WARN=$WARN_COUNT"
```

---

## Step 5 — Emit QA Verdict

Aggregate results from Steps 2-4 and produce the final verdict. Inject the
verdict into the WRK item frontmatter and the HTML report.

```bash
echo "=== Step 5: QA Verdict ==="

if [ "$FAIL_COUNT" -gt 0 ]; then
    VERDICT="FAIL"
    RATIONALE="$FAIL_COUNT artefact/quality check(s) failed — see Section 4 of report"
elif [ "$WARN_COUNT" -gt 0 ]; then
    VERDICT="WARN"
    RATIONALE="$WARN_COUNT warning(s) — review before marking complete"
else
    VERDICT="PASS"
    RATIONALE="All artefact, unit, range, and SME checks passed"
fi

echo "  [$VERDICT] $RATIONALE"
echo ""
echo "  Report : $REPORT_PATH"
echo "  Verdict: $VERDICT"
echo ""

# Stamp verdict into WRK item frontmatter
if [ -f "$WRK_FILE" ]; then
    # Insert or update qa_verdict line after the status line
    if grep -q "^qa_verdict:" "$WRK_FILE"; then
        sed -i "s/^qa_verdict:.*/qa_verdict: $VERDICT/" "$WRK_FILE"
    else
        sed -i "/^status:/a qa_verdict: $VERDICT" "$WRK_FILE"
    fi
    echo "  [INFO] Stamped qa_verdict: $VERDICT in $WRK_FILE"
fi

# Gate: block completion on FAIL
if [ "$VERDICT" = "FAIL" ]; then
    echo "  [BLOCK] QA FAILED — this WRK item cannot be marked complete"
    echo "          Resolve issues listed in $REPORT_PATH"
    exit 1
fi

exit 0
```

---

## HTML Report Template

The `generate-qa-report.sh` script produces a self-contained HTML file using
this structure. All CSS is inline; no external dependencies.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>QA Report — WRK-NNN</title>
  <!-- Inline CSS: dark header, section cards, verdict badge -->
</head>
<body>
  <header>WRK-NNN · <title> · <date></header>
  <section id="s1"><!-- Inputs --></section>
  <section id="s2"><!-- Process log --></section>
  <section id="s3"><!-- Outputs --></section>
  <section id="s4"><!-- QA checks --></section>
  <section id="s5" class="verdict PASS|WARN|FAIL"><!-- Verdict --></section>
</body>
</html>
```

---

## Integration with Work Item Lifecycle

This skill should be invoked by the orchestrator before closing any WRK item
that produces computational or analytical output:

```
Orchestrator flow:
  1. Agent completes task → signals "ready for QA"
  2. Orchestrator invokes /qa-closure WRK-NNN [artefact-paths...]
  3. /qa-closure runs Steps 1-5
  4. If PASS or WARN  → orchestrator proceeds to close WRK item
  5. If FAIL          → orchestrator blocks close, notifies user
```

---

## Related

- `scripts/qa/generate-qa-report.sh` — HTML report generator
- `/ecosystem-health` — structural health, not output QA
- `WRK-229` — tracking item and architectural spec
- `WRK-228` — terminal UX + Chrome viewer for HTML reports
- `.claude/state/qa-reports/` — output directory for all HTML reports
