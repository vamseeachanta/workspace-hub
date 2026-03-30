---
name: nextflow-pipelines-5a-check-genome-availability
description: 'Sub-skill of nextflow-pipelines: 5a. Check genome availability (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# 5a. Check genome availability (+2)

## 5a. Check genome availability


```bash
python scripts/manage_genomes.py check <genome>
# If not installed:
python scripts/manage_genomes.py download <genome>
```

Common genomes: GRCh38 (human), GRCh37 (legacy), GRCm39 (mouse), R64-1-1 (yeast), BDGP6 (fly)

## 5b. Decision points


**DECISION POINT: Confirm with user:**

1. **Genome:** Which reference to use
2. **Pipeline-specific options:**
   - **rnaseq:** aligner (star_salmon recommended, hisat2 for low memory)
   - **sarek:** tools (haplotypecaller for germline, mutect2 for somatic)
   - **atacseq:** read_length (50, 75, 100, or 150)

## 5c. Run pipeline


```bash
nextflow run nf-core/<pipeline> \
    -r <version> \
    -profile docker \
    --input samplesheet.csv \
    --outdir results \
    --genome <genome> \
    -resume
```


*See sub-skills for full details.*
