---
name: qa-closure-step-5-emit-qa-verdict
description: "Sub-skill of qa-closure: Step 5 \u2014 Emit QA Verdict."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 5 — Emit QA Verdict

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
