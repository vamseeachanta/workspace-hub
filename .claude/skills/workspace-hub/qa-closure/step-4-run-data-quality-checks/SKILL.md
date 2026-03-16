---
name: qa-closure-step-4-run-data-quality-checks
description: "Sub-skill of qa-closure: Step 4 \u2014 Run Data Quality Checks."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 4 — Run Data Quality Checks

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
