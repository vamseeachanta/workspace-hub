---
name: nextflow-pipelines-generate-automatically
description: 'Sub-skill of nextflow-pipelines: Generate automatically (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Generate automatically (+2)

## Generate automatically


```bash
python scripts/generate_samplesheet.py /path/to/data <pipeline> -o samplesheet.csv
```

The script:
- Discovers FASTQ/BAM/CRAM files
- Pairs R1/R2 reads
- Infers sample metadata
- Validates before writing

**For sarek:** Script prompts for tumor/normal status if not auto-detected.

## Validate existing samplesheet


```bash
python scripts/generate_samplesheet.py --validate samplesheet.csv <pipeline>
```

## Samplesheet formats


**rnaseq:**
```csv
sample,fastq_1,fastq_2,strandedness
SAMPLE1,/abs/path/R1.fq.gz,/abs/path/R2.fq.gz,auto
```

**sarek:**
```csv
patient,sample,lane,fastq_1,fastq_2,status
patient1,tumor,L001,/abs/path/tumor_R1.fq.gz,/abs/path/tumor_R2.fq.gz,1

*See sub-skills for full details.*
