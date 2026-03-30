---
name: nextflow-pipelines-check-completion
description: 'Sub-skill of nextflow-pipelines: Check completion (+1).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Check completion (+1)

## Check completion


```bash
ls results/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

## Key outputs by pipeline


**rnaseq:**
- `results/star_salmon/salmon.merged.gene_counts.tsv` - Gene counts
- `results/star_salmon/salmon.merged.gene_tpm.tsv` - TPM values

**sarek:**
- `results/variant_calling/*/` - VCF files
- `results/preprocessing/recalibrated/` - BAM files

**atacseq:**
- `results/macs2/narrowPeak/` - Peak calls
- `results/bwa/mergedLibrary/bigwig/` - Coverage tracks

---
