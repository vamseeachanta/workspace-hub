---
name: orcaflex-line-wizard-with-mooring-iteration
description: 'Sub-skill of orcaflex-line-wizard: With Mooring Iteration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# With Mooring Iteration (+1)

## With Mooring Iteration


```python
# Use Line Setup Wizard for initial configuration
# Then use mooring-iteration skill for fine-tuning

# Step 1: Line Setup Wizard for rough adjustment
model.general.LineSetupCalculationMode = "Calculate line lengths"
model["Line1"].LineSetupTargetValue = 800.0
model.InvokeLineSetupWizard()

# Step 2: Fine-tune with iteration skill
from digitalmodel.orcaflex.mooring_tension_iteration import MooringTensionIterator
iterator = MooringTensionIterator(config)
iterator.load_model("adjusted_model.dat")
result = iterator.iterate_to_targets()
```

## With Model Generator


```python
# Generate model from template
from digitalmodel.orcaflex.model_generator import generate_model

model = generate_model(
    template="mooring/spread_mooring",
    config=mooring_config,
    output="initial_model.yml"
)

# Use Line Setup Wizard to achieve target pretensions
import OrcFxAPI
ofx_model = OrcFxAPI.Model("initial_model.yml")
# Configure and run wizard...
```
