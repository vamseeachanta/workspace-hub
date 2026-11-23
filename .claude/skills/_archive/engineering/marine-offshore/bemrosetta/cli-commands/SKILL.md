---
name: bemrosetta-cli-commands
description: 'Sub-skill of bemrosetta: CLI Commands.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Commands

## CLI Commands


```bash
# Convert AQWA to OrcaFlex
bemrosetta convert analysis.LIS -o ./output

# Convert with QTF data
bemrosetta convert analysis.LIS --qtf analysis.QTF -o ./output

# Display file information
bemrosetta info analysis.LIS

# Validate coefficients
bemrosetta validate analysis.LIS --strict --causality

# Convert mesh formats
bemrosetta convert-mesh input.gdf -o output.stl
bemrosetta convert-mesh input.dat -o output.gdf

# Validate mesh quality
bemrosetta validate-mesh hull.gdf --check-normals

# Show module status
bemrosetta status
```
