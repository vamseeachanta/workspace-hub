---
name: qa-closure-step-2-generate-html-report
description: "Sub-skill of qa-closure: Step 2 \u2014 Generate HTML Report."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 2 — Generate HTML Report

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
