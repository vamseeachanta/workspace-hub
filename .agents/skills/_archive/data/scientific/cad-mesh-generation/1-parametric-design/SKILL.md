---
name: cad-mesh-generation-1-parametric-design
description: 'Sub-skill of cad-mesh-generation: 1. Parametric Design (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Parametric Design (+2)

## 1. Parametric Design


```python
from dataclasses import dataclass

@dataclass
class VesselDesignParameters:
    """Parametric vessel design."""
    length: float  # Overall length [m]
    beam: float  # Beam (width) [m]
    depth: float  # Depth [m]
    draft: float  # Design draft [m]
    bow_shape: str = 'straight'  # 'straight', 'raked', 'bulbous'
    stern_shape: str = 'transom'  # 'transom', 'cruiser'
    superstructure: bool = True

    def validate(self) -> bool:
        """Validate design parameters."""
        if self.draft > self.depth:
            raise ValueError("Draft cannot exceed depth")
        if self.beam > self.length:
            raise ValueError("Beam should not exceed length")
        return True
```


## 2. Mesh Size Optimization


```python
def calculate_optimal_mesh_size(
    geometry_length_scale: float,
    analysis_type: str,
    target_accuracy: str = 'medium'
) -> float:
    """
    Calculate optimal mesh size based on geometry and analysis type.

    Args:
        geometry_length_scale: Characteristic length [m]
        analysis_type: 'bem', 'fea_linear', 'fea_nonlinear', 'cfd'
        target_accuracy: 'coarse', 'medium', 'fine'

    Returns:
        Recommended element size [m]
    """
    # Base sizing ratios
    sizing_ratios = {
        'bem': {
            'coarse': 0.10,
            'medium': 0.05,
            'fine': 0.025
        },
        'fea_linear': {
            'coarse': 0.20,
            'medium': 0.10,
            'fine': 0.05
        },
        'fea_nonlinear': {
            'coarse': 0.10,
            'medium': 0.05,
            'fine': 0.025
        },
        'cfd': {
            'coarse': 0.15,
            'medium': 0.075,
            'fine': 0.0375
        }
    }

    ratio = sizing_ratios[analysis_type][target_accuracy]
    element_size = geometry_length_scale * ratio

    return element_size
```


## 3. Quality Checks


```python
def perform_mesh_quality_checks(
    mesh_file: Path,
    min_quality_threshold: float = 0.3
) -> bool:
    """
    Perform comprehensive mesh quality checks.

    Args:
        mesh_file: Mesh file path
        min_quality_threshold: Minimum acceptable quality

    Returns:
        True if mesh passes quality checks
    """
    quality = analyze_mesh_quality(mesh_file)

    checks = {
        'min_quality': quality['min_quality'] >= min_quality_threshold,
        'poor_elements': quality['poor_elements'] == 0,
        'element_count': quality['element_count'] > 0
    }

    passed = all(checks.values())

    if not passed:
        print("Mesh quality check FAILED:")
        for check_name, result in checks.items():
            status = "PASS" if result else "FAIL"
            print(f"  {check_name}: {status}")

    return passed
```
