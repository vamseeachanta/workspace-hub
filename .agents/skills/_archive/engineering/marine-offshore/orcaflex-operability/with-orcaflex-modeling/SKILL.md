---
name: orcaflex-operability-with-orcaflex-modeling
description: 'Sub-skill of orcaflex-operability: With OrcaFlex Modeling (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# With OrcaFlex Modeling (+1)

## With OrcaFlex Modeling


```python
# 1. Run simulations for multiple headings
from digitalmodel.orcaflex.universal import UniversalOrcaFlexRunner

runner = UniversalOrcaFlexRunner()
for heading in range(0, 360, 15):
    runner.run_single(f"mooring_heading_{heading}.yml")

# 2. Run operability analysis
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer

analyzer = OperabilityAnalyzer(simulation_directory="results/.sim/")
analyzer.generate_comprehensive_report(...)
```

## With Post-Processing


```python
# Use OPP for detailed extraction, then operability for envelope
from digitalmodel.orcaflex.opp import OrcaFlexPostProcess
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer

# Extract detailed statistics
opp = OrcaFlexPostProcess()
stats = opp.extract_summary_statistics(...)

# Generate operability envelope
analyzer = OperabilityAnalyzer(...)
envelope = analyzer.generate_operability_envelope(...)
```
