---
name: qa-closure-step-3-invoke-domain-sme-skill
description: "Sub-skill of qa-closure: Step 3 \u2014 Invoke Domain SME Skill."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 3 — Invoke Domain SME Skill

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
