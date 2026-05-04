---
name: orcaflex-modal-analysis-mode-shapes-csv
description: 'Sub-skill of orcaflex-modal-analysis: Mode Shapes CSV (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Mode Shapes CSV (+2)

## Mode Shapes CSV


```csv
modeIndex,name,node,dof,shapeWrtGlobal
0,Riser1,1,X,0.0012
0,Riser1,1,Y,0.0001
0,Riser1,1,Z,0.8523
0,Riser1,2,X,0.0015
...
```

## Mode Summary CSV


```csv
modeIndex,period,name,abs_max_dof,max_dof_values,max_dof_nodes,max_dof_percentages,modes_selected
0,8.523,Riser1,0.852,{'X': 0.001, 'Y': 0.0, 'Z': 0.852},{'X': 1, 'Y': 1, 'Z': 75},{'X': 0.1, 'Y': 0.0, 'Z': 99.8},{'X': False, 'Y': False, 'Z': True}
1,5.234,Riser1,0.723,{'X': 0.723, 'Y': 0.001, 'Z': 0.05},{'X': 50, 'Y': 1, 'Z': 1},{'X': 99.5, 'Y': 0.1, 'Z': 0.4},{'X': True, 'Y': False, 'Z': False}
```

## DOF-Filtered Summary


Output file: `{model_name}_modes_summary_{dof}.csv`

Contains only modes where the specified DOF exceeds the threshold percentage.
