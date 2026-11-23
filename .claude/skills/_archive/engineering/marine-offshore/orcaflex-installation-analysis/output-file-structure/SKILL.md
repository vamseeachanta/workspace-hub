---
name: orcaflex-installation-analysis-output-file-structure
description: 'Sub-skill of orcaflex-installation-analysis: Output File Structure.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Output File Structure

## Output File Structure


```
results/installation/
├── _el_00000m.yml              # Reference depth, base orientation
├── _el_00000m_str_orentation.yml   # Reference depth, zero rotation
├── el_00000m.yml               # Final reference model
├── _el_-0010m.yml              # 10m below reference
├── _el_-0010m_str_orentation.yml
├── el_-0010m.yml
├── _el_-0020m.yml              # 20m below reference
├── _el_-0020m_str_orentation.yml
├── el_-0020m.yml
└── ...
```
