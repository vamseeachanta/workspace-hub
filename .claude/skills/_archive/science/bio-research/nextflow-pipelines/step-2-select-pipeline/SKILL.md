---
name: nextflow-pipelines-step-2-select-pipeline
description: 'Sub-skill of nextflow-pipelines: Step 2: Select Pipeline.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Step 2: Select Pipeline

## Step 2: Select Pipeline


**DECISION POINT: Confirm with user before proceeding.**

| Data Type | Pipeline | Version | Goal |
|-----------|----------|---------|------|
| RNA-seq | `rnaseq` | 3.22.2 | Gene expression |
| WGS/WES | `sarek` | 3.7.1 | Variant calling |
| ATAC-seq | `atacseq` | 2.1.2 | Chromatin accessibility |

Auto-detect from data:
```bash
python scripts/detect_data_type.py /path/to/data
```

For pipeline-specific details:
- [references/pipelines/rnaseq.md](references/pipelines/rnaseq.md)
- [references/pipelines/sarek.md](references/pipelines/sarek.md)
- [references/pipelines/atacseq.md](references/pipelines/atacseq.md)

---
