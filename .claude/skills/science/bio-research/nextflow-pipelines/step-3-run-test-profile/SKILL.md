---
name: nextflow-pipelines-step-3-run-test-profile
description: 'Sub-skill of nextflow-pipelines: Step 3: Run Test Profile.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Step 3: Run Test Profile

## Step 3: Run Test Profile


**Validates environment with small data. MUST pass before real data.**

```bash
nextflow run nf-core/<pipeline> -r <version> -profile test,docker --outdir test_output
```

| Pipeline | Command |
|----------|---------|
| rnaseq | `nextflow run nf-core/rnaseq -r 3.22.2 -profile test,docker --outdir test_rnaseq` |
| sarek | `nextflow run nf-core/sarek -r 3.7.1 -profile test,docker --outdir test_sarek` |
| atacseq | `nextflow run nf-core/atacseq -r 2.1.2 -profile test,docker --outdir test_atacseq` |

Verify:
```bash
ls test_output/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

If test fails, see [references/troubleshooting.md](references/troubleshooting.md).

---
