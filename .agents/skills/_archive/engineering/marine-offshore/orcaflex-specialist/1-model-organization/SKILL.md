---
name: orcaflex-specialist-1-model-organization
description: 'Sub-skill of orcaflex-specialist: 1. Model Organization (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Model Organization (+2)

## 1. Model Organization


```python
# Naming conventions
NAMING_CONVENTIONS = {
    'vessels': 'VesselName',  # e.g., 'FPSO', 'FSO_1'
    'lines': 'Mooring_N' or 'Riser_N',  # e.g., 'Mooring_1', 'Riser_2'
    'buoys': 'Buoy_N' or 'Subsurface_Buoy_N',
    '6d_buoys': '6DBuoy_N',
    'winches': 'Winch_N',
    'line_types': 'Descriptive_Name',  # e.g., 'R4_Studless_Chain', '76mm_Wire'
}

# Model structure best practices
MODEL_STRUCTURE = {
    'stages': [
        'Build-up',  # 100-200s
        'Main simulation',  # 3600-10800s
        'Optional: Transient event'
    ],
    'time_steps': {
        'inner': 0.01,  # 0.01-0.05s
        'log_sample': 0.1  # 0.1-1.0s
    }
}
```


## 2. Simulation Settings


```python
# Recommended simulation settings
SIMULATION_SETTINGS = {
    'implicit': {
        'use_variable_timestep': 'Yes',
        'target_log_sample_interval': 0.1,
        'inner_timestep': 0.01,
        'max_iterations': 20,
        'tolerance': 1e-6
    },
    'explicit': {
        'timestep': 0.001,  # Much smaller for explicit
        'log_sample_interval': 0.1
    }
}
```


## 3. Error Handling


```python
def safe_simulation_run(
    model: OrcFxAPI.Model,
    max_retries: int = 3
) -> bool:
    """
    Run simulation with error handling and retries.

    Args:
        model: OrcaFlex model
        max_retries: Maximum number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            model.RunSimulation()
            return True
        except OrcFxAPI.DynamicsError as e:
            print(f"Dynamics error (attempt {attempt+1}): {e}")
            # Try reducing time step
            current_dt = model.general.InnerTimeStep
            model.general.InnerTimeStep = current_dt * 0.5
            print(f"Reducing time step to {model.general.InnerTimeStep}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    return False
```
