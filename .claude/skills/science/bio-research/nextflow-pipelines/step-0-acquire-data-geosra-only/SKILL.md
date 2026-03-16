---
name: nextflow-pipelines-step-0-acquire-data-geosra-only
description: 'Sub-skill of nextflow-pipelines: Step 0: Acquire Data (GEO/SRA Only).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Step 0: Acquire Data (GEO/SRA Only)

## Step 0: Acquire Data (GEO/SRA Only)


**Skip this step if user has local FASTQ files.**

For public datasets, fetch from GEO/SRA first. See [references/geo-sra-acquisition.md](references/geo-sra-acquisition.md) for the full workflow.

**Quick start:**

```bash
# 1. Get study info
python scripts/sra_geo_fetch.py info GSE110004

# 2. Download (interactive mode)
python scripts/sra_geo_fetch.py download GSE110004 -o ./fastq -i

# 3. Generate samplesheet
python scripts/sra_geo_fetch.py samplesheet GSE110004 --fastq-dir ./fastq -o samplesheet.csv
```

**DECISION POINT:** After fetching study info, confirm with user:
- Which sample subset to download (if multiple data types)
- Suggested genome and pipeline

Then continue to Step 1.

---
