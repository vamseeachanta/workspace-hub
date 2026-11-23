---
name: paraview-interface-verify-data-range
description: 'Sub-skill of paraview-interface: Verify Data Range (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Verify Data Range (+2)

## Verify Data Range


```python
def validate_data_ranges(source, expected_ranges):
    """Validate that data arrays are within expected ranges.

    Args:
        source: ParaView source/filter
        expected_ranges: dict of {'array_name': (min, max)}
    """
    source.UpdatePipeline()
    data_info = source.GetDataInformation()
    checks = {"passed": True, "issues": []}

    for name, (exp_min, exp_max) in expected_ranges.items():
        array_info = data_info.GetArrayInformation(name, 0)  # 0=point, 1=cell
        if not array_info:
            array_info = data_info.GetArrayInformation(name, 1)
        if not array_info:
            checks["issues"].append(f"Array '{name}' not found")
            checks["passed"] = False
            continue

        data_range = array_info.GetComponentRange(0)
        if data_range[0] < exp_min * 0.5 or data_range[1] > exp_max * 2.0:
            checks["issues"].append(
                f"{name}: range [{data_range[0]:.3f}, {data_range[1]:.3f}] "
                f"outside expected [{exp_min}, {exp_max}]"
            )
            checks["passed"] = False

    return checks

# Example: validate typical CFD ranges
validate_data_ranges(reader, {
    'p': (-1e5, 1e5),       # Pressure (Pa, relative)
    'U': (-50, 50),          # Velocity (m/s)
    'k': (0, 100),           # Turbulent kinetic energy
    'omega': (0, 1e6),       # Specific dissipation rate
})
```


## Verify Screenshot Output


```python
import os

def validate_screenshots(output_dir, expected_count=1, min_size_kb=10):
    """Validate that screenshots were generated correctly."""
    checks = {"passed": True, "issues": [], "files": []}

    images = [f for f in os.listdir(output_dir)
              if f.endswith(('.png', '.jpg', '.tiff'))]

    if len(images) < expected_count:
        checks["issues"].append(
            f"Expected {expected_count} images, found {len(images)}"
        )
        checks["passed"] = False

    for img in images:
        path = os.path.join(output_dir, img)
        size_kb = os.path.getsize(path) / 1024
        checks["files"].append({"name": img, "size_kb": size_kb})
        if size_kb < min_size_kb:
            checks["issues"].append(f"{img}: {size_kb:.1f} KB — likely blank render")
            checks["passed"] = False

    return checks
```


## OpenFOAM Case Completeness Check


```python
def validate_openfoam_for_paraview(case_dir):
    """Check that OpenFOAM case is ready for ParaView visualization."""
    import os
    checks = {"passed": True, "issues": []}

    # Check polyMesh exists
    polymesh = os.path.join(case_dir, 'constant', 'polyMesh')
    if not os.path.isdir(polymesh):
        checks["issues"].append("No constant/polyMesh/ — mesh not generated")
        checks["passed"] = False

    # Check time directories
    time_dirs = [d for d in os.listdir(case_dir)
                 if d.replace('.', '').isdigit() and d != '0']
    if not time_dirs:
        checks["issues"].append("No result time directories — simulation not run")
        checks["passed"] = False
    else:
        checks["time_dirs"] = len(time_dirs)

    # Check for .foam file
    foam_files = [f for f in os.listdir(case_dir) if f.endswith('.foam')]
    if not foam_files:
        checks["issues"].append("No .foam file — create with: touch case.foam")

    return checks
```
